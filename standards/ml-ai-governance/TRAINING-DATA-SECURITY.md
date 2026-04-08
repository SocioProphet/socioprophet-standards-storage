# Training Data Security

## Overview

This standard defines the controls required to protect training datasets throughout their
lifecycle: ingestion, storage, processing, and deletion. All ML/AI workloads MUST comply.

Requirements use **MUST/SHOULD/MAY** per RFC 2119.

---

## 1. Data Encryption

### 1.1 At Rest

- Training datasets stored in S3 MUST use SSE-KMS with AES-256-GCM.
- Training datasets stored in databases MUST use transparent data encryption with AES-256-GCM.
- Encryption keys MUST be managed in the approved Vault KMS mount.
- Key rotation MUST occur at least annually, or immediately on key compromise.

### 1.2 In Transit

- All data movement (ingestion, export, inter-service transfer) MUST use TLS 1.3.
- Certificate validation MUST NOT be disabled in any tooling or pipeline code.
- Internal Ray cluster communication MUST use Ray's TLS configuration (see
  [RAY-ECOSYSTEM-GOVERNANCE.md](RAY-ECOSYSTEM-GOVERNANCE.md)).

### 1.3 Within the Ray Cluster

- A unique AES-256-GCM encryption key MUST be generated per training job.
- The per-job key MUST be provisioned from Vault at job start and revoked at job end.
- Object store data held in Ray's plasma store SHOULD be encrypted where hardware supports it.

### 1.4 Memory Encryption

- Platforms that support hardware memory encryption (AMD SEV, Intel TME) SHOULD enable it for
  Ray worker nodes processing confidential or secret data.

---

## 2. Data Access Control

### 2.1 Role-Based Access Control (RBAC)

- Only authorised data scientists with the `ml-data-read` role MAY access training datasets.
- The `ml-data-read` role MUST be granted on a per-dataset, per-project basis.
- Role assignments MUST be reviewed quarterly and revoked promptly on role change or departure.

### 2.2 Audit Logging

- Every read, write, copy, and delete operation on a training dataset MUST generate an audit
  log entry containing: user identity, dataset URI, operation type, timestamp, source IP.
- Audit logs MUST be forwarded to the immutable centralised audit store within 60 seconds.

### 2.3 Time-Limited Access Tokens

- Programmatic access to training data MUST use short-lived tokens (maximum 1 hour expiry).
- Tokens MUST be issued by Vault with the requesting identity and dataset scope embedded.
- Token issuance and revocation MUST be logged.

### 2.4 Revocation on Role Change

- When a data scientist changes project, role, or leaves the organisation, all their active
  tokens for training datasets MUST be revoked within 1 hour.

---

## 3. PII and Sensitive Data

### 3.1 Data Classification

| Classification | Description                        | Encryption Required | Audit Required |
|----------------|------------------------------------|---------------------|----------------|
| Public         | Openly available data              | No                  | No             |
| Internal       | Internal-use only                  | Recommended         | Yes            |
| Confidential   | Business-sensitive                 | Yes (AES-256-GCM)   | Yes            |
| Secret         | Personally identifiable or regulated | Yes (AES-256-GCM) | Yes (enhanced) |

- Every training dataset MUST be assigned a classification label before first use.
- The label MUST be stored as CK metadata alongside the dataset provenance record.

### 3.2 PII Detection and Redaction

- Before use in training, datasets classified as Confidential or Secret MUST be scanned for PII
  using an approved detection tool.
- Detected PII fields MUST be redacted, pseudonymised, or removed.
- Redaction operations MUST be recorded in the preprocessing audit trail
  (see [MODEL-PROVENANCE.md](MODEL-PROVENANCE.md) §2.2).

### 3.3 Differential Privacy

- Datasets containing residual sensitive data MUST have differential privacy (ε ≤ 8, δ ≤ 10⁻⁵)
  applied during training.
- The ε and δ values used MUST be stored in the model provenance record.

### 3.4 Synthetic Data for Testing

- Testing and experimentation MUST use synthetic data where possible.
- Real production data MUST NOT be used in non-production environments without explicit
  classification review and approval.

---

## 4. Data Retention

### 4.1 Retention Periods

| Classification | Minimum Retention | Maximum Retention |
|----------------|-------------------|-------------------|
| Public         | 90 days           | Unlimited         |
| Internal       | 1 year            | 3 years           |
| Confidential   | 2 years           | 5 years           |
| Secret         | 5 years           | 7 years           |

- Retention periods MUST be enforced via automated S3 lifecycle policies or database TTL.

### 4.2 Secure Deletion

- On expiry, training data MUST be deleted using cryptographic erasure (key deletion) for
  encrypted stores.
- Physical media that cannot be cryptographically erased MUST be securely wiped per NIST SP 800-88.
- Deletion events MUST be recorded in the audit log.

### 4.3 Backup Encryption and Retention

- Backups of training datasets MUST be encrypted with the same classification-appropriate key.
- Backup retention MUST not exceed the retention period of the source dataset.
- Backup integrity MUST be verified quarterly.

---

## 5. Data Lineage

### 5.1 Source Tracking

- Every training job MUST record the full list of source tables, S3 prefixes, or CK dataset URIs.
- Source records MUST include the version or snapshot timestamp of each source.

### 5.2 Transformation Tracking

- All transformations (joins, aggregations, filters, feature engineering) MUST be logged with
  input/output schema hashes and the code version that performed them.

### 5.3 Impact Analysis

- The CK backend MUST support queries of the form: "Which models were trained on dataset X?"
- When a dataset is found to contain errors or bias, the lineage graph MUST be traversable to
  identify all affected model versions.

### 5.4 Audit Trail of Lineage Changes

- Any retrospective correction to the lineage record MUST generate an audit event explaining the
  reason, operator identity, and timestamp.

---

## References

- NIST SP 800-53 Rev. 5 AC-3 (Access Enforcement)
- NIST SP 800-53 Rev. 5 AU-2, AU-12 (Audit)
- NIST SP 800-53 Rev. 5 SC-8, SC-28 (Transmission/Storage Confidentiality)
- NIST SP 800-88 Rev. 1 (Media Sanitisation): https://csrc.nist.gov/publications/detail/sp/800-88
