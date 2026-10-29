"""Publish FHIR resource events to Pub/Sub (Phase 2 analytics pipeline).

The API emits Claim and Observation events so the Java Spring Boot pipeline can
denormalize them into BigQuery (ADR-0004). Publishing is:

- **best-effort**: a downstream analytics outage never blocks the clinical API.
- **opt-in**: a no-op unless both ``GCP_PROJECT_ID`` and ``PUBSUB_TOPIC`` are set,
  so local dev and unit tests keep working without GCP credentials.

On GKE the publisher authenticates via Workload Identity (the ``fhir-api``
Kubernetes SA -> GCP ``fhir-api`` SA binding in ``terraform/workload-identity.tf``).
"""
import json
import logging
import os

logger = logging.getLogger("fhir.events")

PROJECT_ID = os.environ.get("GCP_PROJECT_ID")
TOPIC = os.environ.get("PUBSUB_TOPIC")
_PUBLISHED_TYPES = ("Claim", "Observation")

_publisher = None
_publisher_disabled = False


def _client():
    global _publisher, _publisher_disabled
    if not PROJECT_ID or not TOPIC or _publisher_disabled:
        return None
    if _publisher is None:
        try:
            from google.cloud import pubsub_v1

            _publisher = pubsub_v1.PublisherClient()
        except Exception as exc:  # pragma: no cover - depends on environment
            _publisher_disabled = True
            logger.warning("Pub/Sub unavailable; events disabled: %s", exc)
            return None
    return _publisher


def publish(resource_type: str, payload: dict) -> None:
    if resource_type not in _PUBLISHED_TYPES:
        return
    client = _client()
    if client is None:
        return
    try:
        topic_path = client.topic_path(PROJECT_ID, TOPIC)
        data = json.dumps(payload).encode("utf-8")
        client.publish(topic_path, data)
        logger.info("published %s/%s", resource_type, payload.get("id"))
    except Exception as exc:  # pragma: no cover
        logger.warning("publish failed for %s/%s: %s", resource_type, payload.get("id"), exc)
