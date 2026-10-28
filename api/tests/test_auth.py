"""Unit tests for the auth helpers (scope/role/ownership) — no live Keycloak needed."""
from app.auth import belongs_to, can_read, can_write, is_patient_only, scopes


def _claims(*roles, username=None):
    c = {"realm_access": {"roles": list(roles)}}
    if username:
        c["preferred_username"] = username
    return c


def test_role_to_scopes():
    assert "patient/Patient.read" in scopes(_claims("patient"))
    assert "system/*.write" in scopes(_claims("admin"))
    assert "user/Claim.write" in scopes(_claims("adjudicator"))


def test_read_scope_enforcement():
    assert can_read(_claims("clinician"), "Patient")
    assert can_read(_claims("admin"), "Patient")
    assert can_read(_claims("patient"), "Patient")
    assert not can_read(_claims("patient"), "ClaimResponse")


def test_write_scope_enforcement():
    assert can_write(_claims("admin"), "Claim")
    assert can_write(_claims("adjudicator"), "Claim")
    assert can_write(_claims("adjudicator"), "ClaimResponse")
    assert not can_write(_claims("clinician"), "Claim")
    assert not can_write(_claims("patient"), "Claim")


def test_is_patient_only():
    assert is_patient_only(_claims("patient"))
    assert not is_patient_only(_claims("clinician"))
    assert not is_patient_only(_claims("adjudicator"))


def test_belongs_to_patient():
    own = {"resourceType": "Patient", "id": "p-001"}
    assert belongs_to(own, "p-001")
    assert not belongs_to(own, "p-002")


def test_belongs_to_reference():
    obs = {"resourceType": "Observation", "subject": {"reference": "Patient/p-001"}}
    claim = {"resourceType": "Claim", "patient": {"reference": "Patient/p-001"}}
    assert belongs_to(obs, "p-001")
    assert belongs_to(claim, "p-001")
    assert not belongs_to(obs, "p-002")
