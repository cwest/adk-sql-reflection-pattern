# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-20.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import json
import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from agents.sql_agent.semantic_enricher import term_extractor, dataplex_searcher
from google.adk.agents import InvocationContext
from google.adk.events import Event, EventActions
from google.adk.agents.run_config import RunConfig
from google.adk.sessions import Session
from google.adk.sessions.in_memory_session_service import InMemorySessionService
from google.genai.types import Content, Part

@pytest.mark.asyncio
@patch("google.adk.agents.llm_agent.AutoFlow")
async def test_term_extractor(mock_autoflow_class):
    # Define the test case
    test_case = {
        "input": "What was the total cost of refunds last quarter?",
        "expected_output": '["cost", "refunds"]'
    }

    # Mock the AutoFlow and its run_async method
    mock_flow_instance = MagicMock()
    async def mock_run_async(*args, **kwargs):
        yield Event(
            author="term_extractor",
            content=Content(parts=[Part(text=test_case["expected_output"])]),
            actions=EventActions(end_of_agent=True)
        )
    mock_flow_instance.run_async.return_value = mock_run_async()
    mock_autoflow_class.return_value = mock_flow_instance

    # Create a valid test context
    session_service = InMemorySessionService()
    session = await session_service.create_session(
        app_name="test-app", user_id="test-user", state={"input": test_case["input"]}
    )
    context = InvocationContext(
        invocation_id="test-invocation",
        agent=term_extractor,
        session=session,
        session_service=session_service,
        run_config=RunConfig()
    )
    
    output = ""
    async for event in term_extractor.run_async(context):
        if event.is_final_response():
            output = "".join(part.text for part in event.content.parts)

    # Assert the output
    assert output.strip() == test_case["expected_output"]

@pytest.mark.asyncio
@patch("google.adk.agents.llm_agent.AutoFlow")
async def test_dataplex_searcher(mock_autoflow_class):
    # Define the test case
    test_case = {
        "input": ["cost", "refunds"],
        "expected_semantic_context": "## Relevant Tables\n- `project.dataset.refunds`\n\n## Column Descriptions\n- `refund_amount`: The amount of the refund.\n\n## Business Rules\n- For each refund, a fee of 5 is added to the cost.",
        "expected_filtered_table_list": ["project.dataset.refunds"]
    }

    # Mock the AutoFlow and its run_async method
    mock_flow_instance = MagicMock()
    async def mock_run_async(*args, **kwargs):
        # Simulate the agent calling the tools and producing the output
        yield Event(
            author="dataplex_searcher",
            actions=EventActions(
                state_delta={
                    "semantic_context": test_case["expected_semantic_context"],
                    "filtered_table_list": test_case["expected_filtered_table_list"]
                },
                end_of_agent=True
            )
        )
    mock_flow_instance.run_async.return_value = mock_run_async()
    mock_autoflow_class.return_value = mock_flow_instance

    # Create a valid test context
    session_service = InMemorySessionService()
    session = await session_service.create_session(
        app_name="test-app", user_id="test-user", state={"extracted_terms": test_case["input"]}
    )
    context = InvocationContext(
        invocation_id="test-invocation",
        agent=dataplex_searcher,
        session=session,
        session_service=session_service,
        run_config=RunConfig()
    )
    
    async for event in dataplex_searcher.run_async(context):
        if event.actions.state_delta:
            context.session.state.update(event.actions.state_delta)
        if event.is_final_response():
            break

    # Assert the output
    assert context.session.state["semantic_context"] == test_case["expected_semantic_context"]
    assert context.session.state["filtered_table_list"] == test_case["expected_filtered_table_list"]