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
from .config import mcp_connection_params, DATAPLEX_ENABLED
from .prompts import (
    SCHEMA_INSPECTOR_DATAPLEX_PROMPT,
    SCHEMA_INSPECTOR_DEFAULT_PROMPT
)

def create_schema_inspector():
    schema_tools = McpToolset(
        connection_params=mcp_connection_params,
        tool_filter=['list_tables', 'get_table_info']
    )

    instruction = (
        SCHEMA_INSPECTOR_DATAPLEX_PROMPT
        if DATAPLEX_ENABLED
        else SCHEMA_INSPECTOR_DEFAULT_PROMPT
    )

    return LlmAgent(
        model="gemini-2.5-pro",
        name="schema_inspector",
        description="Inspects the BigQuery dataset schema.",
        output_key="schema",
        instruction=instruction,
        tools=[schema_tools]
    )

schema_inspector = create_schema_inspector()