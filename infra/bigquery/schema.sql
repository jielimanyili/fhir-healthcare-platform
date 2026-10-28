-- FHIR Healthcare Analytics — BigQuery schema (Phase 2).
-- Denormalized analytical tables mirror the FHIR subset (ADR-0001).

CREATE TABLE IF NOT EXISTS `claims` (
  id STRING NOT NULL,
  status STRING,
  patient STRING,
  total FLOAT64
);

CREATE TABLE IF NOT EXISTS `observations` (
  id STRING NOT NULL,
  status STRING,
  subject STRING,
  code STRING,
  value FLOAT64
);
