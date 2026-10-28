"""SQLAlchemy models + session factory (Phase 1: Postgres JSONB persistence)."""
from datetime import datetime

from sqlalchemy import (Boolean, Column, DateTime, Integer, String,
                        UniqueConstraint, create_engine)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()


class FhirResource(Base):
    __tablename__ = "fhir_resources"
    id = Column(Integer, primary_key=True, autoincrement=True)
    resource_type = Column(String(50), nullable=False, index=True)
    resource_id = Column(String(64), nullable=False)
    payload = Column(JSONB, nullable=False)
    deidentified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    __table_args__ = (UniqueConstraint("resource_type", "resource_id", name="uq_fhir_resource"),)


class AuditEvent(Base):
    __tablename__ = "audit_events"
    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    method = Column(String(10), nullable=False)
    path = Column(String(512), nullable=False)
    status = Column(Integer, nullable=False)
    user = Column(String(128), nullable=True)


def make_session_factory(url: str):
    engine = create_engine(url, pool_pre_ping=True)
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine, autoflush=False, autocommit=False)
