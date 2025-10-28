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
from .schema_inspector import schema_inspector
from .sql_generator_loop import sql_generator_loop
from .final_responder import final_responder

root_agent = SequentialAgent(
    name="sql_agent",
    description="An agent that can answer questions about Google Trends data using BigQuery.",
    sub_agents=[schema_inspector, sql_generator_loop, final_responder]
)