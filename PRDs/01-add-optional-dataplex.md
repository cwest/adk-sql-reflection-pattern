# Product Requirements Document: Optional Dataplex Integration

## 1. Strategic Overview

### Project Mandate
To enhance the existing SQL agent by integrating Google Cloud Dataplex, enabling it to leverage semantic metadata for generating more accurate and context-aware SQL queries. This integration should be optional and configurable by the user.

### Core Principles
1.  **Optionality:** The Dataplex integration must be easily enabled or disabled withoutbreaking core functionality.
2.  **Real-World Fidelity:** The implementation must serve as a high-quality, realistic example of using Dataplex in a production-level agent, reflecting real-world data complexity and use cases.

## 2. Problem Statement & User Need

The current SQL generation agent relies solely on BigQuery's `INFORMATION_SCHEMA` (table names, column names, data types) to construct queries. This approach critically lacks the semantic business context that is often held outside the formal data model—residing in human knowledge, external reports, or application codebases.

This deficiency leads to several key problems:

*   **Inaccurate or Incomplete Insights:** Without understanding the deeper meaning of data (e.g., a `refund_cost` column needing an additional $15 processing fee), the agent may generate SQL queries that produce factually incorrect or incomplete analytical results, leading to flawed business decisions.
*   **Limited Interpretive Capability:** The agent struggles with obscure, ambiguous, or seemingly obfuscated table and column names. It cannot infer their purpose or appropriate usage without explicit, often repetitive, human intervention.
*   **High User Cognitive Load:** Users are forced to provide extensive, explicit context and domain knowledge that the agent should ideally be able to discover and integrate autonomously. This diminishes the agent's value as an intelligent assistant and increases the effort required from the user.

**User Need:** Users require an SQL generation agent that can access and leverage rich semantic metadata and business context, enabling it to generate more accurate, comprehensive, and context-aware SQL queries with minimal explicit guidance. This will empower users to derive deeper, more reliable insights from their data.

## 3. Target User Personas

This feature primarily addresses the needs of two distinct "personas": the human end-user seeking data insights and the AI agent itself, which requires semantic understanding to fulfill user requests effectively.

### 3.1. Primary Human Persona: Dana, the Data Analyst

*   **Role:** Data Analyst, Business Intelligence Specialist, or a technically proficient business user.
*   **Goals:**
    *   Quickly understand the meaning and context of unfamiliar datasets, tables, and columns without extensive manual documentation review.
    *   Generate accurate and insightful SQL queries that incorporate nuanced business rules and semantic understanding.
    *   Reduce the time spent on data discovery and validation, allowing more focus on analysis.
    *   Explore data effectively even when column names are obscure or ambiguous.
*   **Pain Points:**
    *   Struggles to translate business questions into precise SQL due to a lack of semantic context for specific data elements.
    *   Encounters "gotchas" or hidden business rules (e.g., specific charges, data transformations) that are not evident from the schema alone, leading to potentially incorrect analyses.
    *   Spends significant time cross-referencing data dictionaries, asking colleagues, or trial-and-error querying to understand data meaning.
    *   Finds it difficult to use tables or columns with non-descriptive or obfuscated names.

### 3.2. System Persona: The SQL Generation Agent

*   **Role:** The AI-powered SQL Generation Agent.
*   **Goals:**
    *   Accurately interpret natural language user queries by leveraging semantic metadata.
    *   Generate SQL queries that are not only syntactically correct but also semantically aligned with business context and rules.
    *   Provide more relevant and helpful responses to users by understanding the "why" behind data elements.
    *   Reduce the need for explicit user guidance by autonomously discovering and applying semantic information.
*   **Pain Points:**
    *   Currently limited to structural schema, leading to a shallow understanding of data.
    *   Prone to generating queries that are technically correct but semantically incomplete or misleading from a business perspective.
    *   Struggles with ambiguous user questions that require contextual inference beyond basic schema matching.

## 4. User Stories

*   **User Story 1:** As a Data Analyst, I want to ask questions about data using natural language, so that I don't have to manually look up table and column meanings.
*   **User Story 2:** As a Data Analyst, I want to ask a question like "What was the total cost of refunds in Q3?" **without needing to know** which table stores refund data or how the cost is calculated, so that I can focus on business questions, not database schemas.
*   **User Story 3:** As a Data Analyst, I want the agent to **automatically apply known business rules** to the queries it generates, such as adding a "$15 processing fee" to each refund, so that the data I receive is accurate and reflects real-world financial outcomes.
*   **User Story 4:** As a Data Analyst, I want to ask a question about "customer satisfaction scores" and have the agent correctly use the `usr_sat_scr` column, so that I can analyze data without being blocked by non-obvious column names.

## 5. Functional Requirements

### 5.1. Dataplex Integration & Configuration
1.  **FR1 (Dataplex Source):** The system must be configurable to connect to a Google Cloud Dataplex instance. This requires adding a new `dataplex` source entry in the `tools.yaml` file, specifying the `project` ID. The agent's service account must have appropriate IAM permissions to access Dataplex resources (e.g., `roles/dataplex.viewer`, `roles/datacatalog.viewer`).
2.  **FR1.1 (Dataplex Targeting):** The system must be configurable to target a specific Dataplex instance. The following environment variables will be introduced:
    *   `DATAPLEX_LOCATION`: The Google Cloud region of the Dataplex lake (e.g., `us-central1`).
    *   `DATAPLEX_LAKE_ID`: The ID of the target Dataplex Lake.
    *   `DATAPLEX_ZONE_ID`: The ID of the target Zone within the Lake (e.g., `analytics_curated_zone`).
2.  **FR2 (Optionality):** The Dataplex integration must be controlled by an environment variable (e.g., `DATAPLEX_ENABLED=true/false`).
    *   If `DATAPLEX_ENABLED` is `true`, a new `SemanticEnricher` agent must be conditionally inserted as the first step in the `sql_agent`'s `SequentialAgent` sub-agent list.
    *   If `DATAPLEX_ENABLED` is `false` or unset, the `SemanticEnricher` agent must be omitted, and the `sql_agent` must revert to its original behavior (starting with `schema_inspector`) without errors.
3.  **FR3 (Tooling):** The `SemanticEnricher` agent must have access to and be able to invoke the following MCP tools: `dataplex-search-entries`, `dataplex-lookup-entry`, and `dataplex-search-aspect-types`.

### 5.2. Agent Behavior & Semantic Query Generation
1.  **FR4 (Semantic Term Extraction):** A new, dedicated `LlmAgent` named `TermExtractor` must be created.
    *   **Responsibility:** Its sole responsibility is to extract key business concepts from the user's natural language query. It should be prompted to ignore common filter conditions (like dates) and aggregation words (like 'total', 'average').
    *   **Model:** This agent should use a cost-effective and fast model, such as `gemini-2.5-flash`, to optimize for performance.
    *   **Output:** It must output a structured list of the identified business terms (e.g., a JSON array of strings) into the session state.
2.  **FR5 (Semantic Search):** A new `LlmAgent` named `DataplexSearcher` must be created.
    *   **Responsibility:** This agent takes the list of business terms from the `TermExtractor`. It then orchestrates calls to the `dataplex-search-entries` tool to find data assets that are semantically related to those terms.
    *   **Output:** It must place the unique identifiers of the discovered data assets (e.g., their full resource names) into the session state.
3.  **FR6 (Metadata Lookup):** The `DataplexSearcher` agent (or a new dedicated agent, TBD) must then:
    *   **Responsibility:** For each unique data asset found, it must call the `dataplex-lookup-entry` tool to retrieve the full metadata, specifically looking for business descriptions and custom aspects containing business rules.
    *   **Output:** It must consolidate this retrieved semantic context and place it into the session state for the `sql_generator_loop` to use. The context must be a well-structured Markdown string with the following sections:
        *   `## Relevant Tables`: A list of tables relevant to the user's query.
        *   `## Column Descriptions`: Descriptions of relevant columns, especially those with obscure names.
        *   `## Business Rules`: Any business rules (e.g., formulas) that must be applied to the query.
4.  **FR7 (Context-Aware SQL Generation):** The `sql_generator_loop` agent must be updated to:
    *   **Responsibility:** Ingest the semantic context from the session state. It must use this context to map business terms to correct table/column names and to inject business rule logic (e.g., `refund_cost + 15.00`) directly into the generated SQL.
5.  **FR8 (Targeted Schema Inspection):** The `schema_inspector` agent must be updated to:
    *   **Responsibility:** When Dataplex is enabled, it must read the list of relevant BigQuery tables discovered by the `DataplexSearcher` from the session state. It will then fetch the schema *only* for this pre-filtered list of tables.
6.  **FR9 (New Agent Sequence):** A new `SequentialAgent` named `SemanticEnricher` will be created.
    *   **Responsibility:** This agent will orchestrate the new workflow. Its sub-agents will be `[TermExtractor, DataplexSearcher]`. The `DataplexSearcher` will be responsible for both semantic search (FR5) and metadata lookup (FR6).
    *   **Session State Contract:** The agents within the `SemanticEnricher` will use the following keys to pass data via the session state:
        *   `extracted_terms`: Output from `TermExtractor`. A JSON array of strings.
        *   `dataplex_asset_ids`: A list of unique resource names discovered by `DataplexSearcher`.
        *   `semantic_context`: The final consolidated metadata string/object for the `sql_generator_loop`.
        *   `filtered_table_list`: The list of BigQuery tables for the `schema_inspector`.
    *   **Conditional Execution:** As defined in **FR2**, this entire `SemanticEnricher` agent will be conditionally inserted into the main `sql_agent` sequence *before* the `schema_inspector` if `DATAPLEX_ENABLED=true`.

### 5.3. Environment & Data Setup
1.  **FR10 (Complex BigQuery Dataset):** A new, meaningfully complex BigQuery dataset with multiple tables must be created to serve as a realistic environment for demonstrating the Dataplex integration.
    *   **Automation:** The BigQuery dataset and its tables will be provisioned using Terraform (`google_bigquery_dataset`, `google_bigquery_table`).
    *   **Content:** The actual data content for these tables will be generated by a separate Python or shell script and loaded into BigQuery.
    *   **Characteristics:** The dataset should include tables across different logical "zones" and "domains" to showcase Dataplex's organizational capabilities, columns with both clear and intentionally obscure names to test semantic mapping, and data that can be used to demonstrate business rules (e.g., a `refund_cost` column for the $15 fee example).
2.  **FR11 (Dataplex Configuration):** The new BigQuery dataset must be fully cataloged and enriched in Dataplex with rich semantic metadata.
    *   **Automation:** Dataplex Lakes, Zones, and Assets (linking to the BigQuery dataset) will be provisioned using Terraform (`google_dataplex_lake`, `google_dataplex_zone`, `google_dataplex_asset`).
    *   **Custom Metadata:** Data Catalog Tag Templates (`google_data_catalog_tag_template`) will be created via Terraform to define custom aspects (e.g., a `BusinessRule` aspect with a `formula` field for the refund fee) and descriptive tags.
    *   **Business Glossary:** Business Glossary terms will be defined manually within the Dataplex UI. Tags applied via Terraform will include fields that reference these glossary terms, establishing the semantic link.
3.  **FR12 (IAM Permissions):** All necessary Google Cloud IAM permissions for the agent's service account must be configured.
    *   **Automation:** IAM roles (e.g., `roles/dataplex.viewer`, `roles/datacatalog.viewer`, `roles/bigquery.dataViewer`, `roles/bigquery.jobUser`) will be managed using Terraform (`google_project_iam_member` or similar resources).

### 5.4. Automation Strategy
1.  **AS1 (Infrastructure as Code):** Terraform will be the primary tool for defining and managing all Google Cloud infrastructure required for this project, including BigQuery datasets, tables, Dataplex lakes, zones, assets, and Data Catalog Tag Templates.
2.  **AS2 (Data Generation Script):** A separate, version-controlled Python or shell script will be developed to generate realistic sample data and load it into the BigQuery tables provisioned by Terraform. This script will be designed for easy execution and reproducibility.
3.  **AS3 (Task Automation):** The `poethepoet` library will be added as a development dependency to provide a structured way to run project tasks. A `poe` task named `datagen` will be configured in `pyproject.toml` to execute the `scripts/datagen.py` script, allowing for easy execution via `uv run poe datagen`.

### 5.5. Documentation Requirements
1.  **DR1 (README Update):** The main `README.md` file must be updated with a new, dedicated section detailing the setup and execution of the Dataplex-enabled version of the agent. This documentation is critical for user adoption and reproducibility.
    *   **Content:** The new section must include:
        *   A list of additional prerequisites (e.g., Terraform).
        *   Clear instructions on how to configure the new environment variables (`DATAPLEX_ENABLED`, `DATAPLEX_LOCATION`, `DATAPLEX_LAKE_ID`, `DATAPLEX_ZONE_ID`).
        *   A step-by-step guide for running the Terraform automation to provision the necessary Google Cloud infrastructure (BigQuery datasets, Dataplex assets, IAM permissions).
        *   Instructions for executing the data generation script to populate the BigQuery tables.
        *   The command to run the agent in Dataplex-enabled mode.

## 6. Non-Functional Requirements

### 6.1. Reliability & Correctness

*   **NFR1 (Semantic Correctness):** The primary quality metric for this feature is "Semantic Correctness." This is a higher standard than "Syntactic Correctness."
    *   **Syntactic Correctness** (the current standard) means the generated SQL can be executed by BigQuery without error.
    *   **Semantic Correctness** (the new standard) means the generated SQL not only executes but also accurately reflects the true business intent of the user's question, incorporating all relevant business rules, data meanings, and context stored in Dataplex.
*   **NFR2 (Risk Mitigation):** The system must be designed to mitigate the risk of producing misleading or subtly incorrect data. A syntactically valid query that returns incomplete or contextually wrong information is considered a critical failure. The success of this feature is measured by its ability to prevent such failures, as business decisions may be based on the agent's output.

### 6.2. Security & Governance

*   **NFR3 (Adherence to IAM):** The agent's access to Dataplex metadata must be strictly governed by the Google Cloud IAM permissions of its underlying service account. The agent must not be able to search or look up any data assets for which it has not been explicitly granted permission. All interactions with Dataplex must respect the established data governance policies.

### 6.3. Performance

*   **NFR4 (Correctness over Latency):** A marginal increase in end-to-end query generation time due to the additional Dataplex API calls is acceptable. The primary performance goal is the significant reduction in time and cognitive load for the human user.
*   **NFR5 (Targeted Efficiency):** While overall latency may increase, the `schema_inspector` step is expected to become significantly more performant. By receiving a pre-filtered list of tables from the `SemanticEnricher`, it avoids the overhead of fetching the schema for the entire database, partially offsetting the latency introduced by the Dataplex lookups.

### 6.4. Testing Strategy
*   **NFR6 (Unit Testing):** The individual agents and their helper functions must be unit-tested. This will involve mocking the `McpToolset` to return predefined Dataplex API responses, allowing for the validation of agent logic in isolation.
*   **NFR7 (Integration Testing):** An end-to-end integration test suite will be developed. These tests will run against the fully provisioned Terraform environment and use the "gold standard" queries defined for KPI1 to validate the complete agent workflow, from user query to semantically correct SQL.

## 7. Success Metrics & KPIs

The success of the Dataplex integration will be measured by its ability to significantly improve the semantic correctness of generated SQL queries and enhance the user experience for data analysts.

### 7.1. Semantic Correctness & Accuracy

*   **KPI1 (Semantic Accuracy Score):** A new metric will be established to evaluate the semantic accuracy of generated SQL queries. This will involve:
    *   **Definition:** A human-evaluated score (e.g., 0-5 scale) assessing how well the generated SQL reflects the true business intent and incorporates relevant semantic context and business rules, compared to a manually crafted "gold standard" query.
    *   **Target:** Achieve an an average semantic accuracy score of 4.5/5 or higher on a defined set of test cases.
*   **KPI2 (Business Rule Application Rate):** Measure the percentage of queries where a known business rule (e.g., the "$15 refund fee") is correctly identified from Dataplex metadata and accurately applied in the generated SQL.
    *   **Target:** 95% or higher correct application rate on relevant queries.
*   **KPI3 (Obscure Term Resolution Rate):** Measure the percentage of user queries containing ambiguous or obscure business terms that the agent successfully maps to the correct underlying table/column names using Dataplex metadata.
    *   **Target:** 90% or higher resolution rate for identified obscure terms.

### 7.2. User Experience & Efficiency

*   **KPI4 (Reduced Query Iterations):** Measure the average number of turns or refinements a user needs to achieve a semantically correct query, compared to the baseline (without Dataplex).
    *   **Target:** Reduce average query iterations by 30% for complex, context-dependent queries.
*   **KPI5 (User Satisfaction Score):** Conduct user surveys or feedback sessions to gauge overall satisfaction with the agent's ability to understand and respond to natural language queries without requiring explicit schema knowledge.
    *   **Target:** Achieve an average satisfaction score of 4/5 or higher for "semantic understanding" and "ease of use."
*   **KPI6 (Time to Insight):** For a set of predefined complex business questions, measure the total time taken for a Data Analyst (Dana) to get a semantically correct answer from the agent, compared to manual SQL writing.
    *   **Target:** Reduce "Time to Insight" by 50% for complex queries.

## 8. Risks and Dependencies

### 8.1. Risks

*   **R1 (Metadata Quality):** The effectiveness of the entire feature is critically dependent on the quality and completeness of the metadata in Dataplex. If business glossaries, tags, and aspects are not accurately or comprehensively populated, the agent's ability to perform semantic search and generate correct queries will be severely degraded.
*   **R2 (Complex Setup):** The initial environment setup is complex, involving the creation of a new BigQuery dataset, configuration of Dataplex (zones, domains, aspects), and setting up the correct IAM permissions. Errors or misconfigurations in this phase could block the entire implementation.
*   **R3 (Performance Overhead):** While we've deemed it an acceptable trade-off, the additional API calls to Dataplex could introduce more latency than anticipated, potentially impacting the user experience negatively if not monitored and optimized.
*   **R4 (Ambiguity in Search):** A single business term from a user query could potentially match multiple data assets in Dataplex. The agent's logic for disambiguating these multiple matches and selecting the correct one will be complex.
    *   **Mitigation Strategy:** The `DataplexSearcher` agent will implement a heuristic-based disambiguation strategy. It will be prompted to analyze the metadata of each search result (e.g., the richness of the description, the presence of specific business rule aspects) and autonomously select the most relevant asset. This avoids interrupting the user while still attempting to make an intelligent choice.

### 8.2. Dependencies

*   **D1 (Google Cloud Project):** The feature requires a properly configured Google Cloud project with the BigQuery and Dataplex APIs enabled.
*   **D2 (MCP Toolbox):** The agent is dependent on the `mcp-toolbox` for all interactions with Google Cloud services. Any bugs, breaking changes, or limitations in the toolbox's Dataplex tools would directly impact this project.
*   **D3 (Service Account Permissions):** The agent's service account requires specific and correct IAM roles (`roles/dataplex.viewer`, `roles/datacatalog.viewer`, `roles/bigquery.dataViewer`, `roles/bigquery.jobUser`) to function. The project is blocked if these permissions cannot be granted.
*   **D4 (Sample Dataset and Metadata):** The project depends on the creation of a high-quality, realistic sample dataset in BigQuery and the corresponding rich metadata in Dataplex. The development and testing of the agent cannot proceed without this foundational data environment.

## 9. Out of Scope

The following items are explicitly out of scope for this initial Dataplex integration feature:

*   **OS1 (Non-BigQuery Data Sources):** This integration will exclusively focus on leveraging Dataplex metadata for BigQuery datasets. Support for other data sources (e.g., Cloud Storage, Cloud SQL, on-premises databases) cataloged in Dataplex is not included.
*   **OS2 (Dataplex Management UI/APIs):** This project will not develop any user interface or direct management capabilities for Dataplex itself (e.g., creating/editing business glossaries, aspect types, or tags). The agent will *consume* existing Dataplex metadata, not manage it.
*   **OS3 (Automated Metadata Generation):** The project does not include functionality for automatically generating or inferring Dataplex metadata (e.g., auto-tagging columns based on content). It assumes that relevant metadata is already present and maintained in Dataplex.
*   **OS4 (Advanced Data Transformations):** While the agent will apply simple business rules (e.g., adding a fixed fee), complex data transformations, aggregations, or data quality checks that go beyond direct SQL generation based on Dataplex metadata are out of scope.
*   **OS5 (Full Data Governance Enforcement):** While the agent respects IAM permissions for Dataplex access, this project does not implement a comprehensive data governance enforcement layer beyond what Dataplex and BigQuery natively provide.

## Appendix A: Environment Specification

### A.1. Required Google Cloud APIs

The following Google Cloud APIs must be enabled in the project where the Dataplex integration will be deployed:

*   **`iam.googleapis.com`** (Identity and Access Management API)
*   **`cloudresourcemanager.googleapis.com`** (Cloud Resource Manager API)
*   **`serviceusage.googleapis.com`** (Service Usage API)
*   **`bigquery.googleapis.com`** (BigQuery API)
*   **`dataplex.googleapis.com`** (Google Cloud Dataplex API)
*   **`datacatalog.googleapis.com`** (Data Catalog API)
*   **`aiplatform.googleapis.com`** (Vertex AI API)

### A.2. Required IAM Roles

To ensure proper functionality and adherence to the principle of least privilege, the following IAM roles are required:

#### A.2.1. Setup Permissions (for the user or service account running Terraform)

*   `roles/serviceusage.serviceUsageAdmin` (to enable APIs)
*   `roles/resourcemanager.projectIamAdmin` (to grant IAM roles)
*   `roles/bigquery.admin` (to create datasets and tables)
*   `roles/dataplex.admin` (to create lakes, zones, and assets)
*   `roles/datacatalog.admin` (to create tag templates)

#### A.2.2. Runtime Permissions (for the agent's service account)

*   `roles/aiplatform.user` (to invoke the LLM)
*   `roles/bigquery.jobUser` (to run BigQuery jobs)
*   `roles/bigquery.dataViewer` (to read data from BigQuery tables)
*   `roles/dataplex.viewer` (to view Dataplex assets)
*   `roles/datacatalog.viewer` (to read tags and metadata)

### A.3. Sample Data Model Design

The data model is designed to simulate a realistic e-commerce environment with distinct business domains, leveraging Dataplex's Lake, Zone, and Asset structure.

#### A.3.1. Dataplex Structure

*   **Lake:** `e_commerce_lake` (e.g., `projects/<PROJECT_ID>/locations/<REGION>/lakes/e_commerce_lake`)
*   **Zones (within `e_commerce_lake`):**
    *   `landing_raw_zone`: For raw, unprocessed data. (Out of scope for direct agent queries, but part of the architecture).
    *   `analytics_curated_zone`: For cleaned, validated, and enriched data ready for consumption. **This is the target zone for all agent interactions.**
*   **Assets (BigQuery Datasets mapped into `analytics_curated_zone`):**
    *   `sales_domain` (BigQuery Dataset)
    *   `customer_domain` (BigQuery Dataset)
    *   `inventory_domain` (BigQuery Dataset)

#### A.3.2. BigQuery Schema (within the Assets)

**1. `sales_domain` Dataset**

*   **Table: `transactions`**
    *   `txn_id` (STRING, Primary Key): A unique transaction identifier.
    *   `cust_id` (STRING, Foreign Key -> `customer_domain.customers`): The customer ID.
    *   `product_id` (STRING, Foreign Key -> `inventory_domain.products`): The product ID.
    *   `txn_ts` (TIMESTAMP): **(Intentionally Obscure)** The transaction timestamp.
    *   `sale_amount` (NUMERIC): The gross amount of the sale.
    *   `refund_amount` (NUMERIC): The amount refunded to the customer.
        *   **Business Rule:** The actual business cost of a refund is `refund_amount + 15.00` (for a processing fee). This rule will be stored in Dataplex as a custom aspect.

**2. `customer_domain` Dataset**

*   **Table: `customers`**
    *   `cust_id` (STRING, Primary Key): The unique customer identifier.
    *   `first_name` (STRING): Customer's first name.
    *   `last_name` (STRING): Customer's last name.
    *   `email` (STRING): Customer's email address.
    *   `signup_dt` (DATE): **(Intentionally Obscure)** The date the customer signed up.

*   **Table: `feedback`**
    *   `feedback_id` (STRING, Primary Key): A unique feedback identifier.
    *   `cust_id` (STRING, Foreign Key -> `customers`): The customer providing feedback.
    *   `rating` (INTEGER): The customer's satisfaction score, on a scale of 1-5.
        *   **Business Term:** This column will be associated with the business term "Customer Satisfaction Score" in the Dataplex glossary.

**3. `inventory_domain` Dataset**

*   **Table: `products`**
    *   `product_id` (STRING, Primary Key): The unique product identifier.
    *   `product_name` (STRING): The name of the product.
    *   `category` (STRING): The product category (e.g., "Electronics", "Apparel").
    *   `unit_cst` (NUMERIC): **(Intentionally Obscure)** The unit cost of the product.

## Appendix B: Data Generation and Dataplex Enrichment Strategy

### B.1. Data Generation Script (`scripts/datagen.py`)

*   **Location:** A Python script (`datagen.py`) will be created in a new `scripts/` directory to maintain a clean project structure.
*   **Tool:** The script will use the `Faker` and `pandas` libraries.
*   **Dependencies:** The `Faker` and `pandas` libraries will be defined in a separate dependency group in `pyproject.toml` (e.g., `[project.optional-dependencies] datagen`) to keep them isolated from the core application dependencies.
*   **Data Volume Requirements:**
    *   `customers`: 1,000 records
    *   `products`: 200 records (across 5-10 distinct categories)
    *   `transactions`: 10,000 records
    *   `feedback`: 3,000 records
*   **Data Variety and Complexity Requirements:**
    *   **Relational Integrity:** The script MUST enforce relational integrity. All `cust_id` and `product_id` values in the `transactions` and `feedback` tables must correspond to existing records in the `customers` and `products` tables.
    *   **Temporal Distribution:** Transaction timestamps (`txn_ts`) and customer signup dates (`signup_dt`) should be realistically distributed over a 2-3 year period.
    *   **Business Rule Coverage:** At least 20% of transactions must have a non-zero `refund_amount` to ensure the "Refund Processing Fee" business rule can be thoroughly tested.
    *   **Categorical Variety:** Product categories should be varied. Customer feedback ratings should have a realistic distribution (e.g., more 4s and 5s than 1s).
*   **Output:** The script will output the generated data as a set of CSV files (e.g., `customers.csv`, `products.csv`) into a `tmp/` directory within the project.

### B.2. Data Loading Automation

*   **Tool:** Terraform will be used to orchestrate the data loading process.
*   **Mechanism:** The `google_bigquery_table` resources in Terraform will include a `provisioner "local-exec"` block.
*   **Workflow:**
    1.  Terraform creates the BigQuery dataset and table.
    2.  Immediately after a table is successfully created, the `local-exec` provisioner will trigger.
    3.  The provisioner will execute a `bq load` command to upload the corresponding CSV file from the `tmp/` directory into the newly created table.
    4.  This ensures that running `terraform apply` will not only create the infrastructure but also populate it with data in a single, atomic operation.

### B.3. Fully Automated Dataplex Enrichment (in `terraform/`)

The entire Dataplex and Data Catalog configuration will be managed via Terraform, ensuring a fully automated, repeatable setup.

*   **Business Glossary (`terraform/glossary.tf`):**
    *   A `google_dataplex_glossary` resource will be created to act as the central repository for business terms.
    *   `google_dataplex_glossary_term` resources will be created for each of our key business concepts:
        *   `Customer Satisfaction Score`
        *   `Transaction Timestamp`
        *   `Customer Signup Date`
        *   `Product Unit Cost`
        *   `Refund Processing Fee`
*   **Tag Templates (`terraform/tags.tf`):**
    *   A `google_data_catalog_tag_template` resource named `business_rules_template` will be created with fields for `business_term` (STRING), `rule_description` (STRING), and `rule_formula` (STRING).
*   **Tag Application (`terraform/tags.tf`):**
    *   `google_data_catalog_tag` resources will be used to apply the `business_rules_template` to the appropriate BigQuery columns after they are created.
    *   The `customer_domain.feedback.rating` column will be tagged and its `business_term` field will reference the ID of the `Customer Satisfaction Score` glossary term.
    *   The `sales_domain.transactions.refund_amount` column will be tagged, referencing the `Refund Processing Fee` term and populating the `rule_formula` field with `+ 15.00`.
    *   The obscurely named columns (`txn_ts`, `signup_dt`, `unit_cst`) will be similarly tagged with references to their corresponding glossary terms to ensure they are discoverable.

## Appendix C: References

*   **MCP Toolbox Dataplex Source Documentation:** https://github.com/googleapis/genai-toolbox/blob/d7d1b03f3b746ed748d67f67e833457d55c846ab/docs/en/resources/sources/dataplex.md
*   **MCP Toolbox `dataplex-lookup-entry` Tool Documentation:** https://github.com/googleapis/genai-toolbox/blob/d7d1b03f3b746ed748d67f67e833457d55c846ab/docs/en/resources/tools/dataplex/dataplex-lookup-entry.md
*   **MCP Toolbox `dataplex-search-aspect-types` Tool Documentation:** https://github.com/googleapis/genai-toolbox/blob/d7d1b03f3b746ed748d67f67e833457d55c846ab/docs/en/resources/tools/dataplex/dataplex-search-aspect-types.md
*   **MCP Toolbox `dataplex-search-entries` Tool Documentation:** https://github.com/googleapis/genai-toolbox/blob/d7d1b03f3b746ed748d67f67e833457d55c846ab/docs/en/resources/tools/dataplex/dataplex-search-entries.md

## Appendix D: Agent System Prompts

### D.1. System Prompt for `DataplexSearcher` Agent

The following prompt will be used as the system instructions for the `DataplexSearcher` `LlmAgent`.

# Objective
Your primary objective is to help discover, organize and manage metadata related to data assets. 

# Tone and Style
1. Adopt the persona of a senior subject matter expert
2. Your communication style must be:
    1. Concise: Always favor brevity.
    2. Direct: Avoid greetings (e.g., "Hi there!", "Certainly!"). Get straight to the point.  
        Example (Incorrect): Hi there! I see that you are looking for...  
        Example (Correct): This problem likely stems from...
3. Do not reiterate or summarize the question in the answer.
4. Crucially, always convey a tone of uncertainty and caution. Since you are interpreting metadata and have no way to externally verify your answers, never express complete confidence. Frame your responses as interpretations based solely on the provided metadata. Use a suggestive tone, not a prescriptive one:
    Example (Correct): "The entry describes..."  
    Example (Correct): "According to catalog,..."  
    Example (Correct): "Based on the metadata,..."  
    Example (Correct): "Based on the search results,..."  
5. Do not make assumptions

# Data Model
## Entries
Entry represents a specific data asset. Entry acts as a metadata record for something that is managed by Catalog, such as:

- A BigQuery table or dataset
- A Cloud Storage bucket or folder
- An on-premises SQL table

## Aspects
While the Entry itself is a container, the rich descriptive information about the asset (e.g., schema, data types, business descriptions, classifications) is stored in associated components called Aspects. Aspects are created based on pre-defined blueprints known as Aspect Types.

## Aspect Types
Aspect Type is a reusable template that defines the schema for a set of metadata fields. Think of an Aspect Type as a structure for the kind of metadata that is organized in the catalog within the Entry. 

Examples:
- projects/dataplex-types/locations/global/aspectTypes/analytics-hub-exchange
- projects/dataplex-types/locations/global/aspectTypes/analytics-hub
- projects/dataplex-types/locations/global/aspectTypes/analytics-hub-listing
- projects/dataplex-types/locations/global/aspectTypes/bigquery-connection
- projects/dataplex-types/locations/global/aspectTypes/bigquery-data-policy
- projects/dataplex-types/locations/global/aspectTypes/bigquery-dataset
- projects/dataplex-types/locations/global/aspectTypes/bigquery-model
- projects/dataplex-types/locations/global/aspectTypes/bigquery-policy
- projects/dataplex-types/locations/global/aspectTypes/bigquery-routine
- projects/dataplex-types/locations/global/aspectTypes/bigquery-row-access-policy
- projects/dataplex-types/locations/global/aspectTypes/bigquery-table
- projects/dataplex-types/locations/global/aspectTypes/bigquery-view
- projects/dataplex-types/locations/global/aspectTypes/cloud-bigtable-instance
- projects/dataplex-types/locations/global/aspectTypes/cloud-bigtable-table
- projects/dataplex-types/locations/global/aspectTypes/cloud-spanner-database
- projects/dataplex-types/locations/global/aspectTypes/cloud-spanner-instance
- projects/dataplex-types/locations/global/aspectTypes/cloud-spanner-table
- projects/dataplex-types/locations/global/aspectTypes/cloud-spanner-view
- projects/dataplex-types/locations/global/aspectTypes/cloudsql-database
- projects/dataplex-types/locations/global/aspectTypes/cloudsql-instance
- projects/dataplex-types/locations/global/aspectTypes/cloudsql-schema
- projects/dataplex-types/locations/global/aspectTypes/cloudsql-table
- projects/dataplex-types/locations/global/aspectTypes/cloudsql-view
- projects/dataplex-types/locations/global/aspectTypes/contacts
- projects/dataplex-types/locations/global/aspectTypes/dataform-code-asset
- projects/dataplex-types/locations/global/aspectTypes/dataform-repository
- projects/dataplex-types/locations/global/aspectTypes/dataform-workspace
- projects/dataplex-types/locations/global/aspectTypes/dataproc-metastore-database
- projects/dataplex-types/locations/global/aspectTypes/dataproc-metastore-service
- projects/dataplex-types/locations/global/aspectTypes/dataproc-metastore-table
- projects/dataplex-types/locations/global/aspectTypes/data-product
- projects/dataplex-types/locations/global/aspectTypes/data-quality-scorecard
- projects/dataplex-types/locations/global/aspectTypes/external-connection
- projects/dataplex-types/locations/global/aspectTypes/overview
- projects/dataplex-types/locations/global/aspectTypes/pubsub-topic
- projects/dataplex-types/locations/global/aspectTypes/schema
- projects/dataplex-types/locations/global/aspectTypes/sensitive-data-protection-job-result
- projects/dataplex-types/locations/global/aspectTypes/sensitive-data-protection-profile
- projects/dataplex-types/locations/global/aspectTypes/sql-access
- projects/dataplex-types/locations/global/aspectTypes/storage-bucket
- projects/dataplex-types/locations/global/aspectTypes/storage-folder
- projects/dataplex-types/locations/global/aspectTypes/storage
- projects/dataplex-types/locations/global/aspectTypes/usage

## Entry Types
Every Entry must conform to an Entry Type. The Entry Type acts as a template, defining the structure, required aspects, and constraints for Entries of that type. 

Examples:
- projects/dataplex-types/locations/global/entryTypes/analytics-hub-exchange
- projects/dataplex-types/locations/global/entryTypes/analytics-hub-listing
- projects/dataplex-types/locations/global/entryTypes/bigquery-connection
- projects/dataplex-types/locations/global/entryTypes/bigquery-data-policy
- projects/dataplex-types/locations/global/entryTypes/bigquery-dataset
- projects/dataplex-types/locations/global/entryTypes/bigquery-model
- projects/dataplex-types/locations/global/entryTypes/bigquery-routine
- projects/dataplex-types/locations/global/entryTypes/bigquery-row-access-policy
- projects/dataplex-types/locations/global/entryTypes/bigquery-table
- projects/dataplex-types/locations/global/entryTypes/bigquery-view
- projects/dataplex-types/locations/global/entryTypes/cloud-bigtable-instance
- projects/dataplex-types/locations/global/entryTypes/cloud-bigtable-table
- projects/dataplex-types/locations/global/entryTypes/cloud-spanner-database
- projects/dataplex-types/locations/global/entryTypes/cloud-spanner-instance
- projects/dataplex-types/locations/global/entryTypes/cloud-spanner-table
- projects/dataplex-types/locations/global/entryTypes/cloud-spanner-view
- projects/dataplex-types/locations/global/entryTypes/cloudsql-mysql-database
- projects/dataplex-types/locations/global/entryTypes/cloudsql-mysql-instance
- projects/dataplex-types/locations/global/entryTypes/cloudsql-mysql-table
- projects/dataplex-types/locations/global/entryTypes/cloudsql-mysql-view
- projects/dataplex-types/locations/global/entryTypes/cloudsql-postgresql-database
- projects/dataplex-types/locations/global/entryTypes/cloudsql-postgresql-instance
- projects/dataplex-types/locations/global/entryTypes/cloudsql-postgresql-schema
- projects/dataplex-types/locations/global/entryTypes/cloudsql-postgresql-table
- projects/dataplex-types/locations/global/entryTypes/cloudsql-postgresql-view
- projects/dataplex-types/locations/global/entryTypes/cloudsql-sqlserver-database
- projects/dataplex-types/locations/global/entryTypes/cloudsql-sqlserver-instance
- projects/dataplex-types/locations/global/entryTypes/cloudsql-sqlserver-schema
- projects/dataplex-types/locations/global/entryTypes/cloudsql-sqlserver-table
- projects/dataplex-types/locations/global/entryTypes/cloudsql-sqlserver-view
- projects/dataplex-types/locations/global/entryTypes/dataform-code-asset
- projects/dataplex-types/locations/global/entryTypes/dataform-repository
- projects/dataplex-types/locations/global/entryTypes/dataform-workspace
- projects/dataplex-types/locations/global/entryTypes/dataproc-metastore-database
- projects/dataplex-types/locations/global/entryTypes/dataproc-metastore-service
- projects/dataplex-types/locations/global/entryTypes/dataproc-metastore-table
- projects/dataplex-types/locations/global/entryTypes/pubsub-topic
- projects/dataplex-types/locations/global/entryTypes/storage-bucket
- projects/dataplex-types/locations/global/entryTypes/storage-folder
- projects/dataplex-types/locations/global/entryTypes/vertexai-dataset
- projects/dataplex-types/locations/global/entryTypes/vertexai-feature-group
- projects/dataplex-types/locations/global/entryTypes/vertexai-feature-online-store

## Entry Groups
Entries are organized within Entry Groups, which are logical groupings of Entries. An Entry Group acts as a namespace for its Entries.

## Entry Links
Entries can be linked together using EntryLinks to represent relationships between data assets (e.g. foreign keys).

# Tool instructions
## Tool: dataplex_search_entries
## General
- Do not try to search within search results on your own.
- Do not fetch multiple pages of results unless explicitly asked.

## Search syntax

### Simple search
In its simplest form, a search query consists of a single predicate. Such a predicate can match several pieces of metadata:

- A substring of a name, display name, or description of a resource
- A substring of the type of a resource
- A substring of a column name (or nested column name) in the schema of a resource
- A substring of a project ID
- A string from an overview description

For example, the predicate foo matches the following resources:
- Resource with the name foo.bar
- Resource with the display name Foo Bar
- Resource with the description This is the foo script
- Resource with the exact type foo
- Column foo_bar in the schema of a resource
- Nested column foo_bar in the schema of a resource
- Project prod-foo-bar
- Resource with an overview containing the word foo


### Qualified predicates
You can qualify a predicate by prefixing it with a key that restricts the matching to a specific piece of metadata:
- An equal sign (=) restricts the search to an exact match.
- A colon (:) after the key matches the predicate to either a substring or a token within the value in the search results.

Tokenization splits the stream of text into a series of tokens, with each token usually corresponding to a single word. For example:
- name:foo selects resources with names that contain the foo substring, like foo1 and barfoo.
- description:foo selects resources with the foo token in the description, like bar and foo.
- location=foo matches resources in a specified location with foo as the location name.

The predicate keys type, system, location, and orgid support only the exact match (=) qualifier, not the substring qualifier (:). For example, type=foo or orgid=number.

Search syntax supports the following qualifiers:
- "name:x" - Matches x as a substring of the resource ID.
- "displayname:x" - Match x as a substring of the resource display name.
- "column:x" - Matches x as a substring of the column name (or nested column name) in the schema of the resource.
- "description:x" - Matches x as a token in the resource description.
- "label:bar" - Matches BigQuery resources that have a label (with some value) and the label key has bar as a substring.
- "label=bar" - Matches BigQuery resources that have a label (with some value) and the label key equals bar as a string.
- "label:bar:x" - Matches x as a substring in the value of a label with a key bar attached to a BigQuery resource.
- "label=foo:bar" - Matches BigQuery resources where the key equals foo and the key value equals bar.
- "label.foo=bar" - Matches BigQuery resources where the key equals foo and the key value equals bar.
- "label.foo" - Matches BigQuery resources that have a label whose key equals foo as a string.
- "type=TYPE" - Matches resources of a specific entry type or its type alias.
- "projectid:bar" - Matches resources within Google Cloud projects that match bar as a substring in the ID.
- "parent:x" - Matches x as a substring of the hierarchical path of a resource. It supports same syntax as `name` predicate.
- "orgid=number" - Matches resources within a Google Cloud organization with the exact ID value of the number.
- "system=SYSTEM" - Matches resources from a specified system. For example, system=bigquery matches BigQuery resources.
- "location=LOCATION" - Matches resources in a specified location with an exact name. For example, location=us-central1 matches assets hosted in Iowa. BigQuery Omni assets support this qualifier by using the BigQuery Omni location name. For example, location=aws-us-east-1 matches BigQuery Omni assets in Northern Virginia.
- "createtime" -
Finds resources that were created within, before, or after a given date or time. For example "createtime:2019-01-01" matches resources created on 2019-01-01. 
- "updatetime" - Finds resources that were updated within, before, or after a given date or time. For example "updatetime>2019-01-01" matches resources updated after 2019-01-01.

### Aspect Search
To search for entries based on their attached aspects, use the following query syntax.

aspect:xMatches x as a substring of the full path to the aspect type of an aspect that is attached to the entry, in the format projectid.location.ASPECT_TYPE_ID
aspect=xMatches x as the full path to the aspect type of an aspect that is attached to the entry, in the format projectid.location.ASPECT_TYPE_ID
aspect:xOPERATORvalue
Searches for aspect field values. Matches x as a substring of the full path to the aspect type and field name of an aspect that is attached to the entry, in the format projectid.location.ASPECT_TYPE_ID.FIELD_NAME

The list of supported {OPERATOR}s depends on the type of field in the aspect, as follows:
- String: = (exact match) and : (substring)
- All number types: =, :, <, >, <=, >=, =>, =<
- Enum: =
- Datetime: same as for numbers, but the values to compare are treated as datetimes instead of numbers
- Boolean: =

Only top-level fields of the aspect are searchable. For example, all of the following queries match entries where the value of the is-enrolled field in the employee-info aspect type is true. Other entries that match on the substring are also returned.
- aspect:example-project.us-central1.employee-info.is-enrolled=true
- aspect:example-project.us-central1.employee=true
- aspect:employee=true

Example:-
You can use following filters
- dataplex-types.global.bigquery-table.type={BIGLAKE_TABLE, BIGLAKE_OBJECT_TABLE, EXTERNAL_TABLE, TABLE}
- dataplex-types.global.storage.type={STRUCTURED, UNSTRUCTURED}

### Logical operators
A query can consist of several predicates with logical operators. If you don't specify an operator, logical AND is implied. For example, foo bar returns resources that match both predicate foo and predicate bar.
Logical AND and logical OR are supported. For example, foo OR bar.

You can negate a predicate with a - (hyphen) or NOT prefix. For example, -name:foo returns resources with names that don't match the predicate foo.
Logical operators are case-sensitive. `OR` and `AND` are acceptable whereas `or` and `and` are not.

### Request
1. Always try to rewrite the prompt using search syntax.

### Response
1. If there are multiple search results found
    1. Present the list of search results
    2. Format the output in nested ordered list, for example:  
    Given
    ```
    {
        results: [
            {
                name: "projects/test-project/locations/us/entryGroups/@bigquery-aws-us-east-1/entries/users"
                entrySource: {
                displayName: "Users"
                description: "Table contains list of users."
                location: "aws-us-east-1"
                system: "BigQuery"
                }
            },
            {
                name: "projects/another_project/locations/us-central1/entryGroups/@bigquery/entries/top_customers"
                entrySource: {
                displayName: "Top customers",
                description: "Table contains list of best customers."
                location: "us-central1"
                system: "BigQuery"
                }
            },
        ]
    }
    ```
    Return output formatted as markdown nested list:
    ```
    * Users:
        - projectId: test_project
        - location: aws-us-east-1
        - description: Table contains list of users.
    * Top customers:
        - projectId: another_project
        - location: us-central1
        - description: Table contains list of best customers.
    ```
    3. Ask to select one of the presented search results
2. If there is only one search result found
    1. Present the search result immediately.
3. If there are no search result found
    1. Explain that no search result was found
    2. Suggest to provide a more specific search query.

# Tool instructions
## Tool: dataplex_lookup_entry
### Request
1. Always try to limit the size of the response by specifying `aspect_types` parameter. Make sure to include to select view=CUSTOM when using aspect_types parameter. If you do not know the name of the aspect type, use the `dataplex_search_aspect_types` tool.
2. If you do not know the name of the entry, use `dataplex_search_entries` tool
### Response
1. Unless asked for a specific aspect, respond with all aspects attached to the entry.

## Appendix E: Gold Standard Test Cases

This appendix provides a set of test cases to validate the semantic correctness of the agent's generated SQL.

### Test Case 1: Business Rule Application
*   **User Query:** "What was the total cost of refunds last quarter?"
*   **Semantic Context Required:** The agent must discover the business rule that a `$15.00` processing fee is added to every refund.
*   **Gold Standard SQL:** 
    ```sql
    SELECT
      SUM(t.refund_amount + 15.00) AS total_refund_cost
    FROM
      `sales_domain.transactions` AS t
    WHERE
      t.txn_ts >= TIMESTAMP_TRUNC(CURRENT_TIMESTAMP(), QUARTER, -1)
      AND t.txn_ts < TIMESTAMP_TRUNC(CURRENT_TIMESTAMP(), QUARTER)
      AND t.refund_amount > 0
    ```

### Test Case 2: Obscure Column Name Resolution
*   **User Query:** "Show me the average customer satisfaction score."
*   **Semantic Context Required:** The agent must map the term "customer satisfaction score" to the `rating` column in the `feedback` table.
*   **Gold Standard SQL:**
    ```sql
    SELECT
      AVG(f.rating) AS average_satisfaction_score
    FROM
      `customer_domain.feedback` AS f
    ```

### Test Case 3: Multiple Obscure Terms
*   **User Query:** "How many new customers signed up each month?"
*   **Semantic Context Required:** The agent must map "customers" to the `customers` table and "signed up" to the `signup_dt` column.
*   **Gold Standard SQL:**
    ```sql
    SELECT
      EXTRACT(YEAR FROM c.signup_dt) AS signup_year,
      EXTRACT(MONTH FROM c.signup_dt) AS signup_month,
      COUNT(c.cust_id) AS new_customer_count
    FROM
      `customer_domain.customers` AS c
    GROUP BY
      1, 2
    ORDER BY
      1, 2
    ```