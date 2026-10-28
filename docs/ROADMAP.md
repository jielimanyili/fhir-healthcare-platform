# Roadmap

> Ordering over dates; each item links to its ADR(s).

## Now
- Phase 1 — Postgres JSONB persistence + PHI de-identification + audit logging + RBAC/OIDC — [ADR-0002](adr/0002-healthcare-compliance-and-data.md), [ADR-0003](adr/0003-identity-and-authorization.md).

## Next
- Phase 2 — GCP: Terraform (VPC/firewall/GKE) + Helm + Java Spring Boot pipeline (Pub/Sub → BigQuery) — [ADR-0001](adr/0001-stack-and-architecture.md), [ADR-0004](adr/0004-java-event-pipeline.md).

## Later
- Phase 3 — Google API Gateway + OpenAPI lifecycle + rate limiting/versioning — [ADR-0001](adr/0001-stack-and-architecture.md).
- Spanner / Firestore store variant; ML-Ops (Vertex AI).
