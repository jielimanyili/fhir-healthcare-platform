# Roadmap

> Ordering over dates; each item links to its ADR(s).

## Now
- Phase 0 — local `docker compose`: FastAPI FHIR API + Postgres + Keycloak + Angular UI — [ADR-0003](adr/0003-identity-and-authorization.md).

## Next
- Phase 1 — FHIR R4 subset + PHI de-identification + audit logging + RBAC/OIDC — [ADR-0002](adr/0002-healthcare-compliance-and-data.md), [ADR-0003](adr/0003-identity-and-authorization.md).
- Phase 2 — GCP: Terraform (VPC/firewall/GKE) + Helm + Pub/Sub → BigQuery — [ADR-0001](adr/0001-stack-and-architecture.md).

## Later
- Phase 3 — Google API Gateway + OpenAPI lifecycle + rate limiting/versioning — [ADR-0001](adr/0001-stack-and-architecture.md).
- Spanner / Firestore store variant; ML-Ops (Vertex AI).
