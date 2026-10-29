#!/bin/sh
set -e

# Defaults keep the GKE in-cluster deployment working; Cloud Run overrides
# PORT (8080), API_UPSTREAM and AUTH_UPSTREAM with public endpoints.
PORT="${PORT:-80}"
API_UPSTREAM="${API_UPSTREAM:-http://fhir-api:80}"
AUTH_UPSTREAM="${AUTH_UPSTREAM:-http://fhir-keycloak:8080}"
export PORT API_UPSTREAM AUTH_UPSTREAM

envsubst '${PORT} ${API_UPSTREAM} ${AUTH_UPSTREAM}' \
  < /etc/nginx/conf.d/default.conf.template \
  > /etc/nginx/conf.d/default.conf

exec nginx -g 'daemon off;'
