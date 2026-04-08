# Encryption in Transit — Data Layer FIPS 140-2/140-3 Standard

- Last updated: 2026-01-27
- Status: Active governance document
- Owner: Infrastructure Team + Security Engineering
- Standard references: FIPS 140-2, FIPS 140-3, NIST SP 800-52 Rev 2, RFC 8446

---

## Table of Contents

1. [Overview](#overview)
2. [PostgreSQL](#postgresql)
3. [MongoDB](#mongodb)
4. [Elasticsearch / OpenSearch](#elasticsearch--opensearch)
5. [Redis](#redis)
6. [MinIO](#minio)
7. [RocksDB Replication](#rocksdb-replication)
8. [Certificate Management](#certificate-management)
9. [Approved Cipher Suites](#approved-cipher-suites)
10. [Disallowed Protocols and Cipher Suites](#disallowed-protocols-and-cipher-suites)
11. [Mutual TLS Requirements](#mutual-tls-requirements)
12. [Verification Procedures](#verification-procedures)

---

## Overview

Encryption in transit protects data moving between application services and database systems, between cluster nodes, and between replication partners. All connections to and between data layer components must use TLS 1.3 as the minimum protocol version. TLS 1.2 is prohibited for new connections; existing TLS 1.2 connections must be migrated per the Q2 2026 timeline in `INDEX.md`.

### Scope

This document covers:

- Client-to-server TLS for all six storage systems
- Intra-cluster (node-to-node) TLS for distributed systems
- Replication stream encryption
- Certificate issuance, rotation, and revocation

### TLS 1.3 Requirements

TLS 1.3 removes legacy features that enabled many historical attacks. Key properties required:

- **Forward secrecy by design:** TLS 1.3 mandates ECDHE; there is no negotiation fallback to non-PFS modes.
- **Authenticated encryption:** All TLS 1.3 cipher suites use AEAD (GCM or CHACHA20_POLY1305).
- **Encrypted handshake:** Certificate information is encrypted in TLS 1.3; eavesdroppers cannot determine certificate identity.
- **No renegotiation:** TLS 1.3 eliminates renegotiation, removing the renegotiation MITM vulnerability.

### Mutual TLS (mTLS)

All service-to-database connections from SocioProphet application services must use mutual TLS (mTLS). Clients must present a valid certificate signed by the internal CA (`pki/db-certs`). Database servers must reject connections from clients that do not present a valid certificate.

---

## PostgreSQL

### Server-Side TLS Configuration

```ini
# postgresql.conf
ssl = on
ssl_cert_file = '/etc/postgresql/certs/server.crt'
ssl_key_file  = '/etc/postgresql/certs/server.key'
ssl_ca_file   = '/etc/postgresql/certs/ca.crt'
ssl_crl_file  = '/etc/postgresql/certs/ca.crl'

# TLS 1.3 only
ssl_min_protocol_version = 'TLSv1.3'
ssl_max_protocol_version = 'TLSv1.3'

# Approved cipher suites (TLS 1.3 suites)
ssl_ciphers = 'TLS_AES_256_GCM_SHA384:TLS_CHACHA20_POLY1305_SHA256'
```

### Client Authentication Enforcement (pg_hba.conf)

```conf
# pg_hba.conf — TLS enforcement
# TYPE  DATABASE        USER            ADDRESS                 METHOD
# Require TLS for all non-local connections
hostssl all             all             0.0.0.0/0               scram-sha-256 clientcert=verify-full
hostssl all             all             ::/0                    scram-sha-256 clientcert=verify-full

# Reject non-SSL connections from network
hostnossl all           all             0.0.0.0/0               reject
hostnossl all           all             ::/0                    reject

# Local connections for maintenance (not SSL; restrict to unix socket)
local   all             postgres                                peer
```

### Connection String Validation

Application connection strings must include `sslmode=verify-full`:

```python
# Python — psycopg2
conn = psycopg2.connect(
    host="postgres.internal",
    port=5432,
    dbname="socioprophet",
    user="app_service",
    password=vault_secret,
    sslmode="verify-full",
    sslrootcert="/etc/ssl/certs/internal-ca.crt",
    sslcert="/etc/ssl/certs/app-client.crt",
    sslkey="/etc/ssl/private/app-client.key"
)
```

| sslmode value | Acceptable | Reason |
|---|---|---|
| `verify-full` | ✅ Required | Verifies certificate and hostname |
| `verify-ca` | ⚠️ Conditional | Only for internal services where hostname verification is handled by network policy |
| `require` | ❌ Prohibited | Encrypts but does not verify certificate; vulnerable to MITM |
| `prefer` / `allow` / `disable` | ❌ Prohibited | May fall back to plaintext |

### pg_ident.conf for Certificate CN Mapping

```conf
# pg_ident.conf — map certificate CN to database user
# MAPNAME       SYSTEM-USERNAME         PG-USERNAME
app-services    app_service_cn          app_service
replication     replication_client_cn   replication_user
ops-access      ops_operator_cn         ops_readonly
```

---

## MongoDB

### mongod.conf TLS Configuration

```yaml
# mongod.conf
net:
  port: 27017
  tls:
    mode: requireTLS
    certificateKeyFile: /etc/mongodb/certs/mongod.pem
    CAFile: /etc/mongodb/certs/ca.crt
    allowConnectionsWithoutCertificates: false
    disabledProtocols: "TLS1_0,TLS1_1,TLS1_2"
    allowedTLS1_3Ciphers: "TLS_AES_256_GCM_SHA384:TLS_CHACHA20_POLY1305_SHA256"
    FIPSMode: true
```

> `disabledProtocols: "TLS1_0,TLS1_1,TLS1_2"` combined with `FIPSMode: true` enforces TLS 1.3 exclusively.

### Replica Set Internal TLS

```yaml
# mongod.conf — replica set member internal communication
replication:
  replSetName: "rs0"

net:
  tls:
    mode: requireTLS
    certificateKeyFile: /etc/mongodb/certs/mongod.pem
    clusterAuthMode: x509
    CAFile: /etc/mongodb/certs/ca.crt
```

All replica set members must use x.509 certificates for internal authentication. The certificate CN must match the mongod hostname.

### mongocryptd and CSFLE Transport

When using MongoDB CSFLE (see `ENCRYPTION-AT-REST.md`), the `mongocryptd` process communicates over a local Unix socket only. No network exposure of `mongocryptd` is permitted.

### Client Driver TLS Configuration

```javascript
// Node.js MongoDB driver
const client = new MongoClient('mongodb://mongo.internal:27017', {
  tls: true,
  tlsCAFile: '/etc/ssl/certs/internal-ca.crt',
  tlsCertificateKeyFile: '/etc/ssl/certs/app-client.pem',
  tlsAllowInvalidCertificates: false,
  tlsAllowInvalidHostnames: false,
});
```

---

## Elasticsearch / OpenSearch

### HTTP Layer TLS (Client-to-Node)

```yaml
# elasticsearch.yml
xpack.security.http.ssl.enabled: true
xpack.security.http.ssl.verification_mode: full
xpack.security.http.ssl.certificate_authorities:
  - /etc/elasticsearch/certs/ca.crt
xpack.security.http.ssl.certificate: /etc/elasticsearch/certs/node.crt
xpack.security.http.ssl.key: /etc/elasticsearch/certs/node.key
xpack.security.http.ssl.supported_protocols:
  - TLSv1.3
xpack.security.http.ssl.cipher_suites:
  - TLS_AES_256_GCM_SHA384
  - TLS_CHACHA20_POLY1305_SHA256
```

### Transport Layer TLS (Node-to-Node)

```yaml
# elasticsearch.yml
xpack.security.transport.ssl.enabled: true
xpack.security.transport.ssl.verification_mode: full
xpack.security.transport.ssl.certificate_authorities:
  - /etc/elasticsearch/certs/ca.crt
xpack.security.transport.ssl.certificate: /etc/elasticsearch/certs/node.crt
xpack.security.transport.ssl.key: /etc/elasticsearch/certs/node.key
xpack.security.transport.ssl.supported_protocols:
  - TLSv1.3
xpack.security.transport.ssl.client_authentication: required
```

### Node Certificate Management

Each Elasticsearch node requires a unique certificate with the node's hostname as the Subject Alternative Name (SAN). Use the Vault PKI engine to issue node certificates:

```bash
# Issue a node certificate from Vault PKI
vault write pki/db-certs/issue/elasticsearch-node \
  common_name="es-node-01.internal" \
  alt_names="es-node-01.internal,es-node-01" \
  ip_sans="10.0.1.50" \
  ttl="8760h"

# Output: certificate, private_key, ca_chain
# Write to /etc/elasticsearch/certs/ with appropriate permissions
install -m 640 -o elasticsearch -g elasticsearch node.crt /etc/elasticsearch/certs/
install -m 600 -o elasticsearch -g elasticsearch node.key /etc/elasticsearch/certs/
```

---

## Redis

### Redis TLS Configuration

```conf
# redis.conf — TLS settings
port 0          # Disable plain-text port
tls-port 6380   # TLS-only port

tls-cert-file /etc/redis/certs/redis.crt
tls-key-file  /etc/redis/certs/redis.key
tls-ca-cert-file /etc/redis/certs/ca.crt

# Require client certificates
tls-auth-clients yes

# TLS 1.3 only
tls-protocols "TLSv1.3"
tls-ciphers "TLS_AES_256_GCM_SHA384:TLS_CHACHA20_POLY1305_SHA256"
tls-prefer-server-ciphers yes

# Replication over TLS
tls-replication yes

# Cluster bus over TLS
tls-cluster yes
```

### Redis Sentinel TLS

When using Redis Sentinel for high availability, Sentinel nodes must also enforce TLS:

```conf
# sentinel.conf
tls-port 26380
port 0
tls-cert-file /etc/redis/certs/sentinel.crt
tls-key-file  /etc/redis/certs/sentinel.key
tls-ca-cert-file /etc/redis/certs/ca.crt
tls-auth-clients yes
tls-protocols "TLSv1.3"
```

### Client Connection Example

```python
# Python — redis-py with TLS
import redis, ssl

r = redis.Redis(
    host='redis.internal',
    port=6380,
    ssl=True,
    ssl_certfile='/etc/ssl/certs/app-client.crt',
    ssl_keyfile='/etc/ssl/private/app-client.key',
    ssl_ca_certs='/etc/ssl/certs/internal-ca.crt',
    ssl_check_hostname=True,
    ssl_cert_reqs=ssl.CERT_REQUIRED,
)
```

---

## MinIO

### Server TLS Configuration

```bash
# MinIO TLS certificate placement
# MinIO automatically detects TLS when certs exist at:
install -m 640 -o minio-user -g minio-user public.crt  /etc/minio/certs/public.crt
install -m 600 -o minio-user -g minio-user private.key /etc/minio/certs/private.key
install -m 644 -o minio-user -g minio-user ca.crt      /etc/minio/certs/CAs/internal-ca.crt
```

```bash
# MinIO environment
MINIO_VOLUMES="/data"
# TLS 1.3 enforced by Go TLS stack when certificate is present
# MinIO (written in Go) uses crypto/tls; configure via GODEBUG if needed
GODEBUG=tlsrsakex=0,tlskyber=0  # Disable RSA key exchange; use ECDHE only
```

### Inter-Node Encryption (Distributed MinIO)

```bash
# All inter-node communication in a distributed MinIO deployment uses the
# same TLS certificate. Each node must present a certificate with all node
# hostnames as SANs:
vault write pki/db-certs/issue/minio-node \
  common_name="minio-01.internal" \
  alt_names="minio-01.internal,minio-02.internal,minio-03.internal,minio-04.internal" \
  ip_sans="10.0.2.10,10.0.2.11,10.0.2.12,10.0.2.13" \
  ttl="8760h"
```

### Certificate Management for MinIO

```bash
# Verify TLS configuration
mc alias set myminio https://minio.internal:9000 $ACCESS_KEY $SECRET_KEY \
  --insecure=false

# Check TLS details
openssl s_client -connect minio.internal:9000 -tls1_3 </dev/null 2>&1 \
  | grep -E "(Protocol|Cipher|Certificate)"
```

---

## RocksDB Replication

RocksDB as an embedded store does not natively manage replication. When application services replicate RocksDB state across nodes (e.g., for high availability of local state stores), the replication transport must enforce TLS 1.3.

### Application Replication Transport Requirements

```go
// Go — TLS configuration for RocksDB replication stream
tlsConfig := &tls.Config{
    MinVersion:   tls.VersionTLS13,
    Certificates: []tls.Certificate{clientCert},
    RootCAs:      caCertPool,
    CipherSuites: []uint16{
        tls.TLS_AES_256_GCM_SHA384,
        tls.TLS_CHACHA20_POLY1305_SHA256,
    },
    ServerName: "rocksdb-replica.internal",
}

conn, err := tls.Dial("tcp", "rocksdb-replica.internal:8765", tlsConfig)
```

The application-defined replication protocol must:

1. Use TLS 1.3 with the approved cipher suites.
2. Validate the server certificate against the internal CA.
3. Present a client certificate for mutual authentication.
4. Log all replication connection events to the audit trail.

---

## Certificate Management

### Certificate Authority Hierarchy

```
Internal Root CA (offline; HSM-backed)
└── Data Layer Intermediate CA (Vault PKI engine: pki/db-certs)
    ├── PostgreSQL server and client certificates
    ├── MongoDB node and client certificates
    ├── Elasticsearch node certificates
    ├── Redis server certificates
    ├── MinIO server certificates
    └── Application service client certificates
```

### Certificate Issuance via Vault PKI

```bash
# Issue a database server certificate
vault write pki/db-certs/issue/db-server \
  common_name="postgres-primary.internal" \
  alt_names="postgres-primary.internal,postgres.internal" \
  ip_sans="10.0.3.10" \
  ttl="8760h"  # 365 days; auto-renew at 30-day remaining threshold

# Issue a client certificate for application service
vault write pki/db-certs/issue/app-client \
  common_name="socioprophet-api" \
  ttl="720h"   # 30 days for service client certificates
```

### Certificate Rotation

Certificate rotation is automated through Vault PKI. Each service implementation must:

1. **Watch for expiry:** Monitor the certificate expiry and request renewal when ≤30 days remain.
2. **Reload without restart:** Use TLS session tickets or SIGHUP-based reload where supported.
3. **Revoke old certificates:** After successful rotation, revoke the old certificate through Vault.

```bash
# Revoke an old certificate by serial number
vault write pki/db-certs/revoke \
  serial_number="39:dd:2e:90:b7:23:1f:8d:d3:7d:31:c5:1b:da:84:d0"

# Update CRL
vault write pki/db-certs/crl/rotate
```

### OCSP Stapling

All server certificates must support OCSP stapling. Configure OCSP in PostgreSQL:

```ini
# postgresql.conf
ssl_crl_file = '/etc/postgresql/certs/ca.crl'
# OCSP stapling is handled at the load balancer (HAProxy/nginx) layer
```

For HAProxy in front of PostgreSQL:

```conf
# haproxy.cfg — OCSP stapling
global
    tune.ssl.default-dh-param 4096

frontend postgres_frontend
    bind *:5432 ssl crt /etc/haproxy/certs/postgres.pem \
                    verify required ca-file /etc/haproxy/certs/ca.crt \
                    crl-file /etc/haproxy/certs/ca.crl \
                    no-tls-tickets
    option ssl-hello-chk
```

### Certificate Monitoring

```bash
# Check certificate expiry for all data layer services
for host in postgres.internal mongo.internal es.internal redis.internal minio.internal; do
  expiry=$(echo | openssl s_client -connect ${host}:$(port_for $host) 2>/dev/null \
    | openssl x509 -noout -enddate | cut -d= -f2)
  echo "${host}: expires ${expiry}"
done
```

---

## Approved Cipher Suites

### TLS 1.3 Cipher Suites (Approved)

| Cipher Suite | Key Exchange | Encryption | MAC | Status |
|---|---|---|---|---|
| `TLS_AES_256_GCM_SHA384` | ECDHE (P-384) | AES-256-GCM | SHA-384 | ✅ **Required** |
| `TLS_CHACHA20_POLY1305_SHA256` | ECDHE (X25519) | ChaCha20-Poly1305 | SHA-256 | ✅ **Approved** |
| `TLS_AES_128_GCM_SHA256` | ECDHE (P-256) | AES-128-GCM | SHA-256 | ⚠️ **Conditional** (only where 256-bit is unavailable in a client library) |

> In FIPS 140-3 mode, some implementations restrict `TLS_CHACHA20_POLY1305_SHA256` as ChaCha20 is not in the FIPS 140-2 approved list. Verify your specific FIPS module's support before enabling it. `TLS_AES_256_GCM_SHA384` is the universally compliant default.

### ECDHE Groups (Approved for TLS 1.3 Key Exchange)

| Group | Bit Strength | Status |
|---|---|---|
| P-256 (secp256r1) | 128-bit equivalent | ✅ Approved |
| P-384 (secp384r1) | 192-bit equivalent | ✅ Approved (preferred) |
| P-521 (secp521r1) | 260-bit equivalent | ✅ Approved |
| X25519 | 128-bit equivalent | ⚠️ FIPS 140-3 approved (not 140-2) |

---

## Disallowed Protocols and Cipher Suites

The following must be explicitly disabled in all database TLS configurations:

### Disallowed Protocols

| Protocol | Reason |
|---|---|
| SSLv2 | Protocol-level vulnerabilities; DROWN attack |
| SSLv3 | POODLE attack |
| TLS 1.0 | BEAST, POODLE-TLS attacks; NIST SP 800-52 Rev 2 prohibited |
| TLS 1.1 | Weak cipher support; NIST SP 800-52 Rev 2 prohibited |
| TLS 1.2 | Prohibited for new connections; migration required per Q2 2026 timeline |

### Disallowed TLS 1.2 Cipher Suites (Informational — for migration reference)

| Cipher Suite | Reason |
|---|---|
| `*_RC4_*` | RC4 statistical weaknesses |
| `*_NULL_*` | No encryption |
| `*_anon_*` | No authentication |
| `*_EXPORT_*` | Intentionally weak; FREAK attack |
| `*_DES_*`, `*_3DES_*` | Insufficient key length; Sweet32 |
| `*_MD5` | Weak MAC |
| `TLS_RSA_*` (no ECDHE) | No forward secrecy |
| `*_DHE_RSA_*` with < 3072-bit DH | Insufficient DH parameters |

---

## Mutual TLS Requirements

### Service Identity Matrix

All services connecting to data layer systems must use mTLS. The following matrix defines certificate CN patterns:

| Service | Certificate CN Pattern | Target Systems |
|---|---|---|
| API service | `socioprophet-api` | PostgreSQL, MongoDB, Elasticsearch, Redis |
| Worker service | `socioprophet-worker` | PostgreSQL, MongoDB, Redis |
| Search indexer | `socioprophet-indexer` | Elasticsearch, PostgreSQL |
| Object storage client | `socioprophet-storage` | MinIO |
| Backup agent | `socioprophet-backup` | All systems |
| Monitoring agent | `socioprophet-monitoring` | All systems (read-only) |
| Vault agent | `vault-agent` | All systems (key operations) |

### mTLS Certificate Verification Checklist

For each new service deployment:

- [ ] Service certificate issued by `pki/db-certs` intermediate CA
- [ ] Certificate CN matches service identity pattern
- [ ] Certificate includes `extendedKeyUsage: clientAuth`
- [ ] Certificate stored in Kubernetes Secret with `type: kubernetes.io/tls`
- [ ] Secret mounted read-only at known path (e.g., `/etc/ssl/service/`)
- [ ] Service connection pool configured with `sslmode=verify-full` (or equivalent)
- [ ] Certificate expiry alerting configured (30-day pre-expiry alert to PagerDuty)

---

## Verification Procedures

### Verify TLS Version and Cipher Suite

```bash
# Test TLS 1.3 connection to PostgreSQL
openssl s_client -connect postgres.internal:5432 \
  -starttls postgres \
  -tls1_3 \
  -CAfile /etc/ssl/certs/internal-ca.crt \
  -cert /etc/ssl/certs/test-client.crt \
  -key /etc/ssl/private/test-client.key \
  2>&1 | grep -E "(Protocol|Cipher|Verify)"

# Expected output:
# Protocol  : TLSv1.3
# Cipher    : TLS_AES_256_GCM_SHA384
# Verify return code: 0 (ok)
```

```bash
# Test MongoDB TLS
openssl s_client -connect mongo.internal:27017 \
  -tls1_3 \
  -CAfile /etc/ssl/certs/internal-ca.crt \
  2>&1 | grep -E "(Protocol|Cipher|Verify)"

# Test Elasticsearch TLS
curl -v --cacert /etc/ssl/certs/internal-ca.crt \
     --cert /etc/ssl/certs/app-client.crt \
     --key /etc/ssl/private/app-client.key \
     https://es.internal:9200/_cluster/health 2>&1 \
  | grep -E "(TLS|SSL|Cipher)"

# Test Redis TLS
redis-cli -h redis.internal -p 6380 \
  --tls \
  --cacert /etc/ssl/certs/internal-ca.crt \
  --cert /etc/ssl/certs/app-client.crt \
  --key /etc/ssl/private/app-client.key \
  PING
```

### Automated TLS Compliance Check

See `COMPLIANCE-VALIDATION.md` for the full automated validation script that runs these checks in CI/CD.
