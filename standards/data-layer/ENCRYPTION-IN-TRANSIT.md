# Encryption in Transit Standards

This document uses RFC 2119 language: **MUST**, **SHOULD**, **MAY**.

## 1. Scope

This standard governs all network communication between clients and data systems, and between
data-system nodes (replication, clustering).  It satisfies NIST SP 800-53 SC-8 and SC-17.

## 2. TLS Version Requirements

- **TLS 1.3** is MANDATORY for all new connections.
- **TLS 1.2** is deprecated; it MAY remain temporarily for legacy clients with written exception,
  but MUST be disabled by Q3 2026.
- TLS 1.0 and TLS 1.1 MUST be disabled immediately.
- SSL 2.0 and SSL 3.0 MUST be disabled.

Approved TLS 1.3 cipher suites:

```
TLS_AES_256_GCM_SHA384
TLS_CHACHA20_POLY1305_SHA256
TLS_AES_128_GCM_SHA256   # minimum; prefer 256-bit where supported
```

## 3. Client-Server Encryption

### 3.1 PostgreSQL

- `ssl = on` MUST be set in `postgresql.conf`.
- `pg_hba.conf` MUST use `hostssl` lines (not `host`) for all non-loopback connections.
- Client certificate verification (`verify-full`) MUST be used for service accounts.

```
# postgresql.conf
ssl = on
ssl_cert_file = '/etc/postgresql/server.crt'
ssl_key_file  = '/etc/postgresql/server.key'
ssl_ca_file   = '/etc/postgresql/ca.crt'
ssl_min_protocol_version = 'TLSv1.3'
```

### 3.2 MongoDB

- `net.tls.mode: requireTLS` MUST be set in `mongod.conf`.
- `net.tls.CAFile` and `net.tls.certificateKeyFile` MUST reference validated certificates.
- Client connections MUST use `tls=true&tlsCAFile=...&tlsCertificateKeyFile=...` in the URI.

```yaml
# mongod.conf excerpt
net:
  tls:
    mode: requireTLS
    certificateKeyFile: /etc/mongodb/server.pem
    CAFile: /etc/mongodb/ca.crt
    disabledProtocols: TLS1_0,TLS1_1,TLS1_2
```

### 3.3 Elasticsearch

- `xpack.security.http.ssl.enabled: true` and
  `xpack.security.transport.ssl.enabled: true` MUST be set.
- Certificate pinning MUST be used for internal service-to-Elasticsearch connections.

```yaml
# elasticsearch.yml excerpt
xpack.security.http.ssl:
  enabled: true
  keystore.path: /etc/elasticsearch/certs/http.p12
  verification_mode: certificate
xpack.security.transport.ssl:
  enabled: true
  verification_mode: certificate
  keystore.path: /etc/elasticsearch/certs/transport.p12
```

### 3.4 Redis

- Redis 6.0+ with `tls-port` and `tls-replication yes` MUST be used.
- Plaintext `port` SHOULD be set to `0` (disabled) in production.

```
# redis.conf excerpt
tls-port 6380
port 0
tls-cert-file /etc/redis/tls/redis.crt
tls-key-file  /etc/redis/tls/redis.key
tls-ca-cert-file /etc/redis/tls/ca.crt
tls-min-version TLSv1.3
```

### 3.5 RocksDB

RocksDB is an embedded library; network communication is handled by the application layer.
The application MUST use TLS 1.3 for any remote access to the host.

### 3.6 MinIO

- `MINIO_SERVER_URL` MUST use `https://`.
- `MINIO_VOLUMES` paths MUST not expose unencrypted traffic outside the host.

```bash
MINIO_SERVER_URL=https://minio.internal:9000
MINIO_TLS_CERT_FILE=/etc/minio/tls/public.crt
MINIO_TLS_KEY_FILE=/etc/minio/tls/private.key
```

## 4. Inter-Node Replication

| System | Requirement |
|---|---|
| MongoDB replica set | mTLS REQUIRED — each node presents a client certificate |
| Elasticsearch cluster | TLS on transport layer REQUIRED |
| PostgreSQL streaming replication | `ssl = on`; standby uses `sslmode=verify-full` |
| Redis cluster / sentinel | TLS REQUIRED (Redis 7.0+ native cluster TLS) |
| MinIO distributed | TLS REQUIRED between MinIO nodes |

## 5. Certificate Management

### 5.1 Certificate Standards

- Certificates MUST be X.509 v3.
- Minimum key strength: **RSA-4096** or **ECDSA P-384**.
- Subject Alternative Names (SANs) MUST be used; Common Name alone is insufficient.

### 5.2 Certificate Pinning

- Internal service-to-database connections MUST pin the CA certificate or leaf certificate.
- Pinned certificate hashes MUST be updated as part of the key-rotation procedure.

### 5.3 OCSP Stapling

- Server certificates MUST enable OCSP Stapling where the TLS implementation supports it.
- Clients MUST enforce OCSP revocation checking for external-facing certificates.

### 5.4 Automated Certificate Rotation

- Certificates MUST be rotated before expiry with at least 30 days overlap.
- Rotation MUST be automated (e.g., cert-manager, Vault PKI).
- Rotation events MUST generate audit log entries.

## 6. Disallowed Configurations

- Plaintext connections (`sslmode=disable`, `tls.mode=disabled`) MUST NOT be used in any
  non-loopback production path.
- Self-signed certificates without a trusted internal CA MUST NOT be used.
- Wildcard certificates (`*.example.com`) MUST NOT be used for data-layer endpoints.
