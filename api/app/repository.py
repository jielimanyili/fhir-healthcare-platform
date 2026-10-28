"""In-memory FHIR resource repository (Phase 0).

Postgres JSONB replaces this storage in Phase 1 (ADR-0001 decision #5). The router
layer depends on this interface only, so the swap is localized here.
"""
from typing import Dict, List, Optional, Tuple


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
        out: List[dict] = []
        for (rt, _rid), payload in self._store.items():
            if rt == resource_type and self._matches(payload, filters):
                out.append(payload)
        return out

    @staticmethod
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
