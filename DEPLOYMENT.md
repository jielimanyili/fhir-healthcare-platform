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

```bash
export REGION=us-central1
export REPO="$REGION-docker.pkg.dev/<PROJECT_ID>/fhir"
gcloud auth configure-docker "$REGION-docker.pkg.dev"

docker build -t "$REPO/fhir-api:latest" ./api && docker push "$REPO/fhir-api:latest"
docker build -t "$REPO/fhir-event-pipeline:latest" ./pipeline && docker push "$REPO/fhir-event-pipeline:latest"
```

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

## Wiring to complete (honest notes)

The IaC + app code is complete, but three values are deployment-specific and must be set to **your**
environment before `helm install`:

1. **Cloud SQL connection string** — `values.yaml` `DATABASE_URL`. Use the Cloud SQL connection
   name (`terraform output cloud_sql_connection_name`) + a Cloud SQL Auth Proxy sidecar, or the
   instance's private/public IP.
2. **Workload Identity** — bind the GKE `fhir-pipeline` service account to the `fhir-pipeline` GCP
   SA (Pub/Sub subscriber + BigQuery editor) so the pipeline authenticates without static keys.
3. **Keycloak URL** — `OIDC_ISSUER` / `OIDC_JWKS_URL`. Deploy Keycloak (or use an external IdP) and
   set the reachable URL.

## Teardown (avoid cost)

```bash
terraform destroy
```

## Cost notes

- GKE Autopilot: ~$0.10/hr management fee (~$73/mo; GCP's ~$74.40 GKE free-tier credit often offsets it) + pod compute.
- Cloud SQL `db-f1-micro`: ~$7/mo.
- BigQuery / Pub/Sub: free-tier friendly.
- **Tear down when not demoing** to stay within the $300 trial.
