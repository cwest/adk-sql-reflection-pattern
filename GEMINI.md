# Project Context: ADK SQL Reflection Pattern

## Overview
This project implements a robust SQL generation agent using the Google Gen AI Agent Development Kit (ADK) and MCP Toolbox. It features a reflection loop that validates generated SQL using BigQuery's `dry_run` capability before execution, ensuring safety and reliability.

## Key Technologies
*   **Language:** Python 3.11+
*   **Framework:** Google ADK (`google-adk`)
*   **Tooling:** MCP Toolbox (`mcp-toolbox`)
*   **Database:** Google BigQuery (specifically `bigquery-public-data.google_trends`)
*   **Dependency Management:** `uv`
*   **Process Management:** `honcho`

## Architecture
The agent is a `SequentialAgent` composed of three main stages:
1.  **Schema Inspector:** Fetches database schema using MCP tools (`list_tables`, `get_table_info`).
2.  **SQL Generator Loop (`LoopAgent`):**
    *   *Generator:* Drafts SQL queries.
    *   *Validator:* Performs a `dry_run` via MCP `execute_sql` tool.
    *   *Reviewer:* Analyzes `dry_run` results and either escalates (success) or provides guidance for the next iteration.
3.  **Final Responder:** Executes the valid SQL and presents results to the user.

## Development & Running
*   **Install Dependencies:** `uv sync`
*   **Run Agent:** `uv run honcho start` (Starts both MCP Toolbox and ADK Web UI)
*   **Run Tests:** `PYTHONPATH=. uv run pytest`
*   **Environment:** Requires `.env` file with `GOOGLE_CLOUD_PROJECT`, `TOOLBOX_HOST`, and `TOOLBOX_PORT`.

## Key Files
*   `agents/sql_agent/agent.py`: Root agent definition.
*   `agents/sql_agent/sql_generator_loop.py`: Core reflection loop logic.
*   `tools.yaml`: MCP Toolbox configuration for BigQuery.
*   `Procfile`: Service definitions for `honcho`.
*   `pyproject.toml`: Python dependencies.
