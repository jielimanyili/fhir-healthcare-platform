# Roadmap

> Ordering over dates; each item links to its ADR(s).

## Done
- Deploy to GCP — `terraform apply` + Cloud Build image builds + `helm install`; API + Keycloak + pipeline running on GKE, Pub/Sub → BigQuery verified — [ADR-0001](adr/0001-stack-and-architecture.md).

## Now
- Wire the Google API Gateway to the GKE `fhir-api` LoadBalancer URL (Phase 3).

## Later
- Spanner / Firestore store variant; ML-Ops (Vertex AI).
- SAML 2.0 (B2B SSO) — `ciam-prototype` Phase 2.
