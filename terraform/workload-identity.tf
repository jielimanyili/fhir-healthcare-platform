# ---- Workload Identity -----------------------------------------------------
# Let GKE Kubernetes service accounts act as the GCP service accounts
# (no static keys). Autopilot has Workload Identity enabled by default.

# API: bind GKE `fhir-api` KSA -> GCP `fhir-api` SA (Cloud SQL client).
resource "google_service_account_iam_member" "api_wi" {
  service_account_id = google_service_account.api_sa.name
  role               = "roles/iam.workloadIdentityUser"
  member             = "serviceAccount:${var.project_id}.svc.id.goog[default/fhir-api]"

  # The identity pool PROJECT.svc.id.goog is created by the GKE cluster.
  depends_on = [google_container_cluster.autopilot]
}

resource "google_project_iam_member" "api_cloudsql" {
  project = var.project_id
  role    = "roles/cloudsql.client"
  member  = "serviceAccount:${google_service_account.api_sa.email}"
}

# Pipeline: bind GKE `fhir-pipeline` KSA -> GCP `fhir-pipeline` SA.
resource "google_service_account_iam_member" "pipeline_wi" {
  service_account_id = google_service_account.pipeline_sa.name
  role               = "roles/iam.workloadIdentityUser"
  member             = "serviceAccount:${var.project_id}.svc.id.goog[default/fhir-pipeline]"

  depends_on = [google_container_cluster.autopilot]
}
