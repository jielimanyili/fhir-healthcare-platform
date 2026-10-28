# ADR-0002: Healthcare compliance and data handling

- **Date:** 2026-10-27
- **Status:** Accepted
- **Related:** `README.md`, [ADR-0001](0001-stack-and-architecture.md)

## Context

The platform handles patient-like data, so it must demonstrate the **HIPAA Security Rule** controls
(access control, audit, integrity, authentication, transmission security) and PHI awareness —
without ever touching real patient data.

## Decisions

| # | Decision | Alternatives considered | Rationale |
|---|---|---|---|
| 1 | **Synthetic data only** | Real PHI, public datasets | Real PHI is a non-starter; synthetic data lets us demonstrate the controls honestly. |
| 2 | **PHI de-identification via a toggle + safe-harbor redaction** | Tokenization, full anonymization | A visible redact/restore toggle makes the demo concrete; safe-harbor (18-identifier) removal is the defensible baseline. |
| 3 | **Audit logging on every access (HIPAA 164.312(b))** | Log writes only | Access logging is the key HIPAA control; an audit log view makes it visible. |
| 4 | **RBAC + OIDC via Keycloak (clinician vs admin)** | Static API keys, no auth | OIDC/RBAC demonstrates identity/security/privacy and Person-or-Entity Authentication (164.312(d)). |
| 5 | **Encryption at rest (CMEK) + TLS in transit** | Plaintext | Addressable best practice; shows privacy-by-default. |
| 6 | **Honesty boundary documented** | Claim production compliance | The demo is explicitly not a covered entity and not a compliance program — documented in `docs/ARCHITECTURE.md`. |

## Consequences

- Every access produces an audit record; PHI is redactable on demand.
- The demo communicates healthcare competence without overclaiming HIPAA certification.
- Identity and privacy are first-class (Keycloak realm, RBAC scopes), matching the JD's
  "identity, security, and privacy architectures" preferred qualification.
