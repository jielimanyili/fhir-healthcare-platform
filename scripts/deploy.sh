#!/usr/bin/env bash
# Deploy the FHIR Healthcare Analytics Platform to GCP.
# Usage: GCP_PROJECT_ID=<project-id> ./scripts/deploy.sh
set -euo pipefail

PROJECT_ID="${GCP_PROJECT_ID:?set GCP_PROJECT_ID env var}"
REGION="${REGION:-us-central1}"
REPO="$REGION-docker.pkg.dev/$PROJECT_ID/fhir"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"

echo "== 1. Provision infrastructure (Terraform) =="
cd "$ROOT/terraform"
terraform init
terraform apply -var="project_id=$PROJECT_ID" -var="region=$REGION"

echo "== 2. Build + push images =="
cd "$ROOT"
gcloud auth configure-docker "$REGION-docker.pkg.dev"
docker build -t "$REPO/fhir-api:latest" ./api && docker push "$REPO/fhir-api:latest"
docker build -t "$REPO/fhir-event-pipeline:latest" ./pipeline && docker push "$REPO/fhir-event-pipeline:latest"

echo "== 3. Deploy to GKE (Helm) =="
gcloud container clusters get-credentials fhir-gke --region "$REGION" --project "$PROJECT_ID"
helm upgrade --install fhir "$ROOT/helm/fhir" \
  --set image.repository="$REPO" \
  --set image.tag=latest

echo "Done. Verify with: kubectl get pods"
