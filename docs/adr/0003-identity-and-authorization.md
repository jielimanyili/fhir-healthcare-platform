# ADR-0003: Identity and authorization — Keycloak + SMART on FHIR

- **Date:** 2026-10-27
- **Status:** Accepted
- **Related:** [ADR-0001](0001-stack-and-architecture.md) (decision #6), [ADR-0002](0002-healthcare-compliance-and-data.md) (decision #4), `README.md`, `../../ciam-prototype`

## Context

The platform must demonstrate "identity, security, and privacy architectures" (a CVS preferred
qualification) and gate the adjudication workflow (approve/decline claims) by role. In healthcare,
FHIR APIs are conventionally secured with **SMART App Launch** — OAuth 2.0 + OIDC with FHIR-shaped
scopes (`patient/*.read`, `user/*.write`). A fourth `patient` role models patient-portal access
(SMART standalone launch), where a patient reads only their own record — the patient-access-API
pattern required by the 21st Century Cures Act / CMS interoperability rule. We reuse the existing
`ciam-prototype` Keycloak realm and patterns rather than build a new identity stack.

## Decisions

| # | Decision | Alternatives considered | Rationale |
|---|---|---|---|
| 1 | **Keycloak (self-hosted) as the IdP** | Google Identity Platform, Auth0/Okta | Free, runs in Docker/GKE, reuses `ciam-prototype`, and self-hosting demonstrates identity *architecture* rather than consumption of a managed service. |
| 2 | **Authorization Code + PKCE** for the SPA | Implicit flow | PKCE is the current OIDC best practice for SPAs; the `ciam-prototype` UI already implements it. |
| 3 | **SMART on FHIR scope model** | Hand-rolled role checks | SMART scopes are the healthcare standard for FHIR authorization; they make RBAC real and interview-defensible. |
| 4 | **RBAC via Keycloak realm roles → SMART scopes** | Claim-only, per-user ACLs | Realm roles are the clean, portable mapping; scopes are minted on the access token. |
| 5 | **JWT validation (RS256 + JWKS + issuer + audience) in FastAPI middleware** | Validate at the gateway only | Defense in depth: the gateway checks authN, the API checks authZ (scopes) — the same shape as the `ciam-prototype` Spring Security resource server. |
| 6 | **FastAPI as the resource server** (port of `api-identity`) | Keep Spring Boot | The API is already FastAPI (ADR-0001 #2); the validation pattern is portable. |
| 7 | **Resource-level authorization for the `patient` role** (token `patient` claim ↔ requested `subject`) | Allow `patient/*` for any record | A patient must only access their own record; the middleware checks the token's `patient` claim against the requested resource's `subject` — a simplified stand-in for the SMART `patient` launch context. |

## Role → scope mapping

| Realm role | SMART scopes | Capability |
|---|---|---|
| `patient` | `patient/*.read` (own record only) | read their own Patient / Observation / Claim — full PHI |
| `clinician` | `patient/*.read`, `user/Patient.read`, `user/Observation.read`, `user/Claim.read` | read clinical + financial resources |
| `adjudicator` | clinician scopes + `user/Claim.write`, `user/ClaimResponse.write` | approve / decline claims |
| `admin` | `system/*` | audit log + administration (de-identified analytics) |

## Validation flow

1. SPA logs in via **Authorization Code + PKCE** → receives `id_token` + `access_token`.
2. SPA calls the API with `Authorization: Bearer <access_token>` (through Google API Gateway in Phase 3).
3. FastAPI middleware validates the JWT against Keycloak's **JWKS**, checks `iss` + `aud` + expiry.
4. The middleware enforces the required **SMART scope** for the route (e.g., `user/Claim.write` for `POST /fhir/ClaimResponse`).
5. For the `patient` role, the middleware enforces **ownership** — the token's `patient` claim must equal the requested resource's `subject`.
6. Every authorized access is written to the **audit log** (ADR-0002 #3).

## Non-goals (deliberately out of scope)

- SAML 2.0 (B2B SSO) — noted follow-up (as in `ciam-prototype` Phase 2).
- MFA / step-up authentication.
- Full SMART launch context (`launch` / `fhirUser` context parameters) and patient-level consent — the `patient` claim is a simplified stand-in.
- Production key rotation / secret hardening (demo uses documented manual setup).

## Consequences

- The demo reuses a working Keycloak realm and OIDC/PKCE client, reducing setup risk.
- RBAC is expressed in the healthcare-standard SMART scope vocabulary, strengthening the
  "healthcare + identity" interview story.
- A `patient` role demonstrates resource-level (ownership) authorization and the patient-access-API
  requirement (21st Century Cures Act / CMS interoperability).
- The issuer/client remain swappable (Keycloak → Okta/GCIP) because everything is standard OIDC.
- Deferred items (SAML, MFA, consent) are natural follow-ups, not rework.
