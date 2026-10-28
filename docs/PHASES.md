# Phases

| Phase | Goal | Deliverables | Depends on | Status |
|---|---|---|---|---|
| 0 | Local FHIR API + Angular UI + Docker (in-memory store) | `api/`, `ui/`, `docker-compose.yml` | — | ✅ |
| 1 | Postgres JSONB + compliance (de-identification, audit, RBAC/OIDC) | Postgres repo ✅ · de-identification ✅ · audit ✅ · Keycloak realm ⬜ | Phase 0 | 🟡 |
| 2 | GCP: GKE + BigQuery + Pub/Sub + Java pipeline via Terraform/Helm | `terraform/`, `helm/`, `pipeline/`, BigQuery SQL | Phase 1 | ⬜ |
| 3 | API-first lifecycle (gateway + CI/CD) | `infra/` gateway config, Cloud Build | Phase 2 | ⬜ |

Status legend: ⬜ planned · 🟡 in progress · ✅ done
