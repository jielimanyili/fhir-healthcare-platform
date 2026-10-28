"""Safe-harbor PHI de-identification (ADR-0002 decision #2).

Redacts the 18 HIPAA-identifier fields present in the demo's FHIR subset. For
Patient resources this removes direct identifiers; for Observation/Claim/
ClaimResponse it de-links the patient reference so the clinical/financial data
survives but can no longer be tied back to an individual.
"""
import copy

_PATIENT_PHI = ("identifier", "name", "telecom", "address", "birthDate")
_REFERENCE_FIELDS = ("subject", "patient")


def deidentify(resource: dict) -> dict:
    out = copy.deepcopy(resource)
    if out.get("resourceType") == "Patient":
        for field in _PATIENT_PHI:
            if field in out:
                out[field] = "redacted"
    else:
        for field in _REFERENCE_FIELDS:
            if isinstance(out.get(field), dict):
                out[field] = {"reference": "redacted"}
    meta = out.setdefault("meta", {})
    meta["security"] = [{
        "system": "http://terminology.hl7.org/CodeSystem/v3-Confidentiality",
        "code": "R",
        "display": "restricted",
    }]
    return out
