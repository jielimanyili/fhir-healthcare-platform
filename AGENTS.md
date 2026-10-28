# AGENTS.md

> Instructions for AI coding agents working in this repo.

## Project
FHIR Healthcare Analytics Platform — a HIPAA-aware FHIR (HL7 R4) REST API + Angular UI on GCP (GKE, BigQuery, Pub/Sub). Demo, not production — the point is healthcare interoperability (FHIR), privacy/compliance (PHI de-identification, audit logging, RBAC/OIDC), Python backend (FastAPI), and cloud-native delivery (Terraform/Helm/GKE). Structure: `api/` (FastAPI), `ui/` (Angular 22), `terraform/`, `helm/`, `infra/`.

## Commands
- api install: `cd api && pip install -r requirements.txt`
- api dev:    `cd api && uvicorn app.main:app --reload`   # http://localhost:8000
- api test:   `cd api && pytest`
- ui install: `cd ui && npm install`
- ui dev:     `cd ui && npm start`                        # http://localhost:4200
- full stack: `docker compose up --build`

## Conventions
- FHIR resources are the contract — `api/` owns the FHIR R4 subset (Patient, Claim, Observation); `ui/` consumes it, never reimplements it.
- All patient data is **synthetic**; never introduce real PHI.
- Python is type-hinted (Pydantic models mirror the FHIR shapes); Angular uses standalone components + signals.
- Style guide: `docs/style-guide.md`. (No lint step configured yet.)

## Boundaries (non-negotiable)
- Never read or write `.env` or any secret; use Secret Manager references.
- Don't add dependencies without asking.
- Don't change architecture — propose an ADR first (`docs/adr/`).
- Run tests + build before finishing.

## Review gates
Every change must pass: architecture fit · correctness · security (PHI handling) · test coverage · readability. See `docs/ai-assisted-development.md`.
