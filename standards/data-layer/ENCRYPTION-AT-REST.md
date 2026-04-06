# Encryption at Rest Standards

This document uses RFC 2119 language: **MUST**, **SHOULD**, **MAY**.

## 1. Scope

This standard applies to all persistent and in-memory data stores listed in
[INDEX.md](INDEX.md).  It establishes mandatory algorithm choices, key-management procedures,
and validation requirements to satisfy FIPS 140-2/140-3 and NIST SP 800-53 SC-12/SC-13.

## 2. Approved Algorithms

All encryption at rest MUST use **AES-256-GCM**.  No other symmetric cipher is permitted for
new data.  The following algorithms are explicitly disallowed:

- DES, 3DES (Triple-DES)
- RC2, RC4
- Blowfish, Twofish (not FIPS-approved)
- MD5 (not a cipher, but disallowed for integrity use)
- SHA-1 (disallowed for integrity use)
- AES-128 (insufficient key length for FIPS 140-3 at this classification level)

## 3. Per-System Configuration

### 3.1 PostgreSQL

- Enable the `pgcrypto` extension.
- Use `pgp_sym_encrypt` / `pgp_sym_decrypt` with AES-256-GCM for column-level encryption of
  Confidential and Secret fields.
- Tablespace-level encryption (if using transparent data encryption) MUST also use AES-256.

```sql
-- Example: enable pgcrypto
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- Example: encrypt a value
UPDATE sensitive_table
SET secret_col = pgp_sym_encrypt(plain_text, :key, 'cipher-algo=aes256');
```

### 3.2 MongoDB

- Enable native Encrypted Storage Engine (`encryptedFieldsMap` or WiredTiger encryption).
- Set `security.enableEncryption: true` and `security.encryptionCipherMode: AES256-GCM` in
  `mongod.conf`.
- Master key MUST be managed via an external KMIP-compatible HSM or local key file with
  restricted permissions (`0600`).

```yaml
# mongod.conf excerpt
security:
  enableEncryption: true
  encryptionCipherMode: AES256-GCM
  kmip:
    serverName: kmip.internal
    port: 5696
    clientCertificateFile: /etc/mongodb/kmip-client.pem
    serverCAFile: /etc/mongodb/kmip-ca.pem
```

### 3.3 Elasticsearch

- Enable X-Pack security and set `xpack.security.enabled: true`.
- Configure node-level keystore encryption: `xpack.security.transport.ssl.keystore.path`.
- Index-level encryption MUST use the X-Pack Encrypted Snapshot repository or an external
  KMS integration (AES-256-GCM).

### 3.4 Redis

- Use Redis Enterprise with transparent disk encryption (AES-256-GCM) or encrypt AOF/RDB files
  at the filesystem level (LUKS with AES-256-GCM).
- Community Redis MUST store RDB/AOF on an encrypted volume (AES-256-GCM via dm-crypt/LUKS).

### 3.5 RocksDB

- Integrate the RocksDB Encryption Provider via the OpenSSL plugin
  (`rocksdb::NewEncryptedEnv` with `AES256CTR` or `AES256GCM` cipher).
- Key material MUST be supplied via environment variable or PKCS#11 token — never hardcoded.

### 3.6 MinIO

- Enable native server-side encryption: `MINIO_KMS_SECRET_KEY` or an external KMS (Vault, AWS KMS).
- Default bucket encryption MUST be set to SSE-S3 (AES-256-GCM).

```bash
# MinIO environment — SSE with Vault KMS
MINIO_KMS_KES_ENDPOINT=https://kes.internal:7373
MINIO_KMS_KES_KEY_NAME=minio-key
MINIO_KMS_KES_CERT_FILE=/etc/minio/kes-client.crt
MINIO_KMS_KES_KEY_FILE=/etc/minio/kes-client.key
```

## 4. Key Management

### 4.1 Key Generation

- All data encryption keys (DEKs) MUST be derived using **HKDF-SHA256** from a master key
  (MK) held in an HSM or secrets manager.
- DEKs MUST be at least 256 bits.

### 4.2 Key Rotation

- DEKs MUST be rotated on a **90-day cycle** (FIPS requirement).
- Rotation MUST be automated and triggered by the secrets manager or a scheduled CI/CD pipeline.
- Re-encryption of stored data MUST complete before the old key is archived.

### 4.3 HSM Integration

- Systems with PKCS#11 support (PostgreSQL via `openssl-engine`, MongoDB KMIP, MinIO KES) MUST
  use an HSM for master-key storage in Secret-classified deployments.
- HSM MUST be FIPS 140-2 Level 2 validated (minimum) or Level 3 for Secret classification.

### 4.4 Key Escrow

- Each system's active DEK MUST be escrowed in the secrets manager under a separate escrow key.
- Escrow access MUST require dual-person authorization (break-glass procedure).
- Escrow retrieval MUST generate an immutable audit event.

## 5. Validation Procedures

- After each deployment, run a CAVP (Cryptographic Algorithm Validation Program) self-test where
  available (e.g., `openssl speed -evp aes-256-gcm` against a FIPS provider).
- Verify encryption is active by inspecting on-disk files with `file` or vendor tooling and
  confirming they are opaque (not readable as plaintext).
- Automated CI checks MUST scan configuration files to assert no disallowed algorithms appear
  (see [COMPLIANCE-VALIDATION.md](COMPLIANCE-VALIDATION.md)).
- Annual third-party cryptographic review MUST validate algorithm choices and key lengths.
