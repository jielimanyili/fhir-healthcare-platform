# Phases

| Phase | Goal | Deliverables | Depends on | Status |
|---|---|---|---|---|
| 0 | Local FHIR API + Angular UI + Docker | `api/`, `ui/`, `docker-compose.yml` | — | ⬜ |
| 1 | FHIR R4 + compliance (de-identification, audit, RBAC/OIDC) | FHIR resources, audit middleware, Keycloak realm | Phase 0 | ⬜ |
| 2 | GCP: GKE + BigQuery + Pub/Sub via Terraform/Helm | `terraform/`, `helm/`, BigQuery SQL | Phase 1 | ⬜ |
| 3 | API-first lifecycle (gateway + CI/CD) | `infra/` gateway config, Cloud Build | Phase 2 | ⬜ |

Status legend: ⬜ planned · 🟡 in progress · ✅ done
