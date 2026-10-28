"""FHIR R4 routers + CapabilityStatement (Phase 0/1 subset).

Each resource exposes standard FHIR interactions: create, read, update, delete,
search-type. Search returns a `Bundle` of type `searchset`. Reads support an
optional `deidentified=true` query parameter for safe-harbor PHI redaction.

When `require_auth` is enabled (Phase 1b), FHIR endpoints require an OIDC bearer
token with the appropriate SMART-on-FHIR scope; the `patient` role is further
restricted to its own record.
"""
from typing import Optional, Type
from uuid import uuid4

from fastapi import APIRouter, Body, HTTPException, Request
from pydantic import BaseModel

from .auth import belongs_to, can_read, can_write, get_current_user, is_patient_only, patient_id
from .deidentification import deidentify
from .models import Claim, ClaimResponse, Observation, Patient

_INTERACTIONS = [{"code": c} for c in ("read", "create", "update", "delete", "search-type")]


def _bundle(resources) -> dict:
    return {
        "resourceType": "Bundle",
        "type": "searchset",
        "total": len(resources),
        "entry": [{"resource": r} for r in resources],
    }


def _resource_router(repo, resource_type: str, model: Type[BaseModel], require_auth: bool = False):
    router = APIRouter(prefix=f"/fhir/{resource_type}", tags=[resource_type])

    def _authorize(request: Request, action: str):
        if not require_auth:
            return None
        claims = get_current_user(request)
        allowed = can_read(claims, resource_type) if action == "read" else can_write(claims, resource_type)
        if not allowed:
            raise HTTPException(status_code=403, detail="Insufficient scope")
        return claims

    @router.post("", status_code=201)
    def create(payload: model = Body(...), request: Request = None):
        _authorize(request, "write")
        data = payload.model_dump()
        data["resourceType"] = resource_type
        data["id"] = data.get("id") or uuid4().hex
        return repo.create(resource_type, data["id"], data)

    @router.get("")
    def search(
        family: Optional[str] = None,
        patient: Optional[str] = None,
        subject: Optional[str] = None,
        request: Optional[str] = None,
        status: Optional[str] = None,
        deidentified: bool = False,
        req: Request = None,
    ):
        claims = _authorize(req, "read")
        results = repo.search(
            resource_type,
            family=family,
            patient=patient,
            subject=subject,
            request=request,
            status=status,
        )
        if claims is not None and is_patient_only(claims):
            results = [r for r in results if belongs_to(r, patient_id(claims))]
        if deidentified:
            results = [deidentify(r) for r in results]
        return _bundle(results)

    @router.get("/{rid}")
    def read(rid: str, deidentified: bool = False, request: Request = None):
        claims = _authorize(request, "read")
        resource = repo.get(resource_type, rid)
        if resource is None:
            raise HTTPException(status_code=404, detail="resource not found")
        if claims is not None and is_patient_only(claims) and not belongs_to(resource, patient_id(claims)):
            raise HTTPException(status_code=403, detail="Not authorized for this patient")
        return deidentify(resource) if deidentified else resource

    @router.put("/{rid}")
    def update(rid: str, payload: model = Body(...), request: Request = None):
        _authorize(request, "write")
        if repo.get(resource_type, rid) is None:
            raise HTTPException(status_code=404, detail="resource not found")
        data = payload.model_dump()
        data["resourceType"] = resource_type
        data["id"] = rid
        return repo.update(resource_type, rid, data)

    @router.delete("/{rid}", status_code=204)
    def delete(rid: str, request: Request = None):
        _authorize(request, "write")
        if not repo.delete(resource_type, rid):
            raise HTTPException(status_code=404, detail="resource not found")

    return router


def build_routers(repo, require_auth: bool = False):
    return [
        _resource_router(repo, "Patient", Patient, require_auth),
        _resource_router(repo, "Observation", Observation, require_auth),
        _resource_router(repo, "Claim", Claim, require_auth),
        _resource_router(repo, "ClaimResponse", ClaimResponse, require_auth),
    ]


metadata_router = APIRouter(tags=["metadata"])


@metadata_router.get("/fhir/metadata")
def metadata():
    return {
        "resourceType": "CapabilityStatement",
        "status": "active",
        "date": "2026-10-28",
        "kind": "instance",
        "fhirVersion": "4.0.1",
        "format": ["json"],
        "rest": [{
            "mode": "server",
            "resource": [
                {"type": t, "interaction": _INTERACTIONS}
                for t in ("Patient", "Observation", "Claim", "ClaimResponse")
            ],
        }],
    }
