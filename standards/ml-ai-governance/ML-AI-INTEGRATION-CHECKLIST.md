# ML/AI Integration Checklist

## Overview

This checklist MUST be completed for each new ML/AI system or major model version before it is
promoted to production. Each item links to the governing standard. All items marked **MUST** are
blocking; items marked **SHOULD** are advisory and require documented justification if skipped.

---

## 1. Training Pipeline

| # | Control | Requirement | Standard Reference | Status |
|---|---------|-------------|-------------------|--------|
| 1.1 | Data encrypted at rest | AES-256-GCM in S3 or database | [TRAINING-DATA-SECURITY.md §1.1](TRAINING-DATA-SECURITY.md) | [ ] |
| 1.2 | Data encrypted in transit | TLS 1.3 for all data movement | [TRAINING-DATA-SECURITY.md §1.2](TRAINING-DATA-SECURITY.md) | [ ] |
| 1.3 | Training code reviewed | PR approval with ≥ 1 reviewer outside authoring team | [TRAINING-PIPELINE-SECURITY.md §3.1](TRAINING-PIPELINE-SECURITY.md) | [ ] |
| 1.4 | Ray job runs in Kubernetes pod | Pod security context: no privilege, read-only root | [TRAINING-PIPELINE-SECURITY.md §1.1](TRAINING-PIPELINE-SECURITY.md) | [ ] |
| 1.5 | SBOM generated | CycloneDX JSON covering all transitive deps | [MODEL-PROVENANCE.md §1](MODEL-PROVENANCE.md) | [ ] |
| 1.6 | SBOM signed | ECDSA-P256 signature via Vault | [MODEL-PROVENANCE.md §1.4](MODEL-PROVENANCE.md) | [ ] |
| 1.7 | Audit logging of training events | Submission, start, completion, failure → immutable store | [TRAINING-PIPELINE-SECURITY.md §1.4](TRAINING-PIPELINE-SECURITY.md) | [ ] |
| 1.8 | Dependency vulnerability scan | No critical/high CVEs in runtime deps | [TRAINING-PIPELINE-SECURITY.md §4.2](TRAINING-PIPELINE-SECURITY.md) | [ ] |
| 1.9 | Model artifact signed | ECDSA-P256 over SHA-256 of artifact | [MODEL-PROVENANCE.md §4.4](MODEL-PROVENANCE.md) | [ ] |
| 1.10 | Training output validated | Size, metric, time, and integrity sanity checks pass | [TRAINING-PIPELINE-SECURITY.md §6](TRAINING-PIPELINE-SECURITY.md) | [ ] |

---

## 2. Model Serving (Ray Serve + Clipper)

| # | Control | Requirement | Standard Reference | Status |
|---|---------|-------------|-------------------|--------|
| 2.1 | Endpoints require OIDC auth | All inference endpoints enforce OIDC token validation | [MODEL-SERVING-SECURITY.md §1.1](MODEL-SERVING-SECURITY.md) | [ ] |
| 2.2 | mTLS for service-to-service | Internal calls use mTLS with rotated certs | [MODEL-SERVING-SECURITY.md §1.4](MODEL-SERVING-SECURITY.md) | [ ] |
| 2.3 | Models fetched from CK backend | Version-pinned; artifact hash verified after fetch | [MODEL-SERVING-SECURITY.md §2.1](MODEL-SERVING-SECURITY.md) | [ ] |
| 2.4 | Inference requests logged | Input hash, output, latency, identity → immutable store | [MODEL-SERVING-SECURITY.md §3](MODEL-SERVING-SECURITY.md) | [ ] |
| 2.5 | 90-day inference log retention | WORM storage with minimum 90-day retention | [MODEL-SERVING-SECURITY.md §3.2](MODEL-SERVING-SECURITY.md) | [ ] |
| 2.6 | Model versions immutable | No in-place updates; version bump required | [MODEL-SERVING-SECURITY.md §4.1](MODEL-SERVING-SECURITY.md) | [ ] |
| 2.7 | Canary deployments | New versions start at ≤ 10% traffic | [MODEL-SERVING-SECURITY.md §2.2](MODEL-SERVING-SECURITY.md) | [ ] |
| 2.8 | Automatic rollback configured | Error/latency threshold triggers rollback within 60 s | [MODEL-SERVING-SECURITY.md §2.4](MODEL-SERVING-SECURITY.md) | [ ] |
| 2.9 | Fairness metrics monitored | Monthly recomputation with drift alerting | [FAIRNESS-BIAS-AUDIT.md §5.1](FAIRNESS-BIAS-AUDIT.md) | [ ] |
| 2.10 | A/B test audit trail | Traffic split config and results stored in CK | [MODEL-SERVING-SECURITY.md §2.3](MODEL-SERVING-SECURITY.md) | [ ] |

---

## 3. Model Validation

| # | Control | Requirement | Standard Reference | Status |
|---|---------|-------------|-------------------|--------|
| 3.1 | Functional tests pass | Unit + integration + performance tests green | [MODEL-VALIDATION.md §1](MODEL-VALIDATION.md) | [ ] |
| 3.2 | Regression tests pass | No regression vs. current deployed version | [MODEL-VALIDATION.md §1.4](MODEL-VALIDATION.md) | [ ] |
| 3.3 | Safety tests pass | Adversarial examples, edge cases, OOD | [MODEL-VALIDATION.md §2](MODEL-VALIDATION.md) | [ ] |
| 3.4 | Security tests pass | Extraction hardening, data poisoning checks | [MODEL-VALIDATION.md §3](MODEL-VALIDATION.md) | [ ] |
| 3.5 | Fairness audit completed | All fairness metrics computed and pass thresholds | [FAIRNESS-BIAS-AUDIT.md §1–2](FAIRNESS-BIAS-AUDIT.md) | [ ] |
| 3.6 | Model card created | Stored in CK with bias analysis and limitations | [FAIRNESS-BIAS-AUDIT.md §3.4](FAIRNESS-BIAS-AUDIT.md) | [ ] |
| 3.7 | Compliance checks automated | SBOM completeness, dependency scan, signature verify | [MODEL-VALIDATION.md §4](MODEL-VALIDATION.md) | [ ] |
| 3.8 | Human approval obtained | ML governance team sign-off recorded in CK | [MODEL-VALIDATION.md §5.2](MODEL-VALIDATION.md) | [ ] |

---

## 4. CommonKnowledge (CK) Integration

| # | Control | Requirement | Standard Reference | Status |
|---|---------|-------------|-------------------|--------|
| 4.1 | Model registered in CK | Registration on training completion; atomic | [CK-BACKEND-INTEGRATION.md §1](CK-BACKEND-INTEGRATION.md) | [ ] |
| 4.2 | SBOM attached as metadata | `sbom` and `sbom_signature` fields populated | [CK-BACKEND-INTEGRATION.md §4.1](CK-BACKEND-INTEGRATION.md) | [ ] |
| 4.3 | Governance policies enforced | Approval gate passed before production promotion | [CK-BACKEND-INTEGRATION.md §3.1](CK-BACKEND-INTEGRATION.md) | [ ] |
| 4.4 | Semantic version assigned | vMAJOR.MINOR.PATCH tag on CK artifact | [CK-BACKEND-INTEGRATION.md §2.2](CK-BACKEND-INTEGRATION.md) | [ ] |
| 4.5 | Immutable artifact storage | Content-addressable, post-registration writes blocked | [CK-BACKEND-INTEGRATION.md §1.4](CK-BACKEND-INTEGRATION.md) | [ ] |
| 4.6 | Access control policies applied | `ml-model-read/write/admin` roles enforced | [CK-BACKEND-INTEGRATION.md §3.5](CK-BACKEND-INTEGRATION.md) | [ ] |
| 4.7 | Backup and recovery tested | Quarterly restore test completed with results recorded | [CK-BACKEND-INTEGRATION.md §7.3](CK-BACKEND-INTEGRATION.md) | [ ] |
| 4.8 | Metadata queryable | SPARQL endpoint available and access-logged | [CK-BACKEND-INTEGRATION.md §6.1](CK-BACKEND-INTEGRATION.md) | [ ] |

---

## 5. Ray Ecosystem

| # | Control | Requirement | Standard Reference | Status |
|---|---------|-------------|-------------------|--------|
| 5.1 | Ray Core TLS configured | Driver–worker TLS enabled with internal-CA certs | [RAY-ECOSYSTEM-GOVERNANCE.md §1](RAY-ECOSYSTEM-GOVERNANCE.md) | [ ] |
| 5.2 | Ray dashboard auth configured | Dashboard accessible only via authenticated proxy | [RAY-ECOSYSTEM-GOVERNANCE.md §1.1](RAY-ECOSYSTEM-GOVERNANCE.md) | [ ] |
| 5.3 | Ray Serve traffic splitting | A/B and canary configs validated and audit-logged | [RAY-ECOSYSTEM-GOVERNANCE.md §2.4](RAY-ECOSYSTEM-GOVERNANCE.md) | [ ] |
| 5.4 | Ray Tune results immutable | Trial records written to CK; no post-hoc edits | [RAY-ECOSYSTEM-GOVERNANCE.md §3.2](RAY-ECOSYSTEM-GOVERNANCE.md) | [ ] |
| 5.5 | Ray Train checkpoints encrypted | Checkpoints encrypted; hash stored in provenance | [RAY-ECOSYSTEM-GOVERNANCE.md §4.2](RAY-ECOSYSTEM-GOVERNANCE.md) | [ ] |
| 5.6 | Ray Data lineage tracked | Source → transform → output lineage in CK | [RAY-ECOSYSTEM-GOVERNANCE.md §5.2](RAY-ECOSYSTEM-GOVERNANCE.md) | [ ] |
| 5.7 | Ray Workflows logged | All step events in audit log | [RAY-ECOSYSTEM-GOVERNANCE.md §6.3](RAY-ECOSYSTEM-GOVERNANCE.md) | [ ] |
| 5.8 | Per-worker encryption (AES-256-GCM) | Per-job key from Vault; revoked at job end | [TRAINING-PIPELINE-SECURITY.md §2.3](TRAINING-PIPELINE-SECURITY.md) | [ ] |
| 5.9 | Fault tolerance verified | Worker recovery tested; recovery events logged | [RAY-ECOSYSTEM-GOVERNANCE.md §4.3](RAY-ECOSYSTEM-GOVERNANCE.md) | [ ] |

---

## 6. Inference Monitoring

| # | Control | Requirement | Standard Reference | Status |
|---|---------|-------------|-------------------|--------|
| 6.1 | Prediction latency tracked | p50/p95/p99 exported to Prometheus | [MODEL-SERVING-SECURITY.md §5.3](MODEL-SERVING-SECURITY.md) | [ ] |
| 6.2 | Accuracy/fairness drift detected | Monthly recomputation with ≥ 0.05 drift alerting | [FAIRNESS-BIAS-AUDIT.md §5.2](FAIRNESS-BIAS-AUDIT.md) | [ ] |
| 6.3 | Error rate monitored | HTTP 5xx and model exceptions tracked | [MODEL-SERVING-SECURITY.md §5.3](MODEL-SERVING-SECURITY.md) | [ ] |
| 6.4 | Anomaly alerts configured | Threshold breaches routed to on-call within 5 min | [MODEL-SERVING-SECURITY.md §5.4](MODEL-SERVING-SECURITY.md) | [ ] |
| 6.5 | Audit logs immutable | WORM storage; hash-chained log entries | [MODEL-SERVING-SECURITY.md §3.2](MODEL-SERVING-SECURITY.md) | [ ] |
| 6.6 | Retention policies enforced | 90-day minimum; automated lifecycle rules | [MODEL-SERVING-SECURITY.md §3.2](MODEL-SERVING-SECURITY.md) | [ ] |
| 6.7 | Rollback procedures documented | Documented and tested ≤ 5-minute rollback | [MODEL-SERVING-SECURITY.md §4.3](MODEL-SERVING-SECURITY.md) | [ ] |
| 6.8 | Recovery procedures tested | Quarterly recovery drill results recorded | [CK-BACKEND-INTEGRATION.md §7.3](CK-BACKEND-INTEGRATION.md) | [ ] |

---

## Checklist Completion Process

1. The responsible data scientist fills in each status cell (`[x]` for pass, `[~]` for approved
   exception with ticket reference, `[-]` for not applicable with justification).
2. The completed checklist MUST be submitted as a CK metadata document attached to the model
   version under the key `integration_checklist`.
3. The automated compliance pipeline validates that all blocking items (`MUST`) are either
   checked or carry an approved exception.
4. The ML governance approver reviews the checklist as part of the deployment approval (§5.2 of
   [MODEL-VALIDATION.md](MODEL-VALIDATION.md)).
5. The approved checklist becomes an immutable artifact in the CK audit trail.

---

## References

- [INDEX.md](INDEX.md) — ML/AI Governance Standards Index
- [MODEL-PROVENANCE.md](MODEL-PROVENANCE.md) — Model SBOM & Provenance
- [TRAINING-DATA-SECURITY.md](TRAINING-DATA-SECURITY.md) — Training Data Security
- [TRAINING-PIPELINE-SECURITY.md](TRAINING-PIPELINE-SECURITY.md) — Training Pipeline Security
- [MODEL-SERVING-SECURITY.md](MODEL-SERVING-SECURITY.md) — Model Serving Security
- [MODEL-VALIDATION.md](MODEL-VALIDATION.md) — Model Validation & Testing
- [RAY-ECOSYSTEM-GOVERNANCE.md](RAY-ECOSYSTEM-GOVERNANCE.md) — Ray Ecosystem Governance
- [CK-BACKEND-INTEGRATION.md](CK-BACKEND-INTEGRATION.md) — CK Backend Integration
- [FAIRNESS-BIAS-AUDIT.md](FAIRNESS-BIAS-AUDIT.md) — Fairness & Bias Audit
