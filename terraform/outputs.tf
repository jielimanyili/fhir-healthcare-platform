output "cluster_name" {
  value = google_container_cluster.autopilot.name
}

output "bigquery_dataset" {
  value = google_bigquery_dataset.analytics.dataset_id
}

output "pubsub_topic" {
  value = google_pubsub_topic.events.name
}

output "artifact_registry" {
  value = google_artifact_registry_repository.repo.id
}

output "pipeline_service_account" {
  value = google_service_account.pipeline_sa.email
}

output "cloud_sql_connection_name" {
  value = google_sql_database_instance.postgres.connection_name
}
