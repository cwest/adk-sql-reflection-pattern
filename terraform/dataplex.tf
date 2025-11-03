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

resource "google_dataplex_lake" "e_commerce_lake" {
  project       = var.google_cloud_project
  location      = var.region
  name          = var.dataplex_lake_id
  display_name  = "E-commerce Lake"
  description   = "A Dataplex Lake for the e-commerce domain."
  labels        = {
    "goog-terraform-provisioned" = "true"
  }
}

resource "google_dataplex_zone" "analytics_curated_zone" {
  project       = var.google_cloud_project
  location      = var.region
  lake          = google_dataplex_lake.e_commerce_lake.name
  name          = var.dataplex_zone_id
  display_name  = "Analytics Curated Zone"
  description   = "A curated zone for analytics-ready data."
  type          = "CURATED"
  discovery_spec {
    enabled = true
  }
  resource_spec {
    location_type = "SINGLE_REGION"
  }
  labels        = {
    "goog-terraform-provisioned" = "true"
  }
}

resource "google_dataplex_asset" "sales_domain_asset" {
  project       = var.google_cloud_project
  location      = var.region
  lake          = google_dataplex_lake.e_commerce_lake.name
  dataplex_zone = google_dataplex_zone.analytics_curated_zone.name
  name          = "sales-domain"
  display_name  = "Sales Domain Asset"
  description   = "Asset for the sales domain BigQuery dataset."
  labels        = {
    "goog-terraform-provisioned" = "true"
  }
  discovery_spec {
    enabled = true
  }
  resource_spec {
    name = "projects/${var.google_cloud_project}/datasets/sales_domain"
    type = "BIGQUERY_DATASET"
  }
  depends_on = [google_bigquery_table.transactions]
}

resource "google_dataplex_asset" "inventory_domain_asset" {
  project       = var.google_cloud_project
  location      = var.region
  lake          = google_dataplex_lake.e_commerce_lake.name
  dataplex_zone = google_dataplex_zone.analytics_curated_zone.name
  name          = "inventory-domain"
  display_name  = "Inventory Domain Asset"
  description   = "Asset for the inventory domain BigQuery dataset."
  labels        = {
    "goog-terraform-provisioned" = "true"
  }
  discovery_spec {
    enabled = true
  }
  resource_spec {
    name = "projects/${var.google_cloud_project}/datasets/inventory_domain"
    type = "BIGQUERY_DATASET"
  }
  depends_on = [google_bigquery_table.products]
}

resource "google_dataplex_asset" "customer_domain_asset" {
  project       = var.google_cloud_project
  location      = var.region
  lake          = google_dataplex_lake.e_commerce_lake.name
  dataplex_zone = google_dataplex_zone.analytics_curated_zone.name
  name          = "customer-domain"
  display_name  = "Customer Domain Asset"
  description   = "Asset for the customer domain BigQuery dataset."
  labels        = {
    "goog-terraform-provisioned" = "true"
  }
  discovery_spec {
    enabled = true
  }
  resource_spec {
    name = "projects/${var.google_cloud_project}/datasets/customer_domain"
    type = "BIGQUERY_DATASET"
  }
  depends_on = [
    google_bigquery_table.customers,
    google_bigquery_table.feedback
  ]
}
