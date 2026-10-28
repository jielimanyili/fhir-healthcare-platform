variable "project_id" {
  description = "GCP project id"
  type        = string
}

variable "region" {
  description = "GCP region"
  type        = string
  default     = "us-central1"
}

variable "cluster_name" {
  description = "GKE Autopilot cluster name"
  type        = string
  default     = "fhir-gke"
}

variable "dataset_id" {
  description = "BigQuery dataset id"
  type        = string
  default     = "fhir_analytics"
}
