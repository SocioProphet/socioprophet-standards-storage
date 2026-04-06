# Backup and Recovery Standards

This document uses RFC 2119 language: **MUST**, **SHOULD**, **MAY**.

## 1. Scope

This standard defines backup encryption, storage, recovery testing, and retention requirements
for all data-layer systems, satisfying NIST SP 800-53 CP-9 and CP-10.

## 2. Backup Encryption

- All backups MUST be encrypted with **AES-256-GCM** before leaving the originating host.
- Backup encryption keys (BEKs) MUST be separate from operational DEKs.
- BEKs MUST be stored in the secrets manager under a dedicated backup-key namespace.
- BEK rotation MUST occur on the same 90-day cycle as operational DEKs
  (see [ENCRYPTION-AT-REST.md](ENCRYPTION-AT-REST.md)).
- Key escrow for BEKs MUST support out-of-band (disaster) recovery:
  a printed/air-gapped copy of the escrow key MUST exist in a physically secure location.

## 3. Backup Storage

- Backup destinations MUST be geographically diverse (minimum two data centres or cloud
  regions, at least 100 km apart).
- Backup data MUST be encrypted in transit to the backup destination (TLS 1.3).
- Backup storage MUST use WORM (Write-Once-Read-Many) semantics where the target supports it
  (e.g., MinIO object lock, S3 Object Lock, immutable GCS buckets).
- Access to backup storage MUST be restricted to the backup service account; no human direct
  access without MFA and dual-person authorization.

## 4. Per-System Backup Procedures

| System | Recommended Method | Notes |
|---|---|---|
| PostgreSQL | `pg_basebackup` + WAL archiving | Encrypt stream with `gpg --symmetric --cipher-algo AES256` |
| MongoDB | `mongodump` (BSON + oplog) | Use `--ssl`; encrypt output archive |
| Elasticsearch | Snapshot API to encrypted MinIO repository | Use encrypted snapshot repository |
| Redis | BGSAVE (RDB) + AOF | Store on encrypted volume; copy off-host immediately |
| RocksDB | Application-managed checkpoint | Checkpoint directory on encrypted volume |
| MinIO | MinIO `mc mirror` to secondary MinIO | Both endpoints must have TLS enabled |

## 5. Recovery Testing

- A **full recovery drill** MUST be conducted **quarterly** for each Confidential/Secret system.
- Each drill MUST validate:
  - Recovery Point Objective (RPO): data loss does not exceed the documented threshold.
  - Recovery Time Objective (RTO): system is operational within the documented window.
- Recovery procedures MUST be documented in a runbook accessible without access to the
  production system (stored in an external doc store).
- Recovery drill results MUST be recorded in the audit log and reviewed by the Security Officer.

## 6. Backup Audit Logging

- Every backup operation MUST generate an audit record containing:
  - Who (service account identifier)
  - What (system, database, or bucket name)
  - When (RFC 3339 UTC timestamp)
  - Where (destination storage location)
  - Size and checksum of the backup artifact
- Every restore operation MUST generate an audit record with the same fields, plus the
  initiating operator (human or automated pipeline) and justification.
- Backup audit records MUST be stored in the same immutable audit store as operational logs
  (see [AUDIT-LOGGING.md](AUDIT-LOGGING.md)).

## 7. Retention Schedule

| Tier | Frequency | Retention |
|---|---|---|
| Daily | Every 24 hours | 7 days |
| Weekly | Every 7 days | 4 weeks |
| Monthly | First day of each month | 12 months |
| Annual (compliance) | First day of each year | 7 years |

Compliance backups (annual tier) MUST be kept for **7 years** regardless of operational
data deletion.

## 8. Failure Handling

- Failed backup jobs MUST alert on-call within 15 minutes.
- Three consecutive backup failures MUST escalate to the Security Officer.
- Missing backups beyond the scheduled window MUST be treated as a potential security incident
  and investigated.
