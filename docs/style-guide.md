# Style Guide

> Prose conventions that linters/formatters don't cover. Enforced rules live in the linter/formatter config; this doc is for the rest.

## Python (FastAPI)
- Type-hint all functions; Pydantic models mirror the FHIR shapes.
- Endpoints return FHIR-compliant JSON (`resourceType`, `id`).

## Angular
- Standalone components + signals; no `any` types at the API boundary.

## FHIR
- Use HL7 FHIR R4 terminology; resources are `camelCase` JSON per the spec.
- Resource types are PascalCase (Patient, Claim, Observation); file names kebab-case.
- All patient data is synthetic — no real PHI.

## Naming
- Folders: `api/`, `ui/`, `terraform/`, `helm/`, `infra/`.
- Branches: `feature/<slug>`, `fix/<slug>`.

## Patterns & idioms
- Domain logic in services; routers stay thin.
- Audit and de-identification are cross-cutting middleware, not per-endpoint code.

## Links
- Linter config: TBD (not yet configured).
- Formatter config: TBD (not yet configured).
