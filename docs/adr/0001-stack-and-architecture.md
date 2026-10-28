# ADR-0001: Stack and architecture for the FHIR Healthcare Analytics Platform

- **Date:** 2026-10-27
- **Status:** Accepted
- **Related:** `README.md`, [ADR-0002](0002-healthcare-compliance-and-data.md)

## Context

This is a **demonstration project** (not production software) that exercises healthcare
interoperability, privacy/compliance, and cloud-native patterns in the stack used by CVS Health's
digital teams. Its purpose is to close four interview gaps — GCP/GKE/Google DBs, Python backend,
healthcare/FHIR/HIPAA, and API-first lifecycle — with verifiable, running code.

## Decisions

| # | Decision | Alternatives considered | Rationale |
|---|---|---|---|
| 1 | **HL7 FHIR R4 as the API standard** | Custom REST, GraphQL | FHIR is the healthcare interoperability standard; R4 is the most widely adopted version and instantly signals domain competence. |
| 2 | **Python 3.12 + FastAPI** | Node/Express, Java/Spring | FastAPI closes the "Python backend" gap with typed (Pydantic) models, auto OpenAPI, and async; Java/Spring is already covered elsewhere. |
| 3 | **Angular 22 SPA** | React | Angular is the JD's target frontend; standalone components + signals match current Angular. |
| 4 | **GCP: GKE Autopilot + BigQuery + Pub/Sub** | AWS (already have), Azure | Closes the "GCP/GKE/Google DBs" gap; GKE Autopilot keeps the cluster manageable for a demo. |
| 5 | **Cloud SQL Postgres (JSONB) for FHIR resources** | Firestore, Spanner | JSONB stores FHIR resources as-is; relational fits the "enterprise DB" story; Spanner is a noted follow-up. |
| 6 | **Keycloak for OIDC/RBAC** | Auth0, hand-rolled JWT | Reuses the existing `ciam-prototype`; demonstrates identity/security/privacy (a JD preferred qual). |
| 7 | **Single monorepo (api / ui / terraform / helm / infra)** | Separate repos, Nx | One repo makes the demo easy to clone and review, same as the retirement-planner precedent. |

## Domain assumptions

- The FHIR subset is **Patient, Claim, Observation** (R4) — enough to demonstrate CRUD, search,
  references, and de-identification without full R4 conformance.
- Analytics aggregations (e.g., claims by month, observations by code) run in BigQuery via Pub/Sub.
- Pub/Sub is a **supporting** component, not a JD requirement — the JD names no event engine; it serves the "analytical applications" + "large-scale distributed systems" themes and reuses existing Kafka/Kafka Streams depth.

## Non-goals (deliberately out of scope)

- Full FHIR R4 conformance / terminology servers (SNOMED, LOINC)
- Real PHI or HIPAA covered-entity operations
- Spanner / Firestore (noted follow-ups)
- ML-Ops / Vertex AI models

## Consequences

- The demo runs locally with `docker compose up` and deploys to GKE with Terraform + Helm.
- The FHIR API is client-agnostic (standard JSON), so the same contract serves the Angular SPA and
  any FHIR-capable client — supporting the healthcare-interoperability story.
- Deferred items (Spanner, ML-Ops) are natural follow-ups, not rework.
