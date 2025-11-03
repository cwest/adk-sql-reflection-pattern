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

resource "google_dataplex_aspect_type" "refund_amount_aspect_type" {
  project          = var.project_id
  location         = var.region
  aspect_type_id   = "refund-amount-aspect-type"
  display_name     = "refund_amount"
  description      = "Aspect Type for defining business rules and terms."
  metadata_template = jsonencode({
    name         = "BusinessRulesTemplate"
    type         = "record"
    record_fields = [
      {
        name        = "business_term"
        type        = "string"
        index       = 1
        constraints = {
          required = true
        }
        annotations = {
          display_name = "Business Term"
          description  = "The business term associated with the data asset."
        }
      },
      {
        name        = "rule_description"
        type        = "string"
        index       = 2
        annotations = {
          display_name = "Rule Description"
          description  = "A description of the business rule."
        }
      },
      {
        name        = "rule_formula"
        type        = "string"
        index       = 3
        annotations = {
          display_name = "Rule Formula"
          description  = "The formula or logic for the business rule (e.g., '+ 15.00')."
        }
      }
    ]
  })
}

resource "google_dataplex_aspect_type" "txn_ts_aspect_type" {
  project          = var.project_id
  location         = var.region
  aspect_type_id   = "txn-ts-aspect-type"
  display_name     = "txn_ts"
  description      = "Aspect Type for defining business rules and terms."
  metadata_template = jsonencode({
    name         = "BusinessRulesTemplate"
    type         = "record"
    record_fields = [
      {
        name        = "business_term"
        type        = "string"
        index       = 1
        constraints = {
          required = true
        }
        annotations = {
          display_name = "Business Term"
          description  = "The business term associated with the data asset."
        }
      },
      {
        name        = "rule_description"
        type        = "string"
        index       = 2
        annotations = {
          display_name = "Rule Description"
          description  = "A description of the business rule."
        }
      },
      {
        name        = "rule_formula"
        type        = "string"
        index       = 3
        annotations = {
          display_name = "Rule Formula"
          description  = "The formula or logic for the business rule (e.g., '+ 15.00')."
        }
      }
    ]
  })
}

resource "google_dataplex_aspect_type" "signup_dt_aspect_type" {
  project          = var.project_id
  location         = var.region
  aspect_type_id   = "signup-dt-aspect-type"
  display_name     = "signup_dt"
  description      = "Aspect Type for defining business rules and terms."
  metadata_template = jsonencode({
    name         = "BusinessRulesTemplate"
    type         = "record"
    record_fields = [
      {
        name        = "business_term"
        type        = "string"
        index       = 1
        constraints = {
          required = true
        }
        annotations = {
          display_name = "Business Term"
          description  = "The business term associated with the data asset."
        }
      },
      {
        name        = "rule_description"
        type        = "string"
        index       = 2
        annotations = {
          display_name = "Rule Description"
          description  = "A description of the business rule."
        }
      },
      {
        name        = "rule_formula"
        type        = "string"
        index       = 3
        annotations = {
          display_name = "Rule Formula"
          description  = "The formula or logic for the business rule (e.g., '+ 15.00')."
        }
      }
    ]
  })
}

resource "google_dataplex_aspect_type" "rating_aspect_type" {
  project          = var.project_id
  location         = var.region
  aspect_type_id   = "rating-aspect-type"
  display_name     = "rating"
  description      = "Aspect Type for defining business rules and terms."
  metadata_template = jsonencode({
    name         = "BusinessRulesTemplate"
    type         = "record"
    record_fields = [
      {
        name        = "business_term"
        type        = "string"
        index       = 1
        constraints = {
          required = true
        }
        annotations = {
          display_name = "Business Term"
          description  = "The business term associated with the data asset."
        }
      },
      {
        name        = "rule_description"
        type        = "string"
        index       = 2
        annotations = {
          display_name = "Rule Description"
          description  = "A description of the business rule."
        }
      },
      {
        name        = "rule_formula"
        type        = "string"
        index       = 3
        annotations = {
          display_name = "Rule Formula"
          description  = "The formula or logic for the business rule (e.g., '+ 15.00')."
        }
      }
    ]
  })
}

resource "google_dataplex_aspect_type" "unit_cst_aspect_type" {
  project          = var.project_id
  location         = var.region
  aspect_type_id   = "unit-cst-aspect-type"
  display_name     = "unit_cst"
  description      = "Aspect Type for defining business rules and terms."
  metadata_template = jsonencode({
    name         = "BusinessRulesTemplate"
    type         = "record"
    record_fields = [
      {
        name        = "business_term"
        type        = "string"
        index       = 1
        constraints = {
          required = true
        }
        annotations = {
          display_name = "Business Term"
          description  = "The business term associated with the data asset."
        }
      },
      {
        name        = "rule_description"
        type        = "string"
        index       = 2
        annotations = {
          display_name = "Rule Description"
          description  = "A description of the business rule."
        }
      },
      {
        name        = "rule_formula"
        type        = "string"
        index       = 3
        annotations = {
          display_name = "Rule Formula"
          description  = "The formula or logic for the business rule (e.g., '+ 15.00')."
        }
      }
    ]
  })
}

resource "google_dataplex_entry_group" "bigquery_entry_group" {
  project        = var.project_id
  location       = var.region
  entry_group_id = "bigquery-entry-group"
  display_name   = "BigQuery Entry Group"
  description    = "Entry group for BigQuery tables."
}

resource "google_dataplex_entry_type" "table_entry_type" {
  project        = var.project_id
  location       = var.region
  entry_type_id  = "table"
  display_name   = "Table"
  description    = "Entry type for BigQuery tables."
}

resource "null_resource" "attach_dataplex_metadata" {
  depends_on = [
    google_dataplex_asset.sales_domain_asset,
    google_dataplex_asset.inventory_domain_asset,
    google_dataplex_asset.customer_domain_asset,
    google_dataplex_aspect_type.refund_amount_aspect_type,
    google_dataplex_aspect_type.txn_ts_aspect_type,
    google_dataplex_aspect_type.signup_dt_aspect_type,
    google_dataplex_aspect_type.rating_aspect_type,
    google_dataplex_aspect_type.unit_cst_aspect_type
  ]

  provisioner "local-exec" {
    command = "uv run poe metadata"
    environment = {
      GOOGLE_CLOUD_PROJECT = var.google_cloud_project
      DATAPLEX_LOCATION    = var.region
      DATAPLEX_LAKE_ID     = var.dataplex_lake_id
      DATAPLEX_ZONE_ID     = var.dataplex_zone_id
    }
  }
}
