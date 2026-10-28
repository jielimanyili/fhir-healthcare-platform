from fastapi.testclient import TestClient

from app.main import create_app


def make_client() -> TestClient:
    return TestClient(create_app())


def test_health():
    r = make_client().get("/api/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_metadata_declares_subset():
    r = make_client().get("/fhir/metadata")
    assert r.status_code == 200
    body = r.json()
    assert body["resourceType"] == "CapabilityStatement"
    assert body["fhirVersion"] == "4.0.1"
    types = {res["type"] for res in body["rest"][0]["resource"]}
    assert types == {"Patient", "Observation", "Claim", "ClaimResponse"}


def test_read_patient():
    r = make_client().get("/fhir/Patient/p-001")
    assert r.status_code == 200
    body = r.json()
    assert body["id"] == "p-001"
    assert body["resourceType"] == "Patient"
    assert body["name"][0]["family"] == "Smith"


def test_search_patient_by_family():
    r = make_client().get("/fhir/Patient?family=Smith")
    assert r.status_code == 200
    body = r.json()
    assert body["resourceType"] == "Bundle"
    assert body["total"] == 1
    assert body["entry"][0]["resource"]["id"] == "p-001"


def test_search_observation_by_subject():
    r = make_client().get("/fhir/Observation?subject=Patient/p-001")
    assert r.status_code == 200
    assert r.json()["total"] == 1


def test_search_claimresponse_by_request():
    r = make_client().get("/fhir/ClaimResponse?request=Claim/c-001")
    assert r.status_code == 200
    assert r.json()["total"] == 1


def test_create_patient_assigns_id():
    payload = {
        "resourceType": "Patient",
        "name": [{"family": "Doe", "given": ["John"]}],
        "gender": "male",
    }
    r = make_client().post("/fhir/Patient", json=payload)
    assert r.status_code == 201
    body = r.json()
    assert body["id"]
    assert body["resourceType"] == "Patient"


def test_read_missing_returns_404():
    assert make_client().get("/fhir/Patient/nope").status_code == 404


def test_deidentified_patient_redacts_phi():
    r = make_client().get("/fhir/Patient/p-001?deidentified=true")
    assert r.status_code == 200
    body = r.json()
    assert body["name"] == "redacted"
    assert body["birthDate"] == "redacted"
    assert body["gender"] == "female"  # non-PHI field is kept


def test_audit_records_requests():
    c = make_client()
    c.get("/fhir/Patient/p-001")
    r = c.get("/api/audit")
    assert r.status_code == 200
    paths = [e["path"] for e in r.json()["events"]]
    assert "/fhir/Patient/p-001" in paths
