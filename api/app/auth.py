"""OIDC/JWT validation + SMART-on-FHIR scope enforcement (ADR-0003).

The API validates RS256 JWTs against Keycloak's JWKS (issuer + signature), maps
realm roles to SMART-on-FHIR scopes, and enforces resource/action access plus
patient-level ownership.

Demo simplifications (documented, not production):
- Scopes are derived from realm roles in the API rather than minted on the token
  (production would mint them via Keycloak client scopes).
- The patient user's record id comes from a username -> patient-id map (production
  would use a `patient` / `fhirUser` claim from a SMART launch context).
- Audience is checked leniently (logged) because Keycloak's default `aud` is
  `account` unless an audience mapper is configured.
"""
import logging
import os
from typing import List, Optional

import jwt
from fastapi import HTTPException, Request
from jwt import PyJWKClient

logger = logging.getLogger("fhir.auth")

ISSUER = os.environ.get("OIDC_ISSUER", "http://localhost:8080/realms/fhir")
AUDIENCE = os.environ.get("OIDC_AUDIENCE", "fhir-api")
# JWKS is fetched on the Docker-internal hostname; the issuer in the token is the
# external hostname (localhost when the demo runs from the host).
JWKS_URL = os.environ.get(
    "OIDC_JWKS_URL",
    "http://keycloak:8080/realms/fhir/protocol/openid-connect/certs",
)

# Role -> SMART scopes (ADR-0003 role/scope table).
ROLE_SCOPES = {
    "patient": {"patient/Patient.read", "patient/Observation.read", "patient/Claim.read"},
    "clinician": {"patient/*.read", "user/Patient.read", "user/Observation.read", "user/Claim.read"},
    "adjudicator": {
        "patient/*.read", "user/Patient.read", "user/Observation.read", "user/Claim.read",
        "user/Claim.write", "user/ClaimResponse.write",
    },
    "admin": {"system/*.read", "system/*.write"},
}

# Demo: username -> Patient resource id.
PATIENT_IDS = {"patient1": "p-001"}

_jwks: Optional[PyJWKClient] = None


def _jwks_client() -> PyJWKClient:
    global _jwks
    if _jwks is None:
        _jwks = PyJWKClient(JWKS_URL)
    return _jwks


def decode_token(token: str) -> dict:
    key = _jwks_client().get_signing_key_from_jwt(token)
    claims = jwt.decode(
        token,
        key.key,
        algorithms=["RS256"],
        issuer=ISSUER,
        options={"verify_aud": False},
    )
    aud = claims.get("aud")
    azp = claims.get("azp")
    if AUDIENCE not in (aud if isinstance(aud, list) else [aud]) and azp != AUDIENCE:
        logger.warning("token audience/azp does not include %r", AUDIENCE)
    return claims


# Demo fallback: username -> realm role. The realm JSON configures real Keycloak
# realm roles (and a realm-roles mapper on fhir-api), but realm import does not
# reliably emit `realm_access.roles` in the password-grant token; this map covers
# that case. Production would rely on the token's `realm_access.roles` / SMART scopes.
USER_ROLES = {
    "patient1": ["patient"],
    "clinician1": ["clinician"],
    "adjudicator1": ["adjudicator"],
    "admin1": ["admin"],
}


def roles(claims: dict) -> List[str]:
    realm_roles = claims.get("realm_access", {}).get("roles") or []
    if realm_roles:
        return realm_roles
    return USER_ROLES.get(claims.get("preferred_username"), [])


def scopes(claims: dict) -> List[str]:
    out: List[str] = []
    for role in roles(claims):
        out.extend(ROLE_SCOPES.get(role, []))
    return out


def _granted(claims: dict, resource: str, action: str) -> bool:
    for scope in scopes(claims):
        if "/" not in scope or "." not in scope:
            continue
        _ctx, rest = scope.split("/", 1)
        res, act = rest.split(".", 1)
        if act == action and res in (resource, "*"):
            return True
    return False


def can_read(claims: dict, resource: str) -> bool:
    return _granted(claims, resource, "read")


def can_write(claims: dict, resource: str) -> bool:
    return _granted(claims, resource, "write")


def is_patient_only(claims: dict) -> bool:
    r = roles(claims)
    return "patient" in r and not any(x in r for x in ("clinician", "adjudicator", "admin"))


def patient_id(claims: dict) -> Optional[str]:
    return PATIENT_IDS.get(claims.get("preferred_username"))


def belongs_to(resource: dict, pid: Optional[str]) -> bool:
    """True if the resource is the given patient's own record."""
    if not pid:
        return False
    if resource.get("resourceType") == "Patient":
        return resource.get("id") == pid
    ref = resource.get("subject") or resource.get("patient")
    return isinstance(ref, dict) and ref.get("reference") == f"Patient/{pid}"


def get_current_user(request: Request) -> dict:
    header = request.headers.get("Authorization", "")
    if not header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing bearer token")
    try:
        claims = decode_token(header[7:])
    except jwt.PyJWTError as exc:
        raise HTTPException(status_code=401, detail=f"Invalid token: {exc}")
    request.state.user = claims.get("preferred_username") or claims.get("sub")
    return claims
