# Model Serving & Inference Security

## Overview

This standard defines the security controls for all online inference endpoints, covering
authentication, Ray Serve deployment governance, inference logging, model versioning, runtime
monitoring, and Clipper integration.

Requirements use **MUST/SHOULD/MAY** per RFC 2119.

---

## 1. Endpoint Authentication

### 1.1 OIDC Authentication

- Every inference endpoint MUST require a valid OIDC ID token (or derived bearer token).
- Unauthenticated requests MUST return HTTP 401 and MUST be logged.
- Tokens MUST be validated against the authoritative OIDC provider's JWKS endpoint on every
  request or cached with a maximum TTL of 5 minutes.

### 1.2 Service Accounts

- Each application or service consuming an inference endpoint MUST use a dedicated Kubernetes
  service account with the minimum required permissions.
- Shared credentials across applications are PROHIBITED.

### 1.3 API Keys for Programmatic Access

- Long-running automation clients that cannot obtain OIDC tokens MUST use API keys issued by
  Vault with a maximum TTL of 24 hours.
- API key issuance, rotation, and revocation MUST be logged.

### 1.4 Mutual TLS for Service-to-Service

- Service-to-service calls between internal components (e.g. orchestrator → Ray Serve)
  MUST use mTLS with certificates issued by the internal CA.
- Certificate rotation MUST occur at least every 90 days.

---

## 2. Ray Serve Deployment

### 2.1 Model Fetching from CK Backend

- Ray Serve deployments MUST fetch model artifacts from the CK backend only.
- Deployment configurations MUST pin the model to a specific semantic version (no `latest` tags).
- The CK artifact hash MUST be verified after download before loading the model.

### 2.2 Multiple Model Versions and Gradual Rollout

- Multiple model versions SHOULD be deployable simultaneously to support gradual rollout.
- New model versions MUST start at ≤ 10% traffic (canary) before full promotion.
- Canary traffic percentage MUST be adjustable via deployment configuration without redeployment.

### 2.3 A/B Testing

- A/B test configurations MUST be stored in the deployment record with a rationale.
- Inference logs MUST record which model version served each request to enable offline analysis.
- A/B test results MUST be stored in the CK backend as an immutable experiment record.

### 2.4 Automatic Rollback on Anomalies

- If error rate or latency exceeds configured thresholds, an automatic rollback to the previous
  stable version MUST be triggered within 60 seconds.
- Rollback events MUST be logged and an alert sent to the on-call team.

---

## 3. Inference Logging

### 3.1 Per-Prediction Log Entry

Every prediction MUST generate a log entry containing:

| Field              | Description                                          |
|--------------------|------------------------------------------------------|
| `request_id`       | UUID per request                                     |
| `model_name`       | Model identifier                                     |
| `model_version`    | Semantic version of the serving model                |
| `input_hash`       | SHA-256 of the serialised input (not the input itself) |
| `output`           | Full model output (or hash if output is large)       |
| `latency_ms`       | End-to-end serving latency                           |
| `caller_identity`  | Authenticated principal (user or service account)    |
| `timestamp`        | ISO-8601 UTC                                         |

### 3.2 Immutable Audit Trail

- Inference logs MUST be stored in WORM (Write Once Read Many) storage.
- Log integrity MUST be protected by a cryptographic chain (e.g. hash-chained log entries).
- Minimum retention: 90 days. Extended retention as per the data classification of the inputs.

### 3.3 Privacy Considerations

- Input data containing PII MUST NOT be stored in plain text in inference logs.
- The SHA-256 hash of the input MUST be stored instead.
- If raw inputs are required for debugging, they MUST be stored in a separate encrypted store
  with access restricted to the security team and a 7-day TTL.

---

## 4. Model Versioning

### 4.1 Immutability

- A deployed model version MUST NOT be modified in-place.
- Any change to weights, configuration, or preprocessing code MUST result in a new version.

### 4.2 Version Control in CK Backend

- All model versions MUST be stored and tracked in the CK backend.
- Version history MUST be queryable and auditable.

### 4.3 Rollback Procedures

- Rollback to any previous version MUST be possible within 5 minutes.
- Rollback procedures MUST be documented and tested quarterly.

### 4.4 Audit Trail of Deployments

- Every deployment, promotion, rollback, and retirement event MUST generate an immutable audit
  entry including the operator identity, version affected, and reason.

---

## 5. Inference Monitoring

### 5.1 Prediction Volume Tracking

- Predictions per model version per time window MUST be exported to the monitoring system
  (Prometheus/Grafana).

### 5.2 Accuracy and Fairness Drift Detection

- Where ground-truth labels are available, accuracy MUST be tracked over time.
- Fairness metrics (per [FAIRNESS-BIAS-AUDIT.md](FAIRNESS-BIAS-AUDIT.md)) MUST be recomputed
  monthly and on significant traffic spikes.
- Drift beyond configurable thresholds MUST trigger an alert.

### 5.3 Latency and Error Rate Monitoring

- p50, p95, and p99 latency MUST be tracked per model version.
- Error rates (HTTP 5xx, model exceptions) MUST be tracked and alerted on threshold breach.

### 5.4 Automatic Alerting

- Alerts MUST be routed to the on-call ML engineer within 5 minutes of threshold breach.
- Alert suppression is PROHIBITED without explicit incident ticket justification.

---

## 6. Clipper Integration

### 6.1 Role

- Clipper acts as the prediction-serving intermediary layer between clients and model containers.
- All requests to Clipper MUST be authenticated via OIDC (§1.1) or API key (§1.3).

### 6.2 Model Version Caching

- Clipper MAY cache model binaries for performance, but cached copies MUST be verified against
  the CK backend hash before serving.
- Cache TTL MUST not exceed 24 hours.

### 6.3 Request Batching

- Batching configurations MUST be documented.
- Each batch request MUST produce a single audit log entry per input item, not per batch.

### 6.4 Fallback Models

- A fallback model version MUST be configured for each primary model.
- Fallback activation events MUST be logged with the reason (primary failure, timeout, etc.).

### 6.5 Immutable Prediction Logging

- Clipper MUST forward all prediction logs to the immutable audit store within 60 seconds.
- Clipper log schema MUST match the standard inference log schema (§3.1).

---

## References

- NIST SP 800-53 Rev. 5 AC-3 (Access Enforcement)
- NIST SP 800-53 Rev. 5 IA-2 (Identification and Authentication)
- NIST SP 800-53 Rev. 5 AU-2, AU-12 (Audit)
- NIST SP 800-53 Rev. 5 CA-7 (Continuous Monitoring)
- Ray Serve documentation: https://docs.ray.io/en/latest/serve/
- Clipper: http://clipper.ai/
