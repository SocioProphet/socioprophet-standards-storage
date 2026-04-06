# Data Layer Integration Checklist

This document uses RFC 2119 language: **MUST**, **SHOULD**, **MAY**.

Complete every applicable item before promoting a data-system integration to production.
Record the completion date and operator name next to each item.

---

## PostgreSQL

- [ ] Enable SSL/TLS (`ssl = on`; `ssl_min_protocol_version = TLSv1.3`)
- [ ] Set `pg_hba.conf` to use `hostssl` and `scram-sha-256` for all non-loopback connections
- [ ] Enable the `pgaudit` extension and set `pgaudit.log = 'all'`
- [ ] Enable the `pgcrypto` extension for column-level encryption of Confidential/Secret fields
- [ ] Replace default `postgres` superuser password with a strong credential stored in secrets manager
- [ ] Configure automated encrypted backups (`pg_basebackup` + WAL archiving)
- [ ] Forward audit logs to centralized immutable log store
- [ ] Document the access-control matrix (roles, privileges, object ownership)
- [ ] Run CIS PostgreSQL Benchmark; document any exceptions
- [ ] Schedule quarterly access review

---

## MongoDB

- [ ] Set `net.tls.mode: requireTLS` in `mongod.conf`; disable TLS 1.0, 1.1, 1.2
- [ ] Enable authentication (`security.authorization: enabled`)
- [ ] Set `authenticationMechanisms: SCRAM-SHA-256`
- [ ] Enable native audit logging for all required event types
- [ ] Enable encryption at rest (`security.enableEncryption: true`, cipher `AES256-GCM`)
- [ ] Configure replica set with mTLS (each member presents a client certificate)
- [ ] Configure and test encrypted backup strategy (`mongodump` + encrypted archive)
- [ ] Document RBAC configuration (roles, users, privileges per database)
- [ ] Run CIS MongoDB Benchmark; document any exceptions
- [ ] Test recovery procedures (restore from backup, validate data integrity)

---

## Elasticsearch

- [ ] Enable X-Pack security (`xpack.security.enabled: true`)
- [ ] Enable TLS for HTTP and transport layers
- [ ] Configure authentication (API keys / OIDC for human users; built-in users with strong passwords)
- [ ] Enable audit logging (`xpack.security.audit.enabled: true`) for required event types
- [ ] Configure index-level encryption (encrypted snapshot repository or external KMS)
- [ ] Enable and verify secure inter-node TLS communication
- [ ] Configure Index Lifecycle Management (ILM) for index rotation and archival
- [ ] Set retention policies (hot/warm/cold/delete phases)
- [ ] Document privilege escalation procedures for index administration
- [ ] Run Elasticsearch security hardening checklist; document any exceptions

---

## Redis

- [ ] Enable TLS (`tls-port`; set `port 0` to disable plaintext)
- [ ] Configure ACL (`aclfile`; disable default user)
- [ ] Set strong password (PBKDF2-HMAC-SHA256 derived) for all active users
- [ ] Disable or rename dangerous commands (`FLUSHDB`, `FLUSHALL`, `CONFIG`, `DEBUG`,
  `SHUTDOWN`, `SLAVEOF`)
- [ ] Enable AOF persistence if Redis is used for Critical/Confidential data
- [ ] Set `maxmemory` and `maxmemory-policy` to prevent unbounded growth
- [ ] Enable ACL logging (`acllog-max-len 256`)
- [ ] Forward logs to centralized audit store
- [ ] Document access procedures and key-pattern restrictions per user
- [ ] Verify TLS configuration with `redis-cli --tls` test

---

## MinIO

- [ ] Enable TLS (`MINIO_TLS_CERT_FILE`, `MINIO_TLS_KEY_FILE`)
- [ ] Configure default bucket encryption (SSE-S3 / AES-256-GCM)
- [ ] Configure bucket policies (deny public access where not intended)
- [ ] Enable audit logging (webhook or file target) for all S3 operations
- [ ] Configure IAM policies following least-privilege principle
- [ ] Enable object locking on audit-log and compliance buckets
- [ ] Set lifecycle policies for each bucket (retention + deletion)
- [ ] Test restore procedures (recover object, verify integrity)
- [ ] Document key rotation procedure for the KMS integration
- [ ] Run MinIO security checklist; document any exceptions

---

## RocksDB

- [ ] Enable RocksDB encryption provider (AES-256-GCM via OpenSSL plugin)
- [ ] Supply encryption key via secrets manager or PKCS#11 token (not hardcoded)
- [ ] Store RocksDB data directory on an encrypted volume (dm-crypt/LUKS AES-256-GCM)
- [ ] Implement application-level audit logging for all read/write operations
- [ ] Document backup procedure for RocksDB checkpoint directories
- [ ] Verify checkpoint directories are included in the host's encrypted backup

---

## Post-Integration Sign-Off

All items above applicable to the target system MUST be checked before production deployment.

Sign-off requires:
1. Engineer responsible for integration (name + date)
2. Security review (Security Officer name + date)
3. Link to audit-log evidence for each item

> Record this completed checklist in the project's compliance evidence store.
