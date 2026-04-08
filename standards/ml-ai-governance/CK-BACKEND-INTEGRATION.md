# CommonKnowledge (CK) Backend Integration

## Overview

CommonKnowledge (CK) is the authoritative asset repository and governance system for all ML model
artifacts on the SocioProphet platform. This standard defines how ML/AI workloads MUST integrate
with CK for model registration, versioning, governance enforcement, metadata management,
discovery, and backup/recovery.

Requirements use **MUST/SHOULD/MAY** per RFC 2119.

---

## 1. Model Registration in CK

### 1.1 Registration on Training Completion

- On successful completion of a training job, the model artifact MUST be registered in CK before
  any downstream use.
- Registration MUST be performed by the training orchestrator automatically; manual registration
  is PROHIBITED in production.

### 1.2 Required Registration Fields

| CK Metadata Field        | Source                                                    |
|--------------------------|-----------------------------------------------------------|
| `model_name`             | Training job configuration                                |
| `model_version`          | Computed semantic version (vMAJOR.MINOR.PATCH)            |
| `artifact_hash`          | SHA-256 of primary model artifact                         |
| `sbom`                   | CycloneDX JSON (see [MODEL-PROVENANCE.md](MODEL-PROVENANCE.md)) |
| `sbom_signature`         | Base64-encoded ECDSA-P256 signature of the SBOM           |
| `sbom_signing_key_id`    | Vault key identifier used for signing                     |
| `training_job_id`        | Ray job ID                                                |
| `training_code_sha`      | Git commit SHA of training script                         |
| `training_code_pr`       | PR number of the approved training code                   |
| `training_timestamp`     | ISO-8601 UTC timestamp of job completion                  |
| `metrics`                | JSON object with final accuracy, loss, and other metrics  |
| `data_sources`           | Array of dataset URIs with version identifiers            |

### 1.3 Registration Atomicity

- Registration MUST be atomic: if any required field is missing or any compliance check fails,
  the registration MUST be rolled back and the model MUST NOT be promoted.

### 1.4 Immutable Artifact Storage

- The model artifact MUST be stored in content-addressable, immutable storage within CK.
- After registration, the artifact content MUST NOT be modifiable; a content change requires
  registering a new version.

---

## 2. CK Versioning

### 2.1 Content-Addressable Storage

- Each model version MUST be stored with its SHA-256 hash as the content address.
- Retrieving a version by its content address MUST always return the same bytes.

### 2.2 Semantic Version Tags

- Versions MUST be tagged using semantic versioning (vMAJOR.MINOR.PATCH).
- Convenience tags (`staging`, `production`, `main`) MUST be mutable pointers to a versioned
  artifact.
- Tag mutations MUST generate an audit log entry.

### 2.3 Branch Support

- Experimental model development MAY use feature branches (e.g. `feature/new-architecture`).
- Branch artifacts MUST NOT be deployed to production until merged and re-registered on `main`.

### 2.4 Merge Conflicts

- When two branches produce models with conflicting version numbers, the later-registering
  branch MUST increment its version to avoid a collision.
- Conflict resolution MUST be recorded in the audit trail.

### 2.5 Audit Trail of Version Operations

- Create, tag, promote, demote, deprecate, and delete operations on versions MUST each generate
  an immutable audit event.

---

## 3. CK Governance

### 3.1 Approval Gates

- Promotion from `staging` to `production` MUST require:
  1. All automated compliance checks passing (§1 of [MODEL-VALIDATION.md](MODEL-VALIDATION.md)).
  2. At least one human approval from the ML governance team.
- The approver identity, timestamp, and decision rationale MUST be stored in CK.

### 3.2 Retention Policies

- CK retention policies MUST align with the data classification of the training data used:

  | Training Data Classification | Model Retention |
  |------------------------------|-----------------|
  | Public / Internal            | 2 years         |
  | Confidential                 | 5 years         |
  | Secret                       | 7 years         |

- Retention policies MUST be enforced automatically; manual deletion requires an approved change
  request.

### 3.3 Deletion Policies

- Expired model versions MUST be archived (metadata preserved, artifact purged) unless legal
  hold applies.
- Artifacts under legal hold MUST NOT be purged regardless of retention period.
- Deletion events MUST be logged with the reason (expiry, legal, exception).

### 3.4 Encryption Policies

- All model artifacts at rest in CK MUST be encrypted with AES-256-GCM.
- Encryption keys MUST be managed in Vault and rotated at least annually.

### 3.5 Access Control Policies

- Read access to model artifacts MUST require at minimum the `ml-model-read` role.
- Write/register access MUST require the `ml-model-write` role.
- Delete access MUST require the `ml-model-admin` role AND a second approver.
- Role assignments MUST be reviewed quarterly.

---

## 4. CK Metadata

### 4.1 SBOM Storage

- The CycloneDX SBOM JSON MUST be stored in the CK metadata field `sbom`.
- The SBOM signature MUST be stored in `sbom_signature`.
- Both fields MUST be populated at registration time and MUST NOT be mutated thereafter.

### 4.2 Training Parameters Storage

- Hyperparameters, random seeds, and the training configuration schema MUST be stored in the
  `training_params` metadata field as a structured JSON document.

### 4.3 Metrics Storage

- Final and epoch-level metrics (accuracy, precision, recall, F1, AUC, loss) MUST be stored in
  the `metrics` metadata field.
- Metrics MUST NOT be overwritten after registration; corrections require a new version.

### 4.4 Data Lineage Storage

- The data lineage record (source datasets, transformation steps, preprocessing audit) MUST be
  stored in the `data_lineage` metadata field.
- Format MUST conform to the lineage schema defined in [TRAINING-DATA-SECURITY.md](TRAINING-DATA-SECURITY.md).

### 4.5 CK Audit Log

- All CK operations (reads, writes, promotions, deletions, metadata updates) MUST be appended
  to the CK audit log.
- The audit log MUST be stored in immutable, append-only storage.

---

## 5. CK-to-Ray Serve Integration

### 5.1 Version-Pinned Deployment

- Ray Serve deployment configurations MUST reference a specific CK model version
  (e.g. `ck://models/fraud-detector@v1.2.0`).
- Floating references (e.g. `@production`) MUST NOT be used in deployment configurations;
  they may be used only in canary automation that resolves the reference at deploy time and
  records the resolved version.

### 5.2 Artifact Hash Verification

- After fetching a model from CK, Ray Serve MUST verify the SHA-256 hash against the registered
  `artifact_hash` before loading.

### 5.3 Cache Invalidation

- When a new version is promoted to `production` in CK, all serving replicas using the previous
  `production` version MUST receive an invalidation signal and re-fetch within 5 minutes.

### 5.4 Fallback on Failure

- A fallback version MUST be declared for each deployment.
- If the primary version fails integrity verification or loading, the fallback MUST be activated
  automatically and an alert sent to the on-call team.
- Fallback activations MUST be logged as audit events.

### 5.5 Model Fetch Audit Logging

- Every model fetch from CK by Ray Serve MUST generate an audit log entry: serving node,
  model name, version, timestamp, and success/failure status.

---

## 6. CK Query and Discovery

### 6.1 SPARQL Queries over Model Metadata

- The CK backend MUST expose a SPARQL endpoint for querying model metadata.
- All SPARQL queries MUST be authenticated and logged.

### 6.2 Example Queries

```sparql
# All models trained on a specific dataset
SELECT ?model ?version WHERE {
  ?model ck:trainedOn <ck://datasets/transactions-v3> ;
         ck:version ?version .
}

# Models with accuracy above 95%
SELECT ?model ?version ?accuracy WHERE {
  ?model ck:accuracy ?accuracy ;
         ck:version ?version .
  FILTER (?accuracy > 0.95)
}

# All models depending on a specific library version
SELECT ?model ?version WHERE {
  ?model ck:hasDependency ?dep .
  ?dep purl:name "numpy" ;
       purl:version "1.24.3" .
  ?model ck:version ?version .
}
```

### 6.3 Automated Evidence Generation

- CK queries MUST be usable as automated evidence sources for compliance audits.
- Query results MUST include the execution timestamp and the authenticated principal.

---

## 7. CK Backup and Recovery

### 7.1 Backup Encryption

- All CK backups MUST be encrypted with AES-256-GCM using a backup-specific key stored in Vault.
- The backup key MUST be different from the primary data encryption key.

### 7.2 Off-Site Storage

- Backups MUST be stored in at least two geographically distinct locations.
- Replication lag MUST NOT exceed 5 minutes (RPO ≤ 5 minutes).

### 7.3 Recovery Testing

- Full restore procedures MUST be tested at least quarterly.
- Test results (duration, data integrity check outcome) MUST be recorded and retained for 2 years.
- Recovery Time Objective (RTO): full system available within 1 hour.

### 7.4 Backup Audit Trail

- Backup creation, validation, and deletion events MUST generate audit log entries.

---

## References

- NIST SP 800-53 Rev. 5 CP-9 (Information System Backup)
- NIST SP 800-53 Rev. 5 SI-7 (Software Integrity)
- NIST SP 800-53 Rev. 5 AC-3, AC-6 (Access Control)
- CycloneDX: https://cyclonedx.org/
- SPARQL 1.1: https://www.w3.org/TR/sparql11-query/
