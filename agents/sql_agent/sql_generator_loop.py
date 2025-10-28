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
from .config import mcp_connection_params
from .prompts import GENERATOR_SYSTEM_PROMPT

# --- Generator Agent ---
generator = LlmAgent(
    model="gemini-2.5-pro",
    name="sql_generator",
    output_key="candidate_sql",
    instruction=GENERATOR_SYSTEM_PROMPT + """
You are the SQL Generator.
Read the `schema` from the session state.
Read `guidance` from session state. If it exists, use it to fix your previous query.
Generate a BigQuery SQL query for the user's question.
Output ONLY the SQL query in a markdown code block.
"""
)

# --- Validator Agent ---
validator_tools = McpToolset(
    connection_params=mcp_connection_params,
    tool_filter=['execute_sql']
)

validator = LlmAgent(
    model="gemini-2.5-pro",
    name="sql_validator",
    output_key="dry_run_result",
    instruction="""
You are the SQL Validator.
Read the `candidate_sql` from the session state.
Extract the SQL from the markdown code block if present.
Call the `execute_sql` tool with the extracted SQL and `dry_run=True`.
Output the result of the dry run exactly as returned by the tool.
""",
    tools=[validator_tools]
)

# --- Reviewer Agent ---
def report_validation_result(valid: bool, guidance: str = "", tool_context: ToolContext = None) -> str:
    """
    Reports the validation result.
    Args:
        valid: Whether the SQL is valid based on the dry run.
        guidance: Specific guidance for fixing the SQL if it is invalid.
    """
    tool_context.state['sql_is_valid'] = valid
    if valid:
        tool_context.state['valid_sql'] = tool_context.state.get('candidate_sql')
        tool_context.state['guidance'] = None
        tool_context.actions.escalate = True # Exit loop on success
        return "SQL is valid. Exiting loop."
    else:
        tool_context.state['guidance'] = guidance
        return f"SQL is invalid. Guidance recorded."

reviewer_llm = LlmAgent(
    model="gemini-2.5-pro",
    name="sql_reviewer",
    instruction="""
You are the SQL Reviewer.
Read the `dry_run_result` from session state.
Determine if the SQL is valid based on the dry run result.
Call the `report_validation_result` tool with your determination.
""",
    tools=[report_validation_result]
)

# --- Loop Agent ---
sql_generator_loop = LoopAgent(
    name="sql_loop",
    sub_agents=[generator, validator, reviewer_llm],
    max_iterations=3
)
