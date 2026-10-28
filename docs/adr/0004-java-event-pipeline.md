# ADR-0004: Java Spring Boot event pipeline (Pub/Sub → BigQuery)

- **Date:** 2026-10-28
- **Status:** Accepted
- **Related:** [ADR-0001](0001-stack-and-architecture.md) (decisions #2, #4), `README.md`, `../../cop-data-platform-demo`

## Context

Phase 0 delivered a Python (FastAPI) FHIR API + Angular UI — no Java. But the CVS JD is
"Java/Angular" and requires backend Java and large-scale distributed systems. To make the demo
polyglot and demonstrate Java on GCP, we need a Java component. The natural place is the event
pipeline (Pub/Sub → BigQuery), which is the GCP analog of the already-built COP Data Platform
(Java 17 + Spring Boot Kafka Streams).

## Decisions

| # | Decision | Alternatives considered | Rationale |
|---|---|---|---|
| 1 | **Java 21 + Spring Boot** for the Pub/Sub → BigQuery pipeline | Python (keep single-language), Apache Beam/Dataflow | Reuses COP Data Platform (Java + Spring Boot Kafka Streams) experience; Spring Boot + GCP Pub/Sub starter is the lowest-risk path; Beam/Dataflow is a new framework with no prior exposure. |
| 2 | **Consume Pub/Sub events, write BigQuery aggregations** (claims by month, observations by code) | Batch SQL only | Streaming ingestion demonstrates the JD's "large-scale distributed systems" + "real-time transactions." |
| 3 | **Deploy on GKE via Helm** (same cluster as the API) | Cloud Run | Single deploy surface, matches the "GKE" keyword, reuses `helm/` chart patterns. |

## Consequences

- The demo becomes polyglot: Angular (TypeScript) → Python (FastAPI) → Java (Spring Boot), matching
  the JD's "microservices / API-first / polyglot full-stack" positioning.
- The Java component reuses COP Data Platform patterns (Spring Boot, event-driven, gRPC/REST),
  so it is defensible in interview.
- Adds a `pipeline/` module in Phase 2 (not Phase 0); no impact on the already-shipped Phase 0.
