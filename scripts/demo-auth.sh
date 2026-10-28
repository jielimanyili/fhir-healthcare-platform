#!/usr/bin/env bash
# Phase 1b demo — OIDC/RBAC against the local stack.
# Usage: docker compose up --build -d && sleep 40 && ./scripts/demo-auth.sh
set -euo pipefail

KEYCLOAK="${KEYCLOAK_URL:-http://localhost:8080}"
API="${API_URL:-http://localhost:8000}"

token() {  # token <username> <password>
  curl -s -X POST "$KEYCLOAK/realms/fhir/protocol/openid-connect/token" \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -d "grant_type=password" \
    -d "client_id=fhir-api" \
    -d "client_secret=fhir-api-secret" \
    -d "username=$1" \
    -d "password=$2" \
    | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])"
}

call() {  # call <label> <token> <url...>
  local label="$1"; shift
  local tok="$1"; shift
  local code
  code=$(curl -s -o /tmp/fhir_resp.json -w "%{http_code}" -H "Authorization: Bearer $tok" "$@")
  echo "== $label -> HTTP $code"
  head -c 200 /tmp/fhir_resp.json; echo; echo
}

CLINICIAN=$(token clinician1 clinician1)
PATIENT=$(token patient1 patient1)
ADJUDICATOR=$(token adjudicator1 adjudicator1)
ADMIN=$(token admin1 admin1)

call "clinician reads Patient/p-001" "$CLINICIAN" "$API/fhir/Patient/p-001"
call "patient reads own Patient/p-001" "$PATIENT" "$API/fhir/Patient/p-001"
call "patient reads other Patient/p-002 (should be 403)" "$PATIENT" "$API/fhir/Patient/p-002"
call "clinician tries to write Claim (should be 403)" "$CLINICIAN" -X POST "$API/fhir/Claim" -H "Content-Type: application/json" -d '{"resourceType":"Claim","status":"active"}'
call "adjudicator writes ClaimResponse (should be 201)" "$ADJUDICATOR" -X POST "$API/fhir/ClaimResponse" -H "Content-Type: application/json" -d '{"resourceType":"ClaimResponse","status":"active","request":{"reference":"Claim/c-001"},"patient":{"reference":"Patient/p-001"}}'
call "admin reads audit log" "$ADMIN" "$API/api/audit"

echo "== no token (should be 401)"
curl -s -o /tmp/fhir_resp.json -w "%{http_code}" "$API/fhir/Patient/p-001"; echo
head -c 120 /tmp/fhir_resp.json; echo
