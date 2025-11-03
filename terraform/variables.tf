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

variable "dataplex_admin_user" {
  type        = string
  description = "The user to grant Dataplex Catalog Editor role."
}

variable "project_id" {
  type        = string
  description = "The project ID to deploy to."
}


variable "region" {
  type        = string
  description = "The region to deploy to."
  default     = "us-central1"
}

variable "google_cloud_project" {
  type        = string
  description = "The Google Cloud project ID."
}

variable "dataplex_lake_id" {
  description = "The ID of the Dataplex Lake."
  type        = string
  default     = "e-commerce-lake"
}

variable "dataplex_zone_id" {
  description = "The ID of the Dataplex Zone."
  type        = string
  default     = "analytics-curated-zone"
}
