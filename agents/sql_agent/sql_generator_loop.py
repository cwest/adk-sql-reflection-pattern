# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from google.adk.agents import LoopAgent, LlmAgent
from google.adk.tools.mcp_tool.mcp_toolset import McpToolset
from google.adk.tools.tool_context import ToolContext
from .config import mcp_connection_params, DATAPLEX_ENABLED
from .prompts import (
    GENERATOR_SYSTEM_PROMPT,
    VALIDATOR_SYSTEM_PROMPT,
    REVIEWER_SYSTEM_PROMPT
)

def create_sql_generator_loop():
    sql_tools = McpToolset(
        connection_params=mcp_connection_params,
        tool_filter=['execute_sql']
    )

    def report_validation_result(
        valid: bool, guidance: str = "", tool_context: ToolContext = None
    ) -> str:
        """
        Reports the validation result, updates session state, and controls the loop.
        Args:
            valid: Whether the SQL is valid based on the dry run.
            guidance: Specific guidance for fixing the SQL if it is invalid.
        """
        if valid:
            tool_context.state['valid_sql'] = tool_context.state.get('sql')
            tool_context.state['guidance'] = None
            tool_context.actions.escalate = True  # Exit loop on success
            return "SQL is valid. Exiting loop."
        else:
            tool_context.state['guidance'] = guidance
            return f"SQL is invalid. Guidance for next loop: {guidance}"

    generator_instruction = GENERATOR_SYSTEM_PROMPT
    if DATAPLEX_ENABLED:
        generator_instruction += """
Read the `semantic_context` from the session state and use it to generate a more accurate query.
"""
    generator_instruction += """
You are the SQL Generator.
Read the `schema` from the session state.
Read `guidance` from session state. If it exists, use it to fix your previous query.
Generate a BigQuery SQL query for the user's question.
Output ONLY the SQL query in a markdown code block.
"""

    generator = LlmAgent(
        model="gemini-2.5-pro",
        name="sql_generator",
        description="Generates BigQuery SQL.",
        output_key="sql",
        instruction=generator_instruction,
    )

    validator = LlmAgent(
        model="gemini-2.5-flash",
        name="sql_validator",
        description="Validates BigQuery SQL.",
        output_key="validation_result",
        instruction=VALIDATOR_SYSTEM_PROMPT,
        tools=[sql_tools]
    )

    reviewer = LlmAgent(
        model="gemini-2.5-flash",
        name="sql_reviewer",
        description="Reviews SQL validation results and provides guidance.",
        instruction=REVIEWER_SYSTEM_PROMPT,
        tools=[report_validation_result]
    )

    return LoopAgent(
        name="sql_loop",
        description="A loop that generates and validates SQL until it is correct.",
        sub_agents=[generator, validator, reviewer],
        max_iterations=5
    )

sql_generator_loop = create_sql_generator_loop()
