# Data Layer Audit Logging Standards

This document uses RFC 2119 language: **MUST**, **SHOULD**, **MAY**.

## 1. Scope

This standard defines comprehensive audit-trail requirements for all data-layer systems, satisfying
NIST SP 800-88 and NIST SP 800-53 AU-2, AU-12, and SI-7 controls.

## 2. Required Audit Events

All data systems MUST capture the following event categories:

| Category | Examples |
|---|---|
| Data access | SELECT, GET, SCAN, read |
| Data modification | INSERT, UPDATE, DELETE, PUT, PATCH |
| Authentication | login, token generation, privilege change, logout |
| Configuration | schema changes, security setting changes |
| Administrative | backups, replication changes, node join/leave |

## 3. Per-System Audit Configuration

### 3.1 PostgreSQL — pgaudit

- Install and enable the `pgaudit` extension.
- Set `pgaudit.log = 'all'` (or at minimum `ddl,dml,role`) in `postgresql.conf`.
- Configure `pgaudit.log_catalog = on` for catalog-access logging.

```
# postgresql.conf
shared_preload_libraries = 'pgaudit'
pgaudit.log = 'all'
pgaudit.log_catalog = on
pgaudit.log_relation = on
pgaudit.log_parameter = on
log_destination = 'syslog'
syslog_facility = 'LOCAL0'
syslog_ident = 'postgresql'
```

### 3.2 MongoDB

- Enable audit logging with `--auditDestination` (syslog or file).
- `auditFilter` MUST include `authenticate`, `authCheck`, `createCollection`,
  `dropCollection`, `createIndex`, `dropIndex`, `insert`, `update`, `delete`, `find`,
  `logout`, `createUser`, `dropUser`, `updateUser`, `grantRolesToUser`, `revokeRolesFromUser`.

```yaml
# mongod.conf excerpt
auditLog:
  destination: syslog
  format: JSON
  filter: '{atype: {$in: ["authenticate","authCheck","createCollection","dropCollection","insert","update","delete","find","logout","createUser","dropUser","updateUser"]}}'
```

### 3.3 Elasticsearch

- Set `xpack.security.audit.enabled: true` in `elasticsearch.yml`.
- `xpack.security.audit.logfile.events.include` MUST contain:
  `access_granted`, `access_denied`, `authentication_success`, `authentication_failed`,
  `anonymous_access_denied`, `run_as_granted`, `run_as_denied`,
  `change_password`, `put_user`, `delete_user`.

```yaml
# elasticsearch.yml excerpt
xpack.security.audit.enabled: true
xpack.security.audit.logfile.events.include:
  - access_granted
  - access_denied
  - authentication_success
  - authentication_failed
  - anonymous_access_denied
  - run_as_granted
  - run_as_denied
  - change_password
  - put_user
  - delete_user
```

### 3.4 Redis

- Enable ACL logging: `acllog-max-len 256` in `redis.conf`.
- The `MONITOR` command MAY be used in controlled audit sessions; it MUST NOT run
  continuously in production due to performance impact.
- Dangerous commands (`FLUSHDB`, `FLUSHALL`, `CONFIG`, `DEBUG`, `SHUTDOWN`) MUST be
  disabled or renamed and their invocation attempts logged via ACL rules.

```
# redis.conf excerpt
acllog-max-len 256
loglevel notice
logfile /var/log/redis/redis-server.log
```

### 3.5 MinIO

- Enable MinIO audit logging: `MINIO_AUDIT_WEBHOOK_ENDPOINT` or file logging.
- All S3 API operations MUST be logged with requestor identity (access key or IAM principal),
  bucket, object key, action, timestamp, and source IP.

```bash
MINIO_AUDIT_WEBHOOK_ENABLE_TARGET=on
MINIO_AUDIT_WEBHOOK_ENDPOINT=https://audit-collector.internal/minio
MINIO_AUDIT_WEBHOOK_AUTH_TOKEN=<token>
```

## 4. Immutable Audit Trail Storage

### 4.1 Centralized Logging

- All audit events MUST be forwarded to a centralized log store (e.g., syslog + Loki, or a
  dedicated audit database) within 5 seconds of generation.
- The centralized store MUST NOT be writable by the originating application after initial
  write (WORM semantics).

### 4.2 Cryptographic Hash Chaining

- Each audit record MUST include a SHA-256 hash of the previous record to form a tamper-evident
  chain, per NIST SP 800-88 §4.8.
- Chain integrity MUST be verified nightly by an automated job; failures MUST page on-call.

### 4.3 Timestamps

- Every audit event MUST carry an RFC 3339 UTC timestamp.
- The centralized log store MUST apply an RFC 3161 trusted timestamp to each batch (maximum
  batch interval: 1 minute).

### 4.4 Digital Signatures

- Audit log batches MUST be signed with **ECDSA-P256** before archival.
- The signing key MUST be stored in the HSM and rotated annually.
- Signatures MUST be verifiable without access to the originating system.

## 5. Log Retention

| Tier | Retention Period |
|---|---|
| Hot (queryable) | 90 days |
| Warm (compressed, indexed) | 1 year |
| Cold (archival) | 7 years (minimum) |

- Backups of audit logs MUST follow the same encryption-at-rest requirements as operational data
  (AES-256-GCM).
- Deletion of audit logs before the retention period MUST require dual-person authorization and
  generate an immutable destruction certificate.

## 6. Secure Deletion

- At end of retention, audit logs MUST be deleted using cryptographic erasure: destroy the
  DEK used to encrypt the log segment, then overwrite the ciphertext.
- A destruction certificate MUST be generated and retained for 3 years after deletion.
