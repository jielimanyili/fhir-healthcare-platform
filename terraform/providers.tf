# Provider configuration — authenticates via Application Default Credentials
# (`gcloud auth application-default login`). No static keys.
provider "google" {
  project = var.project_id
  region  = var.region
}

provider "google-beta" {
  project = var.project_id
  region  = var.region
}
