# Google API Gateway (Phase 3) — OpenAPI-driven, OIDC-validated edge.
resource "google_api_gateway_api" "fhir_api" {
  provider = google-beta
  api_id   = "fhir-api"
}

resource "google_api_gateway_api_config" "fhir_config" {
  provider      = google-beta
  api           = google_api_gateway_api.fhir_api.api_id
  api_config_id = "v1"

  openapi_documents {
    document {
      path     = "openapi.yaml"
      contents = filebase64("${path.module}/../infra/gateway/openapi.yaml")
    }
  }

  lifecycle {
    create_before_destroy = true
  }
}

resource "google_api_gateway_gateway" "fhir_gateway" {
  provider    = google-beta
  api         = google_api_gateway_api.fhir_api.api_id
  gateway_id  = "fhir-gateway"
  api_config  = google_api_gateway_api_config.fhir_config.api_config_id
  region      = var.region
}
