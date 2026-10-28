"""FHIR R4 subset models (Pydantic v2).

Implements the four resources in scope (ADR-0001): Patient, Observation, Claim,
ClaimResponse. Fields mirror the FHIR R4 JSON shape; only the demo-relevant subset
is modeled (full R4 conformance is a documented non-goal).
"""
from typing import List, Literal, Optional

from pydantic import BaseModel


class Identifier(BaseModel):
    system: Optional[str] = None
    value: Optional[str] = None


class HumanName(BaseModel):
    use: Optional[str] = None
    family: Optional[str] = None
    given: Optional[List[str]] = None


class Telecom(BaseModel):
    system: Optional[str] = None
    value: Optional[str] = None


class Address(BaseModel):
    city: Optional[str] = None
    state: Optional[str] = None
    postalCode: Optional[str] = None


class Coding(BaseModel):
    system: Optional[str] = None
    code: Optional[str] = None
    display: Optional[str] = None


class CodeableConcept(BaseModel):
    coding: Optional[List[Coding]] = None
    text: Optional[str] = None


class Reference(BaseModel):
    reference: Optional[str] = None
    display: Optional[str] = None


class Quantity(BaseModel):
    value: Optional[float] = None
    unit: Optional[str] = None
    system: Optional[str] = None
    code: Optional[str] = None


class Money(BaseModel):
    value: Optional[float] = None
    currency: Optional[str] = None


class Patient(BaseModel):
    resourceType: Literal["Patient"] = "Patient"
    id: Optional[str] = None
    identifier: Optional[List[Identifier]] = None
    name: Optional[List[HumanName]] = None
    telecom: Optional[List[Telecom]] = None
    gender: Optional[str] = None
    birthDate: Optional[str] = None
    address: Optional[List[Address]] = None


class Observation(BaseModel):
    resourceType: Literal["Observation"] = "Observation"
    id: Optional[str] = None
    status: str
    category: Optional[List[CodeableConcept]] = None
    code: CodeableConcept
    subject: Optional[Reference] = None
    effectiveDateTime: Optional[str] = None
    valueQuantity: Optional[Quantity] = None


class ClaimItem(BaseModel):
    sequence: int = 1
    productOrService: Optional[CodeableConcept] = None


class Claim(BaseModel):
    resourceType: Literal["Claim"] = "Claim"
    id: Optional[str] = None
    status: str
    type: Optional[CodeableConcept] = None
    use: Optional[str] = None
    patient: Optional[Reference] = None
    created: Optional[str] = None
    insurer: Optional[Reference] = None
    priority: Optional[CodeableConcept] = None
    total: Optional[Money] = None
    item: Optional[List[ClaimItem]] = None


class Adjudication(BaseModel):
    category: Optional[CodeableConcept] = None
    amount: Optional[Money] = None
    reason: Optional[CodeableConcept] = None


class ClaimResponseItem(BaseModel):
    itemSequence: Optional[int] = None
    adjudication: Optional[List[Adjudication]] = None


class ClaimResponse(BaseModel):
    resourceType: Literal["ClaimResponse"] = "ClaimResponse"
    id: Optional[str] = None
    status: str
    outcome: Optional[str] = None
    disposition: Optional[str] = None
    request: Optional[Reference] = None
    patient: Optional[Reference] = None
    insurer: Optional[Reference] = None
    created: Optional[str] = None
    item: Optional[List[ClaimResponseItem]] = None
    payment: Optional[Money] = None
