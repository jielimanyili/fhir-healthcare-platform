# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
### Added
- Pub/Sub event publisher in the API (Claim/Observation create/update → `fhir-resource-events`).
- Keycloak (OIDC/RBAC) deployment in the Helm chart (realm ConfigMap + service).

## [0.4.0] - 2026-10-28
### Added
- GKE deployment verified end-to-end: API + Keycloak + pipeline on GKE, Pub/Sub → BigQuery.
### Changed
- Pipeline runtime base image to `eclipse-temurin:21-jre-jammy` (glibc) — fixes a native tcnative/boringssl SIGSEGV.
- `values.yaml` filled with real GCP project values; app images use `imagePullPolicy: Always`.
### Fixed
- Cloud SQL `edition = "ENTERPRISE"`, Workload Identity `depends_on`, API Gateway placeholder address.

## [0.1.0] - 2026-10-27
### Added
- Initial documentation (pre-code).
