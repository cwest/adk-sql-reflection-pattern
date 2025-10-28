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

import pytest
from agents.sql_agent.agent import root_agent
from google.adk.agents import SequentialAgent, LoopAgent, LlmAgent

def test_root_agent_structure():
    assert isinstance(root_agent, SequentialAgent)
    assert len(root_agent.sub_agents) == 3
    assert root_agent.sub_agents[0].name == "schema_inspector"
    assert root_agent.sub_agents[1].name == "sql_loop"
    assert root_agent.sub_agents[2].name == "final_responder"

def test_loop_agent_structure():
    loop_agent = root_agent.sub_agents[1]
    assert isinstance(loop_agent, LoopAgent)
    assert len(loop_agent.sub_agents) == 3
    assert loop_agent.sub_agents[0].name == "sql_generator"
    assert loop_agent.sub_agents[1].name == "sql_validator"
    assert loop_agent.sub_agents[2].name == "sql_reviewer"

def test_schema_inspector_config():
    inspector = root_agent.sub_agents[0]
    assert isinstance(inspector, LlmAgent)
    assert inspector.output_key == "schema"
    assert len(inspector.tools) == 1 # MCPToolset

def test_final_responder_config():
    responder = root_agent.sub_agents[2]
    assert isinstance(responder, LlmAgent)
    assert len(responder.tools) == 1 # MCPToolset
