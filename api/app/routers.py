"""FHIR R4 routers + CapabilityStatement (Phase 0/1 subset).

Each resource exposes standard FHIR interactions: create, read, update, delete,
search-type. Search returns a `Bundle` of type `searchset`. Reads support an
optional `deidentified=true` query parameter for safe-harbor PHI redaction.
"""
from typing import Optional, Type
from uuid import uuid4

from fastapi import APIRouter, Body, HTTPException
from pydantic import BaseModel

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


def _resource_router(repo, resource_type: str, model: Type[BaseModel]):
    router = APIRouter(prefix=f"/fhir/{resource_type}", tags=[resource_type])

    @router.post("", status_code=201)
    def create(payload: model = Body(...)):
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
    ):
        results = repo.search(
            resource_type,
            family=family,
            patient=patient,
            subject=subject,
            request=request,
            status=status,
        )
        if deidentified:
            results = [deidentify(r) for r in results]
        return _bundle(results)

    @router.get("/{rid}")
    def read(rid: str, deidentified: bool = False):
        resource = repo.get(resource_type, rid)
        if resource is None:
            raise HTTPException(status_code=404, detail="resource not found")
        return deidentify(resource) if deidentified else resource

    @router.put("/{rid}")
    def update(rid: str, payload: model = Body(...)):
        if repo.get(resource_type, rid) is None:
            raise HTTPException(status_code=404, detail="resource not found")
        data = payload.model_dump()
        data["resourceType"] = resource_type
        data["id"] = rid
        return repo.update(resource_type, rid, data)

    @router.delete("/{rid}", status_code=204)
    def delete(rid: str):
        if not repo.delete(resource_type, rid):
            raise HTTPException(status_code=404, detail="resource not found")

    return router


def build_routers(repo):
    return [
        _resource_router(repo, "Patient", Patient),
        _resource_router(repo, "Observation", Observation),
        _resource_router(repo, "Claim", Claim),
        _resource_router(repo, "ClaimResponse", ClaimResponse),
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
