# Deployment — GCP

Deploy the FHIR Healthcare Analytics Platform to **GKE + BigQuery + Pub/Sub** (Phases 2 & 3).

## 0. Prerequisites (one-time, ~15 min)

1. **GCP account + billing** — https://console.cloud.google.com → **"Get started for free"**.
   - $300 / 90-day free trial; a card is required to activate (no auto-charge unless you upgrade).
   - Create a project (e.g. `fhir-healthcare`) and note the **project id**.
2. **Install tooling** (macOS):
   ```bash
   brew install --cask google-cloud-sdk
   brew install terraform
   ```
3. **Authenticate + enable APIs**:
   ```bash
   gcloud auth login
   gcloud auth application-default login
   gcloud config set project <PROJECT_ID>
   gcloud services enable \
     container.googleapis.com compute.googleapis.com bigquery.googleapis.com \
     pubsub.googleapis.com artifactregistry.googleapis.com sqladmin.googleapis.com \
     apigateway.googleapis.com servicemanagement.googleapis.com
   ```

## 1. Provision infrastructure (Terraform)

```bash
cd terraform
terraform init
terraform apply -var="project_id=<PROJECT_ID>" -var="region=us-central1"
```

Creates: VPC + firewall, GKE Autopilot (`fhir-gke`), BigQuery dataset (`fhir_analytics`),
Pub/Sub topic + subscription, Artifact Registry (`fhir`), Cloud SQL Postgres, service accounts,
and (Phase 3) the API Gateway.

## 2. Build + push images

> Prefer **Cloud Build** for images — it builds natively on linux/amd64, whereas local
> Apple Silicon builds produce arm64 images that won't run on GKE nodes:

```bash
gcloud builds submit --tag "$REGION-docker.pkg.dev/<PROJECT_ID>/fhir/fhir-api:latest" ./api
gcloud builds submit --tag "$REGION-docker.pkg.dev/<PROJECT_ID>/fhir/fhir-event-pipeline:latest" ./pipeline
```

(Or, on an amd64 machine, `docker build` + `docker push` as in the original script.)

## 3. Deploy to GKE (Helm)

Fill in the `REPLACE_ME` values in `helm/fhir/values.yaml` (see "Wiring to complete" below), then:

```bash
gcloud container clusters get-credentials fhir-gke --region us-central1 --project <PROJECT_ID>
helm upgrade --install fhir ./helm/fhir \
  --set image.repository="$REPO" \
  --set image.tag=latest
kubectl get pods
```

## 4. API Gateway (Phase 3)

`terraform/gateway.tf` applies with the same `terraform apply`. Before applying, replace
`REPLACE_WITH_API_SERVICE_URL` in `infra/gateway/openapi.yaml` with the GKE API service URL
(`kubectl get svc fhir-api`).

## Run the demo (public UI + port-forward)

The `fhir-ui` LoadBalancer serves the SPA publicly with Keycloak login — get its IP with
`kubectl get svc fhir-ui`. For the scripted OIDC/RBAC walkthrough, port-forward and run:

```bash
kubectl port-forward svc/fhir-keycloak 8080:8080 &
kubectl port-forward svc/fhir-api 8000:80 &
./scripts/demo-auth.sh            # OIDC/RBAC walkthrough (clinician/patient/adjudicator/admin)

# Analytics loop: create a Claim (adjudicator) / Observation (admin) → BigQuery
bq query --nouse_legacy_sql --project_id=<PROJECT_ID> \
  'SELECT * FROM `fhir_analytics.claims`'
```

## Wiring (completed)

The three deployment-specific values are wired in `helm/fhir/values.yaml`:

1. **Cloud SQL** — `cloud-sql-proxy` sidecar + Workload Identity (no static keys); `DATABASE_URL` points at `localhost:5432` through the sidecar.
2. **Workload Identity** — GKE KSAs `fhir-api` / `fhir-pipeline` bound to the GCP SAs.
3. **Keycloak** — deployed in-cluster; the API resolves JWKS at `http://fhir-keycloak:8080/...`.

## Teardown (avoid cost)

```bash
terraform destroy
```

## Cost notes

- GKE Autopilot: ~$0.10/hr management fee (~$73/mo; GCP's ~$74.40 GKE free-tier credit often offsets it) + pod compute.
- Cloud SQL `db-f1-micro`: ~$7/mo.
- BigQuery / Pub/Sub: free-tier friendly.
- **Tear down when not demoing** to stay within the $300 trial.
