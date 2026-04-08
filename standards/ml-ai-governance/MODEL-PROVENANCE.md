# Model Provenance & Software Bill of Materials (SBOM)

## Overview

Every model artifact published to the CommonKnowledge (CK) backend MUST carry a complete,
cryptographically signed provenance record. This document specifies the required components,
formats, and signing procedures.

Requirements use **MUST/SHOULD/MAY** per RFC 2119.

---

## 1. Model SBOM

### 1.1 Format

- SBOMs MUST be serialised in CycloneDX JSON (schema version ≥ 1.4).
- Each SBOM MUST be signed with ECDSA-P256 using a key stored in the approved Vault PKI mount.
- The SBOM signature MUST be verified before any model is promoted to staging or production.

### 1.2 Required Fields

| Field                          | Description                                              |
|--------------------------------|----------------------------------------------------------|
| `metadata.component.name`      | Model identifier (e.g. `fraud-detector`)                 |
| `metadata.component.version`   | Semantic version (e.g. `v1.2.0`)                         |
| `metadata.component.hashes`    | SHA-256 of the primary model artifact                    |
| `metadata.timestamp`           | ISO-8601 UTC timestamp of SBOM generation                |
| `components[].type`            | `library` for dependencies, `framework` for ML framework |
| `components[].name`            | Package name (e.g. `tensorflow`, `numpy`)                |
| `components[].version`         | Pinned version string                                    |
| `components[].hashes`          | SHA-256 of the installed wheel/binary                    |
| `components[].purl`            | Package URL (purl) for unambiguous identification        |
| `components[].scope`           | `required` for runtime deps, `optional` for extras       |

### 1.3 Transitive Dependencies

- Transitive (recursive) dependencies MUST be enumerated.
- The SBOM generation tool MUST traverse the full dependency graph.
- A recommended tool is `cyclonedx-bom` (Python) or `cdxgen`.

### 1.4 Signing Procedure

```
1. Generate SBOM JSON file.
2. Compute SHA-256 digest of the file.
3. Sign digest with ECDSA-P256 key (from Vault).
4. Encode signature as Base64 and attach to CK metadata field `sbom_signature`.
5. Store public key fingerprint in CK metadata field `sbom_signing_key_id`.
```

---

## 2. Training Data Provenance

### 2.1 Data Source Record

- The URI of every input dataset MUST be recorded (e.g. `s3://bucket/prefix`, `ck://dataset/v2`).
- The data version or commit hash MUST be recorded at job start time.
- Multiple input sources MUST each carry their own provenance record.

### 2.2 Preprocessing Audit Trail

- Every preprocessing step (filter, join, normalisation, redaction) MUST be logged as an
  immutable event in the centralised audit log.
- Log entries MUST include: step name, input schema hash, output schema hash, operator identity,
  and timestamp.

### 2.3 Data Schema and Statistics

- Input and output schemas MUST be stored as JSON Schema or Avro schema documents.
- Summary statistics (row count, null rates, class distribution) SHOULD be stored in CK metadata.

### 2.4 PII Masking

- Columns classified as PII MUST be masked or redacted before use in training.
- Masking operations MUST be recorded in the preprocessing audit trail.
- Differential privacy parameters (ε, δ) MUST be recorded when applied.

### 2.5 Data Access Audit Logging

- All reads of training datasets MUST be logged: who, what, when, from where.
- Logs MUST be forwarded to the immutable centralised audit store within 60 seconds.

---

## 3. Training Script Provenance

### 3.1 Code Repository Reference

- The GitHub repository URL and commit SHA of the training script MUST be recorded.
- The branch name and PR number that introduced the script SHOULD be recorded.

### 3.2 Code Review Status

- Training scripts MUST receive at least one approved pull-request review before execution.
- The approver identity and approval timestamp MUST be stored in the model provenance record.

### 3.3 Training Parameters

- All hyperparameters and random seeds MUST be recorded.
- Environment variable names used during training MUST be recorded.
- Environment variable **values** that are secrets MUST NOT be stored in provenance records.

### 3.4 Build Artifacts Hash

- The hash (SHA-256) of the Docker image used for training MUST be recorded.
- Reproducible builds: identical inputs SHOULD produce identical image digests.

---

## 4. Model Artifact Record

### 4.1 Artifact Files

- All model weight files, configuration files, and vocabulary/tokeniser files MUST be listed.
- The SHA-256 hash of each file MUST be computed and stored.

### 4.2 Model Signature (Input/Output Specification)

- The model's expected input schema (shape, dtype, range) MUST be documented.
- The model's output schema (classes, score range, output format) MUST be documented.
- This specification MUST be stored in CK metadata as a structured JSON document.

### 4.3 Model Metrics

- Final training metrics (loss, accuracy, precision, recall, F1, AUC) MUST be stored.
- Validation-set metrics MUST be stored separately from training-set metrics.
- Benchmark dataset metrics SHOULD be stored where applicable.

### 4.4 Model Hash and Signature

- The canonical model artifact (primary weight file or archive) MUST be hashed with SHA-256.
- The hash MUST be signed with ECDSA-P256 using the same Vault PKI key used for the SBOM.
- The signature and signing key ID MUST be stored in CK metadata.

---

## 5. Training Job Record

### 5.1 Required Fields

| Field              | Description                                              |
|--------------------|----------------------------------------------------------|
| `ray_job_id`       | Ray cluster job identifier                               |
| `start_time`       | ISO-8601 UTC timestamp                                   |
| `end_time`         | ISO-8601 UTC timestamp                                   |
| `duration_seconds` | Wall-clock duration                                      |
| `gpu_hours`        | Total GPU-hours consumed (0 if CPU-only)                 |
| `peak_ram_gb`      | Peak RAM usage across all workers                        |
| `final_loss`       | Final training loss value                                |
| `final_accuracy`   | Final training accuracy (if classification)              |
| `operator_id`      | Identity of the person who submitted the job             |
| `reason`           | Business justification for initiating training           |

### 5.2 Audit Logging

- The job submission, start, completion, and any failure events MUST be logged to the immutable
  audit store.
- Log entries MUST include operator identity, timestamp, and job ID.

---

## 6. CommonKnowledge (CK) Integration

### 6.1 Registration on Training Completion

- On successful completion of a training job, the model MUST be registered in the CK backend.
- Registration MUST be atomic: if any required provenance field is missing, registration MUST fail
  and the model MUST NOT be promoted.

### 6.2 SBOM Storage

- The CycloneDX SBOM JSON MUST be attached as CK metadata under the key `sbom`.
- The SBOM signature MUST be stored under `sbom_signature`.

### 6.3 Model Versioning via CK

- Each training run MUST produce a new semantic version (vMAJOR.MINOR.PATCH).
- Version bumping rules:
  - PATCH: same architecture, incremental data update.
  - MINOR: architectural change or significant dataset change.
  - MAJOR: breaking change to input/output schema.

### 6.4 Governance Policies and Approval Gates

- CK governance policies MUST require at least one approver from the ML governance team before a
  model is promoted from `staging` to `production`.
- Automated compliance checks (SBOM completeness, signature validity) MUST pass before human
  approval is requested.

### 6.5 Audit Trail of Model Mutations

- Every CK operation on a model (create, update metadata, promote, retire) MUST generate an
  immutable audit event.

---

## References

- CycloneDX specification: https://cyclonedx.org/specification/overview/
- NIST SP 800-53 Rev. 5 SI-7 (Software/Information Integrity)
- NIST SP 800-53 Rev. 5 AU-2, AU-12 (Audit events and generation)
