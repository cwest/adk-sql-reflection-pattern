# Product Requirements Document: ADK & MCP SQL Generation Agent Example

## 1. Strategic Overview
*   **Project Mandate:** Create a canonical, educational example of an SQL Generation Agent using the Agent Development Kit (ADK) and Model Context Protocol (MCP) Toolbox. The agent must demonstrate advanced patterns, specifically a "reflection loop" for self-correcting SQL generation.
*   **Core Principles:**
    *   **Read-Only Safety:** The agent must strictly execute only `SELECT` queries to ensure data integrity.
    *   **Accuracy through Validation:** All generated SQL must be validated via a BigQuery dry run before actual execution.
    *   **Simplicity in Authentication:** Leverage Google Cloud `gcloud` Application Default Credentials (ADC) for seamless, secure authentication without managing keys.
    *   **Framework Showcase:** Serve as a best-practice reference for integrating ADK agents with standard MCP tools.

## 2. Problem Statement & User Need
*   **Problem Statement (Developer Focus):** Developers building GenAI agents often struggle to implement robust SQL generation that reliably produces valid queries. They lack clear, canonical examples of how to use modern frameworks like ADK and MCP to build self-correcting systems.
*   **User Need (Developer Focus):** A reference implementation that clearly demonstrates how to build a validation loop (generate -> dry run -> correct) to ensure high-quality SQL output.
*   **End-User Need (Agent Capability):** A conversational interface that allows users to ask natural language questions about a specific dataset and receive accurate, data-backed answers without needing to know SQL or the specific schema.

## 3. Target User Personas
1.  **Primary Persona: The AI Engineer (Learner)**
    *   **Goal:** To master advanced agent patterns in ADK, specifically tool integration and self-correction loops.
    *   **Pain Point:** Existing documentation can be too abstract; needs concrete, working code examples to understand complex flows.
2.  **Secondary Persona: The Data Explorer (End-User)**
    *   **Goal:** To quickly extract insights from the `google_trends` dataset without writing code.
    *   **Pain Point:** Blocked by lack of SQL knowledge or unfamiliarity with the specific table structure.

## 4. User Stories
*   **As an AI Engineer**, I want to see a clear implementation of a "reflection loop" using ADK's `LoopAgent`, so that I can understand how to build agents that self-correct their own errors.
*   **As an AI Engineer**, I want to see how to integrate standard MCP Toolbox tools with ADK agents, so that I can easily give my agents access to external systems like BigQuery.
*   **As a Data Explorer**, I want to ask natural language questions about Google Trends data and get a text answer along with the SQL used, so that I can trust the result and potentially learn from the query.

## 5. Functional Requirements

### 5.1 System Configuration
*   **Target Dataset:** Pre-configured to operate on `bigquery-public-data.google_trends`.
*   **Authentication:** Must use Google Cloud Application Default Credentials (ADC) via `gcloud auth application-default login`.
*   **LLM:** Must use **Gemini 2.5 Pro (`gemini-2.5-pro`)** for all agent steps to ensure sufficient reasoning capability.

### 5.2 Root Agent Workflow (SequentialAgent)
The main agent must be a `SequentialAgent` that orchestrates the following steps linearly:

1.  **Schema Inspection Step (LlmAgent):**
    *   Uses MCP Toolbox to query `INFORMATION_SCHEMA` for the target dataset.
    *   Extracts and stores table names, column names, and data types in the agent's state.

2.  **SQL Generation & Validation Loop Step (LoopAgent):**
    *   Executes a loop with a maximum of 3 iterations.
    *   **Generate SQL (LlmAgent):** Generates a BigQuery `SELECT` statement based on the user question and schema. Uses prior feedback if available.
    *   **Dry Run Validation (LlmAgent):** Uses MCP Toolbox to execute the query in `dry_run` mode.
    *   **Review (LlmAgent):** Analyzes the dry run result. If successful, terminates loop. If failed, generates guidance based on the error and continues to next iteration.

3.  **Final Execution & Response Step (LlmAgent):**
    *   Executes the validated SQL query using MCP Toolbox (real run).
    *   Analyzes the returned data rows.
    *   Generates a natural language response answering the original question.
    *   **Requirement:** Must always include the final executed SQL query in the response for transparency.

## 6. Non-Functional Requirements
*   **Code Quality:** The example code must be heavily commented, modular, and follow Python best practices to serve effectively as a teaching tool.
*   **Security (Least Privilege):** The agent must strictly adhere to read-only operations. It must not attempt any data modification commands.
*   **Performance:** The validation loop should be efficient, with dry runs not causing excessive delay to the final user response.

## 7. Success Metrics & KPIs
*   **Qualitative:** Positive feedback from developers regarding the clarity and usefulness of the example.
*   **Quantitative (Testing):**
    *   **Success Rate:** >90% of valid natural language test queries result in a correct SQL query after the validation loop.
    *   **Self-Correction:** The agent successfully corrects at least 50% of initially invalid queries within the 3-loop limit.

## 8. Dataset & Test Cases
*   **Dataset:** `bigquery-public-data.google_trends`
*   **Key Tables:**
    *   `international_top_rising_terms`
    *   `international_top_terms`
    *   `top_rising_terms`
    *   `top_terms`
*   **Test Cases for Validation:**
    1.  "What were the top 5 rising search terms in the 'New York, NY' DMA last week?"
    2.  "Compare the top ranked term in Japan vs Brazil for the most recent available week."
    3.  "List the terms with the highest percent gain in the UK yesterday."

## 9. Risks and Dependencies
*   **Dependencies:**
    *   Stability of the ADK and MCP Toolbox APIs.
    *   Availability and schema stability of the `bigquery-public-data.google_trends` dataset.
    *   Continued availability and performance of the `gemini-2.5-pro` model.
*   **Risks:**
    *   LLM hallucinations leading to syntactically valid but semantically incorrect queries (hard to catch with dry run).
    *   Complexity of the multi-agent setup might be overwhelming for absolute beginners.

## 10. Out of Scope
*   Any SQL operations other than `SELECT` (INSERT, UPDATE, DELETE, DROP, etc.).
*   Multi-turn conversations or maintaining state between distinct user questions.
*   Data visualization (charts, graphs).
*   User-facing authentication or frontend UI beyond a CLI.
