# Encryption at Rest — Data Layer FIPS 140-2/140-3 Standard

- Last updated: 2026-01-27
- Status: Active governance document
- Owner: Platform DBA Team + Security Engineering
- Standard references: FIPS 140-2, FIPS 140-3, NIST SP 800-111, NIST SP 800-57 Part 1

---

## Table of Contents

1. [Overview](#overview)
2. [PostgreSQL](#postgresql)
3. [MongoDB](#mongodb)
4. [Elasticsearch / OpenSearch](#elasticsearch--opensearch)
5. [Redis](#redis)
6. [MinIO](#minio)
7. [RocksDB](#rocksdb)
8. [Key Management — HashiCorp Vault Integration](#key-management--hashicorp-vault-integration)
9. [Key Derivation Standard](#key-derivation-standard)
10. [Key Rotation Schedules](#key-rotation-schedules)
11. [Approved Algorithms Table](#approved-algorithms-table)
12. [Disallowed Algorithms](#disallowed-algorithms)

---

## Overview

Encryption at rest protects stored data from unauthorized disclosure when physical or logical access controls fail. All data layer systems must encrypt persisted data using AES-256-GCM with FIPS-validated cryptographic modules. Encryption keys must never be stored alongside the data they protect; all key material is managed exclusively through HashiCorp Vault with an HSM-backed unseal configuration in production.

### Scope

This document covers:

- Storage engine encryption (transparent data encryption where available)
- File-system level encryption for data directories
- Backup file encryption
- Key material management for all six storage systems

This document does **not** cover application-layer field encryption (governed by the application service security standard) except where it is a required complement to storage-engine encryption for specific data classification levels (see `DATA-CLASSIFICATION.md`).

### General Requirements

- All persistent volumes hosting database data directories must be encrypted.
- Encryption must be enabled at the storage engine level, not only at the volume level, to protect data from engine-level privilege escalation.
- Volume-level encryption (dm-crypt/LUKS with AES-256-XTS) is required as a defense-in-depth layer in addition to, not instead of, storage engine encryption.
- Key material must be derived through HKDF-SHA-256 from Vault-managed master keys and must never appear in configuration files, environment variables, or logs.

---

## PostgreSQL

### pgcrypto Extension

The `pgcrypto` extension provides column-level encryption for specific sensitive fields. It must be installed and configured for any table containing Confidential or above data (see `DATA-CLASSIFICATION.md`).

```sql
-- Install pgcrypto
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- Encrypt a sensitive column using AES-256 (pgp_sym_encrypt uses AES-256-CBC internally;
-- for GCM, use application-side encryption with Vault transit engine)
INSERT INTO sensitive_data (id, encrypted_field)
VALUES (
  gen_random_uuid(),
  pgp_sym_encrypt('sensitive value', current_setting('app.encryption_key'))
);

-- Decrypt
SELECT pgp_sym_decrypt(encrypted_field::bytea, current_setting('app.encryption_key'))
FROM sensitive_data WHERE id = $1;
```

> **Note:** For GCM mode (required for new implementations), use the Vault Transit Secrets Engine from the application layer rather than pgcrypto directly. pgcrypto column encryption is acceptable for existing data where AES-256-CBC is in use during migration.

### Transparent Data Encryption (TDE)

PostgreSQL natively does not ship with TDE. Two compliant approaches are required:

**Option A — pg_tde extension (PostgreSQL 16+):**

```ini
# postgresql.conf
shared_preload_libraries = 'pg_tde'

# Enable TDE for a tablespace
[pg_tde configuration]
default_encryption = on
key_provider = 'vault'
vault_url = 'https://vault.internal:8200'
vault_token_path = '/run/secrets/vault_token'
key_name = 'postgres-tde-key'
```

**Option B — Filesystem encryption as the primary layer (LUKS):**

```bash
# Data directory on LUKS-encrypted volume
cryptsetup luksFormat --cipher aes-xts-plain64 --key-size 512 /dev/sdb
cryptsetup luksOpen /dev/sdb pg_data_encrypted
mkfs.ext4 /dev/mapper/pg_data_encrypted
mount /dev/mapper/pg_data_encrypted /var/lib/postgresql/data
```

Both options may be combined for defense-in-depth.

### Tablespace Encryption

When using pg_tde, tablespace-level encryption should be applied so that all objects within a tablespace inherit encryption automatically:

```sql
-- Create an encrypted tablespace
CREATE TABLESPACE encrypted_ts
  LOCATION '/var/lib/postgresql/data/encrypted'
  WITH (encryption_key_id = 'postgres-tde-key');

-- Move sensitive table to encrypted tablespace
ALTER TABLE sensitive_data SET TABLESPACE encrypted_ts;
```

### WAL Encryption

Write-ahead log (WAL) files contain plaintext data and must be encrypted. When using pg_basebackup for streaming backups, WAL must be encrypted in the archive:

```bash
# pg_basebackup with compression and encryption via Vault-managed key
pg_basebackup \
  --host=localhost \
  --username=replication_user \
  --pgdata=/backup/pg_base \
  --wal-method=stream \
  --compress=gzip \
  --checkpoint=fast
# Post-processing: encrypt the backup archive
vault write transit/encrypt/postgres-backup \
  plaintext=$(base64 /backup/pg_base.tar.gz)
```

---

## MongoDB

### Encrypted Storage Engine (WiredTiger)

MongoDB Enterprise provides native encryption-at-rest through the WiredTiger storage engine. This is the required configuration for all production deployments.

```yaml
# mongod.conf — security section
security:
  enableEncryption: true
  encryptionKeyIdentifier: "mongodb-wiredtiger-key"
  kmip:
    serverName: vault.internal
    port: 5696
    clientCertificateFile: /etc/mongodb/kmip-client.pem
    clientCertificatePassword: ""  # use file-based credential, not inline
    serverCAFile: /etc/mongodb/kmip-ca.pem
```

The `encryptionKeyIdentifier` references the KMIP key managed by HashiCorp Vault's KMIP Secrets Engine. Each mongod instance uses a unique key identifier; replica set members each have their own key but share the same master key hierarchy.

### KMIP Integration

HashiCorp Vault exposes a KMIP-compatible endpoint at `vault.internal:5696`. MongoDB connects to this endpoint for all key operations:

```hcl
# Vault KMIP secrets engine configuration
path "kmip/config" {
  capabilities = ["create", "update"]
}

# MongoDB role
resource "vault_kmip_secret_role" "mongodb" {
  path      = vault_kmip_secret_backend.this.path
  role      = "mongodb-encryption"
  tls_client_key_type    = "ec"
  tls_client_key_bits    = 256
  operation_get          = true
  operation_get_attributes = true
  operation_locate       = true
  operation_register     = false
}
```

### Field-Level Encryption

For data classified as Restricted or Secret (see `DATA-CLASSIFICATION.md`), MongoDB Client-Side Field Level Encryption (CSFLE) is required in addition to storage engine encryption:

```javascript
// MongoDB CSFLE configuration — Node.js driver example
const mongooseEncryption = {
  keyVaultNamespace: "encryption.__keyVault",
  kmsProviders: {
    kmip: {
      endpoint: "vault.internal:5696"
    }
  },
  schemaMap: {
    "socioprophet.incidents": {
      bsonType: "object",
      encryptMetadata: {
        keyId: [new Binary(Buffer.from(DEK_UUID, "hex"), 4)]
      },
      properties: {
        pii_field: {
          encrypt: {
            bsonType: "string",
            algorithm: "AEAD_AES_256_CBC_HMAC_SHA_512-Deterministic"
          }
        },
        sensitive_payload: {
          encrypt: {
            bsonType: "string",
            algorithm: "AEAD_AES_256_CBC_HMAC_SHA_512-Random"
          }
        }
      }
    }
  }
};
```

> Use `AEAD_AES_256_CBC_HMAC_SHA_512-Deterministic` for equality-searchable fields. Use `-Random` for non-searchable fields requiring stronger semantic security.

---

## Elasticsearch / OpenSearch

### Index-Level Encryption

Elasticsearch with X-Pack Security (or OpenSearch with Security Plugin) provides encrypted storage through integration with the Java Security Manager and a FIPS-validated JVM:

```yaml
# elasticsearch.yml
xpack.security.enabled: true
xpack.security.fips_mode.enabled: true

# Keystore — keys managed through Elasticsearch keystore tool
# Store Vault credentials in the secure keystore, never in plain config
```

The underlying JVM must use a FIPS-validated provider (Bouncy Castle FIPS `bc-fips-*.jar` or RSA BSAFE):

```bash
# JVM options for FIPS mode
-Djava.security.properties=/etc/elasticsearch/fips_java.security
-Dorg.bouncycastle.fips.approved_only=true
```

Primary encryption is provided at the filesystem level (LUKS-encrypted volumes) combined with the X-Pack encrypted keystore. Elasticsearch does not natively support per-index block-level encryption without a third-party plugin; the LUKS layer is therefore required and not optional.

### Snapshot Encryption

Elasticsearch snapshots must be stored in an encrypted repository:

```json
PUT _snapshot/encrypted_backup
{
  "type": "s3",
  "settings": {
    "bucket": "socioprophet-es-snapshots",
    "endpoint": "minio.internal:9000",
    "protocol": "https",
    "server_side_encryption": true,
    "storage_class": "standard"
  }
}
```

MinIO (the snapshot target) enforces SSE-KMS automatically for all objects in the snapshot bucket. See the [MinIO](#minio) section for SSE configuration.

### Keystore Management

```bash
# Add Vault credentials to Elasticsearch keystore
bin/elasticsearch-keystore add s3.client.default.access_key
bin/elasticsearch-keystore add s3.client.default.secret_key

# Rotate keystore secrets
bin/elasticsearch-keystore remove s3.client.default.access_key
bin/elasticsearch-keystore add s3.client.default.access_key
# Rolling restart required after keystore change
```

---

## Redis

### RDB and AOF File Encryption

Redis does not natively encrypt RDB or AOF persistence files. The following controls are required:

1. **Filesystem encryption (mandatory):** Redis data directory must reside on a LUKS AES-256-XTS encrypted volume.
2. **Encrypted replication:** All replication traffic must use TLS (see `ENCRYPTION-IN-TRANSIT.md`).
3. **Encrypted backup export:** All RDB snapshots must be encrypted before transmission to backup storage.

```bash
# Encrypt an RDB snapshot for archival
openssl enc -aes-256-gcm \
  -K $(vault read -field=key secret/redis/backup-key) \
  -iv $(openssl rand -hex 16) \
  -in /var/lib/redis/dump.rdb \
  -out /backup/redis/dump.rdb.enc
```

### Key Rotation for Persistence Files

When rotating the backup encryption key:

1. Retrieve the new key from Vault (`vault read secret/redis/backup-key`).
2. Re-encrypt all existing RDB archives using the new key.
3. Update the Vault secret version reference in the backup restore playbook.
4. Verify decryption of a sample archive before retiring the old key version.

### Redis Configuration for Data Protection

```conf
# redis.conf — persistence settings hardened
save 900 1
save 300 10
save 60 10000
appendonly yes
appendfsync everysec
no-appendfsync-on-rewrite no
auto-aof-rewrite-percentage 100
auto-aof-rewrite-min-size 64mb

# Data directory on encrypted volume
dir /var/lib/redis  # mount point of LUKS volume
```

---

## MinIO

### Server-Side Encryption Overview

MinIO supports three server-side encryption modes. The required mode depends on data classification:

| Mode | Description | Required For |
|---|---|---|
| **SSE-KMS** | MinIO generates a DEK, encrypts it with Vault KMS, stores encrypted DEK with object | Confidential and above |
| **SSE-S3** | MinIO manages keys internally with an auto-generated master key | Internal classification |
| **SSE-C** | Client provides the encryption key per request | Special use cases only |

### SSE-KMS Configuration (Primary)

```yaml
# MinIO environment configuration
MINIO_KMS_KES_ENDPOINT: https://kes.internal:7373
MINIO_KMS_KES_KEY_FILE: /etc/kes/client.key
MINIO_KMS_KES_CERT_FILE: /etc/kes/client.cert
MINIO_KMS_KES_CAPATH: /etc/kes/ca.cert
MINIO_KMS_KES_KEY_NAME: minio-default-key
```

KES (Key Encryption Service) acts as a sidecar that translates MinIO key requests to Vault API calls:

```yaml
# kes-config.yaml
address: 0.0.0.0:7373

tls:
  key:  /etc/kes/server.key
  cert: /etc/kes/server.cert

keystore:
  vault:
    endpoint: https://vault.internal:8200
    engine:   kv/     # KV v2 secrets engine
    version:  v2
    prefix:   minio/
    approle:
      id:     <vault_approle_id>
      secret: <vault_approle_secret_from_file>
```

### Object-Level Encryption Policy

```bash
# Enforce SSE-KMS as default for a bucket
mc encrypt set sse-kms minio-default-key myminio/socioprophet-artifacts

# Verify encryption is set
mc encrypt info myminio/socioprophet-artifacts
```

### Key Management and Rotation

```bash
# Create a new key version in Vault via KES
kes key create minio-default-key-v2

# Update MinIO to use new key (existing objects retain their DEK encrypted
# under old key until re-encryption job completes)
mc admin kms key status myminio

# Re-encrypt all objects in a bucket after key rotation
mc mirror --preserve myminio/bucket myminio/bucket  # triggers re-encryption
```

---

## RocksDB

### Block-Level Encryption Plugin

RocksDB's `EncryptionProvider` interface enables block-level encryption. The CTR mode plugin provided with RocksDB encrypts each block independently.

```cpp
// RocksDB encryption configuration — C++
#include "rocksdb/encryption.h"

rocksdb::Options options;

// Retrieve key material from Vault (application must implement Vault client)
std::string encryption_key = VaultClient::GetSecret("rocksdb/data-key");

auto enc_provider = rocksdb::NewCTREncryptionProvider(
    rocksdb::CTREncryptionProviderOptions{
        .cipher = rocksdb::CTRCipherType::AES256_CTR,
        .key = encryption_key,
    });

options.env = rocksdb::NewEncryptedEnv(rocksdb::Env::Default(), enc_provider);
```

> AES-256-CTR is used here because CTR mode is the block-level primitive exposed by the RocksDB plugin. The application layer wraps backup archives in AES-256-GCM for authenticated encryption before transmission.

### File Permission Requirements

```bash
# RocksDB data directory — restrictive permissions required
install -d -m 700 -o rocksdb-service -g rocksdb-service /var/lib/rocksdb/data
install -d -m 700 -o rocksdb-service -g rocksdb-service /var/lib/rocksdb/wal

# Validate permissions (run as part of compliance check)
find /var/lib/rocksdb -not -perm 700 -not -perm 600 -exec echo "PERMISSION VIOLATION: {}" \;
```

### Key Derivation for RocksDB

```python
# Python example — derive RocksDB block encryption key from Vault master
import hvac
import hashlib, hmac, os

client = hvac.Client(url='https://vault.internal:8200', token=vault_token)
master_key = bytes.fromhex(
    client.secrets.kv.v2.read_secret_version(
        path='rocksdb/master-key'
    )['data']['data']['value']
)

# HKDF-SHA-256 derivation
info = b'rocksdb-block-encryption-v1'
salt = os.urandom(32)
derived_key = hmac.new(salt, master_key, hashlib.sha256).digest()
# Use derived_key as the block encryption key — pass to EncryptionProvider
```

---

## Key Management — HashiCorp Vault Integration

HashiCorp Vault is the authoritative key management system for all data layer encryption keys. All systems must obtain keys through Vault; no system may self-generate long-lived encryption keys outside of Vault's key lifecycle management.

### Vault Secrets Engine Topology

```
vault/
├── transit/           # Encryption-as-a-service (Vault encrypts data for systems without native KMS)
│   ├── postgres-tde
│   ├── redis-backup
│   └── rocksdb-backup
├── kmip/              # KMIP protocol endpoint for MongoDB WiredTiger
│   └── mongodb-wiredtiger
├── kv/v2/             # Static secrets (DEK-encrypted keys, service credentials)
│   ├── postgres/
│   ├── elasticsearch/
│   ├── redis/
│   └── rocksdb/
└── pki/               # Certificate authority for TLS certificates
    ├── internal-ca/
    └── db-certs/
```

### AppRole Authentication

Each database service authenticates to Vault using the AppRole method with a role-specific policy:

```hcl
# Vault policy — PostgreSQL encryption role
path "transit/encrypt/postgres-tde" {
  capabilities = ["update"]
}
path "transit/decrypt/postgres-tde" {
  capabilities = ["update"]
}
path "transit/rotate/postgres-tde" {
  capabilities = ["update"]
}
path "kv/data/postgres/*" {
  capabilities = ["read"]
}
```

```bash
# Retrieve AppRole credentials for PostgreSQL service
vault write auth/approle/role/postgres \
  token_policies="postgres-encryption" \
  token_ttl=1h \
  token_max_ttl=4h \
  secret_id_ttl=10m
```

### HSM Integration (Production)

In production, Vault's unseal keys and the root CA private key are stored in an HSM (PKCS#11-compatible). The Vault auto-unseal configuration:

```hcl
# vault.hcl
seal "pkcs11" {
  lib            = "/usr/lib/softhsm/libsofthsm2.so"
  slot           = "0"
  pin            = "file:/run/secrets/hsm_pin"
  key_label      = "vault-hsm-unseal-key"
  hmac_key_label = "vault-hsm-hmac-key"
  generate_key   = "false"
}
```

---

## Key Derivation Standard

All encryption keys used by data layer systems are derived from Vault-managed master keys using HKDF-SHA-256 as specified in RFC 5869 and NIST SP 800-56C.

### Derivation Parameters

```
HKDF-SHA-256(IKM, salt, info) → OKM

Where:
  IKM  = Master key retrieved from Vault transit engine (256-bit)
  salt = Random 256-bit value, stored alongside encrypted data
  info = Context string identifying the system and key purpose:
         "socioprophet-<system>-<purpose>-v<version>"
  OKM  = Derived key material (256-bit for AES-256 keys)

Examples of info strings:
  "socioprophet-postgres-tde-v1"
  "socioprophet-mongodb-wiredtiger-v1"
  "socioprophet-redis-backup-v1"
  "socioprophet-rocksdb-block-v1"
```

A key version suffix (`v1`, `v2`, ...) must be incremented whenever the key hierarchy is rotated, ensuring derived keys from different rotation generations are cryptographically independent.

---

## Key Rotation Schedules

| System | Key Type | Rotation Frequency | Rotation Method | Vault Path |
|---|---|---|---|---|
| PostgreSQL | TDE master key | 90 days | pg_tde key rotation API + Vault transit rotate | `transit/postgres-tde` |
| PostgreSQL | Backup encryption key | 90 days | Vault transit rotate + re-encrypt archives | `transit/postgres-backup` |
| MongoDB | WiredTiger KMIP key | 90 days | KMIP key rotation via Vault KMIP engine | `kmip/mongodb-wiredtiger` |
| MongoDB | CSFLE DEKs | 180 days | MongoDB CSFLE rewrap operation | `kv/v2/mongodb/deks` |
| Elasticsearch | Keystore secrets | 90 days | `elasticsearch-keystore` tool + rolling restart | `kv/v2/elasticsearch` |
| Redis | Backup encryption key | 90 days | Manual re-encrypt + Vault secret rotation | `transit/redis-backup` |
| MinIO | KES default key | 90 days | `kes key create` + update MinIO config | KES → Vault |
| RocksDB | Block encryption key | 90 days | Application restart with new derived key | `transit/rocksdb-backup` |
| All systems | TLS certificates | 365 days (auto-renew at 30-day remaining) | Vault PKI auto-renew | `pki/db-certs` |

Key rotation events must be logged to the audit trail and verified by a second authorized operator (four-eyes principle) for production environments.

---

## Approved Algorithms Table

| Algorithm | Mode | Key Size | Use Case | FIPS Reference |
|---|---|---|---|---|
| AES | GCM | 256-bit | At-rest encryption (primary) | FIPS 197, SP 800-38D |
| AES | CTR | 256-bit | RocksDB block encryption | FIPS 197, SP 800-38A |
| AES | XTS | 512-bit (two 256-bit keys) | Full-volume encryption (LUKS) | FIPS 197, SP 800-38E |
| AES | KW | 256-bit | Key wrapping in Vault | SP 800-38F |
| HMAC | SHA-256 | 256-bit | Backup integrity verification | FIPS 198-1 |
| HKDF | SHA-256 | Variable | Key derivation | SP 800-56C Rev 2 |
| RSA-OAEP | SHA-256 | 3072+ bit | Key transport | FIPS 186-5 |

---

## Disallowed Algorithms

The following must not appear in any data layer encryption configuration:

| Algorithm | Mode | Reason |
|---|---|---|
| AES | ECB | No semantic security; deterministic output |
| AES | CBC (new implementations) | No authentication; padding oracle risk |
| 3DES | CBC | NIST deprecated; Sweet32 |
| DES | Any | Insufficient key length; FIPS non-compliant |
| RC4 | Stream | Statistically weak |
| Blowfish / Twofish | Any | Non-FIPS approved |
| RSA PKCS#1 v1.5 | Encryption | Bleichenbacher padding oracle |
| MD5 | Hash | Collision attacks; FIPS non-compliant |
| SHA-1 | Hash | Collision attacks; prohibited from new use |
