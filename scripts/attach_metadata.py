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

import os
import time
from google.cloud import dataplex_v1
from google.protobuf.struct_pb2 import Struct
import google.api_core.exceptions

def get_project_number(project_id: str) -> str:
    """Gets the project number for a given project ID."""
    import google.auth
    from google.cloud import resourcemanager_v3

    print(f"Fetching project number for project ID: {project_id}...")
    creds, _ = google.auth.default()
    client = resourcemanager_v3.ProjectsClient(credentials=creds)
    request = resourcemanager_v3.GetProjectRequest(name=f"projects/{project_id}")
    project = client.get_project(request=request)
    project_number = project.name.split("/")[1]
    print(f"Found project number: {project_number}")
    return project_number

def attach_aspect(
    client: dataplex_v1.CatalogServiceClient,
    project_id: str,
    project_number: str,
    region: str,
    entry_group_id: str,
    entry_id: str,
    aspect_type_id: str,
    column: str,
    aspect_data: dict,
):
    """Attaches a Dataplex aspect to a BigQuery column."""
    entry_path = client.entry_path(
        project=project_number,
        location=region,
        entry_group=entry_group_id,
        entry=entry_id,
    )
    print(f"  DEBUG: Constructed entry_path: {entry_path}")
    aspect_type_path = f"projects/{project_number}/locations/{region}/aspectTypes/{aspect_type_id}"
    aspect_key = f"{project_id}.{region}.{aspect_type_id}"

    print(f"\nProcessing entry: {entry_id}")
    print(f"  Column: {column}")
    print(f"  Checking for Dataplex entry at path: {entry_path}...")

    # Polling logic to wait for the entry to be created
    max_retries = 12
    retry_delay_seconds = 10
    for attempt in range(max_retries):
        try:
            existing_entry = client.get_entry(name=entry_path)
            print(f"  SUCCESS: Dataplex entry found on attempt {attempt + 1}.")
            break
        except google.api_core.exceptions.NotFound:
            print(f"  INFO: Entry not found on attempt {attempt + 1}/{max_retries}. Retrying in {retry_delay_seconds}s...")
            time.sleep(retry_delay_seconds)
    else:
        print(f"  ERROR: Dataplex entry not found after {max_retries} attempts. Aborting.")
        raise RuntimeError(f"Failed to find Dataplex entry: {entry_path}")

    aspect = dataplex_v1.Aspect()
    aspect.aspect_type = aspect_type_path
    aspect.path = f"schema.fields.{column}"

    s = Struct()
    s.update(aspect_data)
    aspect.data = s

    new_entry = dataplex_v1.Entry()
    new_entry.name = existing_entry.name
    new_entry.aspects = existing_entry.aspects
    new_entry.aspects[aspect_key] = aspect

    request = dataplex_v1.UpdateEntryRequest(
        entry=new_entry,
        update_mask={"paths": ["aspects"]},
        aspect_keys=[aspect_key],
    )
    print(f"  Attaching aspect to column '{column}'...")
    client.update_entry(request=request)
    print(f"  SUCCESS: Successfully attached aspect to column '{column}' for entry '{entry_id}'")

def main():
    """Main function to attach metadata to BigQuery columns."""
    project_id = os.getenv("GOOGLE_CLOUD_PROJECT")
    region = os.getenv("DATAPLEX_LOCATION")
    entry_group_id = "@bigquery"

    if not all([project_id, region]):
        raise ValueError("GOOGLE_CLOUD_PROJECT and DATAPLEX_LOCATION must be set.")

    print("--- Starting Dataplex Metadata Attachment Script ---")
    print(f"Project ID: {project_id}")
    print(f"Region: {region}")

    project_number = get_project_number(project_id)
    client = dataplex_v1.CatalogServiceClient()

    domain_map = {
        "sales_domain": {
            "transactions": [
                ("refund_amount", "refund-amount-aspect-type", {
                    "business_term": "Refund Processing Fee",
                    "rule_description": "A $15.00 processing fee is added to the cost of every refund.",
                    "rule_formula": "+ 15.00",
                }),
                ("txn_ts", "txn-ts-aspect-type", {"business_term": "Transaction Timestamp"}),
            ]
        },
        "customer_domain": {
            "customers": [("signup_dt", "signup-dt-aspect-type", {"business_term": "Customer Signup Date"})],
            "feedback": [("rating", "rating-aspect-type", {"business_term": "Customer Satisfaction Score"})],
        },
        "inventory_domain": {
            "products": [("unit_cst", "unit-cst-aspect-type", {"business_term": "Product Unit Cost"})],
        }
    }

    for dataset_id, tables in domain_map.items():
        for table, aspects in tables.items():
            entry_id = f"bigquery.googleapis.com/projects/{project_id}/datasets/{dataset_id}/tables/{table}"
            for column, aspect_type_id, data in aspects:
                attach_aspect(
                    client,
                    project_id,
                    project_number,
                    region,
                    entry_group_id,
                    entry_id,
                    aspect_type_id,
                    column,
                    data,
                )
    
    print("\n--- Script finished successfully. ---")

if __name__ == "__main__":
    main()
