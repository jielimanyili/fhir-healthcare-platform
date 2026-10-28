# Roadmap

> Ordering over dates; each item links to its ADR(s).

## Now
- Phase 2 deploy — `terraform apply` + `helm install` + push pipeline image (pending a GCP account) — [ADR-0001](adr/0001-stack-and-architecture.md), [ADR-0004](adr/0004-java-event-pipeline.md).

## Next
- Phase 3 — Google API Gateway + OpenAPI lifecycle + rate limiting/versioning + Cloud Build CI/CD — [ADR-0001](adr/0001-stack-and-architecture.md).

## Later
- Phase 3 — Google API Gateway + OpenAPI lifecycle + rate limiting/versioning — [ADR-0001](adr/0001-stack-and-architecture.md).
- Spanner / Firestore store variant; ML-Ops (Vertex AI).
