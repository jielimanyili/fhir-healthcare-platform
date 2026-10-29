# Demo script

Two ways to demo the FHIR Healthcare Analytics Platform: a **browser walkthrough**
(~90 seconds, visual) or a **terminal walkthrough** (curl + BigQuery, more technical).

## Quick facts

| Thing | Value |
|---|---|
| **UI (Cloud Run)** | https://fhir-ui-bmux3qfmza-uc.a.run.app |
| **API (GKE LoadBalancer)** | http://34.170.81.71 |
| **BigQuery dataset** | `model-summit-97213.fhir_analytics` (tables: `claims`, `observations`) |

**Demo credentials** (all data is synthetic):

| Username | Password | Role |
|---|---|---|
| `clinician1` | `clinician1` | reads all patients |
| `patient1` | `patient1` | reads only own record |
| `admin1` | `admin1` | full read/write + audit |
| `adjudicator1` | `adjudicator1` | writes Claim / ClaimResponse |

---

## Option A — Browser walkthrough (~90 s)

Record with **Cmd + Shift + 5** (enable the microphone under Options), or QuickTime →
File → New Screen Recording, or Loom.

| Time | You do | You say |
|---|---|---|
| 0:00 | Open `https://fhir-ui-bmux3qfmza-uc.a.run.app` | "I built a live healthcare platform to demonstrate the stack in the CVS Health role — FHIR, Angular, Python, Java, on GCP." |
| 0:12 | Sign in `clinician1` / `clinician1` | "It's behind Keycloak — OIDC with role-based access. As a clinician, I can see all patients." |
| 0:22 | Sign out, sign in `patient1` / `patient1` | "Same endpoint, but as a patient, I only see my own record — that's SMART-on-FHIR scoping and ownership." |
| 0:32 | Open `…/fhir/metadata` | "Under the hood it's a real FHIR R4 API — that's the CapabilityStatement." |
| 0:42 | Open BigQuery → `fhir_analytics.claims` | "Every claim and observation flows through a Java Spring Boot pipeline — Pub/Sub into BigQuery — so it's not just a static page." |
| 0:55 | Wrap up | "Deployed on GKE and Cloud Run with Terraform and Helm. Full source is on GitHub. Happy to go deeper." |

---

## Option B — Terminal walkthrough (curl + BigQuery)

Copy/paste the whole block. Requires `curl`, `python3`, and `bq` (Google Cloud SDK).

```bash
BASE="https://fhir-ui-bmux3qfmza-uc.a.run.app"

# 1) Landing page
curl -s -o /dev/null -w "GET / -> %{http_code}\n" "$BASE/"

# 2) Sign in (clinician) — Keycloak OIDC, resource-owner password grant
TOKEN=$(curl -s -X POST "$BASE/auth/realms/fhir/protocol/openid-connect/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "grant_type=password" -d "client_id=fhir-ui" \
  -d "username=clinician1" -d "password=clinician1" \
  | python3 -c "import sys,json;print(json.load(sys.stdin)['access_token'])")

# 3) List patients (clinician sees all)
curl -s "$BASE/fhir/Patient" -H "Authorization: Bearer $TOKEN" | python3 -m json.tool

# 4) De-identified read (PHI redacted)
curl -s "$BASE/fhir/Patient/p-001?deidentified=true" \
  -H "Authorization: Bearer $TOKEN" | python3 -m json.tool

# 5) FHIR R4 CapabilityStatement
curl -s "$BASE/fhir/metadata" | python3 -m json.tool

# 6) Audit log (every request recorded — raw API, no auth)
curl -s "http://34.170.81.71/api/audit" | python3 -m json.tool

# 7) Analytics in BigQuery (Java pipeline: Pub/Sub -> BigQuery)
bq query --nouse_legacy_sql --project_id=model-summit-97213 \
  'SELECT id, status, patient, total FROM `model-summit-97213.fhir_analytics.claims`'
```

### Expected highlights

**#3 — patient list (clinician):**
```json
{ "resourceType": "Bundle", "type": "searchset", "total": 2, "entry": [ ... ] }
```

**#4 — de-identified patient (PHI redacted):**
```json
{ "id": "p-001", "name": "redacted", "gender": "female", "address": "redacted",
  "telecom": "redacted", "birthDate": "redacted", "identifier": "redacted",
  "meta": { "security": [ { "system": ".../v3-Confidentiality", "code": "R" } ] } }
```

**#6 — audit log:**
```json
{ "events": [ { "method": "GET", "path": "/fhir/Patient/p-001", "status": 200, "user": "clinician1" }, ... ] }
```

**#7 — BigQuery (one row from the live pipeline):**
```
+----------------------------------+--------+---------------+-------+
| id                               | status | patient       | total |
+----------------------------------+--------+---------------+-------+
| 5a997fbd1ff84509bc276d4afafd8d19 | active | Patient/p-001 | 250.0 |
+----------------------------------+--------+---------------+-------+
```

---

## Option C — Full RBAC write demo (scripted)

The `demo-auth.sh` script exercises every role (clinician / patient / adjudicator /
admin) including writes and the audit log. It runs against in-cluster services via
port-forward:

```bash
kubectl port-forward svc/fhir-keycloak 8080:8080 &
kubectl port-forward svc/fhir-api 8000:80 &
./scripts/demo-auth.sh
```

---

## Notes

- **URLs are dynamic.** Find them with:
  - UI: `gcloud run services describe fhir-ui --region us-central1 --format='value(status.url)'`
  - API: `kubectl get svc fhir-api -o jsonpath='{.status.loadBalancer.ingress[0].ip}'`
- **Cost.** The GKE cluster, Cloud SQL, and LoadBalancers bill continuously. Tear down
  with `terraform destroy` when not demoing (see `DEPLOYMENT.md`).
- **All data is synthetic** — no real PHI.
