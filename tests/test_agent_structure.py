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

import importlib
import pytest
from google.adk.agents import SequentialAgent, LoopAgent, LlmAgent

@pytest.fixture
def agent_modules():
    from agents.sql_agent import agent, config
    return agent, config

def test_root_agent_structure_dataplex_disabled(monkeypatch, agent_modules):
    agent_module, config_module = agent_modules
    monkeypatch.setenv("DATAPLEX_ENABLED", "false")
    importlib.reload(config_module)
    importlib.reload(agent_module)
    root_agent = agent_module.create_root_agent()

    assert isinstance(root_agent, SequentialAgent)
    assert len(root_agent.sub_agents) == 3
    assert root_agent.sub_agents[0].name == "schema_inspector"
    assert root_agent.sub_agents[1].name == "sql_loop"
    assert root_agent.sub_agents[2].name == "final_responder"

def test_root_agent_structure_dataplex_enabled(monkeypatch, agent_modules):
    agent_module, config_module = agent_modules
    monkeypatch.setenv("DATAPLEX_ENABLED", "true")
    importlib.reload(config_module)
    importlib.reload(agent_module)
    root_agent = agent_module.create_root_agent()

    assert isinstance(root_agent, SequentialAgent)
    assert len(root_agent.sub_agents) == 4
    assert root_agent.sub_agents[0].name == "semantic_enricher"
    assert root_agent.sub_agents[1].name == "schema_inspector"
    assert root_agent.sub_agents[2].name == "sql_loop"
    assert root_agent.sub_agents[3].name == "final_responder"

def test_loop_agent_structure(monkeypatch, agent_modules):
    agent_module, config_module = agent_modules
    # The loop agent is always present, just its index changes.
    # We can test with either setting, it should be the same.
    monkeypatch.setenv("DATAPLEX_ENABLED", "false")
    importlib.reload(config_module)
    importlib.reload(agent_module)
    root_agent = agent_module.create_root_agent()
    loop_agent = root_agent.sub_agents[1] # Index when disabled

    assert isinstance(loop_agent, LoopAgent)
    assert len(loop_agent.sub_agents) == 3
    assert loop_agent.sub_agents[0].name == "sql_generator"
    assert loop_agent.sub_agents[1].name == "sql_validator"
    assert loop_agent.sub_agents[2].name == "sql_reviewer"
