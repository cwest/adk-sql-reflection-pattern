# ADK SQL Generation Agent with Reflection

This project demonstrates how to build a robust SQL generation agent using the [Google Gen AI Agent Development Kit (ADK)](https://github.com/google/adk-python) and [MCP Toolbox](https://github.com/googleapis/genai-toolbox).

It features a **reflection loop** where generated SQL queries are validated using BigQuery's `dry_run` capability before being executed, ensuring high reliability and safety.

## Architecture

The agent is composed of several sub-agents orchestrated sequentially:

1.  **Schema Inspector**: Queries BigQuery `INFORMATION_SCHEMA` via MCP to understand the dataset.
2.  **SQL Generator Loop** (`LoopAgent`):
    *   **Generator**: Drafts SQL based on the user question and schema.
    *   **Validator**: Performs a dry run of the SQL via MCP to check for syntax and semantic errors.
    *   **Reviewer**: Analyzes the dry run result. If it fails, it provides guidance back to the Generator for the next iteration.
3.  **Final Responder**: Executes the validated SQL and answers the user's question with the data.

## Prerequisites

*   Python 3.11+
*   [`uv`](https://github.com/astral-sh/uv) for dependency management.
*   [Google Cloud SDK (`gcloud`)](https://cloud.google.com/sdk/docs/install) installed and configured.
*   [`mcp-toolbox`](https://github.com/googleapis/genai-toolbox) binary installed and on your system PATH.

## Setup

1.  **Clone the repository:**
    ```bash
    git clone <repo_url>
    cd adk-sql-reflection-pattern
    ```

2.  **Install dependencies:**
    ```bash
    uv sync
    ```

3.  **Authenticate with Google Cloud:**
    Ensure you have Application Default Credentials (ADC) set up.
    ```bash
    gcloud auth application-default login
    ```

4.  **Configure Environment:**
    Copy `.env.example` to `.env` and update it with your Google Cloud Project ID:
    ```bash
    cp .env.example .env
    # Edit .env and set GOOGLE_CLOUD_PROJECT=your-project-id
    ```

## Running the Agent

We use `honcho` to run both the MCP Toolbox server and the ADK web UI.

```bash
uv run honcho start
```

This will start:
*   **Toolbox**: An MCP server exposing BigQuery tools on port 5000.
*   **ADK Web UI**: The agent interface, typically accessible at `http://localhost:8000` (check console output for exact URL).

Open the ADK Web UI, select the `sql_agent`, and start asking questions about Google Trends data!

## Project Structure

*   `agents/sql_agent/`: Contains the agent implementation.
    *   `agent.py`: The root `SequentialAgent` definition.
    *   `schema_inspector.py`: Agent for retrieving database schema.
    *   `sql_generator_loop.py`: The core reflection loop (Generator, Validator, Reviewer).
    *   `final_responder.py`: Agent for executing the final query and answering.
    *   `prompts.py`: Detailed system instructions for SQL generation.
    *   `config.py`: Shared configuration (MCP connection parameters).
*   `tools.yaml`: Configuration for MCP Toolbox, defining the BigQuery tools.
*   `Procfile`: Defines the services for `honcho`.
*   `pyproject.toml`: Project dependencies.
