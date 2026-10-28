"""FHIR resource repositories.

- InMemoryRepository: Phase 0 (dev/tests, no database).
- PostgresRepository: Phase 1 (JSONB persistence, ADR-0001 decision #5).

Both expose the same interface so the router layer is storage-agnostic.
"""
from typing import Dict, List, Optional, Tuple

from sqlalchemy import select

from .db import FhirResource


def _matches(payload: dict, filters: dict) -> bool:
    for key, value in filters.items():
        if value is None:
            continue
        if key == "family":
            names = payload.get("name") or []
            if not any((n or {}).get("family") == value for n in names):
                return False
        elif key in ("patient", "subject", "request"):
            ref_obj = payload.get(key)
            ref = ref_obj.get("reference") if isinstance(ref_obj, dict) else None
            if ref != value:
                return False
        elif key == "status":
            if payload.get("status") != value:
                return False
    return True


class InMemoryRepository:
    def __init__(self) -> None:
        self._store: Dict[Tuple[str, str], dict] = {}

    def create(self, resource_type: str, resource_id: str, payload: dict) -> dict:
        self._store[(resource_type, resource_id)] = payload
        return payload

    def get(self, resource_type: str, resource_id: str) -> Optional[dict]:
        return self._store.get((resource_type, resource_id))

    def update(self, resource_type: str, resource_id: str, payload: dict) -> dict:
        self._store[(resource_type, resource_id)] = payload
        return payload

    def delete(self, resource_type: str, resource_id: str) -> bool:
        return self._store.pop((resource_type, resource_id), None) is not None

    def search(self, resource_type: str, **filters: Optional[str]) -> List[dict]:
        return [
            payload
            for (rt, _rid), payload in self._store.items()
            if rt == resource_type and _matches(payload, filters)
        ]


class PostgresRepository:
    def __init__(self, session_factory) -> None:
        self.session_factory = session_factory

    def create(self, resource_type: str, resource_id: str, payload: dict) -> dict:
        with self.session_factory() as session:
            existing = session.execute(
                select(FhirResource).where(
                    FhirResource.resource_type == resource_type,
                    FhirResource.resource_id == resource_id,
                )
            ).scalar_one_or_none()
            if existing is None:
                session.add(FhirResource(resource_type=resource_type, resource_id=resource_id, payload=payload))
                session.commit()
        return payload

    def get(self, resource_type: str, resource_id: str) -> Optional[dict]:
        with self.session_factory() as session:
            row = session.execute(
                select(FhirResource).where(
                    FhirResource.resource_type == resource_type,
                    FhirResource.resource_id == resource_id,
                )
            ).scalar_one_or_none()
        return row.payload if row else None

    def update(self, resource_type: str, resource_id: str, payload: dict) -> Optional[dict]:
        with self.session_factory() as session:
            row = session.execute(
                select(FhirResource).where(
                    FhirResource.resource_type == resource_type,
                    FhirResource.resource_id == resource_id,
                )
            ).scalar_one_or_none()
            if row is None:
                return None
            row.payload = payload
            session.commit()
        return payload

    def delete(self, resource_type: str, resource_id: str) -> bool:
        with self.session_factory() as session:
            row = session.execute(
                select(FhirResource).where(
                    FhirResource.resource_type == resource_type,
                    FhirResource.resource_id == resource_id,
                )
            ).scalar_one_or_none()
            if row is None:
                return False
            session.delete(row)
            session.commit()
        return True

    def search(self, resource_type: str, **filters: Optional[str]) -> List[dict]:
        with self.session_factory() as session:
            rows = session.execute(
                select(FhirResource).where(FhirResource.resource_type == resource_type)
            ).scalars().all()
        return [r.payload for r in rows if _matches(r.payload, filters)]
