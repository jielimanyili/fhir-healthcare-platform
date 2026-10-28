# Architecture — FHIR Healthcare Analytics Platform

> C4-lite view of the FHIR Healthcare Analytics Platform demo. Decisions ("why") live in
> [`docs/adr/`](adr/).

## 1. System Context (C4 Level 1)

```mermaid
flowchart LR
  U[Clinician / admin user] -->|HTTPS| S[FHIR Healthcare Analytics Platform]
  S -->|synthetic resources| DB[(Cloud SQL Postgres)]
  S -->|events| B[(BigQuery)]
```

A single self-contained system: a FHIR API + Angular UI that ingest synthetic patient/claim/
observation data, apply PHI de-identification, log audit events, and aggregate analytics in BigQuery.

## 2. Containers (C4 Level 2)

```mermaid
flowchart TB
  U[User's browser] -->|SPA| A[Angular UI]
  U -->|OIDC| K[Keycloak]
  A -->|/fhir/*| G[Google API Gateway]
  G -->|validate OIDC| K
  G -->|forward| F[FastAPI FHIR API]
  F -->|resources| P[(Cloud SQL Postgres - FHIR JSONB)]
  F -->|events| M[Pub/Sub]
  M --> J[Java Spring Boot pipeline] --> B[(BigQuery)]
  F -->|audit| L[Cloud Logging audit trail]
```

| Container | Technology | Responsibility |
|---|---|---|
| Angular UI | Angular 22 (standalone) | SPA: search/display FHIR resources, de-identification toggle, audit viewer |
| API Gateway | Google API Gateway (OpenAPI) | Routing, OIDC auth, rate limiting, versioning (API-first lifecycle) |
| FHIR API | Python FastAPI + Pydantic | FHIR R4 resources (Patient, Claim, Observation), validation, PHI de-identification, audit events |
| Keycloak | Keycloak | OIDC/OAuth2 IdP; RBAC (clinician vs admin scopes) |
| Postgres | Cloud SQL (PostgreSQL, JSONB) | System of record for FHIR resources |
| Pub/Sub | Google Pub/Sub | Event stream (resource created/updated) |
| Event pipeline | Java 21 + Spring Boot | Consumes Pub/Sub events, writes BigQuery aggregations |
| BigQuery | Google BigQuery | Analytical store + SQL aggregations |
| Orchestration | GKE Autopilot (Helm) + Terraform | Runs API/UI; IaC for VPC, firewall, cluster, datasets |

## 3. Request flow

```mermaid
sequenceDiagram
  actor U as User
  participant UI as Angular UI
  participant G as API Gateway
  participant K as Keycloak
  participant F as FastAPI FHIR API
  participant P as Cloud SQL Postgres
  participant M as Pub/Sub
  participant J as Java pipeline
  participant B as BigQuery

  U->>UI: search patients
  UI->>G: GET /fhir/Patient?family=...
  G->>K: validate OIDC token
  G->>F: forward (scopes)
  F->>P: query FHIR JSONB
  P-->>F: rows
  F->>F: de-identify if flag set
  F-->>G: FHIR Bundle
  G-->>UI: 200 JSON
  F->>M: publish Patient.updated
  M->>J: consume event
  J->>B: write aggregation
```

## 4. Components (C4 Level 3)

The two application containers decompose into these components.

### 4.1 API container — FastAPI

```mermaid
flowchart TB
  subgraph API["FastAPI FHIR API (Python)"]
    direction TB
    AUTH["Auth middleware (JWT + SMART scopes)"]
    AUDIT["Audit middleware"]
    ROUTERS["FHIR routers: Patient / Observation / Claim / ClaimResponse"]
    SVC["Domain services (adjudication, analytics)"]
    DEID["De-identification service"]
    REPO["FHIR repository (Postgres JSONB)"]
    PUB["Pub/Sub publisher"]
  end
  GW[API Gateway] --> AUTH --> AUDIT --> ROUTERS --> SVC
  SVC --> DEID
  SVC --> REPO --> P[(Cloud SQL Postgres)]
  SVC --> PUB --> M[Pub/Sub]
```

### 4.2 UI container — Angular

```mermaid
flowchart TB
  subgraph UI["Angular 22 SPA"]
    direction TB
    AUTH["Auth service (OIDC + PKCE)"]
    GUARD["Auth + role guards"]
    VIEWS["Patient / Observation / Claim / Audit views"]
    CLIENT["FHIR API client (HttpClient)"]
  end
  AUTH --> GUARD --> VIEWS --> CLIENT --> GW[API Gateway]
```

### 4.3 Repository mapping

| Component | Repo folder |
|---|---|
| FHIR routers, domain services, middleware, repository, Pydantic models | `api/` |
| Views, guards, auth service, FHIR client | `ui/` |
| VPC, firewall, GKE Autopilot, BigQuery, Pub/Sub (Terraform) | `terraform/` |
| Java event pipeline (Pub/Sub consumer → BigQuery) | `pipeline/` |
| GKE deployment chart | `helm/` |
| Keycloak realm + API gateway (OpenAPI) config | `infra/` |

## 5. Data model

FHIR resources are stored as JSONB in Postgres (one table per resource type), with a `deidentified`
flag. All rows are synthetic.

| resource_type | id | payload (JSONB) | deidentified |
|---|---|---|---|
| Patient | p-001 | `{ name, birthDate, ... }` | false |
| Claim | c-001 | `{ patient.reference, total, ... }` | false |
| Observation | o-001 | `{ code, valueQuantity, ... }` | false |

BigQuery mirrors an analytics-friendly (denormalized) shape for aggregation.

## 6. Key decisions

Point to `docs/adr/`:
- [ADR-0001](adr/0001-stack-and-architecture.md) — stack + architecture.
- [ADR-0002](adr/0002-healthcare-compliance-and-data.md) — FHIR subset, synthetic data, PHI handling, RBAC.
- [ADR-0003](adr/0003-identity-and-authorization.md) — Keycloak IdP + SMART on FHIR scopes + JWT validation.
- [ADR-0004](adr/0004-java-event-pipeline.md) — Java Spring Boot pipeline (Pub/Sub → BigQuery).

## 7. Honesty boundary

- **Demo, not production** — no real PHI, not a HIPAA covered entity, not a substitute for a compliance program.
- FHIR subset only (Patient / Claim / Observation), not full R4 conformance.
- GKE Autopilot (managed), not multi-node production operations.

## 8. Future work

- Full FHIR search + pagination (`_include`, `_count`).
- Spanner or Firestore as an alternative store.
- ML-Ops (Vertex AI) for readmission/claim models.
- Workload Identity + Terraform Cloud hardening.
