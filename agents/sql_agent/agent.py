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

from google.adk.agents import SequentialAgent
from .config import DATAPLEX_ENABLED
from .schema_inspector import create_schema_inspector
from .semantic_enricher import create_semantic_enricher
from .sql_generator_loop import create_sql_generator_loop
from .final_responder import create_final_responder

def create_root_agent():
    sub_agents = [
        create_schema_inspector(),
        create_sql_generator_loop(),
        create_final_responder()
    ]
    if DATAPLEX_ENABLED:
        sub_agents.insert(0, create_semantic_enricher())

    return SequentialAgent(
        name="sql_agent",
        description="An agent that can answer questions about Google Trends data using BigQuery.",
        sub_agents=sub_agents
    )

root_agent = create_root_agent()