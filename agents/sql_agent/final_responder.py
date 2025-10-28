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

execution_tools = McpToolset(
    connection_params=mcp_connection_params,
    tool_filter=['execute_sql']
)

final_responder = LlmAgent(
    model="gemini-2.5-pro",
    name="final_responder",
    description="Executes the final SQL and answers the user's question.",
    instruction="""
You are the Final Responder.
Read `sql_is_valid` from session state.
If `sql_is_valid` is true:
  1. Read `valid_sql` from session state.
  2. Call `execute_sql` with `valid_sql` (ensure `dry_run` is False or omitted).
  3. Answer the user's original question based on the data returned by `execute_sql`.
  4. ALWAYS include the executed SQL query in your final response, formatted in a markdown code block.
If `sql_is_valid` is false or missing (loop failed to converge):
  1. Apologize to the user and explain that you could not generate a valid query.
  2. Provide the last `candidate_sql` and the `guidance` (error message) from session state to help them understand what went wrong.
""",
    tools=[execution_tools]
)