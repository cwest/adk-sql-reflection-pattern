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

resource "null_resource" "generate_csv_data" {
  provisioner "local-exec" {
    command = "uv run poe datagen"
  }
}

resource "google_bigquery_dataset" "sales_domain" {
  project    = var.google_cloud_project
  dataset_id = "sales_domain"
  location   = var.region
  labels     = {
    "goog-terraform-provisioned" = "true"
  }
}

resource "google_bigquery_dataset" "inventory_domain" {
  project    = var.google_cloud_project
  dataset_id = "inventory_domain"
  location   = var.region
  labels     = {
    "goog-terraform-provisioned" = "true"
  }
}

resource "google_bigquery_dataset" "customer_domain" {
  project    = var.google_cloud_project
  dataset_id = "customer_domain"
  location   = var.region
  labels     = {
    "goog-terraform-provisioned" = "true"
  }
}

resource "google_bigquery_table" "transactions" {
  project               = var.google_cloud_project
  dataset_id            = google_bigquery_dataset.sales_domain.dataset_id
  table_id              = "transactions"
  deletion_protection = false
  labels                = {
    "goog-terraform-provisioned" = "true"
  }

  depends_on = [null_resource.generate_csv_data]

  provisioner "local-exec" {
    command = "bq load --autodetect --skip_leading_rows=1 ${google_bigquery_dataset.sales_domain.dataset_id}.${self.table_id} ../data/transactions.csv"
  }
}

resource "google_bigquery_table" "products" {
  project               = var.google_cloud_project
  dataset_id            = google_bigquery_dataset.inventory_domain.dataset_id
  table_id              = "products"
  deletion_protection = false
  labels                = {
    "goog-terraform-provisioned" = "true"
  }

  depends_on = [null_resource.generate_csv_data]

  provisioner "local-exec" {
    command = "bq load --autodetect --skip_leading_rows=1 ${google_bigquery_dataset.inventory_domain.dataset_id}.${self.table_id} ../data/products.csv"
  }
}

resource "google_bigquery_table" "customers" {
  project               = var.google_cloud_project
  dataset_id            = google_bigquery_dataset.customer_domain.dataset_id
  table_id              = "customers"
  deletion_protection = false
  labels                = {
    "goog-terraform-provisioned" = "true"
  }

  depends_on = [null_resource.generate_csv_data]

  provisioner "local-exec" {
    command = "bq load --autodetect --skip_leading_rows=1 ${google_bigquery_dataset.customer_domain.dataset_id}.${self.table_id} ../data/customers.csv"
  }
}

resource "google_bigquery_table" "feedback" {
  project               = var.google_cloud_project
  dataset_id            = google_bigquery_dataset.customer_domain.dataset_id
  table_id              = "feedback"
  deletion_protection = false
  labels                = {
    "goog-terraform-provisioned" = "true"
  }

  depends_on = [null_resource.generate_csv_data]

  provisioner "local-exec" {
    command = "bq load --autodetect --skip_leading_rows=1 ${google_bigquery_dataset.customer_domain.dataset_id}.${self.table_id} ../data/feedback.csv"
  }
}