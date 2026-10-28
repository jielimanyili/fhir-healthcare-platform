"""Synthetic seed data — no real PHI (ADR-0002 decision #1)."""
from .repository import InMemoryRepository


def seed(repo: InMemoryRepository) -> None:
    repo.create("Patient", "p-001", {
        "resourceType": "Patient",
        "id": "p-001",
        "identifier": [{"system": "urn:oid:1.2.840.114350.1.13", "value": "MRN-000123"}],
        "name": [{"use": "official", "family": "Smith", "given": ["Jane"]}],
        "telecom": [{"system": "phone", "value": "555-0100"}],
        "gender": "female",
        "birthDate": "1980-05-12",
        "address": [{"city": "Dayton", "state": "OH", "postalCode": "45458"}],
    })

    repo.create("Patient", "p-002", {
        "resourceType": "Patient",
        "id": "p-002",
        "name": [{"use": "official", "family": "Johnson", "given": ["Robert"]}],
        "gender": "male",
        "birthDate": "1975-11-03",
        "address": [{"city": "Columbus", "state": "OH", "postalCode": "43215"}],
    })

    repo.create("Observation", "o-001", {
        "resourceType": "Observation",
        "id": "o-001",
        "status": "final",
        "category": [{"coding": [{"system": "http://terminology.hl7.org/CodeSystem/observation-category", "code": "laboratory"}]}],
        "code": {"coding": [{"system": "http://loinc.org", "code": "718-7", "display": "Hemoglobin"}]},
        "subject": {"reference": "Patient/p-001"},
        "effectiveDateTime": "2026-10-20",
        "valueQuantity": {"value": 13.8, "unit": "g/dL", "system": "http://unitsofmeasure.org", "code": "g/dL"},
    })

    repo.create("Claim", "c-001", {
        "resourceType": "Claim",
        "id": "c-001",
        "status": "active",
        "type": {"coding": [{"code": "professional"}]},
        "use": "claim",
        "patient": {"reference": "Patient/p-001"},
        "created": "2026-10-21",
        "insurer": {"reference": "Organization/org-001"},
        "total": {"value": 145.00, "currency": "USD"},
    })

    repo.create("ClaimResponse", "cr-001", {
        "resourceType": "ClaimResponse",
        "id": "cr-001",
        "status": "active",
        "outcome": "complete",
        "disposition": "Approved - paid in full",
        "request": {"reference": "Claim/c-001"},
        "patient": {"reference": "Patient/p-001"},
        "created": "2026-10-22",
        "item": [{"itemSequence": 1, "adjudication": [{"category": {"coding": [{"code": "benefit"}]}, "amount": {"value": 145.00, "currency": "USD"}}]}],
        "payment": {"amount": {"value": 145.00, "currency": "USD"}},
    })
