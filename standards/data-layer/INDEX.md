# Data Layer Standards — Master Index

This document uses RFC 2119 language: **MUST**, **SHOULD**, **MAY**.

## 1. Overview

The data layer encompasses every persistent and in-memory storage system used by the SocioProphet
platform.  All systems in this layer are subject to FIPS 140-2/140-3 cryptographic requirements,
NIST SP 800-53 Rev. 5 controls, and the platform-wide audit and access-control policies.

## 2. System Catalogue

| System | Type | Role |
|---|---|---|
| PostgreSQL | Relational | Configuration DB, structured records |
| MongoDB | NoSQL document store | Audit logs, flexible schemas |
| Elasticsearch | Search & analytics | Full-text search, immutable audit index |
| Redis | In-memory cache | Session store, ephemeral cache |
| RocksDB | Embedded key-value | Local node caching |
| MinIO | S3-compatible object storage | Artifacts, backups, static assets |

## 3. Encryption Requirements

| System | At Rest | In Transit |
|---|---|---|
| PostgreSQL | AES-256-GCM via pgcrypto | TLS 1.3 (require SSL) |
| MongoDB | AES-256-GCM (native) | TLS 1.3 (+ mTLS for replication) |
| Elasticsearch | AES-256-GCM (X-Pack) | TLS 1.3 (+ TLS inter-node) |
| Redis | AES-256-GCM (Redis Enterprise) | TLS 1.3 (Redis 6.0+) |
| RocksDB | AES-256-GCM (OpenSSL integration) | N/A — local only |
| MinIO | AES-256-GCM (native or HSM) | TLS 1.3 |

All key material MUST be derived with HKDF-SHA256 and rotated on a 90-day cycle.
See [ENCRYPTION-AT-REST.md](ENCRYPTION-AT-REST.md) and
[ENCRYPTION-IN-TRANSIT.md](ENCRYPTION-IN-TRANSIT.md).

## 4. Audit Trail Requirements

| System | Mechanism | Required Events |
|---|---|---|
| PostgreSQL | pgaudit extension | DML, DDL, SECURITY events |
| MongoDB | Native audit logging | All DB ops, auth, config changes |
| Elasticsearch | X-Pack audit logs | Index access, config, authentication |
| Redis | ACL logging / MONITOR | Auth, dangerous commands |
| MinIO | S3 access logs | All operations with requestor identity |
| RocksDB | Application-level logging | N/A — local only |

Audit logs MUST be stored in a Write-Once-Read-Many (WORM) store with cryptographic hash chaining
and RFC 3161 timestamps.  Minimum retention is 7 years.
See [AUDIT-LOGGING.md](AUDIT-LOGGING.md).

## 5. Access Control Requirements

Every data system MUST enforce least-privilege RBAC.  Default credentials MUST be replaced before
deployment.  Service account credentials MUST be stored in a secrets manager.
See [ACCESS-CONTROL.md](ACCESS-CONTROL.md).

## 6. Integration Checklist

Per-database pre-production checklists are maintained in
[INTEGRATION-CHECKLIST.md](INTEGRATION-CHECKLIST.md).

## 7. Cross-References

| Topic | Document |
|---|---|
| Encryption at rest | [ENCRYPTION-AT-REST.md](ENCRYPTION-AT-REST.md) |
| Encryption in transit | [ENCRYPTION-IN-TRANSIT.md](ENCRYPTION-IN-TRANSIT.md) |
| Audit logging | [AUDIT-LOGGING.md](AUDIT-LOGGING.md) |
| Access control | [ACCESS-CONTROL.md](ACCESS-CONTROL.md) |
| Data classification | [DATA-CLASSIFICATION.md](DATA-CLASSIFICATION.md) |
| Backup & recovery | [BACKUP-RECOVERY.md](BACKUP-RECOVERY.md) |
| Hardening | [HARDENING.md](HARDENING.md) |
| Integration checklist | [INTEGRATION-CHECKLIST.md](INTEGRATION-CHECKLIST.md) |
| Compliance validation | [COMPLIANCE-VALIDATION.md](COMPLIANCE-VALIDATION.md) |
| Platform cryptographic standards | ../../docs/standards/050-security-oidc-policy.md |

## 8. Migration and Deployment

1. All new data systems MUST pass the integration checklist before production deployment.
2. Migrations that change encryption keys MUST follow the key-rotation procedure in
   [ENCRYPTION-AT-REST.md](ENCRYPTION-AT-REST.md).
3. Schema migrations MUST emit DDL events captured by the relevant audit mechanism.
4. Rollback procedures MUST be documented and tested before each release.

## 9. NIST 800-53 Control Alignment

| Control | Satisfied by |
|---|---|
| AC-2 Account Management | ACCESS-CONTROL.md |
| AC-3 Access Enforcement | ACCESS-CONTROL.md |
| AC-17 Remote Access | ENCRYPTION-IN-TRANSIT.md |
| AU-2 Audit Events | AUDIT-LOGGING.md |
| AU-12 Audit Generation | AUDIT-LOGGING.md |
| CA-7 Continuous Monitoring | COMPLIANCE-VALIDATION.md |
| SC-7 Boundary Protection | HARDENING.md |
| SC-8 Transmission Confidentiality | ENCRYPTION-IN-TRANSIT.md |
| SC-12 Cryptographic Key Establishment | ENCRYPTION-AT-REST.md |
| SC-13 Cryptographic Protection | ENCRYPTION-AT-REST.md |
| SI-2 Flaw Remediation | HARDENING.md |
| SI-7 Software/Information Integrity | AUDIT-LOGGING.md |

## 10. Implementation Status

| System | TLS | Encryption @ Rest | Audit Logging | Access Control | Target |
|---|---|---|---|---|---|
| PostgreSQL | Required | Planned | Planned | SCRAM-SHA-256 | Q3 2026 |
| MongoDB | Required | Planned | Planned | SCRAM-SHA-256 | Q3 2026 |
| Elasticsearch | Required | Planned | Planned | API Keys + OIDC | Q3 2026 |
| Redis | Required (6.0+) | Planned | Limited | ACL (6.0+) | Q3 2026 |
| MinIO | Required | Native AES-256 | Access Logs | IAM Policies | Q3 2026 |
| RocksDB | N/A (Local) | Planned | N/A (Local) | N/A (Local) | Q3 2026 |
