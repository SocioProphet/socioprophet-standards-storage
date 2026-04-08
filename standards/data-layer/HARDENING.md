# Database Hardening Standards

This document uses RFC 2119 language: **MUST**, **SHOULD**, **MAY**.

## 1. Scope

This standard defines security hardening procedures for all data-layer systems, satisfying
NIST SP 800-53 SC-7, SI-2, CM-6, and CM-7.

## 2. Network Isolation

- Data systems MUST NOT be directly reachable from the public internet.
- Access MUST be restricted to the application-tier network segment; direct DBA shell access
  from developer workstations MUST require a bastion host, MFA, and a time-limited access request
  recorded in the audit log.
- Firewall / security-group rules MUST use IP-address whitelisting; open-world rules
  (`0.0.0.0/0`) are prohibited.
- Each data system MUST listen on a non-standard port OR be protected by a network-layer ACL
  that limits exposure to only approved source CIDRs.

## 3. Authentication Hardening

- Default credentials supplied by the vendor MUST be replaced before the system is connected
  to any network.
- Service account credentials MUST be stored in the platform secrets manager; they MUST NOT
  appear in:
  - Source code or configuration files committed to VCS
  - Container images or build artifacts
  - Plaintext environment variable files stored on disk
- Password policies MUST comply with NIST SP 800-63B as defined in
  [ACCESS-CONTROL.md](ACCESS-CONTROL.md).
- Account lockout MUST be enforced after 10 consecutive failed authentication attempts.

## 4. Configuration Hardening

### 4.1 TLS / Encryption

- SSL/TLS MUST be enabled; plaintext connections MUST be rejected (see
  [ENCRYPTION-IN-TRANSIT.md](ENCRYPTION-IN-TRANSIT.md)).
- Weak cipher suites (RC4, DES, 3DES, export-grade ciphers) MUST be explicitly disabled.
- Server configuration MUST be verified with a TLS scanner (e.g., `testssl.sh`) after every
  certificate rotation.

### 4.2 Minimal Attack Surface

- All unnecessary services, plugins, and extensions MUST be disabled or uninstalled.
  Enable only what is required for the current use case.
- PostgreSQL: disable `pg_read_server_files`, `pg_write_server_files` for non-admin roles.
- MongoDB: disable `--httpInterface` (removed in 3.6, but confirm absent in config).
- Elasticsearch: disable the deprecated HTTP basic auth in favour of X-Pack.
- Redis: disable or rename dangerous commands (`FLUSHDB`, `FLUSHALL`, `CONFIG`, `DEBUG`,
  `SHUTDOWN`, `SLAVEOF`, `REPLICAOF`, `BGREWRITEAOF`, `BGSAVE`).

### 4.3 Audit Logging Level

- Logging MUST be set to capture all authentication, authorization, and data-modification
  events as defined in [AUDIT-LOGGING.md](AUDIT-LOGGING.md).
- Log verbosity MUST NOT be reduced below the audit-minimum level in production.

### 4.4 Memory Safety

- Redis: set `maxmemory` and `maxmemory-policy` to prevent unbounded memory growth that could
  cause OOM-based eviction of audit data.
- MongoDB: set `wiredTigerCacheSizeGB` appropriately to avoid swapping sensitive data to disk
  unencrypted.

## 5. Vulnerability Management

- Critical CVEs (CVSS 9.0+) MUST be patched within **7 days** of public disclosure.
- High CVEs (CVSS 7.0–8.9) MUST be patched within **30 days**.
- Medium and Low CVEs MUST be scheduled within the next regular maintenance window.
- Patches MUST be applied first in a staging environment with a defined test plan before
  production deployment.
- Rollback procedures MUST be documented and tested for every patch deployment.
- Patch activity MUST be recorded in the audit log with the CVE reference, patch version,
  operator, and deployment timestamp.

## 6. Hardening Verification

- A CIS Benchmark or equivalent hardening checklist MUST be run against each new system
  deployment and after major version upgrades.
- Results MUST be documented; any failed checks that are accepted as a risk MUST have a written
  exception signed by the Security Officer.
- Automated configuration-drift detection MUST alert within 1 hour of any out-of-band change
  to a hardening-relevant setting.
# Hardening — Data Layer FIPS 140-2/140-3 Standard

- Last updated: 2026-01-27
- Status: Active governance document
- Owner: Infrastructure Team + Platform DBA Team
- Standard references: NIST SP 800-53 CM-6, CM-7, SI-2, SI-3, SC-7, FIPS 140-2/140-3

---

## Table of Contents

1. [Overview](#overview)
2. [PostgreSQL](#postgresql)
3. [MongoDB](#mongodb)
4. [Elasticsearch / OpenSearch](#elasticsearch--opensearch)
5. [Redis](#redis)
6. [MinIO](#minio)
7. [RocksDB](#rocksdb)
8. [Container and Kubernetes Network Policies](#container-and-kubernetes-network-policies)
9. [Security Scanning and Vulnerability Management](#security-scanning-and-vulnerability-management)
10. [Configuration Drift Detection](#configuration-drift-detection)
11. [NIST 800-53 Control Compliance](#nist-800-53-control-compliance)

---

## Overview

Hardening reduces the attack surface of each data layer component by disabling unnecessary services, restricting network exposure, enforcing authentication on all interfaces, and applying OS-level controls. Hardened configurations are defined here as the baseline; any deviation requires a documented exception approved by the CISO.

### Hardening Principles

- **Minimal footprint:** Every feature, protocol, extension, and network port that is not explicitly required must be disabled.
- **Defense in depth:** Network isolation, OS hardening, application-level hardening, and container security policies are applied as independent, overlapping layers.
- **Immutable baseline:** Configuration is managed through Infrastructure-as-Code (Terraform/Ansible). Manual configuration changes are detected as drift and auto-remediated within 15 minutes.
- **Patch currency:** Security patches must be applied within 72 hours of a critical CVE disclosure and within 14 days of high-severity CVE disclosure.

---

## PostgreSQL

### Network Binding

```ini
# postgresql.conf — restrict listening addresses
listen_addresses = '10.0.3.10'   # Bind to internal IP only; never 0.0.0.0 or *
port = 5432

# Connection limits — prevent resource exhaustion
max_connections = 200
superuser_reserved_connections = 5
```

### OS-Level Hardening

```bash
# PostgreSQL process user — dedicated non-privileged user
useradd -r -s /bin/false -d /var/lib/postgresql postgres
chown -R postgres:postgres /var/lib/postgresql
chmod 700 /var/lib/postgresql/data

# Data directory — restrictive permissions
chmod 700 /var/lib/postgresql/data
chmod 600 /var/lib/postgresql/data/postgresql.conf
chmod 600 /var/lib/postgresql/data/pg_hba.conf

# Disable unnecessary OS capabilities
# Run in systemd with CapabilityBoundingSet restriction
```

```ini
# /etc/systemd/system/postgresql.service.d/hardening.conf
[Service]
CapabilityBoundingSet = CAP_NET_BIND_SERVICE
NoNewPrivileges = true
PrivateTmp = true
ProtectSystem = strict
ProtectHome = true
ReadWritePaths = /var/lib/postgresql /var/log/postgresql /var/run/postgresql
RestrictAddressFamilies = AF_INET AF_INET6 AF_UNIX
RestrictSUIDSGID = true
```

### Firewall Rules

```bash
# UFW rules for PostgreSQL
ufw allow from 10.0.0.0/8 to any port 5432 proto tcp  # Internal network only
ufw deny from any to any port 5432  # Deny all other access
```

### PostgreSQL Configuration Hardening

```ini
# postgresql.conf — security settings
# Disable trust authentication (never allow passwordless access)
# (enforced in pg_hba.conf — no 'trust' method entries)

# Logging — enable for forensics
log_connections = on
log_disconnections = on
log_duration = off          # Performance; enable only for investigation
log_error_verbosity = default
log_hostname = off          # Do not log hostnames; log IPs only
log_line_prefix = '%m [%p] %q%u@%d %r '
log_statement = 'ddl'       # Log all DDL; DML logged by pgaudit
log_min_duration_statement = 5000  # Log queries slower than 5 seconds

# Security
ssl_prefer_server_ciphers = on
password_encryption = 'scram-sha-256'

# Extensions — only load required extensions
shared_preload_libraries = 'pgaudit,pg_tde,pg_stat_statements'
```

### Disabling Dangerous Functions

```sql
-- Revoke public EXECUTE on functions that can write to the filesystem
REVOKE EXECUTE ON FUNCTION pg_read_file(text) FROM PUBLIC;
REVOKE EXECUTE ON FUNCTION pg_read_file(text, bigint, bigint) FROM PUBLIC;
REVOKE EXECUTE ON FUNCTION pg_ls_dir(text) FROM PUBLIC;
REVOKE EXECUTE ON FUNCTION pg_write_file(text, text) FROM PUBLIC;

-- Restrict COPY TO/FROM PROGRAM to superusers only
-- (superuser access is already MFA-gated per ACCESS-CONTROL.md)
```

---

## MongoDB

### mongod.conf Security Settings

```yaml
# mongod.conf — complete security configuration
net:
  bindIp: 10.0.3.20      # Internal IP only; never 0.0.0.0
  port: 27017
  ipv6: false
  tls:
    mode: requireTLS
    certificateKeyFile: /etc/mongodb/certs/mongod.pem
    CAFile: /etc/mongodb/certs/ca.crt
    allowConnectionsWithoutCertificates: false
    disabledProtocols: "TLS1_0,TLS1_1,TLS1_2"
    FIPSMode: true

security:
  authorization: enabled
  javascriptEnabled: false    # Disable server-side JavaScript (reduces attack surface)
  clusterAuthMode: x509
  enableEncryption: true
  kmip:
    serverName: vault.internal
    port: 5696
    clientCertificateFile: /etc/mongodb/certs/kmip-client.pem
    serverCAFile: /etc/mongodb/certs/kmip-ca.pem

operationProfiling:
  mode: slowOp
  slowOpThresholdMs: 100

storage:
  dbPath: /var/lib/mongodb
  wiredTiger:
    engineConfig:
      journalCompressor: snappy
    collectionConfig:
      blockCompressor: snappy

systemLog:
  destination: file
  path: /var/log/mongodb/mongod.log
  logAppend: true
  logRotate: reopen
  verbosity: 0
  component:
    accessControl:
      verbosity: 1     # Log auth events
    network:
      verbosity: 1     # Log connection events
```

### Disabling Server-Side JavaScript

```javascript
// Confirm JavaScript is disabled
db.adminCommand({ serverStatus: 1 }).security
// Expected: { "javascriptEnabled": false }
```

### mongocryptd Isolation

```bash
# mongocryptd must listen on local Unix socket only
mongocryptd --port 27020 --idleShutdownTimeoutSecs 60 --logpath /var/log/mongodb/mongocryptd.log

# Firewall: block external access to mongocryptd port
ufw deny from any to any port 27020
```

---

## Elasticsearch / OpenSearch

### Network Settings

```yaml
# elasticsearch.yml — network hardening
network.host: 10.0.3.30    # Internal IP only
http.port: 9200
transport.port: 9300

# Disable cross-origin requests
http.cors.enabled: false

# Security bootstrap checks (must pass before cluster starts)
xpack.security.enabled: true
xpack.security.fips_mode.enabled: true

# Prevent Elasticsearch from running as root
# (enforced at OS/container level; Elasticsearch refuses to start as root)
```

### Bootstrap Checks

Elasticsearch performs mandatory bootstrap checks before starting. All of the following must pass:

| Check | Required Setting |
|---|---|
| File descriptor limit | `ulimit -n 65536` minimum |
| Memory lock | `bootstrap.memory_lock: true` |
| Max virtual memory | `vm.max_map_count = 262144` |
| JVM heap | Set to 50% of available RAM (max 32GB) |
| Swapping disabled | `swapoff -a`; `vm.swappiness = 0` |

```yaml
# elasticsearch.yml
bootstrap.memory_lock: true
```

```bash
# /etc/security/limits.conf
elasticsearch soft memlock unlimited
elasticsearch hard memlock unlimited
elasticsearch soft nofile 65536
elasticsearch hard nofile 65536
```

### Cluster Isolation

```yaml
# elasticsearch.yml — cluster isolation
discovery.seed_hosts:
  - "es-node-01.internal:9300"
  - "es-node-02.internal:9300"
  - "es-node-03.internal:9300"
cluster.initial_master_nodes:
  - "es-node-01"
  - "es-node-02"
  - "es-node-03"

# Prevent accidental cluster joining from unauthorized nodes
cluster.name: socioprophet-production  # Unique cluster name
node.name: es-node-01                  # Unique node name
```

### Disabling Dangerous APIs

```yaml
# elasticsearch.yml — disable unnecessary features
# Disable dynamic scripting except where required
script.allowed_types: stored
script.allowed_contexts: search, update

# Disable unsecured monitoring APIs
xpack.monitoring.enabled: false  # Use external APM instead
```

---

## Redis

### Protected Mode and Bind Address

```conf
# redis.conf — network hardening
protected-mode yes         # Require auth if not localhost
bind 10.0.3.40 127.0.0.1   # Internal IP + localhost only
port 0                     # Disable plain-text port completely
tls-port 6380              # TLS only

# Authentication — strong password via Vault
requirepass ""             # Empty: use ACL system instead (see ACCESS-CONTROL.md)
# ACL file manages all user authentication

# Disable all remote admin
# CONFIG and SHUTDOWN are renamed (see ACCESS-CONTROL.md)
```

### Rename Dangerous Commands

```conf
# redis.conf — rename dangerous commands
# Note: Same configuration as ACCESS-CONTROL.md; ensure consistency
rename-command FLUSHALL    ""
rename-command FLUSHDB     ""
rename-command DEBUG       ""
rename-command CONFIG      "CONFIG-__ADMIN_ONLY__"
rename-command SHUTDOWN    "SHUTDOWN-__ADMIN_ONLY__"
rename-command REPLICAOF   "REPLICAOF-__ADMIN_ONLY__"
rename-command SLAVEOF     ""      # Deprecated; disable entirely
rename-command MODULE      ""      # No module loading in production
rename-command RESET       "RESET-__ADMIN_ONLY__"
```

### Resource Limits

```conf
# redis.conf — resource limits to prevent DoS
maxmemory 8gb
maxmemory-policy allkeys-lru

# Connection limits
maxclients 1000
tcp-backlog 511
timeout 300             # Disconnect idle clients after 5 minutes
tcp-keepalive 60
```

### OS-Level Hardening

```bash
# Redis process isolation
useradd -r -s /bin/false -d /var/lib/redis redis
chown -R redis:redis /var/lib/redis /var/log/redis
chmod 700 /var/lib/redis
```

```ini
# /etc/systemd/system/redis.service.d/hardening.conf
[Service]
NoNewPrivileges = true
PrivateTmp = true
ProtectSystem = strict
ProtectHome = true
ReadWritePaths = /var/lib/redis /var/log/redis /var/run/redis
RestrictAddressFamilies = AF_INET AF_INET6 AF_UNIX
MemoryLimit = 10G
```

---

## MinIO

### Network Policies

```bash
# MinIO listens on TLS only
MINIO_VOLUMES="/data{1...8}"
# Bind to internal interface
MINIO_ADDRESS=10.0.3.50:9000
MINIO_CONSOLE_ADDRESS=10.0.3.50:9001  # Console on separate port; restrict further
```

### Admin API Restrictions

```bash
# Restrict MinIO admin operations to dedicated management network
# Using network policy (Kubernetes) or firewall rule (bare metal)

# Disable browser-based console in production (use mc CLI only)
MINIO_BROWSER=off

# Restrict console to management VLAN
ufw allow from 10.0.100.0/24 to any port 9001  # Management VLAN only
ufw deny from any to any port 9001             # Deny all other console access
```

### Erasure Set Configuration

```bash
# Minimum erasure set for production: EC:4 (4 data, 4 parity)
# This configuration survives loss of any 4 drives in an 8-drive set
mc admin config set myminio storage_class \
  standard="EC:4"

# Verify erasure configuration
mc admin info myminio | grep -A 5 "Erasure"
```

---

## RocksDB

### File Permission Requirements

```bash
# RocksDB data and WAL directories — strict permissions
DATA_DIR="/var/lib/rocksdb/data"
WAL_DIR="/var/lib/rocksdb/wal"
BACKUP_DIR="/backup/rocksdb"

install -d -m 700 -o rocksdb-svc -g rocksdb-svc "${DATA_DIR}"
install -d -m 700 -o rocksdb-svc -g rocksdb-svc "${WAL_DIR}"
install -d -m 700 -o rocksdb-svc -g rocksdb-svc "${BACKUP_DIR}"

# Verify: no world-readable files in RocksDB directories
find "${DATA_DIR}" "${WAL_DIR}" -perm /o+r -o -perm /o+w -o -perm /o+x 2>/dev/null \
  | while read f; do echo "PERMISSION VIOLATION: $f"; done
```

### Directory Isolation

RocksDB data directories must be isolated from application directories:

```bash
# Separate mount point for RocksDB data (LUKS-encrypted volume)
# Mount separately from the OS and application volumes
cryptsetup luksOpen /dev/sdc rocksdb_data
mkfs.xfs /dev/mapper/rocksdb_data
mount /dev/mapper/rocksdb_data /var/lib/rocksdb

# XFS ACLs for additional isolation
setfacl -m u:rocksdb-svc:rwx /var/lib/rocksdb
setfacl -m g:rocksdb-svc:rx /var/lib/rocksdb
setfacl -m o::--- /var/lib/rocksdb
```

---

## Container and Kubernetes Network Policies

All data layer components deployed in Kubernetes must have explicit NetworkPolicy resources that deny all traffic by default and permit only documented communication paths.

### Default Deny Policy

```yaml
# Apply to all database namespaces
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-all
  namespace: data-layer
spec:
  podSelector: {}
  policyTypes:
    - Ingress
    - Egress
```

### PostgreSQL Network Policy

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-postgres
  namespace: data-layer
spec:
  podSelector:
    matchLabels:
      app: postgres
  policyTypes:
    - Ingress
    - Egress
  ingress:
    - from:
        - namespaceSelector:
            matchLabels:
              name: socioprophet-app
          podSelector:
            matchLabels:
              db-access: postgres
      ports:
        - protocol: TCP
          port: 5432
    - from:
        - namespaceSelector:
            matchLabels:
              name: monitoring
      ports:
        - protocol: TCP
          port: 9187   # postgres_exporter
  egress:
    - to:
        - namespaceSelector:
            matchLabels:
              name: vault
      ports:
        - protocol: TCP
          port: 8200
    - to:
        - namespaceSelector: {}
          podSelector:
            matchLabels:
              k8s-app: kube-dns
      ports:
        - protocol: UDP
          port: 53
```

### MongoDB Network Policy

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-mongodb
  namespace: data-layer
spec:
  podSelector:
    matchLabels:
      app: mongodb
  policyTypes:
    - Ingress
    - Egress
  ingress:
    - from:
        - namespaceSelector:
            matchLabels:
              name: socioprophet-app
          podSelector:
            matchLabels:
              db-access: mongodb
      ports:
        - protocol: TCP
          port: 27017
    - from:
        - podSelector:
            matchLabels:
              app: mongodb    # Replica set internal communication
      ports:
        - protocol: TCP
          port: 27017
  egress:
    - to:
        - podSelector:
            matchLabels:
              app: mongodb    # Replica set peer connections
      ports:
        - protocol: TCP
          port: 27017
    - to:
        - namespaceSelector:
            matchLabels:
              name: vault
      ports:
        - protocol: TCP
          port: 5696    # KMIP
```

### Pod Security Standards

```yaml
# Kubernetes Pod Security Policy / Security Context for database pods
apiVersion: v1
kind: Pod
spec:
  securityContext:
    runAsNonRoot: true
    runAsUser: 999        # Database service UID
    fsGroup: 999
    seccompProfile:
      type: RuntimeDefault
  containers:
    - name: postgres
      securityContext:
        allowPrivilegeEscalation: false
        readOnlyRootFilesystem: true
        capabilities:
          drop:
            - ALL
          add:
            - NET_BIND_SERVICE   # Only if binding to port < 1024
```

---

## Security Scanning and Vulnerability Management

### Container Image Scanning

```yaml
# CI/CD pipeline — Trivy image scan for all database sidecar images
- name: Scan database images
  run: |
    trivy image \
      --exit-code 1 \
      --severity CRITICAL,HIGH \
      --ignore-unfixed \
      --format sarif \
      --output trivy-results.sarif \
      postgres:15-alpine

    trivy image --exit-code 1 --severity CRITICAL,HIGH \
      mongo:7.0-enterprise

    trivy image --exit-code 1 --severity CRITICAL,HIGH \
      docker.elastic.co/elasticsearch/elasticsearch:8.12.0

    trivy image --exit-code 1 --severity CRITICAL,HIGH \
      redis:7.2-alpine

    trivy image --exit-code 1 --severity CRITICAL,HIGH \
      minio/minio:latest
```

### CVE Patch Timeline

| Severity | Patch Deadline | Process |
|---|---|---|
| Critical (CVSS ≥ 9.0) | 72 hours | Emergency change; skip standard change window |
| High (CVSS 7.0–8.9) | 14 days | Standard change process |
| Medium (CVSS 4.0–6.9) | 60 days | Batch with next maintenance window |
| Low (CVSS < 4.0) | 180 days | Planned maintenance |

### Configuration CIS Benchmark Scanning

```bash
# Run CIS benchmark scans quarterly
# PostgreSQL
docker run --rm \
  -v /var/lib/postgresql:/var/lib/postgresql:ro \
  -v /etc/postgresql:/etc/postgresql:ro \
  instrumentisto/cis-docker-benchmark:latest postgresql

# MongoDB
lynis audit system --tests-from-group malware,authentication,storage
```

---

## Configuration Drift Detection

All database configurations are managed as Infrastructure-as-Code and must match the declared state at all times.

### Drift Detection with Ansible

```yaml
# ansible/playbooks/detect-drift.yml
- name: Detect PostgreSQL configuration drift
  hosts: postgres_servers
  tasks:
    - name: Check postgresql.conf against baseline
      ansible.builtin.template:
        src: templates/postgresql.conf.j2
        dest: /etc/postgresql/15/main/postgresql.conf
        mode: '0600'
      check_mode: yes
      register: pg_conf_drift

    - name: Alert on drift
      when: pg_conf_drift.changed
      ansible.builtin.uri:
        url: "https://alertmanager.internal/api/v2/alerts"
        method: POST
        body_format: json
        body:
          - labels:
              alertname: ConfigurationDrift
              severity: warning
              system: postgresql
              host: "{{ inventory_hostname }}"
```

### Automated Remediation

```bash
#!/bin/bash
# drift-remediation.sh — run every 15 minutes via cron
ansible-playbook /ansible/playbooks/postgres-hardening.yml \
  --limit "{{ affected_host }}" \
  --tags "configuration" \
  --diff \
  2>&1 | tee -a /var/log/drift-remediation.log

# If drift was found and remediated, notify Security Engineering
if grep -q "changed" /var/log/drift-remediation.log; then
  alert "Configuration drift detected and remediated on ${HOST}. Review /var/log/drift-remediation.log"
fi
```

---

## NIST 800-53 Control Compliance

| Control | Title | Implementation |
|---|---|---|
| CM-6 | Configuration Settings | CIS benchmark baselines; IaC-managed configurations; drift detection |
| CM-7 | Least Functionality | All unnecessary ports, services, and features disabled per-system above |
| CM-8 | System Component Inventory | All database instances tracked in CMDB; Kubernetes namespace manifest |
| SI-2 | Flaw Remediation | CVE patch timeline enforced; Trivy scanning in CI/CD |
| SI-3 | Malware Protection | Container image scanning; read-only root filesystem; no arbitrary code execution |
| SC-7 | Boundary Protection | Kubernetes NetworkPolicy; firewall rules; bind to internal IPs only |
| SC-28 | Protection of Information at Rest | All data directories on LUKS-encrypted volumes + storage engine encryption |
| SA-11 | Developer Security Testing | Security scanning integrated into CI/CD pipeline for database image builds |
