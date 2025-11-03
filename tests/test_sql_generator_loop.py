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

@pytest.fixture
def sql_generator_loop_modules():
    from agents.sql_agent import sql_generator_loop, config
    return sql_generator_loop, config

def test_generator_prompt_dataplex_disabled(monkeypatch, sql_generator_loop_modules):
    sql_generator_loop_module, config_module = sql_generator_loop_modules
    monkeypatch.setenv("DATAPLEX_ENABLED", "false")
    importlib.reload(config_module)
    importlib.reload(sql_generator_loop_module)
    loop = sql_generator_loop_module.create_sql_generator_loop()
    generator = loop.sub_agents[0]
    
    # Assert that the core instructions are present
    assert "Read the `schema` from the session state" in generator.instruction
    assert "Read `guidance` from session state" in generator.instruction
    # Assert that the Dataplex-specific instruction is absent
    assert "semantic_context" not in generator.instruction

def test_generator_prompt_dataplex_enabled(monkeypatch, sql_generator_loop_modules):
    sql_generator_loop_module, config_module = sql_generator_loop_modules
    monkeypatch.setenv("DATAPLEX_ENABLED", "true")
    importlib.reload(config_module)
    importlib.reload(sql_generator_loop_module)
    loop = sql_generator_loop_module.create_sql_generator_loop()
    generator = loop.sub_agents[0]

    # Assert that the core instructions are present
    assert "Read the `schema` from the session state" in generator.instruction
    assert "Read `guidance` from session state" in generator.instruction
    # Assert that the Dataplex-specific instruction is present
    assert "Read the `semantic_context` from the session state" in generator.instruction
