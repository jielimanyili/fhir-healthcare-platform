"""FastAPI application factory."""
from fastapi import FastAPI

from .repository import InMemoryRepository
from .routers import build_routers, metadata_router
from .seed import seed


def create_app() -> FastAPI:
    repo = InMemoryRepository()
    seed(repo)

    app = FastAPI(title="FHIR Healthcare Analytics Platform", version="0.1.0")

    app.include_router(metadata_router)
    for router in build_routers(repo):
        app.include_router(router)

    @app.get("/")
    def root():
        return {"service": "fhir-healthcare-platform", "fhirVersion": "4.0.1"}

    @app.get("/api/health")
    def health():
        return {"status": "ok", "service": "fhir-healthcare-platform"}

    return app


app = create_app()
