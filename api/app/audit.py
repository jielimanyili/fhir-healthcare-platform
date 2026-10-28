"""Audit logging middleware + in-memory audit view (ADR-0002 decision #3).

Every request is recorded (method, path, status, user). The `user` field is
populated from the JWT subject once Phase 1b (Keycloak) lands; until then it is
None. A Postgres-backed audit table is a noted follow-up.
"""
import logging
from collections import deque
from datetime import datetime, timezone
from typing import List, Optional

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

logger = logging.getLogger("fhir.audit")

_events: "deque[dict]" = deque(maxlen=1000)


def record(method: str, path: str, status: int, user: Optional[str] = None) -> None:
    event = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "method": method,
        "path": path,
        "status": status,
        "user": user,
    }
    _events.append(event)
    logger.info("AUDIT %s %s -> %s user=%s", method, path, status, user)


def recent(limit: int = 50) -> List[dict]:
    return list(_events)[-limit:]


class AuditMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        record(
            request.method,
            request.url.path,
            response.status_code,
            getattr(request.state, "user", None),
        )
        return response
