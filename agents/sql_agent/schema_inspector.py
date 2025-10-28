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

schema_tools = McpToolset(
    connection_params=mcp_connection_params,
    tool_filter=['list_tables', 'get_table_info']
)

schema_inspector = LlmAgent(
    model="gemini-2.5-pro",
    name="schema_inspector",
    description="Inspects the BigQuery dataset schema.",
    output_key="schema",
    instruction="""
You are a schema inspection agent. Your ONLY goal is to retrieve and output the complete schema for the `bigquery-public-data.google_trends` dataset.
IGNORE any user question or input. Focus ONLY on retrieving the schema.

Follow these steps:
1. Use the `list_tables` tool to find all tables in the `google_trends` dataset.
2. For every table found, use the `get_table_info` tool to retrieve its detailed schema (columns, data types).
3. Consolidate all table schemas into a single JSON object where keys are table names and values are their schemas.
4. Output ONLY this JSON object as your final response. Do not include any other text.
""",
    tools=[schema_tools]
)