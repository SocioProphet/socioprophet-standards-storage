# Training Pipeline Security

## Overview

This standard defines security controls for ML training jobs executed via the Ray ecosystem on
Kubernetes. It covers job isolation, distributed training security, code execution controls,
dependency management, GPU security, and output validation.

Requirements use **MUST/SHOULD/MAY** per RFC 2119.

---

## 1. Ray Job Security

### 1.1 Kubernetes Pod Isolation

- Every Ray training job MUST run in an isolated Kubernetes pod (not on the host network).
- Pod security context MUST set:
  - `allowPrivilegeEscalation: false`
  - `readOnlyRootFilesystem: true`
  - `runAsNonRoot: true`
  - `seccompProfile.type: RuntimeDefault`

### 1.2 Resource Limits

- Every pod MUST declare explicit resource requests and limits for CPU, memory, and GPU.
- Unbounded resource requests MUST be rejected by admission control.
- Resource quotas MUST be enforced at the Kubernetes namespace level per team.

### 1.3 Network Policies

- Egress from Ray worker pods MUST be restricted to:
  - The Ray head node (internal cluster communication).
  - Approved data sources (S3, CK backend, Vault).
  - The centralised logging endpoint.
- All other egress MUST be denied by default NetworkPolicy.

### 1.4 Audit Logging

- All Ray job events (submission, start, completion, failure, cancellation) MUST be captured and
  forwarded to the immutable centralised audit store.
- Log entries MUST include: job ID, operator identity, resource consumption, and final status.

---

## 2. Distributed Training with Ray

### 2.1 Ray Core: Driver–Worker TLS

- TLS MUST be enabled between the Ray driver and all worker nodes.
- Certificates MUST be issued by the internal CA and rotated at least every 90 days.
- Mutual TLS (mTLS) SHOULD be used for worker-to-worker communication.

### 2.2 Ray Tune: Hyperparameter Tuning Audit Trail

- Every trial configuration and its results MUST be recorded in the CK backend.
- Trial results MUST be immutable once written; corrections require creating a new trial record.
- The search algorithm and stopping criterion used MUST be logged.

### 2.3 Ray Train: Distributed Training Encryption

- Per-worker encryption keys (AES-256-GCM) MUST be derived from the per-job Vault key.
- Model checkpoints written during training MUST be encrypted before being persisted.
- Checkpoint integrity MUST be verified (SHA-256) before loading in fault-recovery scenarios.

### 2.4 Ray Data: Data Loading Audit

- All Ray Data read operations MUST log the dataset URI, number of rows read, and operator
  identity.
- Data shuffle/partition operations that change data order or composition MUST be logged.

---

## 3. Code Execution Security

### 3.1 Code Review Requirement

- Training scripts MUST be merged via an approved pull request before execution in any
  non-development environment.
- At least one reviewer from outside the authoring team MUST approve the PR.

### 3.2 Prohibited Constructs

- The use of `eval()`, `exec()`, or dynamic code generation in training scripts is PROHIBITED.
- Network requests to arbitrary external URLs from within training jobs are PROHIBITED unless
  the destination is in the approved allowlist and the call is logged.

### 3.3 Secrets Management

- Secrets (credentials, API keys, tokens) MUST be injected into training pods as environment
  variables sourced from Vault via the Vault Agent Injector or equivalent.
- Secrets MUST NOT be hardcoded in training scripts, Dockerfiles, or configuration files.
- Secret values MUST NOT be written to logs or included in provenance records.

### 3.4 Code Signing for ML Scripts

- Production training scripts MUST be signed (GPG or Sigstore cosign) by the merging engineer.
- The runner MUST verify the signature before executing the script.

---

## 4. Dependency Isolation

### 4.1 Pinned Docker Image

- Ray training jobs MUST use a Docker image with all Python dependencies pinned to exact
  versions (e.g. `==2.13.0`), not floating ranges.
- The base image digest (SHA-256) MUST be recorded in the training job provenance record.

### 4.2 Container Image Scanning

- Every training image MUST be scanned with Trivy or Grype before use.
- Images with critical or high CVEs MUST NOT be used in production training runs.
- Scan results MUST be stored alongside the training job provenance record.

### 4.3 Transitive Dependency Scanning

- The full dependency tree (including transitive deps) MUST be scanned.
- The SBOM for the training environment MUST enumerate all transitive dependencies
  (see [MODEL-PROVENANCE.md](MODEL-PROVENANCE.md) §1).

### 4.4 Reproducible Builds

- The same pinned image tag, same code commit, and same hyperparameters SHOULD produce
  numerically identical or statistically equivalent models.
- A reproducibility check SHOULD be run on a sampled subset of training jobs.

---

## 5. GPU Security

### 5.1 GPU Access Control

- GPU access MUST be controlled via Kubernetes resource quotas and RBAC.
- A pod MUST NOT request GPU resources unless the submitting service account has the `gpu-user`
  role.

### 5.2 GPU Memory Isolation

- Each job MUST run in its own GPU context; memory namespace isolation MUST be enforced.
- GPU memory MUST be zeroed between jobs using the device driver's secure-erase capability where
  available.

### 5.3 GPU Firmware Validation

- GPU firmware versions MUST be inventoried and validated against a known-good list during node
  provisioning.
- Firmware update procedures MUST follow the approved change management process.

### 5.4 Audit Logging of GPU Allocation

- GPU allocation and deallocation events MUST be logged, including job ID, device ID, and
  duration.

---

## 6. Training Output Validation

### 6.1 Model Size Sanity Checks

- The output model artifact size MUST fall within an expected range (configurable per model
  family); outliers MUST trigger an alert and block promotion.

### 6.2 Metric Sanity Checks

- Final training accuracy MUST exceed the baseline for the task (configurable).
- Final training loss MUST be below the configured threshold.
- Metrics that fall outside expected bounds MUST cause the job to be flagged for manual review.

### 6.3 Training Time Checks

- Jobs that complete significantly faster than expected (< 50% of typical duration) MUST be
  flagged as suspicious and require manual sign-off before the model is used.

### 6.4 File Integrity Verification

- SHA-256 checksums of all output artifacts MUST be computed immediately after job completion
  and stored in the model provenance record.
- Any subsequent mismatch between stored and computed checksums MUST trigger an incident.

---

## References

- NIST SP 800-53 Rev. 5 CM-7 (Least Functionality)
- NIST SP 800-53 Rev. 5 SC-8, SC-28 (Confidentiality)
- NIST SP 800-53 Rev. 5 SI-2 (Flaw Remediation)
- NIST SP 800-53 Rev. 5 SI-7 (Software Integrity)
- Ray security documentation: https://docs.ray.io/en/latest/ray-security/
