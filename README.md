# ADK SQL Generation Agent with Reflection

This project demonstrates how to build a robust SQL generation agent using the
[Google Gen AI Agent Development Kit (ADK)](https://github.com/google/adk-python)
and [MCP Toolbox](https://github.com/googleapis/genai-toolbox).

It features a **reflection loop** where generated SQL queries are validated
using BigQuery's `dry_run` capability before being executed, ensuring high
reliability and safety.

This project also includes an optional **Dataplex integration** that enriches
the agent's understanding of the data by fetching semantic context from a data
catalog.

## Architecture

The agent is composed of several sub-agents orchestrated sequentially:

1.  **Semantic Enricher** (Optional, if `DATAPLEX_ENABLED=true`):
    - **Term Extractor**: Extracts key business terms from the user's query.
    - **Dataplex Searcher**: Searches Dataplex for tables and metadata related
      to the extracted terms.
2.  **Schema Inspector**: Queries BigQuery `INFORMATION_SCHEMA` via MCP to
    understand the dataset. If Dataplex is enabled, it uses the filtered table
    list from the Semantic Enricher.
3.  **SQL Generator Loop** (`LoopAgent`):
    - **Generator**: Drafts SQL based on the user question, schema, and optional
      semantic context from Dataplex.
    - **Validator**: Performs a dry run of the SQL via MCP to check for syntax
      and semantic errors.
    - **Reviewer**: Analyzes the dry run result. If it fails, it provides
      guidance back to the Generator for the next iteration.
4.  **Final Responder**: Executes the validated SQL and answers the user's
    question with the data.

## Prerequisites

- Python 3.11+
- [`uv`](https://github.com/astral-sh/uv) for dependency management.
- [Google Cloud SDK (`gcloud`)](https://cloud.google.com/sdk/docs/install)
  installed and configured.
- [`mcp-toolbox`](https://github.com/googleapis/genai-toolbox) binary installed
  and on your system PATH.
- [Terraform](https://www.terraform.io/downloads) installed.

## Setup

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/cwest/adk-sql-reflection-pattern.git
    cd adk-sql-reflection-pattern
    ```

2.  **Install dependencies:**

    This project uses `uv` to manage dependencies. To ensure you have all
    packages for development and for running both the standard and Dataplex-enabled
    modes, install the project with all optional dependencies:

    ```bash
    uv pip install ".[dev,dataplex]"
    ```

    This will install the base requirements plus packages for testing and Dataplex
    integration.

3.  **Authenticate with Google Cloud:** Ensure you have Application Default
    Credentials (ADC) set up.

    ```bash
    gcloud auth application-default login
    ```

4.  **Configure Environment:** Copy `.env.example` to `.env` and set your
    `GOOGLE_CLOUD_PROJECT`. The other variables depend on the mode you wish to
    run.
    ```bash
    cp .env.example .env
    ```

---

## Running the Agent

This project has two distinct modes.

### Standard Mode (Default)

This mode uses the public `bigquery-public-data.google_trends` dataset and does
**not** require any Terraform setup.

1.  **Configure Environment:** Ensure `DATAPLEX_ENABLED` is set to `false` or
    commented out in your `.env` file. You only need to set your project ID.

    ```dotenv
    GOOGLE_CLOUD_PROJECT=your-project-id
    # DATAPLEX_ENABLED=false
    ```

2.  **Run the Agent:**

    ```bash
    uv run honcho start
    ```

3.  **Test the Agent:** Open the ADK Web UI (usually `http://localhost:8000`)
    and use the sample queries from
    [tests/test_cases_google_trends.md](./tests/test_cases_google_trends.md).

### Dataplex-Enabled Mode

This mode demonstrates how the agent can use semantic metadata from Dataplex to
answer more complex questions. It requires provisioning a sample e-commerce
dataset and Dataplex resources using Terraform.

1.  **Configure Environment:** Update your `.env` file to enable Dataplex mode
    and configure the necessary resource IDs.

    ```dotenv
    GOOGLE_CLOUD_PROJECT=your-project-id
    DATAPLEX_ENABLED=true
    DATAPLEX_LAKE_ID=e-commerce-lake
    DATAPLEX_ZONE_ID=analytics-curated-zone
    DATAPLEX_LOCATION=us-central1
    ```

2.  **Provision Infrastructure with Terraform:** The Terraform configuration
    will automatically:

    - Create the BigQuery datasets and tables for the e-commerce example.
    - Create the Dataplex Lake, Zone, and Assets.
    - Run a script to generate sample data and load it into BigQuery.
    - Run a script to attach semantic metadata from Dataplex to the BigQuery
      tables.

    First, initialize Terraform:

    ```bash
    terraform -chdir=terraform init
    ```

    Then, apply the configuration. You must provide variables for your project
    and the user you want to grant Dataplex admin permissions to.

    ```bash
    export GCP_PROJECT="your-project-id"
    export GCP_REGION="us-central1"
    export DATAPLEX_ADMIN="your-email@example.com"

    terraform -chdir=terraform apply -auto-approve \
      -var="project_id=$GCP_PROJECT" \
      -var="google_cloud_project=$GCP_PROJECT" \
      -var="region=$GCP_REGION" \
      -var="dataplex_admin_user=$DATAPLEX_ADMIN" \
      -var="dataplex_lake_id=e-commerce-lake" \
      -var="dataplex_zone_id=analytics-curated-zone"
    ```

3.  **Run the Agent:**

    ```bash
    uv run honcho start
    ```

4.  **Test the Agent:** Open the ADK Web UI and use the sample queries from
    [tests/test_cases_dataplex.md](./tests/test_cases_dataplex.md). These
    queries are specifically designed to test the agent's use of business rules
    and semantic understanding from Dataplex.

---

This will start:

- **Toolbox**: An MCP server exposing BigQuery and Dataplex tools on port 5000.
- **ADK Web UI**: The agent interface, typically accessible at
  `http://localhost:8000` (check console output for exact URL).

## Project Structure

- `agents/sql_agent/`: Contains the agent implementation.
  - `agent.py`: The root `SequentialAgent` definition.
  - `semantic_enricher.py`: Optional agent for enriching queries with Dataplex
    context.
  - `schema_inspector.py`: Agent for retrieving database schema.
  - `sql_generator_loop.py`: The core reflection loop (Generator, Validator,
    Reviewer).
  - `final_responder.py`: Agent for executing the final query and answering.
  - `prompts.py`: Detailed system instructions for SQL generation.
  - `config.py`: Shared configuration (MCP connection parameters).
- `tools.yaml`: Configuration for MCP Toolbox, defining the BigQuery and
  Dataplex tools.
- `Procfile`: Defines the services for `honcho`.
- `pyproject.toml`: Project dependencies.
- `terraform/`: Contains Terraform configuration files for provisioning Google
  Cloud resources.
  - `main.tf`: Main Terraform configuration, including provider setup.
  - `variables.tf`: Input variables for Terraform scripts.
  - `bigquery.tf`: BigQuery dataset and table definitions.
  - `dataplex.tf`: Dataplex Lake, Zone, Assets, and Aspect Type definitions.
  - `iam.tf`: IAM policy definitions (placeholder).
