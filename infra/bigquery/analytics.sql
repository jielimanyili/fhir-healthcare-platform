-- FHIR Healthcare Analytics — example aggregations.

-- Total approved claim amount per patient.
SELECT patient, SUM(total) AS total_approved
FROM `claims`
WHERE status = 'active'
GROUP BY patient;

-- Claim volume by month.
SELECT
  patient,
  COUNT(*) AS claim_count,
  SUM(total) AS total_amount
FROM `claims`
GROUP BY patient
ORDER BY total_amount DESC;

-- Observations by LOINC code.
SELECT code, COUNT(*) AS observation_count, AVG(value) AS avg_value
FROM `observations`
GROUP BY code
ORDER BY observation_count DESC;
