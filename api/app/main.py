"""FastAPI application factory."""
import os

from fastapi import FastAPI

from .audit import AuditMiddleware, recent
from .db import make_session_factory
from .repository import InMemoryRepository, PostgresRepository
from .routers import build_routers, metadata_router
from .seed import seed


def create_app(repository=None, require_auth: bool = False):
    if repository is None:
        url = os.environ.get("DATABASE_URL")
        repository = PostgresRepository(make_session_factory(url)) if url else InMemoryRepository()
        seed(repository)

    app = FastAPI(title="FHIR Healthcare Analytics Platform", version="0.3.0")
    app.add_middleware(AuditMiddleware)
    app.include_router(metadata_router)
    for router in build_routers(repository, require_auth=require_auth):
        app.include_router(router)

    @app.get("/")
    def root():
        return {"service": "fhir-healthcare-platform", "fhirVersion": "4.0.1"}

    @app.get("/api/health")
    def health():
        return {"status": "ok", "service": "fhir-healthcare-platform"}

    @app.get("/api/audit")
    def audit(limit: int = 50):
        return {"events": recent(limit)}

    return app


app = create_app(require_auth=os.environ.get("REQUIRE_AUTH") == "true")
