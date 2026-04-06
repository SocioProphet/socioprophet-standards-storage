# Audit Logging — Data Layer FIPS 140-2/140-3 Standard

- Last updated: 2026-01-27
- Status: Active governance document
- Owner: Security Engineering
- Standard references: NIST SP 800-53 AU-2, AU-6, AU-9, AU-12, AU-14, FIPS 140-2/140-3

---

## Table of Contents

1. [Overview](#overview)
2. [PostgreSQL — pgaudit](#postgresql--pgaudit)
3. [MongoDB — Audit Log](#mongodb--audit-log)
4. [Elasticsearch / OpenSearch — Audit Logging](#elasticsearch--opensearch--audit-logging)
5. [Redis — ACL Log and Command Audit](#redis--acl-log-and-command-audit)
6. [MinIO — Audit Logging](#minio--audit-logging)
7. [RocksDB — Application-Level Audit Requirements](#rocksdb--application-level-audit-requirements)
8. [Centralized Audit Log Aggregation](#centralized-audit-log-aggregation)
9. [Immutable Audit Log Requirements](#immutable-audit-log-requirements)
10. [Log Format Standard](#log-format-standard)
11. [Retention Policy](#retention-policy)
12. [NIST 800-53 Control Compliance](#nist-800-53-control-compliance)

---

## Overview

Audit logging is a mandatory control for all data layer components. Every access event, authentication attempt, privilege escalation, schema change, and administrative operation must produce a structured, tamper-evident audit record. These records are the foundation for incident investigation, compliance certification, and regulatory reporting.

### Audit Logging Principles

- **Completeness:** Log every event category defined per system below. Absence of a log entry must not be possible for covered event types.
- **Integrity:** Audit records must be cryptographically signed or hash-chained to detect tampering.
- **Immutability:** Once written, audit records must not be modifiable or deletable by any database-level user, including superusers.
- **Availability:** Audit logs must be available for query within 15 minutes of the event for active investigations.
- **Retention:** Minimum 7-year retention for all audit log records.

### Minimum Event Categories (All Systems)

| Event Category | Examples |
|---|---|
| Authentication | Login success, login failure, logout, credential change |
| Authorization | Permission check success/failure, role change, privilege grant/revoke |
| Data access | SELECT / read operations on Restricted and above data |
| Data modification | INSERT, UPDATE, DELETE, document update, object overwrite |
| Schema/index change | DDL operations, index creation/deletion, mapping change |
| Administrative | Configuration change, server restart, backup initiation |
| Key management | Encryption key access, key rotation, DEK generation |
| Cryptographic operations | TLS handshake events (where configurable) |

---

## PostgreSQL — pgaudit

### Installation and Configuration

The `pgaudit` extension provides session-level and object-level auditing for PostgreSQL. It is mandatory for all production PostgreSQL instances.

```bash
# Install pgaudit (must match PostgreSQL major version)
apt-get install postgresql-15-pgaudit
```

```ini
# postgresql.conf
shared_preload_libraries = 'pgaudit'

# Session-level audit — log all DDL, role changes, and connection events
pgaudit.log = 'ddl, role, connection'

# Object-level audit — log DML on tables tagged for auditing
pgaudit.log_level = 'log'
pgaudit.log_client = off        # Do not expose audit to client
pgaudit.log_relation = on       # Include relation name in each log record
pgaudit.log_parameter = on      # Log bind parameters (scrub PII in aggregation layer)
pgaudit.log_statement_once = off

# Log rotation
log_destination = 'syslog'
syslog_facility = 'LOCAL0'
syslog_ident = 'postgres'
log_line_prefix = '%m [%p] %q%u@%d '
```

### Object-Level Auditing for Sensitive Tables

```sql
-- Tag sensitive tables for object-level audit (all DML logged)
SELECT pgaudit.set_config('log', 'read,write,dml', false);

-- Apply to specific role (read access on restricted tables)
SECURITY LABEL FOR pgaudit ON TABLE incidents IS 'RESTRICTED';
SECURITY LABEL FOR pgaudit ON TABLE user_pii IS 'RESTRICTED';
SECURITY LABEL FOR pgaudit ON TABLE audit_records IS 'RESTRICTED';
```

### Audit Event Types Captured

| Event Type | pgaudit Log Class | Configuration |
|---|---|---|
| DDL (CREATE, ALTER, DROP) | `ddl` | `pgaudit.log = 'ddl,...'` |
| DML on tagged tables (SELECT) | `read` | Object-level via SECURITY LABEL |
| DML on tagged tables (INSERT/UPDATE/DELETE) | `write` | Object-level via SECURITY LABEL |
| Role and privilege changes | `role` | `pgaudit.log = '...,role,...'` |
| Connection / authentication | `connection` | `pgaudit.log = '...,connection'` |
| Function calls | `function` | `pgaudit.log = '...,function'` |
| All other statements (admin mode only) | `misc` | Enable for superuser sessions only |

### Sample pgaudit Log Record

```
2026-01-27 14:23:01.456 UTC [12345] app_service@socioprophet LOG:
  AUDIT: SESSION,1,1,READ,SELECT,TABLE,public.incidents,
  "SELECT id, title FROM incidents WHERE tenant_id = $1",<not logged>
```

---

## MongoDB — Audit Log

### mongod Audit Configuration

```yaml
# mongod.conf
auditLog:
  destination: file
  format: JSON
  path: /var/log/mongodb/audit.json
  filter: >
    {
      atype: {
        $in: [
          "authenticate", "authCheck", "logout",
          "createCollection", "dropCollection",
          "createDatabase", "dropDatabase",
          "createIndex", "dropIndex",
          "renameCollection",
          "createUser", "dropUser", "updateUser",
          "grantRolesToUser", "revokeRolesFromUser",
          "createRole", "dropRole", "updateRole",
          "find", "insert", "update", "delete",
          "getMore", "aggregate",
          "shutdown", "replSetReconfig",
          "logout"
        ]
      }
    }
```

### Audit Filter for High-Sensitivity Operations

```javascript
// More restrictive filter for Restricted data collections
{
  atype: "find",
  "param.ns": { $regex: "^socioprophet\\.(incidents|user_pii|secrets)" }
}
```

### Sample MongoDB Audit Record

```json
{
  "atype": "authenticate",
  "ts": { "$date": "2026-01-27T14:23:01.456+00:00" },
  "uuid": { "$binary": { "base64": "abc123...", "subType": "04" } },
  "local": { "ip": "10.0.1.10", "port": 27017 },
  "remote": { "ip": "10.0.1.5", "port": 54321 },
  "users": [{ "user": "app_service", "db": "socioprophet" }],
  "roles": [{ "role": "readWrite", "db": "socioprophet" }],
  "result": 0,
  "param": { "user": "app_service", "db": "socioprophet", "mechanism": "SCRAM-SHA-256" }
}
```

### Audit Event Types Captured

| Event Type | atype Value | Notes |
|---|---|---|
| Authentication success/failure | `authenticate` | Includes mechanism (SCRAM-SHA-256) |
| Authorization check | `authCheck` | Per-operation privilege validation |
| User management | `createUser`, `dropUser`, `updateUser` | |
| Role management | `createRole`, `grantRolesToUser`, etc. | |
| Data read (sensitive collections) | `find`, `getMore`, `aggregate` | Filter to sensitive namespaces |
| Data modification | `insert`, `update`, `delete` | |
| DDL operations | `createCollection`, `dropCollection`, `createIndex` | |
| Replica set changes | `replSetReconfig` | |
| Server shutdown | `shutdown` | |

---

## Elasticsearch / OpenSearch — Audit Logging

### X-Pack Audit Configuration

```yaml
# elasticsearch.yml
xpack.security.audit.enabled: true
xpack.security.audit.logfile.emit_node_name: true
xpack.security.audit.logfile.emit_node_host_address: true
xpack.security.audit.logfile.emit_node_host_name: true

# Event categories to log
xpack.security.audit.logfile.events.include:
  - ACCESS_GRANTED
  - ACCESS_DENIED
  - ANONYMOUS_ACCESS_DENIED
  - AUTHENTICATION_SUCCESS
  - AUTHENTICATION_FAILED
  - REALM_AUTHENTICATION_FAILED
  - CONNECTION_GRANTED
  - CONNECTION_DENIED
  - TAMPERED_REQUEST
  - RUN_AS_GRANTED
  - RUN_AS_DENIED
  - SECURITY_CONFIG_CHANGE

# Exclude high-volume non-sensitive events (adjust per deployment)
xpack.security.audit.logfile.events.exclude:
  - SYSTEM_ACCESS_GRANTED

# Output — write to file for Fluentd pickup
xpack.security.audit.outputs: [ logfile ]
```

### Index-Level Audit Filtering

```yaml
# Log access to specific sensitive indices at higher verbosity
xpack.security.audit.logfile.events.include:
  - ACCESS_GRANTED
  - ACCESS_DENIED
xpack.security.audit.logfile.events.filter.index:
  - name: "RESTRICTED_*"  # All restricted-class indices
    events: [ ACCESS_GRANTED, ACCESS_DENIED, AUTHENTICATION_SUCCESS ]
```

### Sample Elasticsearch Audit Record

```json
{
  "@timestamp": "2026-01-27T14:23:01.456Z",
  "event.type": "access_granted",
  "event.action": "indices:data/read/search",
  "node.name": "es-node-01",
  "node.id": "es-node-01-uuid",
  "origin.type": "rest",
  "origin.address": "10.0.1.5:54321",
  "request.id": "req-abc123",
  "indices": ["incidents"],
  "user.name": "app_service",
  "user.realm": "internal",
  "authentication.type": "REALM"
}
```

---

## Redis — ACL Log and Command Audit

Redis does not provide a dedicated audit log in the style of PostgreSQL or MongoDB. A multi-layer approach is required.

### ACL Log Configuration

```conf
# redis.conf
# ACL log captures authorization failures
acllog-max-len 1024

# Log slow commands (captures all commands exceeding threshold)
slowlog-log-slower-than 0   # 0 = log every command (audit mode; adjust per performance requirement)
slowlog-max-len 10000

# Logging
loglevel verbose
logfile /var/log/redis/redis-server.log
syslog-enabled yes
syslog-ident redis
syslog-facility local1
```

### ACL Log Query

```bash
# Query ACL log (authorization failures)
redis-cli -h redis.internal -p 6380 \
  --tls --cacert /etc/ssl/certs/internal-ca.crt \
  --cert /etc/ssl/certs/ops-client.crt \
  --key /etc/ssl/private/ops-client.key \
  ACL LOG

# Reset ACL log after forwarding to SIEM
redis-cli ... ACL LOG RESET
```

### Command Monitoring for Audit

For real-time command-level auditing, a Redis MONITOR proxy is deployed as a sidecar:

```python
# Redis audit proxy — Python example
# Connects as monitor client, forwards to Fluentd
import redis
import json
import logging

def redis_audit_monitor(host, port, certs):
    r = redis.Redis(host=host, port=port, ssl=True, **certs)
    with r.monitor() as m:
        for command in m.listen():
            audit_record = {
                "timestamp": command['time'],
                "client": command['client_address'],
                "db": command['db'],
                "command": command['command'],
                "args": command['args'],
                "system": "redis"
            }
            # Forward to Fluentd
            forward_to_fluentd(audit_record)
```

> `MONITOR` has performance impact. In production, use selective ACL logging combined with the proxy only for privileged operations channels.

### Audit Event Types Captured

| Event Type | Source | Notes |
|---|---|---|
| Authentication failure | ACL LOG | `WRONGPASS` errors |
| Authorization failure | ACL LOG | Command not permitted for user |
| Privileged command execution | MONITOR / slow log | CONFIG SET, DEBUG, REPLICAOF |
| Key expiry events | Keyspace notifications | Enable `notify-keyspace-events "KEx"` |
| Dangerous command use | ACL LOG | Renamed dangerous commands (see HARDENING.md) |

---

## MinIO — Audit Logging

### Audit Log Configuration

```bash
# Enable audit logging via MinIO environment
MINIO_AUDIT_WEBHOOK_ENABLE_PRIMARY=on
MINIO_AUDIT_WEBHOOK_ENDPOINT_PRIMARY=https://fluentd.internal:9880/minio-audit
MINIO_AUDIT_WEBHOOK_AUTH_TOKEN_PRIMARY=<vault-managed-token>
MINIO_AUDIT_WEBHOOK_CLIENT_CERT_PRIMARY=/etc/minio/certs/audit-client.crt
MINIO_AUDIT_WEBHOOK_CLIENT_KEY_PRIMARY=/etc/minio/certs/audit-client.key
```

### Audit via mc admin

```bash
# Configure audit webhook via mc
mc admin config set myminio audit_webhook:primary \
  endpoint="https://fluentd.internal:9880/minio-audit" \
  auth_token="$(vault read -field=token secret/minio/audit-webhook)" \
  client_cert="/etc/minio/certs/audit-client.crt" \
  client_key="/etc/minio/certs/audit-client.key"

mc admin service restart myminio
```

### S3 Audit Events Captured

| Event Type | Description |
|---|---|
| `s3:ObjectCreated:*` | Object PUT, POST, COPY |
| `s3:ObjectRemoved:*` | Object DELETE |
| `s3:ObjectAccessed:Get` | Object GET (Restricted buckets only) |
| `s3:BucketCreated` | Bucket creation |
| `s3:BucketRemoved` | Bucket deletion |
| `s3:BucketPolicyChanged` | Policy modification |
| Admin actions | User create/delete, policy attach/detach, key rotation |

### Sample MinIO Audit Record

```json
{
  "version": "1",
  "deploymentid": "minio-cluster-uuid",
  "time": "2026-01-27T14:23:01.456Z",
  "event": {
    "name": "s3:ObjectCreated:Put",
    "bucket": "socioprophet-artifacts",
    "object": "incidents/2026/01/27/report.parquet",
    "contentType": "application/octet-stream",
    "userMetadata": { "X-Amz-Server-Side-Encryption": "aws:kms" }
  },
  "requestID": "req-abc123",
  "remotehost": "10.0.1.5",
  "userAgent": "socioprophet-storage-service/1.0",
  "accessKey": "socioprophet-storage",
  "sessionToken": ""
}
```

---

## RocksDB — Application-Level Audit Requirements

RocksDB is an embedded library with no built-in audit logging. Application services using RocksDB must implement audit logging at the application layer.

### Required Application Audit Events

Every application wrapping RocksDB must emit audit events for:

| Event | Required Fields |
|---|---|
| Key read | `timestamp`, `key_prefix` (not full key), `caller_identity`, `operation_id` |
| Key write | `timestamp`, `key_prefix`, `value_size_bytes`, `caller_identity`, `operation_id` |
| Key delete | `timestamp`, `key_prefix`, `caller_identity`, `operation_id` |
| Compaction | `timestamp`, `level`, `bytes_compacted`, `service_instance` |
| Backup initiation | `timestamp`, `backup_id`, `encryption_key_version`, `caller_identity` |
| Key rotation | `timestamp`, `old_key_version`, `new_key_version`, `operator_identity` |

### Application Audit Library Interface

```python
# Required audit interface for RocksDB-wrapping services
from socioprophet.audit import DataLayerAuditLogger

logger = DataLayerAuditLogger(
    system="rocksdb",
    service_instance="worker-01",
    fluentd_endpoint="https://fluentd.internal:9880/rocksdb-audit"
)

# Emit audit event on every write
with logger.operation("write", caller_identity=ctx.service_identity) as op:
    db.put(key, value)
    op.record(key_prefix=key[:16], value_size=len(value))
```

---

## Centralized Audit Log Aggregation

All data layer audit logs are aggregated into a central immutable store using the following pipeline:

```
Database Audit Log (file/syslog/webhook)
        │
        ▼
Fluentd Forwarder (per node)
        │  TLS 1.3, mTLS
        ▼
Fluentd Aggregator (HA pair)
        │  Enrichment: add hostname, cluster_id, FIPS_compliance_version
        ▼
OpenSearch (audit index, WORM policy via ISM)
        │
        ▼
S3/MinIO Archive (WORM bucket, 7-year retention)
```

### Fluentd Configuration (Per System Source)

```xml
<!-- /etc/fluentd/conf.d/postgres-audit.conf -->
<source>
  @type syslog
  port 514
  bind 127.0.0.1
  tag postgres.audit
  <parse>
    @type regexp
    expression /^(?<time>[^ ]*) \[(?<pid>[^\]]*)\] (?<user>[^@]*)@(?<database>[^ ]*) (?<message>.*)$/
    time_key time
    time_format %Y-%m-%d %H:%M:%S.%N %Z
  </parse>
</source>

<match postgres.audit>
  @type forward
  <server>
    host fluentd-aggregator.internal
    port 24224
  </server>
  <transport tls>
    ca_path /etc/ssl/certs/internal-ca.crt
    cert_path /etc/ssl/certs/fluentd-client.crt
    private_key_path /etc/ssl/private/fluentd-client.key
    version TLSv1_3
  </transport>
  <buffer>
    @type file
    path /var/log/fluentd/postgres-audit-buffer
    flush_mode interval
    flush_interval 5s
  </buffer>
</match>
```

---

## Immutable Audit Log Requirements

### WORM Storage for OpenSearch Indices

Use the Index State Management (ISM) plugin to enforce write-once, read-many (WORM) semantics:

```json
PUT _plugins/_ism/policies/audit-worm-policy
{
  "policy": {
    "description": "Audit log immutability policy",
    "states": [{
      "name": "hot",
      "actions": [{
        "read_only": {}
      }],
      "transitions": [{
        "state_name": "archive",
        "conditions": { "min_index_age": "90d" }
      }]
    }, {
      "name": "archive",
      "actions": [{
        "read_only": {}
      }],
      "transitions": [{
        "state_name": "delete",
        "conditions": { "min_index_age": "7y" }
      }]
    }]
  }
}
```

### Hash Chain Integrity

Each audit record must include a chained hash linking it to the previous record:

```python
# Audit record hash chain
import hashlib, json

def chain_hash(previous_hash: str, record: dict) -> str:
    """Compute SHA-256 of (previous_hash || record_json)."""
    content = previous_hash + json.dumps(record, sort_keys=True, separators=(',', ':'))
    return hashlib.sha256(content.encode()).hexdigest()

# Record includes:
record = {
    "seq": 1000042,
    "timestamp": "2026-01-27T14:23:01.456Z",
    "system": "postgres",
    "event": "authenticate",
    "user": "app_service",
    "result": "success",
    "prev_hash": "a3f8...",
}
record["hash"] = chain_hash(record["prev_hash"], {k: v for k, v in record.items() if k != "hash"})
```

### WORM Archive in MinIO

```bash
# Enable object locking (WORM) on audit archive bucket
mc mb --with-lock myminio/socioprophet-audit-archive

# Set default retention (governance mode, 7 years)
mc retention set --default GOVERNANCE "7y" myminio/socioprophet-audit-archive
```

---

## Log Format Standard

All audit log records across all systems must be normalized to the following JSON structure before ingestion into the central store:

```json
{
  "schema_version": "1.0",
  "timestamp": "<ISO 8601 with UTC timezone>",
  "event_id": "<UUID v4>",
  "sequence": <monotonically increasing integer per system>,
  "prev_hash": "<SHA-256 of previous record>",
  "hash": "<SHA-256 of this record>",
  "system": "<postgres|mongodb|elasticsearch|redis|minio|rocksdb>",
  "cluster_id": "<cluster identifier>",
  "node_id": "<node hostname>",
  "event_type": "<authenticate|authorize|read|write|ddl|admin|key_management>",
  "event_subtype": "<system-specific subtype>",
  "result": "<success|failure|error>",
  "actor": {
    "type": "<user|service|operator|system>",
    "identity": "<username or CN>",
    "ip_address": "<source IP>",
    "authenticated_via": "<SCRAM-SHA-256|x509|OIDC|LDAP>"
  },
  "resource": {
    "type": "<table|collection|index|key|bucket|object>",
    "name": "<resource name>",
    "database": "<database or namespace>"
  },
  "operation": {
    "type": "<SELECT|INSERT|UPDATE|DELETE|CREATE|DROP|...>",
    "parameters_hash": "<SHA-256 of sanitized parameters — not plaintext>",
    "rows_affected": <integer or null>
  },
  "classification": "<PUBLIC|INTERNAL|CONFIDENTIAL|RESTRICTED|SECRET>",
  "fips_context": {
    "tls_version": "TLSv1.3",
    "cipher_suite": "TLS_AES_256_GCM_SHA384"
  }
}
```

---

## Retention Policy

| Archive Tier | Duration | Storage | Access Pattern |
|---|---|---|---|
| Hot (active) | 0–90 days | OpenSearch (primary cluster) | Real-time query for investigations |
| Warm (recent) | 90 days–1 year | OpenSearch (warm nodes or S3-backed) | On-demand query |
| Cold (compliance) | 1–7 years | MinIO WORM bucket + Glacier-equivalent | Rare; compliance audit only |
| Legal hold | Indefinite (legal order) | Separate WORM bucket | Case-by-case |

Audit logs must never be deleted before the 7-year minimum retention period unless subject to a documented legal destruction order that supersedes the retention requirement. All destruction events must themselves produce an audit record.

---

## NIST 800-53 Control Compliance

| Control | Title | Implementation |
|---|---|---|
| AU-2 | Event Logging | Per-system event categories defined in this document; all required events covered |
| AU-3 | Content of Audit Records | Normalized log format with all required fields (timestamp, actor, resource, result) |
| AU-4 | Audit Log Storage Capacity | Fluentd buffer + OpenSearch sizing monitored; alert at 80% capacity |
| AU-5 | Response to Audit Logging Process Failures | Fluentd alert on buffer full / connection failure; database configured to fail-safe on audit failure |
| AU-6 | Audit Record Review, Analysis, and Reporting | Weekly automated anomaly scan; quarterly manual review by Security Engineering |
| AU-8 | Time Stamps | All timestamps in UTC; time synchronization via NTP (Chrony with authenticated NTP) |
| AU-9 | Protection of Audit Information | WORM storage; hash chains; restricted write access; separate audit log credentials |
| AU-10 | Non-repudiation | Cryptographic signatures on audit records; chain-of-custody via hash chain |
| AU-11 | Audit Record Retention | 7-year minimum per tier policy |
| AU-12 | Audit Record Generation | Each system configured to generate records for all AU-2 event types |
| AU-14 | Session Audit | Database session identifiers included in all log records |
