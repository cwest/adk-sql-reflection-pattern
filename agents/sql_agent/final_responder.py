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

from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool.mcp_toolset import McpToolset
from .config import mcp_connection_params

def create_final_responder():
    sql_tools = McpToolset(
        connection_params=mcp_connection_params,
        tool_filter=['execute_sql']
    )

    return LlmAgent(
        model="gemini-2.5-pro",
        name="final_responder",
        description="Executes the final SQL and responds to the user.",
        instruction="""
You are the Final Responder.
Read the `valid_sql` from the session state.
Execute the SQL using the `execute_sql` tool with `dry_run=False`.
Format the results in a clear, human-readable way.
Present the formatted results to the user as your final answer.
""",
        tools=[sql_tools]
    )

final_responder = create_final_responder()