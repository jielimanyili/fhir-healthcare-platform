# FHIR Healthcare Analytics Platform — GCP infrastructure (Phase 2).
# VPC/firewall -> GKE Autopilot -> BigQuery + Pub/Sub + Artifact Registry + IAM.

# ---- networking -----------------------------------------------------------
resource "google_compute_network" "vpc" {
  name                    = "fhir-vpc"
  auto_create_subnetworks = false
}

resource "google_compute_subnetwork" "subnet" {
  name          = "fhir-subnet"
  network       = google_compute_network.vpc.id
  region        = var.region
  ip_cidr_range = "10.0.0.0/16"
}

resource "google_compute_firewall" "allow_ingress" {
  name    = "fhir-allow-ingress"
  network = google_compute_network.vpc.name

  allow {
    protocol = "tcp"
    ports    = ["80", "443"]
  }

  source_ranges = ["0.0.0.0/0"]
}

# ---- GKE Autopilot --------------------------------------------------------
resource "google_container_cluster" "autopilot" {
  name               = var.cluster_name
  location           = var.region
  enable_autopilot   = true
  network            = google_compute_network.vpc.id
  subnetwork         = google_compute_subnetwork.subnet.id
  deletion_protection = false

  ip_allocation_policy {}
}

# ---- BigQuery -------------------------------------------------------------
resource "google_bigquery_dataset" "analytics" {
  dataset_id = var.dataset_id
  location   = var.region
}

resource "google_bigquery_table" "claims" {
  dataset_id = google_bigquery_dataset.analytics.dataset_id
  table_id   = "claims"
  schema = jsonencode([
    { name = "id", type = "STRING" },
    { name = "status", type = "STRING" },
    { name = "patient", type = "STRING" },
    { name = "total", type = "FLOAT" },
  ])
}

resource "google_bigquery_table" "observations" {
  dataset_id = google_bigquery_dataset.analytics.dataset_id
  table_id   = "observations"
  schema = jsonencode([
    { name = "id", type = "STRING" },
    { name = "status", type = "STRING" },
    { name = "subject", type = "STRING" },
    { name = "code", type = "STRING" },
    { name = "value", type = "FLOAT" },
  ])
}

# ---- Pub/Sub --------------------------------------------------------------
resource "google_pubsub_topic" "events" {
  name = "fhir-resource-events"
}

resource "google_pubsub_subscription" "events_sub" {
  name  = "fhir-resource-events-sub"
  topic = google_pubsub_topic.events.name
}

# ---- Artifact Registry ----------------------------------------------------
resource "google_artifact_registry_repository" "repo" {
  location      = var.region
  repository_id = "fhir"
  format        = "DOCKER"
}

# ---- Service accounts + IAM ----------------------------------------------
resource "google_service_account" "pipeline_sa" {
  account_id   = "fhir-pipeline"
  display_name = "FHIR Pipeline (Pub/Sub -> BigQuery)"
}

resource "google_project_iam_member" "pipeline_bigquery" {
  project = var.project_id
  role    = "roles/bigquery.dataEditor"
  member  = "serviceAccount:${google_service_account.pipeline_sa.email}"
}

resource "google_project_iam_member" "pipeline_pubsub" {
  project = var.project_id
  role    = "roles/pubsub.subscriber"
  member  = "serviceAccount:${google_service_account.pipeline_sa.email}"
}

resource "google_service_account" "api_sa" {
  account_id   = "fhir-api"
  display_name = "FHIR API (FastAPI)"
}

resource "google_project_iam_member" "api_pubsub" {
  project = var.project_id
  role    = "roles/pubsub.publisher"
  member  = "serviceAccount:${google_service_account.api_sa.email}"
}

# ---- Cloud SQL (Postgres) ------------------------------------------------
resource "google_sql_database_instance" "postgres" {
  name                = "fhir-postgres"
  database_version    = "POSTGRES_16"
  region              = var.region
  deletion_protection = false

  settings {
    tier = "db-f1-micro"
  }
}

resource "google_sql_database" "fhir" {
  name     = "fhir"
  instance = google_sql_database_instance.postgres.name
}

resource "google_sql_user" "fhir" {
  name     = "fhir"
  instance = google_sql_database_instance.postgres.name
  password = "fhir-demo-password" # demo only — use Secret Manager in production
}
