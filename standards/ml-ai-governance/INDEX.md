# ML/AI Governance Standards Index

## Overview

Machine Learning and AI systems introduce unique compliance challenges around model provenance,
training data security, inference endpoint authentication, and supply chain integrity. This index
defines the governance framework that all ML/AI workloads running within the SocioProphet platform
MUST satisfy to achieve and maintain FIPS 140-2/140-3 alignment.

Requirements use **MUST/SHOULD/MAY** per RFC 2119.

---

## 1. Role of ML/AI in FIPS Compliance

ML/AI pipelines process sensitive data, produce artifacts that influence decisions, and expose
network-accessible inference endpoints. Each stage introduces cryptographic, access-control, and
auditability obligations that map directly to NIST SP 800-53 Rev. 5 controls.

Key obligations:

- Cryptographic operations (model signing, data encryption) MUST use FIPS-approved algorithms.
- All data in transit MUST be protected with TLS 1.3 (SC-8).
- All data at rest MUST be encrypted with AES-256-GCM (SC-28).
- Audit events MUST be generated for every training job, serving request, and data access (AU-2, AU-12).
- Supply-chain artifacts (SBOMs) MUST be produced and signed for every model version (SI-7).

---

## 2. Ray Ecosystem as Standard ML Platform

The Ray ecosystem is the designated distributed ML platform across all SocioProphet environments.

| Component    | Role                          | Governance Document                              |
|--------------|-------------------------------|--------------------------------------------------|
| Ray Core     | Distributed task scheduling   | [RAY-ECOSYSTEM-GOVERNANCE.md](RAY-ECOSYSTEM-GOVERNANCE.md) |
| Ray Serve    | Online model serving          | [MODEL-SERVING-SECURITY.md](MODEL-SERVING-SECURITY.md) |
| Ray Tune     | Hyperparameter optimisation   | [RAY-ECOSYSTEM-GOVERNANCE.md](RAY-ECOSYSTEM-GOVERNANCE.md) |
| Ray Train    | Distributed model training    | [TRAINING-PIPELINE-SECURITY.md](TRAINING-PIPELINE-SECURITY.md) |
| Ray Data     | Scalable data ingestion       | [TRAINING-DATA-SECURITY.md](TRAINING-DATA-SECURITY.md) |
| Ray Workflows| ML workflow orchestration     | [RAY-ECOSYSTEM-GOVERNANCE.md](RAY-ECOSYSTEM-GOVERNANCE.md) |

---

## 3. CommonKnowledge (CK) as Asset Backend

CommonKnowledge (CK) is the authoritative asset repository for all ML model artifacts. It provides
content-addressable storage, semantic versioning, governance approval gates, and SPARQL-queryable
metadata. See [CK-BACKEND-INTEGRATION.md](CK-BACKEND-INTEGRATION.md) for the full specification.

---

## 4. Model Lifecycle

```
Training → Validation → Serving → Retirement
    ↓            ↓          ↓           ↓
  SBOM       Test Suite  Endpoint   Secure
  + Sign     + Audit     Auth +     Deletion
             + Approve   Logging
```

Each phase transition MUST be recorded in the CK audit trail and MUST satisfy the relevant
sub-standards listed in this index.

| Phase       | Primary Standard                                          |
|-------------|-----------------------------------------------------------|
| Training    | [TRAINING-PIPELINE-SECURITY.md](TRAINING-PIPELINE-SECURITY.md) |
| Validation  | [MODEL-VALIDATION.md](MODEL-VALIDATION.md)               |
| Serving     | [MODEL-SERVING-SECURITY.md](MODEL-SERVING-SECURITY.md)   |
| Retirement  | [TRAINING-DATA-SECURITY.md](TRAINING-DATA-SECURITY.md) §Data Retention |

---

## 5. Training Data Security

Training datasets are classified, encrypted, and access-controlled per
[TRAINING-DATA-SECURITY.md](TRAINING-DATA-SECURITY.md). Key requirements:

- Data at rest: AES-256-GCM (S3, database).
- Data in transit: TLS 1.3.
- PII: detected, redacted, and subject to differential privacy where applicable.
- Access: RBAC with time-limited tokens (≤ 1 hour) and full audit logging.

---

## 6. Model Versioning and Provenance

Every model artifact MUST carry a signed SBOM in CycloneDX JSON format. Provenance covers:

- Training framework and all transitive dependencies.
- Training data source, version, and preprocessing audit trail.
- Training script Git commit SHA and PR approval status.
- Model metrics and SHA-256 hash of the artifact.
- ECDSA-P256 signature over the artifact.

Full specification: [MODEL-PROVENANCE.md](MODEL-PROVENANCE.md).

---

## 7. Inference Endpoint Security

All inference endpoints MUST require OIDC authentication. Service-to-service calls MUST use mTLS.
Every prediction MUST be logged to an immutable WORM store with a minimum 90-day retention period.

Full specification: [MODEL-SERVING-SECURITY.md](MODEL-SERVING-SECURITY.md).

---

## 8. Supply Chain Integrity (Model SBOM)

A Software Bill of Materials (SBOM) in CycloneDX format MUST be generated for:

- The training environment (base image + Python dependencies).
- The model artifact (framework + weights + config).

SBOMs MUST be signed with ECDSA-P256 and stored in the CK backend alongside the model artifact.

---

## 9. Fairness and Bias

Models that influence decisions about individuals MUST undergo a fairness audit before deployment.
Bias mitigation strategies MUST be documented. Fairness metrics MUST be monitored post-deployment
with drift detection and quarterly re-auditing.

Full specification: [FAIRNESS-BIAS-AUDIT.md](FAIRNESS-BIAS-AUDIT.md).

---

## 10. Integration Checklist

A per-system compliance checklist covering all lifecycle phases is maintained at
[ML-AI-INTEGRATION-CHECKLIST.md](ML-AI-INTEGRATION-CHECKLIST.md).

---

## NIST 800-53 Control Alignment

| Control | Title                        | ML/AI Scope                                         |
|---------|------------------------------|-----------------------------------------------------|
| AC-2    | Account Management           | Data scientist accounts, model-serving service accounts |
| AC-3    | Access Enforcement           | Training data RBAC, model artifact access, inference auth |
| AU-2    | Audit Events                 | Training jobs, data access, serving requests        |
| AU-12   | Audit Generation             | Immutable inference logs, training event logs       |
| CA-7    | Continuous Monitoring        | Fairness drift, accuracy drift, anomaly detection   |
| IA-2    | Identification/Authentication| OIDC endpoints, API keys from Vault                 |
| SC-8    | Transmission Confidentiality | TLS 1.3 for all data movement, Ray TLS              |
| SC-12   | Cryptographic Key Management | AES-256-GCM keys, ECDSA-P256 signing keys           |
| SI-2    | Flaw Remediation             | Dependency scanning, base image patching            |
| SI-7    | Software Integrity           | SBOM, model artifact signing, reproducible builds   |

---

## ML/AI System Integration Status

| System     | Training Data Security | Model Provenance | Inference Audit | CK Integration | Status      |
|------------|------------------------|------------------|-----------------|----------------|-------------|
| Ray Core   | ✅ Planned             | ✅ Planned       | ✅ Planned      | ✅ Planned     | 📋 Q3 2026 |
| Ray Serve  | ✅ Planned             | ✅ Planned       | ✅ Planned      | ✅ Planned     | 📋 Q3 2026 |
| Ray Tune   | ✅ Planned             | ✅ Planned       | N/A             | ✅ Planned     | 📋 Q3 2026 |
| Ray Train  | ✅ Planned             | ✅ Planned       | N/A             | ✅ Planned     | 📋 Q3 2026 |
| TensorFlow | ✅ Planned             | ✅ Planned       | ✅ Planned      | ✅ Planned     | 📋 Q3 2026 |
| PyTorch    | ✅ Planned             | ✅ Planned       | ✅ Planned      | ✅ Planned     | 📋 Q3 2026 |
| Clipper    | N/A                    | ✅ Planned       | ✅ Planned      | ✅ Planned     | 📋 Q3 2026 |
| CK Backend | ✅ Planned             | ✅ Core          | ✅ Core         | ✅ Core        | 📋 Q3 2026 |

---

## References

- NIST SP 800-53 Rev. 5: https://csrc.nist.gov/publications/detail/sp/800-53/rev-5
- NIST SP 800-88: https://csrc.nist.gov/publications/detail/sp/800-88
- Ray: https://www.ray.io/
- CycloneDX (SBOM): https://cyclonedx.org/
- Kubeflow: https://www.kubeflow.org/
- TensorFlow: https://www.tensorflow.org/
- PyTorch: https://pytorch.org/
- Clipper: http://clipper.ai/
