# Backup and Recovery — Data Layer FIPS 140-2/140-3 Standard

- Last updated: 2026-01-27
- Status: Active governance document
- Owner: Platform DBA Team
- Standard references: NIST SP 800-53 CP-6, CP-9, CP-10, FIPS 140-2/140-3

---

## Table of Contents

1. [Overview](#overview)
2. [PostgreSQL](#postgresql)
3. [MongoDB](#mongodb)
4. [Elasticsearch / OpenSearch](#elasticsearch--opensearch)
5. [Redis](#redis)
6. [MinIO](#minio)
7. [RocksDB](#rocksdb)
8. [Backup Verification and Testing](#backup-verification-and-testing)
9. [Retention Policy](#retention-policy)
10. [Recovery Objectives](#recovery-objectives)
11. [Disaster Recovery Testing Schedule](#disaster-recovery-testing-schedule)
12. [NIST 800-53 Control Compliance](#nist-800-53-control-compliance)

---

## Overview

Encrypted backups protect data against ransomware, accidental deletion, and infrastructure failure. All backups must be encrypted using FIPS-approved algorithms before transmission to backup storage, and the backup storage medium itself must enforce encryption at rest. Backup encryption keys must be managed through HashiCorp Vault and must be stored separately from the backup data they protect.

### Backup Encryption Principles

1. **Separate key storage:** Backup encryption keys are stored in Vault under a separate key path from the production data encryption keys. A compromise of the production database must not compromise backup archives.
2. **Pre-transmission encryption:** Data must be encrypted before it leaves the source host, not only after it arrives at the backup destination.
3. **Integrity verification:** Every backup archive includes an HMAC-SHA-256 checksum computed before transmission and verified after storage.
4. **Encryption of encryption keys:** Backup DEKs are themselves wrapped using Vault's Transit engine with the backup KEK. The actual DEK is stored with the archive metadata, wrapped.

### RTO and RPO Summary

| System | RTO Target | RPO Target | Backup Frequency |
|---|---|---|---|
| PostgreSQL | < 4 hours | < 1 hour | Continuous WAL + daily base backup |
| MongoDB | < 4 hours | < 1 hour | Continuous oplog + daily snapshot |
| Elasticsearch | < 2 hours (index rebuild) | < 4 hours | Hourly snapshot |
| Redis | < 30 minutes | < 15 minutes | 15-minute RDB snapshots |
| MinIO | < 4 hours | < 1 hour | Site replication (active-active) + daily export |
| RocksDB | < 2 hours | < 1 hour | Hourly checkpoint |

---

## PostgreSQL

### pg_basebackup with Encryption

```bash
#!/bin/bash
# Encrypted base backup script
set -euo pipefail

BACKUP_DIR="/backup/postgres/$(date +%Y%m%d_%H%M%S)"
VAULT_ADDR="https://vault.internal:8200"
KEY_PATH="transit/postgres-backup"

# Retrieve wrapped DEK from Vault
DEK_HEX=$(vault write -field=plaintext \
  ${KEY_PATH}/datakey/plaintext \
  key_version=latest \
  bits=256 \
  | base64 -d | xxd -p -c 32)

WRAPPED_DEK=$(vault write -field=ciphertext \
  ${KEY_PATH}/encrypt \
  plaintext=$(echo -n ${DEK_HEX} | base64))

mkdir -p "${BACKUP_DIR}"

# Generate IV before encryption (must be stored for later decryption)
IV_HEX=$(openssl rand -hex 16)

# Stream base backup, compress, and encrypt
pg_basebackup \
  --host=localhost \
  --username=backup_agent \
  --pgdata=- \
  --wal-method=stream \
  --format=tar \
  --compress=9 \
  --checkpoint=fast \
  --progress 2>/dev/null \
| openssl enc -aes-256-gcm \
    -K "${DEK_HEX}" \
    -iv "${IV_HEX}" \
    -out "${BACKUP_DIR}/base_backup.tar.gz.enc"

# Store IV alongside backup so it can be used for decryption
echo "${IV_HEX}" > "${BACKUP_DIR}/backup.iv"

# Compute and store HMAC-SHA-256 checksum
HMAC_KEY=$(vault read -field=hmac_key secret/postgres/backup-hmac)
openssl dgst -sha256 -hmac "${HMAC_KEY}" \
  "${BACKUP_DIR}/base_backup.tar.gz.enc" \
  > "${BACKUP_DIR}/base_backup.tar.gz.enc.hmac"

# Store wrapped DEK alongside backup (not the plaintext DEK)
echo "${WRAPPED_DEK}" > "${BACKUP_DIR}/wrapped_dek.txt"

# Upload to MinIO backup bucket
mc cp "${BACKUP_DIR}/" myminio/socioprophet-backups/postgres/
```

### WAL Archiving with Encryption

```ini
# postgresql.conf — WAL archiving
archive_mode = on
archive_command = '/usr/local/bin/encrypt_and_archive_wal.sh %p %f'
archive_timeout = 300  # Force WAL switch every 5 minutes for RPO < 5 min
```

```bash
#!/bin/bash
# /usr/local/bin/encrypt_and_archive_wal.sh
# $1 = source path, $2 = WAL filename
WAL_SOURCE="$1"
WAL_FILE="$2"

DEK_HEX=$(vault write -field=plaintext \
  transit/postgres-wal/datakey/plaintext bits=256 \
  | base64 -d | xxd -p -c 32)

openssl enc -aes-256-gcm \
  -K "${DEK_HEX}" \
  -iv "$(openssl rand -hex 16 | tee "/backup/postgres/wal/${WAL_FILE}.iv")" \
  -in "${WAL_SOURCE}" \
  -out "/backup/postgres/wal/${WAL_FILE}.enc"

mc cp "/backup/postgres/wal/${WAL_FILE}.enc" \
  "myminio/socioprophet-backups/postgres/wal/${WAL_FILE}.enc"
mc cp "/backup/postgres/wal/${WAL_FILE}.iv" \
  "myminio/socioprophet-backups/postgres/wal/${WAL_FILE}.iv"
```

### Point-in-Time Recovery (PITR) Procedure

```bash
# PITR procedure — restore to specific timestamp
TARGET_TIME="2026-01-27 12:00:00 UTC"

# 1. Decrypt and restore base backup
WRAPPED_DEK=$(cat /restore/base_backup/wrapped_dek.txt)
DEK_HEX=$(vault write -field=plaintext \
  transit/postgres-backup/decrypt \
  ciphertext="${WRAPPED_DEK}" \
  | base64 -d | xxd -p -c 32)

openssl enc -d -aes-256-gcm \
  -K "${DEK_HEX}" \
  -iv "$(cat /restore/base_backup/backup.iv)" \
  -in /restore/base_backup.tar.gz.enc \
  -out /restore/base_backup.tar.gz

tar -xzf /restore/base_backup.tar.gz -C /var/lib/postgresql/data/

# 2. Configure recovery.conf
cat > /var/lib/postgresql/data/recovery.conf <<EOF
restore_command = '/usr/local/bin/decrypt_and_restore_wal.sh %f %p'
recovery_target_time = '${TARGET_TIME}'
recovery_target_action = 'promote'
EOF

# 3. Start PostgreSQL in recovery mode
pg_ctl start -D /var/lib/postgresql/data/
```

---

## MongoDB

### mongodump with Encryption

```bash
#!/bin/bash
# Encrypted MongoDB dump script
DUMP_DIR="/backup/mongodb/$(date +%Y%m%d_%H%M%S)"
mkdir -p "${DUMP_DIR}"

# Dump with GZIP compression
mongodump \
  --host mongo.internal:27017 \
  --ssl \
  --sslCAFile /etc/ssl/certs/internal-ca.crt \
  --sslPEMKeyFile /etc/ssl/certs/backup-agent.pem \
  --authenticationMechanism SCRAM-SHA-256 \
  --username backup_agent \
  --password "$(vault read -field=password secret/mongodb/backup-agent)" \
  --db socioprophet \
  --gzip \
  --archive="${DUMP_DIR}/socioprophet.archive.gz"

# Encrypt the archive
DEK_HEX=$(vault write -field=plaintext \
  transit/mongodb-backup/datakey/plaintext bits=256 \
  | base64 -d | xxd -p -c 32)

WRAPPED_DEK=$(vault write -field=ciphertext \
  transit/mongodb-backup/encrypt \
  plaintext=$(echo -n "${DEK_HEX}" | base64))

IV_HEX=$(openssl rand -hex 16)
openssl enc -aes-256-gcm \
  -K "${DEK_HEX}" \
  -iv "${IV_HEX}" \
  -in "${DUMP_DIR}/socioprophet.archive.gz" \
  -out "${DUMP_DIR}/socioprophet.archive.gz.enc"

echo "${WRAPPED_DEK}" > "${DUMP_DIR}/wrapped_dek.txt"
echo "${IV_HEX}" > "${DUMP_DIR}/backup.iv"

# Remove plaintext archive immediately
shred -u "${DUMP_DIR}/socioprophet.archive.gz"

mc cp "${DUMP_DIR}/" myminio/socioprophet-backups/mongodb/
```

### Oplog-Based Continuous Backup

```javascript
// Oplog tailing for continuous backup (RPO < 1 hour)
// This runs as a separate backup service
const changeStream = db.watch([], {
  fullDocument: 'updateLookup',
  startAfter: lastResumeToken
});

changeStream.on('change', (event) => {
  // Encrypt and forward to backup queue
  const encrypted = vaultTransit.encrypt(
    'mongodb-oplog-backup',
    JSON.stringify(event)
  );
  backupQueue.push({
    seq: event.clusterTime,
    data: encrypted,
    resumeToken: event._id
  });
});
```

### Replica Set Backup Strategy

```bash
# Backup from secondary to avoid impacting primary
mongodump \
  --host mongo-secondary-01.internal:27017 \
  --readPreference secondary \
  --ssl \
  --sslCAFile /etc/ssl/certs/internal-ca.crt \
  --sslPEMKeyFile /etc/ssl/certs/backup-agent.pem \
  --authenticationMechanism SCRAM-SHA-256 \
  --username backup_agent \
  --password "$(vault read -field=password secret/mongodb/backup-agent)" \
  --oplog \
  --gzip \
  --archive | encrypt_and_upload_to_minio "mongodb"
```

---

## Elasticsearch / OpenSearch

### Snapshot Lifecycle Management (SLM)

```json
// Create an SLM policy for hourly snapshots
PUT _slm/policy/hourly-snapshots
{
  "schedule": "0 0 * * * ?",
  "name": "<socioprophet-snap-{now/d}>",
  "repository": "encrypted-minio-backup",
  "config": {
    "indices": ["incidents-*", "search-*"],
    "ignore_unavailable": false,
    "include_global_state": false
  },
  "retention": {
    "expire_after": "30d",
    "min_count": 168,
    "max_count": 720
  }
}
```

### Encrypted Snapshot Repository (MinIO/S3)

```json
// Register MinIO as snapshot repository with SSE-KMS
PUT _snapshot/encrypted-minio-backup
{
  "type": "s3",
  "settings": {
    "bucket": "socioprophet-es-snapshots",
    "endpoint": "minio.internal:9000",
    "protocol": "https",
    "path_style_access": true,
    "server_side_encryption": true,
    "compress": true
  }
}
```

MinIO enforces SSE-KMS on all objects in this bucket (configured via `mc encrypt set`), providing a second encryption layer on top of Elasticsearch's own snapshot compression.

### Cross-Cluster Replication for DR

```json
// Configure CCR for disaster recovery
PUT _cluster/settings
{
  "persistent": {
    "cluster.remote.dr-cluster.seeds": ["es-dr-01.internal:9300"],
    "cluster.remote.dr-cluster.transport.tls.enabled": true
  }
}

// Create follower index
PUT /incidents-2026.01/_ccr/follow
{
  "remote_cluster": "dr-cluster",
  "leader_index": "incidents-2026.01"
}
```

---

## Redis

### RDB Snapshot Encryption

```conf
# redis.conf — snapshot configuration
save 900 1
save 300 10
save 60 10000
stop-writes-on-bgsave-error yes
rdbcompression yes
rdbchecksum yes
dbfilename dump.rdb
dir /var/lib/redis
```

```bash
#!/bin/bash
# Encrypt and upload Redis RDB snapshot
RDB_PATH="/var/lib/redis/dump.rdb"
SNAPSHOT_NAME="redis-$(date +%Y%m%d_%H%M%S).rdb.enc"

# Trigger a synchronous background save
redis-cli -h redis.internal -p 6380 \
  --tls --cacert /etc/ssl/certs/internal-ca.crt \
  --cert /etc/ssl/certs/backup-agent.crt \
  --key /etc/ssl/private/backup-agent.key \
  BGSAVE

# Wait for save to complete
while [ "$(redis-cli ... LASTSAVE)" -le "${SAVE_START}" ]; do sleep 1; done

# Encrypt RDB
DEK_HEX=$(vault write -field=plaintext transit/redis-backup/datakey/plaintext bits=256 \
  | base64 -d | xxd -p -c 32)
WRAPPED_DEK=$(vault write -field=ciphertext transit/redis-backup/encrypt \
  plaintext=$(echo -n "${DEK_HEX}" | base64))

IV_HEX=$(openssl rand -hex 16)
openssl enc -aes-256-gcm \
  -K "${DEK_HEX}" \
  -iv "${IV_HEX}" \
  -in "${RDB_PATH}" \
  -out "/backup/redis/${SNAPSHOT_NAME}"

echo "${WRAPPED_DEK}" > "/backup/redis/${SNAPSHOT_NAME}.key"
echo "${IV_HEX}" > "/backup/redis/${SNAPSHOT_NAME}.iv"
mc cp "/backup/redis/${SNAPSHOT_NAME}" \
  "myminio/socioprophet-backups/redis/${SNAPSHOT_NAME}"
```

### AOF Backup Encryption

```bash
# Encrypt AOF file for archival
# AOF is the primary durability mechanism; RDB is the backup mechanism
AOF_PATH="/var/lib/redis/appendonly.aof"
AOF_ARCHIVE="redis-aof-$(date +%Y%m%d_%H%M%S).aof.enc"

redis-cli ... BGREWRITEAOF
sleep 5  # Wait for rewrite

AOF_IV_HEX=$(openssl rand -hex 16)
openssl enc -aes-256-gcm \
  -K "${DEK_HEX}" \
  -iv "${AOF_IV_HEX}" \
  -in "${AOF_PATH}" \
  -out "/backup/redis/${AOF_ARCHIVE}"

echo "${AOF_IV_HEX}" > "/backup/redis/${AOF_ARCHIVE}.iv"
mc cp "/backup/redis/${AOF_ARCHIVE}" \
  "myminio/socioprophet-backups/redis/aof/${AOF_ARCHIVE}"
mc cp "/backup/redis/${AOF_ARCHIVE}.iv" \
  "myminio/socioprophet-backups/redis/aof/${AOF_ARCHIVE}.iv"
```

### Redis Cluster Backup

For Redis Cluster deployments, each shard must be backed up independently:

```bash
for NODE in redis-01 redis-02 redis-03 redis-04 redis-05 redis-06; do
  redis-cli -h ${NODE}.internal -p 6380 \
    --tls --cacert /etc/ssl/certs/internal-ca.crt \
    --cert /etc/ssl/certs/backup-agent.crt \
    --key /etc/ssl/private/backup-agent.key \
    BGSAVE
  # Encrypt and upload per-node RDB as above
done
```

---

## MinIO

### Erasure Coding Configuration

MinIO erasure coding provides data durability within a site. Configure erasure sets for the required durability:

```bash
# 8-drive erasure set: 4 data + 4 parity (survives loss of any 4 drives)
MINIO_VOLUMES="/data{1...8}"
# Storage class configuration
mc admin config set myminio storage_class \
  standard="EC:4" \
  rrs="EC:2"
```

### Site Replication for DR

```bash
# Configure site replication between primary and DR sites
mc admin replicate add \
  myminio-primary myminio-dr \
  --replicate "delete,delete-marker,existing-objects"

# Verify replication status
mc admin replicate status myminio-primary
```

### Encrypted Backup Export Policy

```bash
# Export policy — create a versioned, lifecycle-managed backup bucket
mc mb myminio/socioprophet-backups
mc version enable myminio/socioprophet-backups

# Lifecycle: transition to cold storage after 90 days
mc ilm rule add myminio/socioprophet-backups \
  --id "archive-after-90d" \
  --transition-days 90 \
  --storage-class "GLACIER" \
  --expired-object-delete-marker

# Enforce SSE-KMS on all backup objects
mc encrypt set sse-kms minio-default-key myminio/socioprophet-backups
```

---

## RocksDB

### Checkpoint-Based Backup

```cpp
// RocksDB backup using BackupEngine
#include "rocksdb/utilities/backup_engine.h"

rocksdb::BackupEngineOptions backup_opts("/backup/rocksdb");
backup_opts.backup_env = encrypted_env;  // Same encrypted env as production DB

rocksdb::BackupEngine* backup_engine;
auto status = rocksdb::BackupEngine::Open(
    rocksdb::Env::Default(),
    backup_opts,
    &backup_engine
);

// Create a backup
status = backup_engine->CreateNewBackup(db);

// Verify backup integrity
status = backup_engine->VerifyBackup(backup_id);
```

### Backup Encryption

```python
# Post-processing: encrypt RocksDB backup directory
import subprocess, os, secrets

backup_path = "/backup/rocksdb/latest"
archive_path = f"/backup/rocksdb/archive/rocksdb-{timestamp}.tar.enc"
iv_path = f"/backup/rocksdb/archive/rocksdb-{timestamp}.tar.iv"

# Generate and persist IV before encryption
iv_hex = secrets.token_hex(16)
with open(iv_path, "w") as f:
    f.write(iv_hex)

# Tar and encrypt in one pipe (IV read from file so it is always stored)
subprocess.run([
    "bash", "-c",
    f"tar -czf - {backup_path} | "
    f"openssl enc -aes-256-gcm "
    f"-K $(vault read -field=key transit/rocksdb-backup/export) "
    f"-iv {iv_hex} "
    f"-out {archive_path}"
], check=True)

# Upload archive and IV to MinIO
subprocess.run([
    "mc", "cp", archive_path,
    f"myminio/socioprophet-backups/rocksdb/"
], check=True)
subprocess.run([
    "mc", "cp", iv_path,
    f"myminio/socioprophet-backups/rocksdb/"
], check=True)
```

---

## Backup Verification and Testing

### Automated Checksum Validation

Every backup archive must include an HMAC-SHA-256 checksum verified after upload:

```bash
#!/bin/bash
# backup-verify.sh — run after every backup
ARCHIVE_PATH="$1"
HMAC_KEY=$(vault read -field=value secret/backup/hmac-key)

# Compute HMAC on local file
LOCAL_HMAC=$(openssl dgst -sha256 -hmac "${HMAC_KEY}" "${ARCHIVE_PATH}" \
  | awk '{print $2}')

# Download and verify against stored checksum
STORED_HMAC=$(mc cat "myminio/socioprophet-backups/${ARCHIVE_PATH}.hmac")

if [ "${LOCAL_HMAC}" != "${STORED_HMAC}" ]; then
  echo "INTEGRITY FAILURE: ${ARCHIVE_PATH}" | \
    tee -a /var/log/backup-integrity.log
  # Alert via PagerDuty
  curl -X POST https://events.pagerduty.com/v2/enqueue \
    -H "Authorization: Token $(vault read -field=key secret/pagerduty/token)" \
    -d '{"routing_key":"...","event_action":"trigger","payload":{"summary":"Backup integrity failure","severity":"critical"}}'
  exit 1
fi
```

### Quarterly Restore Testing

A full restore test must be performed quarterly for each system. The restore test must:

1. Restore to a **dedicated isolated test environment** (never to production).
2. Decrypt the backup archive using the key from Vault.
3. Verify that all expected data is present and consistent.
4. Measure restore time against the RTO target.
5. Document the results in the DR test log.

```bash
#!/bin/bash
# quarterly-restore-test.sh — PostgreSQL example
RESTORE_HOST="postgres-dr-test.internal"
BACKUP_DATE="${1:-latest}"  # Pass backup date as argument or use latest

echo "[$(date)] Starting quarterly PostgreSQL restore test" | tee -a /var/log/dr-test.log

# Download and decrypt backup
mc cp "myminio/socioprophet-backups/postgres/${BACKUP_DATE}/base_backup.tar.gz.enc" \
  /restore/
WRAPPED_DEK=$(mc cat "myminio/socioprophet-backups/postgres/${BACKUP_DATE}/wrapped_dek.txt")
DEK_HEX=$(vault write -field=plaintext transit/postgres-backup/decrypt \
  ciphertext="${WRAPPED_DEK}" | base64 -d | xxd -p -c 32)

openssl enc -d -aes-256-gcm -K "${DEK_HEX}" -iv "<iv>" \
  -in /restore/base_backup.tar.gz.enc -out /restore/base_backup.tar.gz

# Restore to test environment
tar -xzf /restore/base_backup.tar.gz -C /restore/pgdata/
pg_ctl start -D /restore/pgdata/ -o "-p 5433"

# Validate data integrity
psql -h localhost -p 5433 -U postgres -d socioprophet \
  -c "SELECT COUNT(*) FROM incidents;" | tee -a /var/log/dr-test.log

echo "[$(date)] Restore test complete. RTO measured: $((SECONDS / 60)) minutes" \
  | tee -a /var/log/dr-test.log
```

---

## Retention Policy

| Tier | Duration | Storage Location | Format |
|---|---|---|---|
| Daily backups | 30 days | MinIO (`socioprophet-backups`) | Encrypted archive + wrapped DEK |
| Weekly backups | 12 months | MinIO cold storage (GLACIER tier) | Encrypted archive + wrapped DEK |
| Monthly backups | 7 years | MinIO WORM bucket (`socioprophet-compliance-archive`) | Encrypted archive + wrapped DEK |
| WAL / oplog / AOF | 7 days hot, then archive | MinIO → cold | Encrypted per-file |
| DR test results | Indefinite | `standards/audit-forensics/` | Signed test report |

### Retention Enforcement

```bash
# MinIO lifecycle policy for backup retention
mc ilm rule add myminio/socioprophet-backups \
  --id "expire-daily-after-30d" \
  --prefix "postgres/daily/" \
  --expiry-days 30

mc ilm rule add myminio/socioprophet-backups \
  --id "expire-weekly-after-365d" \
  --prefix "postgres/weekly/" \
  --expiry-days 365
```

---

## Recovery Objectives

| System | RTO | RPO | Recovery Strategy | Validation Frequency |
|---|---|---|---|---|
| PostgreSQL | < 4 hours | < 1 hour (WAL streaming) | PITR from base backup + WAL | Quarterly full restore |
| MongoDB | < 4 hours | < 1 hour (oplog tailing) | Restore from dump + oplog replay | Quarterly full restore |
| Elasticsearch | < 2 hours | < 4 hours (hourly snapshots) | Restore from snapshot to new cluster | Semi-annual |
| Redis | < 30 minutes | < 15 minutes | Restore from RDB; replay AOF if available | Monthly smoke test |
| MinIO | < 4 hours | < 1 hour (site replication) | Failover to DR site; restore from replication | Quarterly |
| RocksDB | < 2 hours | < 1 hour (checkpoint) | Restore from encrypted checkpoint | Quarterly |

**RTO < 4 hours** and **RPO < 1 hour** are the platform-wide SLO targets. Individual systems with lower targets (Redis: RTO < 30 min) must be tracked separately.

---

## Disaster Recovery Testing Schedule

| Test Type | Frequency | Scope | Lead | Documentation |
|---|---|---|---|---|
| Tabletop exercise | Quarterly | All six systems; simulate ransomware + data center failure | Platform DBA Team + Ops | DR-TABLETOP-{YYYYQ}.md in audit-forensics/ |
| Restore verification (automated) | Monthly | Checksum validation + test DB spin-up | DevSecOps (automated) | CI/CD report |
| Full restore test (manual) | Quarterly | Full recovery of each system to test environment | Platform DBA Team | DR-RESTORE-{YYYY-MM}.md |
| Cross-region failover test | Semi-annual | Fail primary to DR; validate reads/writes | Platform DBA + Infra | DR-FAILOVER-{YYYY-MM}.md |
| Annual DR exercise | Annual | Full company-wide DR including data layer | CISO + Platform DBA | Annual DR Report |

---

## NIST 800-53 Control Compliance

| Control | Title | Implementation |
|---|---|---|
| CP-6 | Alternate Storage Site | MinIO site replication to secondary data center; DR cluster for all systems |
| CP-7 | Alternate Processing Site | DR environment maintains hot standby for PostgreSQL and MongoDB |
| CP-9 | System Backup | Per-system encrypted backup procedures documented above; automated and verified |
| CP-10 | System Recovery and Reconstitution | PITR and restore procedures documented; quarterly testing |
| CP-12 | Safe Mode | PostgreSQL and MongoDB configured with `stop-writes-on-bgsave-error yes` / transaction abort on backup failure |
| SC-28 | Protection of Information at Rest | All backup archives encrypted with AES-256-GCM; keys in Vault |
