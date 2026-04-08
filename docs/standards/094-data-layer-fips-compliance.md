# Data Layer FIPS Compliance Standard

This document uses RFC 2119 language: **MUST**, **SHOULD**, **MAY**.

## 1. Overview

This standard defines FIPS 140-2/140-3 compliance requirements for all six SocioProphet data store systems. Requirements cover encryption in transit (TLS), encryption at rest (AES-256-GCM), audit logging, RBAC, and backup/recovery.

These requirements implement the following NIST 800-53 controls:
- **SC-8** — Transmission Confidentiality and Integrity (TLS)
- **SC-28** — Protection of Information at Rest (encryption at rest)
- **AC-3** — Access Enforcement (RBAC)
- **AU-12** — Audit Record Generation (audit logging)

---

## 2. Universal Requirements (All Data Stores)

The following requirements MUST be applied to all six data stores.

### 2.1 Transport Layer Security (SC-8)
- All client connections MUST use **TLS 1.3** minimum.
- TLS 1.2 MAY be permitted only with documented exception for legacy clients.
- Cipher suites MUST be restricted to AEAD-only (e.g., `TLS_AES_256_GCM_SHA384`).
- Server certificates MUST use ECDSA-P256 or RSA-4096 minimum.
- Certificate pinning MUST be configured for critical paths (internal service-to-database connections).
- OCSP Stapling MUST be enabled for certificate revocation checks.
- Anonymous or unauthenticated connections MUST be disabled.

### 2.2 Audit Logging (AU-12)
- All data modification events (INSERT, UPDATE, DELETE) MUST be logged.
- All DDL events (CREATE, ALTER, DROP) MUST be logged.
- All authentication events (login, logout, failure) MUST be logged.
- All privileged operations MUST be logged.
- Audit logs MUST be forwarded to the centralized audit store within 60 seconds.
- Log format MUST conform to `093-forensic-audit-nist-800-88.md` schema.

### 2.3 Role-Based Access Control (AC-3)
- A dedicated service account MUST be created per application tier (read-only, read-write, admin).
- Application accounts MUST NOT have database administration privileges.
- DBA accounts MUST be separated from application accounts.
- Default/vendor credentials MUST be changed before deployment.
- Quarterly access reviews MUST be conducted and documented.
- Password/credential rotation MUST occur every 90 days (automated via Vault).

### 2.4 Backup and Recovery
- All backups MUST be encrypted with AES-256-GCM.
- Backup encryption keys MUST be managed by Vault, separate from data encryption keys.
- Backups MUST be stored in geographically diverse, off-site locations (minimum 2 regions).
- Recovery testing MUST be conducted quarterly with documented RPO/RTO validation.
- Backup retention MUST follow the schedule in `093-forensic-audit-nist-800-88.md` (7 years for compliance data).

---

## 3. PostgreSQL (System-of-Record)

**Repository**: `SocioProphet/postgres`  
**Role**: Incident state, policy/audit, relational data

### 3.1 Encryption in Transit
- `ssl = on` MUST be configured in `postgresql.conf`.
- `ssl_min_protocol_version = TLSv1.3` MUST be set.
- `ssl_ciphers = 'HIGH:!aNULL:!MD5:!RC4'` MUST be enforced.
- Client authentication MUST require `clientcert=verify-full` in `pg_hba.conf` for service connections.

### 3.2 Encryption at Rest
- The **pgcrypto** extension MUST be enabled.
- Column-level encryption MUST use `pgcrypto` with AES-256-GCM for PII, secrets, and audit tokens.
- Tablespace encryption SHOULD use filesystem-level encryption (LUKS/dm-crypt) as a defense-in-depth measure.

### 3.3 Audit Logging
- The **pgaudit** extension MUST be installed and configured.
- `pgaudit.log = 'write, ddl, role'` MUST be set to capture DML/DDL/SECURITY events.
- `pgaudit.log_catalog = on` SHOULD be enabled to log catalog accesses.
- Audit logs MUST be exported to the centralized log store via `pg_audit` log shipping.

### 3.4 RBAC
- Roles MUST be structured: `app_read`, `app_write`, `app_admin`, `dba`.
- Row-Level Security (RLS) MUST be enabled for multi-tenant tables.
- `REVOKE ALL ON SCHEMA public FROM PUBLIC` MUST be applied on all databases.
- Superuser role MUST NOT be used by application accounts.

### 3.5 Implementation Evidence
- TLS configuration: `SocioProphet/postgres/conf/postgresql.conf`
- pgaudit setup: `SocioProphet/postgres/conf/pgaudit.conf`
- RBAC roles: `SocioProphet/postgres/migrations/000-rbac-setup.sql`

---

## 4. MongoDB (Document Store)

**Repository**: `SocioProphet/mongo`  
**Role**: Domain documents, configs, runbooks, annotations

### 4.1 Encryption in Transit
- `net.tls.mode: requireTLS` MUST be set in `mongod.conf`.
- `net.tls.disabledProtocols: TLS1_0,TLS1_1,TLS1_2` SHOULD be set to allow TLS 1.3 only.
- Client certificates MUST be required for all service connections (`net.tls.CAFile`).

### 4.2 Encryption at Rest
- **Native Encrypted Storage Engine** (Queryable Encryption or CSFLE) MUST be enabled.
- Encryption algorithm MUST be AES-256-GCM.
- Key management MUST use Vault KMIP integration.

### 4.3 Audit Logging
- `security.auditLog.destination: file` MUST be configured.
- `security.auditLog.filter` MUST capture: `authenticate`, `createCollection`, `dropCollection`, `insert`, `update`, `delete`, `createUser`, `dropUser`.
- Audit logs MUST be in JSON format and forwarded to the centralized log store.

### 4.4 RBAC
- Built-in roles MUST be used over custom roles where sufficient.
- `readWrite` role MUST NOT include `dbAdmin` or `userAdmin` privileges.
- Application connections MUST use `readWrite` or custom least-privilege roles.
- `root` role MUST be disabled for non-DBA accounts.

### 4.5 Implementation Evidence
- TLS configuration: `SocioProphet/mongo/conf/mongod.conf`
- CSFLE setup: `SocioProphet/mongo/scripts/enable-encryption.js`
- RBAC roles: `SocioProphet/mongo/scripts/create-roles.js`

---

## 5. Elasticsearch / OpenSearch (Search and Audit Store)

**Repository**: `SocioProphet/elasticsearch`  
**Role**: Full-text search, audit log centralization

### 5.1 Encryption in Transit
- `xpack.security.http.ssl.enabled: true` MUST be configured.
- `xpack.security.transport.ssl.enabled: true` MUST be configured for inter-node traffic.
- `xpack.security.http.ssl.supported_protocols: [TLSv1.3]` MUST be set.
- Client certificate authentication MUST be required for service connections.

### 5.2 Encryption at Rest
- **X-Pack Encryption at Rest** MUST be enabled.
- Encryption algorithm: AES-256-GCM (configured at OS/filesystem level with Elasticsearch data directory encryption).
- Index-level encryption SHOULD be used for sensitive indices (audit logs, PII).

### 5.3 Audit Logging
- `xpack.security.audit.enabled: true` MUST be configured.
- Audit events MUST include: `authentication_success`, `authentication_failed`, `access_granted`, `access_denied`, `index_create`, `index_delete`.
- Audit logs MUST be written to a separate, immutable index with ILM freeze policy.

### 5.4 RBAC
- X-Pack Security roles MUST be defined per application tier.
- Index-level access control MUST restrict application accounts to their own indices.
- `superuser` role MUST be restricted to DBA accounts only.
- Kibana access MUST require OIDC authentication.

### 5.5 Implementation Evidence
- TLS configuration: `SocioProphet/elasticsearch/config/elasticsearch.yml`
- Security roles: `SocioProphet/elasticsearch/config/roles.yml`
- ILM policy: `SocioProphet/elasticsearch/policies/audit-ilm.json`

---

## 6. Redis (Cache and Session Store)

**Repository**: `SocioProphet/redis`  
**Role**: Distributed cache, session management, pub/sub

### 6.1 Encryption in Transit
- `tls-port` MUST be enabled; plain-text port MUST be disabled in production.
- `tls-protocols TLSv1.3` MUST be set.
- `tls-auth-clients yes` MUST be configured to require client certificates.
- `requirepass` MUST be set (or replaced by ACL authentication).

### 6.2 Encryption at Rest
- Redis persistence files (RDB/AOF) MUST be stored on encrypted volumes (LUKS/dm-crypt or cloud-provider encryption).
- Sensitive cached values SHOULD use application-layer AES-256-GCM encryption before storing in Redis.
- Redis Enterprise with encryption at rest MUST be used in production environments handling PII.

### 6.3 Audit Logging
- **Redis ACL LOG** MUST be enabled: `acllog-max-len 512`.
- ACL logging captures failed and denied command attempts.
- **Redis MONITOR** MUST NOT be used in production (performance impact); use ACL logging instead.
- Redis access logs MUST be exported to the centralized audit store via a log forwarder.

### 6.4 RBAC
- **Redis ACLs** MUST be configured per service: `ACL SETUSER app_read ON >password ~* &* +@read`.
- The default user MUST be disabled: `ACL SETUSER default off`.
- `CONFIG` and `DEBUG` commands MUST be restricted to DBA accounts.
- Password rotation MUST be automated every 90 days via Vault dynamic secrets.

### 6.5 Implementation Evidence
- TLS configuration: `SocioProphet/redis/conf/redis.conf`
- ACL setup: `SocioProphet/redis/conf/users.acl`
- Vault dynamic secrets: `SocioProphet/redis/vault/redis-secrets.hcl`

---

## 7. MinIO (Object Storage)

**Repository**: `SocioProphet/minio`  
**Role**: Binary artifacts, Parquet shards, model binaries, backups

### 7.1 Encryption in Transit
- HTTPS MUST be enforced: `MINIO_SERVER_TLS_CERT_FILE` and `MINIO_SERVER_TLS_KEY_FILE` MUST be configured.
- Plaintext HTTP MUST be disabled in production environments.
- TLS 1.3 MUST be enforced via server TLS configuration.
- Client certificate authentication MUST be required for service-to-MinIO connections.

### 7.2 Encryption at Rest
- **Native Server-Side Encryption (SSE-S3 or SSE-C)** MUST be enabled.
- Encryption algorithm: AES-256-GCM.
- MinIO Key Management Service (KES) integration MUST be configured with Vault as the KMS backend.
- Object-level encryption MUST be applied to all buckets containing sensitive data.

### 7.3 Audit Logging
- `MINIO_AUDIT_WEBHOOK_ENABLE` MUST be configured to forward audit events.
- S3 operation events MUST be captured: `s3:GetObject`, `s3:PutObject`, `s3:DeleteObject`, `s3:ListBucket`.
- Requestor identity MUST be included in all audit events.
- Audit logs MUST be forwarded to the centralized log store.

### 7.4 RBAC
- MinIO IAM policies MUST be defined per application tier.
- Bucket policies MUST restrict cross-tenant access.
- `consoleAdmin` group MUST be restricted to DBA accounts.
- Service account access keys MUST be rotated every 90 days via Vault.

### 7.5 Implementation Evidence
- TLS configuration: `SocioProphet/minio/env/minio.env`
- SSE configuration: `SocioProphet/minio/config/config.env`
- IAM policies: `SocioProphet/minio/policies/`

---

## 8. RocksDB (Embedded Store)

**Repository**: `SocioProphet/rocksdb`  
**Role**: Embedded local state, P2P node local storage

### 8.1 Encryption in Transit
- RocksDB is an embedded library; transport encryption is handled by the application layer.
- Applications using RocksDB MUST use TLS 1.3 for all network communication.
- gRPC or similar transport MUST enforce TLS when exposing RocksDB-backed data over the network.

### 8.2 Encryption at Rest
- **RocksDB Encrypted Environment** MUST be used (built-in encryption block cache).
- Where the application layer wrapping RocksDB supports AEAD, AES-256-GCM MUST be used for data encryption, consistent with the universal requirement in `090-fips-nist-compliance.md`.
- If using RocksDB's native `EncryptedEnv` (which is limited to AES-CTR internally), this constitutes a documented exception: the CTR-mode encryption MUST be combined with mandatory filesystem-level volume encryption (AES-256-GCM via LUKS or cloud-provider encryption) as a compensating control to achieve authenticated encryption at rest.
- Encryption keys MUST be stored in Vault and injected at runtime via the secret injection sidecar.
- Database files MUST NOT be stored on unencrypted filesystem volumes.

### 8.3 Audit Logging
- Applications wrapping RocksDB MUST emit audit events for all write operations.
- Operation type, key prefix (non-sensitive), actor, timestamp MUST be included.
- RocksDB WAL (Write-Ahead Log) MAY be used as an evidence source for forensic recovery.

### 8.4 RBAC
- Access to RocksDB is process-scoped; OS-level permissions (file ownership, `chmod 700`) MUST restrict access to the owning service account.
- Multiple processes MUST NOT share a RocksDB instance (single-writer guarantee).
- Access control MUST be enforced at the application layer using the authenticated identity.

### 8.5 Implementation Evidence
- Encryption setup: `SocioProphet/rocksdb/src/encrypted_env.cc`
- Key injection: `SocioProphet/rocksdb/k8s/secret-injection.yaml`

---

## 9. Shared Infrastructure Requirements

### 9.1 Network Isolation
- All data store services MUST run in a dedicated Kubernetes namespace with network policies.
- Default-deny network policies MUST restrict ingress to only authorized application namespaces.
- See `095-orchestration-fips-compliance.md` for Kubernetes network policy specifications.

### 9.2 Secret Injection
- All database credentials MUST be injected at runtime via Vault Agent or Vault Secrets Operator.
- Credentials MUST NOT be baked into container images or environment variable manifests.
- See `095-orchestration-fips-compliance.md` for Vault configuration.

## Related Standards

- `090-fips-nist-compliance.md` — Cryptographic requirements
- `091-nist-800-53-control-mappings.md` — NIST 800-53 control mappings (SC-8, SC-28, AC-3, AU-12)
- `093-forensic-audit-nist-800-88.md` — Forensic audit trail requirements
- `095-orchestration-fips-compliance.md` — Kubernetes orchestration and Vault integration
