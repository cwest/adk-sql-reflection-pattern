# Implementation Plan: ADK & MCP SQL Generation Agent

## Overview
This plan details the implementation of an SQL Generation Agent using ADK and MCP Toolbox, as defined in `PRDs/00-adk-mcp-sql-agent.md`. The agent will use a reflection loop to validate SQL queries against BigQuery before execution.

## Requirements Summary
- **Target Dataset:** `bigquery-public-data.google_trends`
- **Authentication:** Google Cloud ADC
- **LLM:** `gemini-2.5-pro`
- **Architecture:** ADK `SequentialAgent` with a nested `LoopAgent` for reflection.
- **Tooling:** MCP Toolbox for BigQuery integration, running as a server managed by `honcho`.
- **Key Feature:** SQL validation via BigQuery dry runs.
- **Process Management:** `uv` for dependencies, `honcho` for running services.

## Research Findings
- **ADK Structure:** ADK `adk web` expects an `AGENTS_DIR` containing subdirectories for each agent (e.g., `agents/sql_agent/agent.py`).
- **ADK & MCP:** ADK supports MCP via `MCPToolset`. We will use `StreamableHTTPConnectionParams` to connect to the `toolbox` server.
- **MCP Toolbox:** Supports custom `tools.yaml` with environment variable substitution (e.g., `${GOOGLE_CLOUD_PROJECT}`).
- **Arbitrary SQL & Dry Runs:** `bigquery-execute-sql` tool kind supports `dry_run`. We will define `validate_sql` (`dry_run: true`) and `execute_sql` in `tools.yaml`.
- **Loop Termination:** `LoopAgent` supports a `condition` parameter (callable taking state, returning bool).
- **SQL Best Practices:** Detailed system instructions for BigQuery SQL generation have been identified.

## Implementation Tasks

### Phase 1: Foundation & Setup
1.  **Environment Setup**
    -   Description: Initialize project with `uv`, create virtual environment, install ADK, `mcp`, `honcho`.
    -   Files: `pyproject.toml`, `.venv/` (created by uv), `uv.lock`
    -   Dependencies: Python 3.11+, `uv` installed.
    -   Estimated effort: 30 mins

2.  **Toolbox Configuration**
    -   Description: Create `tools.yaml` with `bigquery-public-data` source and tools: `list_tables`, `get_table_info`, `validate_sql` (dry_run=true), `execute_sql`. Use `${GOOGLE_CLOUD_PROJECT}` for the billing project ID in the source configuration.
    -   Files: `tools.yaml`
    -   Dependencies: `toolbox` binary on PATH (assumed).
    -   Estimated effort: 15 mins

3.  **Process Management (Honcho)**
    -   Description: Create `Procfile` to run `toolbox` as an HTTP server and `adk_web` for the agents directory.
    -   Files: `Procfile`
    -   Content:
        -   `toolbox: toolbox --tools-file tools.yaml --port 5000`
        -   `adk_web: uv run adk web agents`
    -   Dependencies: Task 2
    -   Estimated effort: 15 mins

4.  **MCP Connection Verification**
    -   Description: Create `agents/sql_agent/` directory with `__init__.py` and `agent.py`. Define a basic `LlmAgent` in `agent.py` with `MCPToolset` connected to `localhost:5000`. Run `honcho start` and verify in web UI.
    -   Files: `agents/sql_agent/__init__.py`, `agents/sql_agent/agent.py`
    -   Dependencies: Task 3
    -   Estimated effort: 30 mins

### Phase 2: Agent Implementation
5.  **Schema Inspection Agent**
    -   Description: Implement `LlmAgent` in `agents/sql_agent/schema_inspector.py` using `list_tables` and `get_table_info` via MCP (HTTP) to populate agent state.
    -   Files: `agents/sql_agent/schema_inspector.py`
    -   Dependencies: Task 4
    -   Estimated effort: 1 hour

6.  **SQL Generation & Validation Loop**
    -   Description: Implement `LoopAgent` in `agents/sql_agent/sql_generator_loop.py`.
        -   **Generator:** Drafts SQL using schema. Incorporate detailed system instructions into the prompt.
        -   **Validator:** Calls `validate_sql` (dry run) via MCP.
        -   **Reviewer:** Updates state based on dry run result (sets `sql_is_valid` flag).
        -   **Loop Termination:** Use `condition=lambda state: not state.get("sql_is_valid", False)` in `LoopAgent` constructor.
    -   Files: `agents/sql_agent/sql_generator_loop.py`
    -   Dependencies: Task 5
    -   Estimated effort: 2 hours

7.  **Final Execution Agent**
    -   Description: Implement `LlmAgent` in `agents/sql_agent/final_responder.py` that uses `execute_sql` via MCP for final result.
    -   Files: `agents/sql_agent/final_responder.py`
    -   Dependencies: Task 6
    -   Estimated effort: 1 hour

### Phase 3: Integration & Testing
8.  **Root Agent Orchestration**
    -   Description: Update `agents/sql_agent/agent.py` to import and combine all agents into a main `SequentialAgent`.
    -   Files: `agents/sql_agent/agent.py`
    -   Dependencies: Task 7
    -   Estimated effort: 1 hour

9.  **Testing & Validation**
    -   Description: Run agent via `adk web` against test cases. Verify not just the final answer, but also that the generated SQL adheres to best practices (e.g., `SAFE_CAST`, no `SELECT *`, `QUALIFY` for window functions). Iterate on prompts if violations are found.
    -   Files: `tests/test_cases.txt`
    -   Dependencies: Task 8
    -   Estimated effort: 2 hours

10. **Comprehensive Documentation**
    -   Description: Update `README.md` to include:
        -   Project overview and architecture.
        -   Prerequisites: `uv`, `toolbox` binary, Google Cloud ADC.
        -   Setup instructions: `uv sync`, `gcloud auth application-default login`, ensure `GOOGLE_CLOUD_PROJECT` env var is set.
        -   Running instructions: `uv run honcho start`.
        -   Codebase walkthrough for new developers.
    -   Files: `README.md`
    -   Dependencies: All previous tasks.
    -   Estimated effort: 1 hour

## Technical Design

### Data Flow
(Same as previous, but MCP connection is via HTTP to `localhost:5000`)

### Key Dependencies
-   `google-genai-adk`: Agent framework
-   `mcp`: Model Context Protocol SDK
-   `honcho`: Process manager
-   `uv`: Package manager
-   `mcp-toolbox`: External binary (must be on PATH)

## Success Criteria
- [ ] `honcho start` successfully launches `toolbox` and `adk web`.
- [ ] Agent authenticates via ADC and connects to `toolbox` via HTTP.
- [ ] Reflection loop works using `validate_sql` and `condition`.
- [ ] Generated SQL adheres to best practices (safety, efficiency).
- [ ] Final response includes SQL and data.
- [ ] Read-only operations only.