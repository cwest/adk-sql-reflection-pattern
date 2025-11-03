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
from agents.sql_agent.prompts import (
    SCHEMA_INSPECTOR_DATAPLEX_PROMPT,
    SCHEMA_INSPECTOR_DEFAULT_PROMPT
)

@pytest.fixture
def schema_inspector_modules():
    from agents.sql_agent import schema_inspector, config
    return schema_inspector, config

def test_schema_inspector_prompt_dataplex_disabled(monkeypatch, schema_inspector_modules):
    schema_inspector_module, config_module = schema_inspector_modules
    monkeypatch.setenv("DATAPLEX_ENABLED", "false")
    importlib.reload(config_module)
    importlib.reload(schema_inspector_module)
    inspector = schema_inspector_module.create_schema_inspector()
    assert inspector.instruction == SCHEMA_INSPECTOR_DEFAULT_PROMPT

def test_schema_inspector_prompt_dataplex_enabled(monkeypatch, schema_inspector_modules):
    schema_inspector_module, config_module = schema_inspector_modules
    monkeypatch.setenv("DATAPLEX_ENABLED", "true")
    importlib.reload(config_module)
    importlib.reload(schema_inspector_module)
    inspector = schema_inspector_module.create_schema_inspector()
    assert inspector.instruction == SCHEMA_INSPECTOR_DATAPLEX_PROMPT
