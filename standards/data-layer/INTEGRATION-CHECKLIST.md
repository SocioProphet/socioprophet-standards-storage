# Integration Checklist — Data Layer FIPS 140-2/140-3 Standard

- Last updated: 2026-01-27
- Status: Active governance document
- Owner: Security Engineering + Platform DBA Team
- Standard references: FIPS 140-2, FIPS 140-3, NIST SP 800-53

---

## Table of Contents

1. [How to Use This Checklist](#how-to-use-this-checklist)
2. [PostgreSQL Compliance Checklist](#postgresql-compliance-checklist)
3. [MongoDB Compliance Checklist](#mongodb-compliance-checklist)
4. [Elasticsearch / OpenSearch Compliance Checklist](#elasticsearch--opensearch-compliance-checklist)
5. [Redis Compliance Checklist](#redis-compliance-checklist)
6. [MinIO Compliance Checklist](#minio-compliance-checklist)
7. [RocksDB Compliance Checklist](#rocksdb-compliance-checklist)
8. [NIST 800-53 Control Compliance Matrix](#nist-800-53-control-compliance-matrix)
9. [Compliance Status Legend](#compliance-status-legend)

---

## How to Use This Checklist

This checklist is the operational validation artifact for FIPS 140-2/140-3 compliance across the data layer. It must be:

1. **Reviewed quarterly** by Security Engineering and signed off by the relevant system owner.
2. **Updated in CI/CD** — automated checks in `COMPLIANCE-VALIDATION.md` update the status of automatable items.
3. **Attached to audit evidence** — a snapshot of this file at each quarterly review is archived in `standards/audit-forensics/`.

Status symbols:
- ✅ Verified and passing (automated check or last manual review ≤ 90 days ago)
- 🔄 In progress (implementation underway per timeline in `INDEX.md`)
- ❌ Not started
- ⚠️ Requires attention (automated check failing or exception pending)
- N/A Not applicable to this system

---

## PostgreSQL Compliance Checklist

### Encryption at Rest

| # | Check | Status | Verification Method | Last Checked |
|---|---|---|---|---|
| PG-EAR-01 | PostgreSQL data directory resides on LUKS AES-256-XTS encrypted volume | 🔄 | `cryptsetup status /dev/mapper/pg_data` | — |
| PG-EAR-02 | pg_tde extension installed and enabled | 🔄 | `SELECT * FROM pg_extension WHERE extname = 'pg_tde'` | — |
| PG-EAR-03 | TDE key managed through HashiCorp Vault | 🔄 | `vault read transit/postgres-tde` returns valid key | — |
| PG-EAR-04 | pgcrypto installed for column-level encryption | 🔄 | `SELECT * FROM pg_extension WHERE extname = 'pgcrypto'` | — |
| PG-EAR-05 | Sensitive columns use AES-256-GCM (via Vault Transit) | 🔄 | Code review of column encryption usage | — |
| PG-EAR-06 | WAL archiving encrypts WAL files before upload | 🔄 | Verify `archive_command` script uses encryption | — |
| PG-EAR-07 | Encryption key rotation performed within last 90 days | 🔄 | Vault key metadata: `vault read transit/postgres-tde` | — |
| PG-EAR-08 | No AES-CBC or 3DES in use | 🔄 | Grep configuration for legacy algorithms | — |

### Encryption in Transit

| # | Check | Status | Verification Method | Last Checked |
|---|---|---|---|---|
| PG-EIT-01 | `ssl = on` in postgresql.conf | ✅ | `SHOW ssl;` | 2026-01-27 |
| PG-EIT-02 | `ssl_min_protocol_version = 'TLSv1.3'` | ✅ | `SHOW ssl_min_protocol_version;` | 2026-01-27 |
| PG-EIT-03 | `ssl_ciphers` set to approved suites only | ✅ | `SHOW ssl_ciphers;` | 2026-01-27 |
| PG-EIT-04 | pg_hba.conf uses `hostssl` only (no `host` or `hostnossl` for network) | ✅ | Review pg_hba.conf; `SELECT * FROM pg_hba_file_rules` | 2026-01-27 |
| PG-EIT-05 | `clientcert=verify-full` in pg_hba.conf for all network connections | ✅ | Review pg_hba.conf | 2026-01-27 |
| PG-EIT-06 | Application connection strings use `sslmode=verify-full` | ✅ | Code review; grep connection strings | 2026-01-27 |
| PG-EIT-07 | Server certificate issued by internal CA; valid; not expired | ✅ | `openssl s_client -connect postgres.internal:5432 -starttls postgres` | 2026-01-27 |
| PG-EIT-08 | TLS 1.0, 1.1, 1.2 disabled | ✅ | `openssl s_client -tls1_2 ...` returns handshake failure | 2026-01-27 |

### Audit Logging

| # | Check | Status | Verification Method | Last Checked |
|---|---|---|---|---|
| PG-AL-01 | pgaudit extension installed and loaded | 🔄 | `SELECT * FROM pg_extension WHERE extname = 'pgaudit'` | — |
| PG-AL-02 | `pgaudit.log` covers ddl, role, connection | 🔄 | `SHOW pgaudit.log;` | — |
| PG-AL-03 | Sensitive tables have object-level audit via SECURITY LABEL | 🔄 | `SELECT * FROM pg_seclabels WHERE provider = 'pgaudit'` | — |
| PG-AL-04 | Audit logs forwarded to Fluentd aggregator | 🔄 | Check Fluentd pipeline for postgres source | — |
| PG-AL-05 | Audit logs in central OpenSearch index | 🔄 | Query `postgres-audit-*` index | — |
| PG-AL-06 | Log retention ≥ 7 years configured in ISM policy | 🔄 | Verify ISM policy on audit index | — |
| PG-AL-07 | `log_connections = on` and `log_disconnections = on` | 🔄 | `SHOW log_connections; SHOW log_disconnections;` | — |

### Access Control

| # | Check | Status | Verification Method | Last Checked |
|---|---|---|---|---|
| PG-AC-01 | `password_encryption = 'scram-sha-256'` | ✅ | `SHOW password_encryption;` | 2026-01-27 |
| PG-AC-02 | No users with MD5 hashed passwords | ✅ | `SELECT usename FROM pg_shadow WHERE passwd NOT LIKE 'SCRAM-SHA-256$%' AND passwd IS NOT NULL` returns 0 rows | 2026-01-27 |
| PG-AC-03 | Row-level security enabled on multi-tenant tables | ✅ | `SELECT tablename FROM pg_tables WHERE rowsecurity = true` | 2026-01-27 |
| PG-AC-04 | Service accounts use Vault dynamic credentials (no static passwords) | 🔄 | Verify Vault database secrets engine configuration | — |
| PG-AC-05 | No service account holds SUPERUSER privilege | ✅ | `SELECT usename FROM pg_user WHERE usesuper AND usename != 'postgres'` returns 0 rows | 2026-01-27 |
| PG-AC-06 | OIDC / federated auth configured (Vault bridge) | 🔄 | Vault OIDC auth method active | — |
| PG-AC-07 | MFA required for operator direct database access | 🔄 | Vault MFA policy enforced for DBA group | — |

### Backup and Recovery

| # | Check | Status | Verification Method | Last Checked |
|---|---|---|---|---|
| PG-BR-01 | Base backups encrypted before upload to MinIO | 🔄 | Review backup script; verify `.enc` suffix in backup bucket | — |
| PG-BR-02 | WAL archives encrypted in archive storage | 🔄 | Sample WAL files in MinIO; confirm encrypted | — |
| PG-BR-03 | Backup encryption keys stored in Vault (not with backup) | 🔄 | `vault read transit/postgres-backup` returns key; not stored in MinIO | — |
| PG-BR-04 | Quarterly restore test performed and documented | ❌ | DR test log in audit-forensics/ | — |
| PG-BR-05 | HMAC-SHA-256 checksum verified after each backup | 🔄 | backup-verify.sh exits 0 | — |
| PG-BR-06 | PITR procedure tested and documented | ❌ | PITR test log in audit-forensics/ | — |

### Hardening

| # | Check | Status | Verification Method | Last Checked |
|---|---|---|---|---|
| PG-H-01 | `listen_addresses` bound to internal IP only | 🔄 | `SHOW listen_addresses;` | — |
| PG-H-02 | No `trust` authentication in pg_hba.conf | ✅ | `grep 'trust' /etc/postgresql/*/main/pg_hba.conf` returns nothing | 2026-01-27 |
| PG-H-03 | pg_read_file and pg_ls_dir revoked from PUBLIC | 🔄 | `\df pg_read_file` shows no public access | — |
| PG-H-04 | systemd hardening (NoNewPrivileges, PrivateTmp, etc.) | 🔄 | `systemctl cat postgresql | grep NoNewPrivileges` | — |
| PG-H-05 | CIS PostgreSQL benchmark scan passes | 🔄 | Run CIS benchmark scan; zero critical findings | — |

---

## MongoDB Compliance Checklist

### Encryption at Rest

| # | Check | Status | Verification Method | Last Checked |
|---|---|---|---|---|
| MG-EAR-01 | WiredTiger encryption enabled (`enableEncryption: true`) | 🔄 | `db.adminCommand({serverStatus:1}).security.SSLServerSubjectName` | — |
| MG-EAR-02 | KMIP integration with HashiCorp Vault configured | 🔄 | `mongod.conf` has `security.kmip` section | — |
| MG-EAR-03 | KMIP client certificate valid and not expired | 🔄 | Check KMIP client cert expiry | — |
| MG-EAR-04 | CSFLE configured for Restricted/Secret collections | 🔄 | Code review of CSFLE schema maps | — |
| MG-EAR-05 | Encryption key rotation performed within last 90 days | 🔄 | Vault KMIP key metadata | — |
| MG-EAR-06 | Data directory on LUKS-encrypted volume | 🔄 | `cryptsetup status /dev/mapper/mongo_data` | — |

### Encryption in Transit

| # | Check | Status | Verification Method | Last Checked |
|---|---|---|---|---|
| MG-EIT-01 | `net.tls.mode: requireTLS` in mongod.conf | ✅ | `db.adminCommand({getCmdLineOpts:1})` | 2026-01-27 |
| MG-EIT-02 | `disabledProtocols: TLS1_0,TLS1_1,TLS1_2` | ✅ | `openssl s_client -tls1_2 -connect mongo.internal:27017` fails | 2026-01-27 |
| MG-EIT-03 | `FIPSMode: true` in net.tls | ✅ | `db.adminCommand({serverStatus:1}).security` | 2026-01-27 |
| MG-EIT-04 | `clusterAuthMode: x509` for replica set | ✅ | `db.adminCommand({getCmdLineOpts:1})` | 2026-01-27 |
| MG-EIT-05 | `allowConnectionsWithoutCertificates: false` | ✅ | `db.adminCommand({getCmdLineOpts:1})` | 2026-01-27 |
| MG-EIT-06 | Client drivers configured with TLS and cert validation | ✅ | Code review of MongoDB client configuration | 2026-01-27 |

### Audit Logging

| # | Check | Status | Verification Method | Last Checked |
|---|---|---|---|---|
| MG-AL-01 | `auditLog.destination: file` configured | 🔄 | `mongod.conf` has `auditLog` section | — |
| MG-AL-02 | Audit filter covers all required event types | 🔄 | Review `auditLog.filter` against required event list | — |
| MG-AL-03 | Audit logs forwarded to Fluentd | 🔄 | Fluentd config has MongoDB source | — |
| MG-AL-04 | Audit log retention ≥ 7 years | 🔄 | ISM policy on `mongodb-audit-*` index | — |

### Access Control

| # | Check | Status | Verification Method | Last Checked |
|---|---|---|---|---|
| MG-AC-01 | `security.authorization: enabled` in mongod.conf | ✅ | `db.adminCommand({getCmdLineOpts:1})` | 2026-01-27 |
| MG-AC-02 | `security.javascriptEnabled: false` | ✅ | `db.adminCommand({serverStatus:1}).security` | 2026-01-27 |
| MG-AC-03 | No service accounts with `root` or `dbOwner` roles | ✅ | `db.system.users.find({roles:{$elemMatch:{role:{$in:['root','dbOwner']}}}})` | 2026-01-27 |
| MG-AC-04 | All users use SCRAM-SHA-256 authentication | ✅ | `db.system.users.find({mechanisms:{$ne:['SCRAM-SHA-256']}})` returns empty | 2026-01-27 |
| MG-AC-05 | LDAP authorization configured | 🔄 | `mongod.conf` `security.ldap` section | — |
| MG-AC-06 | OIDC authentication configured (MongoDB 7.0) | 🔄 | `security.oidc` configuration | — |

### Backup and Recovery

| # | Check | Status | Verification Method | Last Checked |
|---|---|---|---|---|
| MG-BR-01 | mongodump encrypted before upload | 🔄 | Verify backup script | — |
| MG-BR-02 | Oplog backup running for continuous RPO | 🔄 | Verify oplog backup service | — |
| MG-BR-03 | Backups taken from secondary replica | 🔄 | Review backup script host configuration | — |
| MG-BR-04 | Quarterly restore test documented | ❌ | DR test log | — |

### Hardening

| # | Check | Status | Verification Method | Last Checked |
|---|---|---|---|---|
| MG-H-01 | `net.bindIp` set to internal IP only | 🔄 | `db.adminCommand({getCmdLineOpts:1})` | — |
| MG-H-02 | mongocryptd accessible via local socket only | 🔄 | `netstat -tlnp` for port 27020 | — |
| MG-H-03 | systemd hardening applied | 🔄 | Review mongodb.service | — |

---

## Elasticsearch / OpenSearch Compliance Checklist

### Encryption at Rest

| # | Check | Status | Verification Method | Last Checked |
|---|---|---|---|---|
| ES-EAR-01 | `xpack.security.fips_mode.enabled: true` | ✅ | `GET /_nodes/settings?filter_path=**.fips_mode` | 2026-01-27 |
| ES-EAR-02 | FIPS JVM provider (Bouncy Castle FIPS) configured | ✅ | `GET /_nodes/jvm?filter_path=**.vm_name` | 2026-01-27 |
| ES-EAR-03 | Data directories on LUKS-encrypted volumes | ✅ | `cryptsetup status` on ES data mounts | 2026-01-27 |
| ES-EAR-04 | Snapshots stored in SSE-KMS encrypted repository | ✅ | `GET _snapshot/encrypted-minio-backup` | 2026-01-27 |
| ES-EAR-05 | Elasticsearch keystore populated via `elasticsearch-keystore` | ✅ | `bin/elasticsearch-keystore list` | 2026-01-27 |

### Encryption in Transit

| # | Check | Status | Verification Method | Last Checked |
|---|---|---|---|---|
| ES-EIT-01 | `xpack.security.http.ssl.enabled: true` | ✅ | `GET /` returns HTTPS only | 2026-01-27 |
| ES-EIT-02 | `xpack.security.transport.ssl.enabled: true` | ✅ | Node-to-node communication encrypted | 2026-01-27 |
| ES-EIT-03 | `supported_protocols: [TLSv1.3]` | ✅ | `openssl s_client -connect es.internal:9200 -tls1_2` fails | 2026-01-27 |
| ES-EIT-04 | `client_authentication: required` on transport | ✅ | Verify node certificates required | 2026-01-27 |
| ES-EIT-05 | All node certificates issued by internal CA | ✅ | Vault PKI issue log | 2026-01-27 |

### Audit Logging

| # | Check | Status | Verification Method | Last Checked |
|---|---|---|---|---|
| ES-AL-01 | `xpack.security.audit.enabled: true` | ✅ | `GET /_cluster/settings` | 2026-01-27 |
| ES-AL-02 | All required event types in `events.include` | ✅ | Review elasticsearch.yml audit config | 2026-01-27 |
| ES-AL-03 | Audit index has WORM ISM policy | ✅ | `GET _plugins/_ism/policies/audit-worm-policy` | 2026-01-27 |
| ES-AL-04 | Audit logs retained ≥ 7 years | ✅ | ISM policy delete phase = 7y | 2026-01-27 |

### Access Control

| # | Check | Status | Verification Method | Last Checked |
|---|---|---|---|---|
| ES-AC-01 | `xpack.security.enabled: true` | ✅ | `GET /_cluster/health` requires auth | 2026-01-27 |
| ES-AC-02 | Index-level permissions applied to all indices | ✅ | `GET _security/role/socioprophet_app` | 2026-01-27 |
| ES-AC-03 | Document-level security on multi-tenant indices | ✅ | DLS query in tenant roles | 2026-01-27 |
| ES-AC-04 | Field-level security hides PII from unauthorized roles | ✅ | Test query with search_user role | 2026-01-27 |
| ES-AC-05 | OIDC authentication configured | ✅ | Keycloak OIDC realm active | 2026-01-27 |
| ES-AC-06 | API keys expire within 30 days | ✅ | `GET _security/api_key` for all active keys | 2026-01-27 |

### Backup and Recovery

| # | Check | Status | Verification Method | Last Checked |
|---|---|---|---|---|
| ES-BR-01 | SLM policy creates hourly snapshots | ✅ | `GET _slm/policy/hourly-snapshots` | 2026-01-27 |
| ES-BR-02 | Snapshots stored in encrypted MinIO repository | ✅ | `mc encrypt info myminio/socioprophet-es-snapshots` | 2026-01-27 |
| ES-BR-03 | CCR configured for DR cluster | ✅ | `GET _cluster/settings` for remote cluster | 2026-01-27 |
| ES-BR-04 | Restore test performed semi-annually | ❌ | DR test log | — |

### Hardening

| # | Check | Status | Verification Method | Last Checked |
|---|---|---|---|---|
| ES-H-01 | `bootstrap.memory_lock: true` | ✅ | `GET /_nodes/stats/os?filter_path=**.mem.swap_used_in_bytes` | 2026-01-27 |
| ES-H-02 | `network.host` bound to internal IP | ✅ | `GET /_nodes/settings` | 2026-01-27 |
| ES-H-03 | `http.cors.enabled: false` | ✅ | elasticsearch.yml review | 2026-01-27 |

---

## Redis Compliance Checklist

### Encryption at Rest

| # | Check | Status | Verification Method | Last Checked |
|---|---|---|---|---|
| RD-EAR-01 | Redis data directory on LUKS AES-256-XTS encrypted volume | 🔄 | `cryptsetup status /dev/mapper/redis_data` | — |
| RD-EAR-02 | RDB snapshot backups encrypted before archival | 🔄 | Verify backup script | — |
| RD-EAR-03 | AOF backup encrypted before archival | 🔄 | Verify backup script | — |
| RD-EAR-04 | Backup encryption key in Vault | 🔄 | `vault read transit/redis-backup` | — |

### Encryption in Transit

| # | Check | Status | Verification Method | Last Checked |
|---|---|---|---|---|
| RD-EIT-01 | Plain-text port 6379 disabled (`port 0`) | 🔄 | `redis-cli ... INFO server` — no port 6379 listener | — |
| RD-EIT-02 | `tls-port 6380` active | 🔄 | `redis-cli --tls ... -p 6380 PING` | — |
| RD-EIT-03 | `tls-protocols "TLSv1.3"` | 🔄 | `openssl s_client -tls1_2 -connect redis.internal:6380` fails | — |
| RD-EIT-04 | `tls-auth-clients yes` (client cert required) | 🔄 | Connection without client cert fails | — |
| RD-EIT-05 | `tls-replication yes` | 🔄 | `redis-cli ... INFO replication` shows TLS for replicas | — |

### Audit Logging

| # | Check | Status | Verification Method | Last Checked |
|---|---|---|---|---|
| RD-AL-01 | ACL log enabled (`acllog-max-len > 0`) | 🔄 | `redis-cli ... ACL LOG` | — |
| RD-AL-02 | `loglevel verbose` or `loglevel debug` for audit mode | 🔄 | `redis-cli ... CONFIG GET loglevel` | — |
| RD-AL-03 | Redis audit proxy forwarding to Fluentd | 🔄 | Fluentd has redis-monitor source | — |
| RD-AL-04 | Privileged command access logged | 🔄 | Review renamed command audit trail | — |

### Access Control

| # | Check | Status | Verification Method | Last Checked |
|---|---|---|---|---|
| RD-AC-01 | Default user disabled (`user default off`) | 🔄 | `redis-cli ... ACL LIST` — default user is off | — |
| RD-AC-02 | All service accounts have key-pattern restrictions | 🔄 | `redis-cli ... ACL LIST` — all users have `~<pattern>` | — |
| RD-AC-03 | Dangerous commands renamed/disabled | 🔄 | `redis-cli ... FLUSHALL` returns ERR | — |
| RD-AC-04 | `protected-mode yes` | 🔄 | `redis-cli ... CONFIG GET protected-mode` | — |
| RD-AC-05 | ACL credentials managed via Vault | 🔄 | Verify ACL user passwords from Vault | — |

### Backup and Recovery

| # | Check | Status | Verification Method | Last Checked |
|---|---|---|---|---|
| RD-BR-01 | 15-minute RDB save schedule configured | 🔄 | `redis-cli ... CONFIG GET save` | — |
| RD-BR-02 | AOF enabled with `appendfsync everysec` | 🔄 | `redis-cli ... CONFIG GET appendonly` | — |
| RD-BR-03 | Encrypted RDB backup uploaded to MinIO | ❌ | Check MinIO backup bucket | — |
| RD-BR-04 | Restore test performed quarterly | ❌ | DR test log | — |

### Hardening

| # | Check | Status | Verification Method | Last Checked |
|---|---|---|---|---|
| RD-H-01 | `bind` set to internal IP + loopback only | 🔄 | `redis-cli ... CONFIG GET bind` | — |
| RD-H-02 | `maxmemory-policy` set to prevent unbounded growth | 🔄 | `redis-cli ... CONFIG GET maxmemory-policy` | — |
| RD-H-03 | systemd hardening applied | 🔄 | Review redis.service | — |

---

## MinIO Compliance Checklist

### Encryption at Rest

| # | Check | Status | Verification Method | Last Checked |
|---|---|---|---|---|
| MN-EAR-01 | SSE-KMS enabled as default for all production buckets | ✅ | `mc encrypt info myminio/socioprophet-*` | 2026-01-27 |
| MN-EAR-02 | KES configured with Vault backend | ✅ | `kes key status minio-default-key` | 2026-01-27 |
| MN-EAR-03 | KES-to-Vault TLS using internal CA | ✅ | KES config has Vault TLS settings | 2026-01-27 |
| MN-EAR-04 | Encryption key rotation within 90 days | 🔄 | `kes key list` — check key creation date | — |
| MN-EAR-05 | Restricted bucket enforces SSE-KMS on every object | ✅ | `mc encrypt info myminio/socioprophet-restricted-data` | 2026-01-27 |

### Encryption in Transit

| # | Check | Status | Verification Method | Last Checked |
|---|---|---|---|---|
| MN-EIT-01 | HTTPS only (`MINIO_ADDRESS` on 9000, TLS cert present) | ✅ | `openssl s_client -connect minio.internal:9000` | 2026-01-27 |
| MN-EIT-02 | TLS certificate issued by internal CA | ✅ | Vault PKI issue log | 2026-01-27 |
| MN-EIT-03 | Inter-node TLS for distributed deployment | ✅ | All nodes use same multi-SAN certificate | 2026-01-27 |
| MN-EIT-04 | TLS 1.3 enforced (Go crypto/tls config) | ✅ | `openssl s_client -tls1_2 -connect minio.internal:9000` fails | 2026-01-27 |

### Audit Logging

| # | Check | Status | Verification Method | Last Checked |
|---|---|---|---|---|
| MN-AL-01 | Audit webhook configured to Fluentd | 🔄 | `mc admin config get myminio audit_webhook` | — |
| MN-AL-02 | S3 bucket notification events captured for sensitive buckets | 🔄 | `mc event list myminio/socioprophet-restricted-data` | — |
| MN-AL-03 | Audit records in central OpenSearch index | 🔄 | Query `minio-audit-*` index | — |
| MN-AL-04 | Audit archive bucket has WORM retention | ✅ | `mc retention info myminio/socioprophet-audit-archive` | 2026-01-27 |

### Access Control

| # | Check | Status | Verification Method | Last Checked |
|---|---|---|---|---|
| MN-AC-01 | All buckets have explicit bucket policies (no public access) | ✅ | `mc anonymous get myminio/socioprophet-*` returns "Access Denied" | 2026-01-27 |
| MN-AC-02 | Deny non-TLS access bucket policy applied | ✅ | HTTP request returns 403 | 2026-01-27 |
| MN-AC-03 | OIDC integration configured | 🔄 | `mc admin config get myminio identity_openid` | — |
| MN-AC-04 | Service accounts use IAM policies (no admin policy) | ✅ | `mc admin user list myminio` — check policy assignments | 2026-01-27 |
| MN-AC-05 | Browser console disabled in production | ✅ | `MINIO_BROWSER=off` in environment | 2026-01-27 |

### Backup and Recovery

| # | Check | Status | Verification Method | Last Checked |
|---|---|---|---|---|
| MN-BR-01 | Site replication configured to DR site | ✅ | `mc admin replicate status myminio` | 2026-01-27 |
| MN-BR-02 | Erasure coding set to EC:4 | ✅ | `mc admin info myminio` | 2026-01-27 |
| MN-BR-03 | Lifecycle policy expires old backup objects | ✅ | `mc ilm rule list myminio/socioprophet-backups` | 2026-01-27 |
| MN-BR-04 | Quarterly DR failover test performed | ❌ | DR test log | — |

### Hardening

| # | Check | Status | Verification Method | Last Checked |
|---|---|---|---|---|
| MN-H-01 | `MINIO_ADDRESS` bound to internal IP only | ✅ | Network listener check | 2026-01-27 |
| MN-H-02 | Console port restricted to management VLAN | ✅ | Firewall rule verification | 2026-01-27 |
| MN-H-03 | `MINIO_BROWSER=off` | ✅ | Environment check | 2026-01-27 |
| MN-H-04 | Kubernetes NetworkPolicy applied to MinIO pods | ✅ | `kubectl get networkpolicy -n data-layer` | 2026-01-27 |

---

## RocksDB Compliance Checklist

### Encryption at Rest

| # | Check | Status | Verification Method | Last Checked |
|---|---|---|---|---|
| RK-EAR-01 | `EncryptionProvider` initialized with AES-256-CTR | ❌ | Code review of RocksDB initialization | — |
| RK-EAR-02 | Block encryption key derived via HKDF-SHA-256 from Vault | ❌ | Code review of key derivation | — |
| RK-EAR-03 | Data directory on LUKS-encrypted volume | ❌ | `cryptsetup status /dev/mapper/rocksdb_data` | — |
| RK-EAR-04 | Backup archives encrypted with AES-256-GCM | ❌ | Verify backup pipeline | — |
| RK-EAR-05 | Encryption key rotation every 90 days | ❌ | Application restart schedule + Vault key rotation | — |

### Encryption in Transit

| # | Check | Status | Verification Method | Last Checked |
|---|---|---|---|---|
| RK-EIT-01 | Replication stream uses TLS 1.3 | 🔄 | Code review of replication transport config | — |
| RK-EIT-02 | Client certificate required for replication connections | 🔄 | Code review | — |

### Audit Logging

| # | Check | Status | Verification Method | Last Checked |
|---|---|---|---|---|
| RK-AL-01 | Application-level audit logging implemented for all key operations | ❌ | Code review of RocksDB wrapper | — |
| RK-AL-02 | Audit events forwarded to Fluentd | ❌ | Fluentd configuration | — |
| RK-AL-03 | Audit records include required fields (see AUDIT-LOGGING.md) | ❌ | Code review + sample log record | — |

### Access Control

| # | Check | Status | Verification Method | Last Checked |
|---|---|---|---|---|
| RK-AC-01 | Application RBAC wrapper implemented | ❌ | Code review | — |
| RK-AC-02 | Key-space partitioning enforced per caller | ❌ | Code review | — |
| RK-AC-03 | Data directory permissions 700 (no world access) | ❌ | `find /var/lib/rocksdb -perm /o+rwx` returns nothing | — |

### Backup and Recovery

| # | Check | Status | Verification Method | Last Checked |
|---|---|---|---|---|
| RK-BR-01 | Checkpoint-based backup configured | ❌ | Code review | — |
| RK-BR-02 | Backup archive encrypted and uploaded to MinIO | ❌ | MinIO backup bucket | — |
| RK-BR-03 | Quarterly restore test | ❌ | DR test log | — |

### Hardening

| # | Check | Status | Verification Method | Last Checked |
|---|---|---|---|---|
| RK-H-01 | Data and WAL directories created with mode 700 | ❌ | `stat /var/lib/rocksdb/data` | — |
| RK-H-02 | Separate LUKS mount for RocksDB data | ❌ | Mount table | — |
| RK-H-03 | RocksDB service runs as dedicated non-root user | ❌ | `ps aux | grep rocksdb` | — |

---

## NIST 800-53 Control Compliance Matrix

| Control | Control Title | PG | MG | ES | RD | MN | RK | Overall |
|---|---|---|---|---|---|---|---|---|
| AC-2 | Account Management | 🔄 | 🔄 | ✅ | 🔄 | ✅ | ❌ | 🔄 |
| AC-3 | Access Enforcement | ✅ | ✅ | ✅ | 🔄 | ✅ | ❌ | 🔄 |
| AC-6 | Least Privilege | ✅ | ✅ | ✅ | 🔄 | ✅ | ❌ | 🔄 |
| AU-2 | Event Logging | 🔄 | 🔄 | ✅ | 🔄 | 🔄 | ❌ | 🔄 |
| AU-9 | Audit Protection | 🔄 | 🔄 | ✅ | ❌ | ✅ | ❌ | 🔄 |
| AU-11 | Audit Retention | 🔄 | 🔄 | ✅ | ❌ | 🔄 | ❌ | 🔄 |
| CM-6 | Configuration Settings | 🔄 | 🔄 | ✅ | 🔄 | ✅ | ❌ | 🔄 |
| CM-7 | Least Functionality | 🔄 | ✅ | ✅ | 🔄 | ✅ | ❌ | 🔄 |
| CP-9 | System Backup | 🔄 | 🔄 | ✅ | ❌ | ✅ | ❌ | 🔄 |
| IA-2 | Identification/Authentication | ✅ | ✅ | ✅ | 🔄 | 🔄 | ❌ | 🔄 |
| IA-5 | Authenticator Management | ✅ | ✅ | ✅ | 🔄 | 🔄 | ❌ | 🔄 |
| SC-7 | Boundary Protection | 🔄 | 🔄 | ✅ | 🔄 | ✅ | ❌ | 🔄 |
| SC-8 | Transmission Confidentiality | ✅ | ✅ | ✅ | 🔄 | ✅ | 🔄 | 🔄 |
| SC-28 | Protection at Rest | 🔄 | 🔄 | ✅ | 🔄 | ✅ | ❌ | 🔄 |
| SI-2 | Flaw Remediation | 🔄 | 🔄 | 🔄 | 🔄 | 🔄 | 🔄 | 🔄 |

---

## Compliance Status Legend

| Symbol | Meaning |
|---|---|
| ✅ | Implemented and verified (automated check or manual review ≤ 90 days) |
| 🔄 | In progress — implementation underway per Q2–Q4 2026 timeline |
| ❌ | Not started — scheduled per timeline in `INDEX.md` |
| ⚠️ | Attention required — automated check failing or exception pending |
| N/A | Not applicable to this system |
