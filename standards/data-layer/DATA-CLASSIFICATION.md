# Data Classification and Handling

This document uses RFC 2119 language: **MUST**, **SHOULD**, **MAY**.

## 1. Scope

This standard defines sensitivity levels and per-system classification assignments, satisfying
NIST SP 800-53 SI controls and data-governance obligations.

## 2. Sensitivity Levels

| Level | Definition | Encryption Requirement |
|---|---|---|
| **Public** | Intentionally releasable; no harm from disclosure | Recommended (not mandatory) |
| **Internal** | Business operational data; limited audience | Encryption in transit REQUIRED; at rest RECOMMENDED |
| **Confidential** | Sensitive operational or personal data | Encryption at rest + in transit REQUIRED; access control + audit logging REQUIRED |
| **Secret** | Highly sensitive; regulatory or national-security implications | All Confidential controls + HSM key management + forensic-grade audit retention |

## 3. Per-System Default Classification

| System | Default Level | Rationale |
|---|---|---|
| PostgreSQL | Confidential | Configuration DB typically holds credentials and operational parameters |
| MongoDB (audit logs) | Secret | Audit records are forensic evidence; tampering would undermine compliance |
| MongoDB (general) | Confidential | Document store typically holds operational records |
| Elasticsearch | Confidential | Search index may expose sensitive record content |
| Redis (cache) | Internal | Ephemeral cache does not persist sensitive data by default |
| Redis (session store) | Confidential | Sessions contain authentication tokens |
| MinIO (artifacts) | Secret | Build artifacts may contain signing keys or compliance evidence |
| MinIO (public assets) | Public | Intentionally served without authentication |
| RocksDB | Internal | Local node cache; bounded scope |

Operators MAY escalate but MUST NOT downgrade classification without a documented risk
acceptance signed by the Security Officer.

## 4. Mandatory Encryption Thresholds

| Level | At Rest | In Transit |
|---|---|---|
| Public | MAY omit | RECOMMENDED |
| Internal | RECOMMENDED | REQUIRED |
| Confidential | REQUIRED (AES-256-GCM) | REQUIRED (TLS 1.3) |
| Secret | REQUIRED (AES-256-GCM + HSM) | REQUIRED (TLS 1.3 + mTLS) |

## 5. Data Retention

| Level | Minimum Retention | Maximum Retention |
|---|---|---|
| Public | As needed | Unlimited |
| Internal | 1 year | 5 years |
| Confidential | 3 years | 7 years |
| Secret | 7 years | Per regulatory mandate |

Retention schedules MUST be enforced through automated lifecycle policies (e.g., MinIO object
lifecycle, PostgreSQL partitioning + scheduled purge, Elasticsearch Index Lifecycle Management).

## 6. Data Destruction

- When retention expires, data MUST be destroyed using cryptographic erasure: destroy the
  encryption key for the data segment, then overwrite or delete the ciphertext.
- Physical media containing Secret data MUST be physically destroyed per NIST SP 800-88
  guidelines before disposal.
- A **certificate of destruction** MUST be generated for Confidential and Secret data.
  The certificate MUST include: data description, system, date/time, operator, method, and
  a digital signature from the platform PKI.
- Certificates of destruction MUST be retained for 7 years.

## 7. Cross-References

- [ENCRYPTION-AT-REST.md](ENCRYPTION-AT-REST.md) — algorithm and key-management requirements
- [ENCRYPTION-IN-TRANSIT.md](ENCRYPTION-IN-TRANSIT.md) — TLS requirements
- [ACCESS-CONTROL.md](ACCESS-CONTROL.md) — RBAC and least-privilege controls
- [AUDIT-LOGGING.md](AUDIT-LOGGING.md) — audit trail for Secret and Confidential data
# Data Classification — Data Layer FIPS 140-2/140-3 Standard

- Last updated: 2026-01-27
- Status: Active governance document
- Owner: Security Engineering + CISO
- Standard references: NIST SP 800-53 RA-2, SC-28, MP-3, FIPS 140-2/140-3, NIST SP 800-122 (PII)

---

## Table of Contents

1. [Overview](#overview)
2. [Classification Levels](#classification-levels)
3. [Per-System Data Classification Mapping](#per-system-data-classification-mapping)
4. [Encryption Requirements by Classification](#encryption-requirements-by-classification)
5. [Masking and Tokenization Requirements](#masking-and-tokenization-requirements)
6. [PII Handling Procedures](#pii-handling-procedures)
7. [Data Lifecycle Management](#data-lifecycle-management)
8. [Cross-System Data Flow Classification](#cross-system-data-flow-classification)
9. [Labeling Requirements](#labeling-requirements)
10. [Access Control Requirements by Classification](#access-control-requirements-by-classification)
11. [Audit Requirements by Classification](#audit-requirements-by-classification)

---

## Overview

Data classification establishes the sensitivity level of data assets and drives downstream security controls including encryption strength, access permissions, audit verbosity, retention constraints, and masking requirements. All data stored in or transiting through the SocioProphet data layer must be assigned a classification level at the point of creation.

### Classification Governance

- The data owner (the team responsible for producing the data) is responsible for assigning and maintaining classification labels.
- The Security Engineering team reviews classification assignments quarterly and may escalate underclassified data.
- No data may be reclassified to a lower level without CISO approval and documented justification.
- Data classification labels are inherited: a system or bucket containing any Restricted data is treated as Restricted in its entirety unless physical or cryptographic isolation can be demonstrated.

---

## Classification Levels

### Level 1 — Public

**Definition:** Data that is intended for public consumption or that carries no privacy or security risk if disclosed.

**Examples:**
- Published API documentation
- Public status page content
- Open-source software artifacts

**Controls required:** None beyond basic availability. Integrity protection recommended.

---

### Level 2 — Internal

**Definition:** Data that is not intended for external disclosure but whose exposure would cause minimal harm. General operational data with no personal or sensitive content.

**Examples:**
- Internal metrics dashboards
- Non-sensitive configuration parameters
- Anonymized aggregate statistics
- Internal runbooks (non-security-sensitive)

**Controls required:** Encryption in transit (TLS 1.3). Basic access control (authenticated users only). No special encryption at rest requirements beyond the default storage-level encryption applied to all data.

---

### Level 3 — Confidential

**Definition:** Data whose unauthorized disclosure could cause moderate harm to the organization, individuals, or business operations. Includes non-public business data and operational data with commercial sensitivity.

**Examples:**
- Incident reports (non-PII fields)
- Internal SLA metrics and performance data
- Vendor contract terms
- Security tool configurations (non-credential)
- Database schemas and data models

**Controls required:**
- Encryption in transit: TLS 1.3
- Encryption at rest: AES-256-GCM (storage engine level)
- Access control: RBAC with named role assignments
- Audit: Read access logged for privileged users; all writes logged
- Backup: Encrypted backups required

---

### Level 4 — Restricted

**Definition:** Data whose unauthorized disclosure could cause serious harm. Includes personal information, credentials, and sensitive operational data.

**Examples:**
- PII (names, email addresses, phone numbers, IP addresses)
- Authentication credentials and session tokens
- API keys and service credentials
- Detailed incident timelines with user attribution
- Security audit findings
- Customer data subject to contractual obligations

**Controls required:**
- Encryption in transit: TLS 1.3 (mTLS required)
- Encryption at rest: AES-256-GCM (storage engine + field-level encryption)
- Masking: PII fields masked in logs, query results for unauthorized callers
- Tokenization: PII tokens used in cross-system references
- Access control: RBAC with MFA for privileged access; least-privilege grants reviewed quarterly
- Audit: All reads and writes logged; log records retained for 7 years
- Backup: Encrypted backups; restore access requires MFA + approval

---

### Level 5 — Secret

**Definition:** Data whose unauthorized disclosure could cause severe harm to individuals, the organization, or national security interests. The most sensitive classification level.

**Examples:**
- Private cryptographic key material
- HSM access codes and PIN values
- Root CA certificates and signing keys
- Vault unseal keys and recovery tokens
- Regulatory investigation materials
- Zero-day vulnerability details

**Controls required:**
- All Restricted controls, plus:
- Encryption at rest: AES-256-GCM + mandatory field-level encryption (CSFLE for MongoDB; application-layer for others)
- Key management: Keys stored exclusively in HSM-backed Vault; never on disk in plaintext
- Access control: Break-glass access only; dual authorization required; CISO notification on access
- Audit: Every access event triggers real-time alert; immutable hash-chained record
- Backup: Separate encrypted backup with distinct key hierarchy; restore requires dual authorization
- Data at rest must never appear in search indexes, logs, or monitoring systems in plaintext

---

## Per-System Data Classification Mapping

### PostgreSQL

| Schema/Table | Classification | Encryption Tier | Notes |
|---|---|---|---|
| `public.incidents` | Confidential | Storage engine (AES-256-GCM) | Incident metadata; no PII in this table |
| `public.incident_reporters` | Restricted | Storage engine + column-level | PII: name, email, phone |
| `public.users` | Restricted | Storage engine + column-level | PII: email, hashed password |
| `public.tenants` | Confidential | Storage engine | Tenant configuration; non-PII |
| `public.audit_records` | Restricted | Storage engine | Audit trail; may contain user identity |
| `public.encryption_key_refs` | Secret | Storage engine | References to Vault key paths; never key material |
| `public.api_credentials` | Secret | Storage engine + column-level (AES-256-GCM via Vault Transit) | API keys; tokenized at rest |

### MongoDB

| Collection | Classification | Encryption Tier | Notes |
|---|---|---|---|
| `socioprophet.domain_documents` | Confidential | WiredTiger encryption | Variable-schema domain data |
| `socioprophet.user_profiles` | Restricted | WiredTiger + CSFLE on PII fields | PII in specific fields only |
| `socioprophet.change_streams` | Internal | WiredTiger encryption | Operational event log |
| `socioprophet.session_state` | Restricted | WiredTiger + field-level | Session tokens; user identity |

### Elasticsearch / OpenSearch

| Index Pattern | Classification | Encryption Tier | Notes |
|---|---|---|---|
| `incidents-*` | Confidential | LUKS volume + FIPS JVM keystore | Full-text search on incident content |
| `search-users-*` | Restricted | LUKS volume + field masking | User data projected into search; DLS applied |
| `audit-*` | Restricted | LUKS volume (read-only ISM policy) | Audit log index; WORM after 1 hour |
| `metrics-*` | Internal | LUKS volume | Operational metrics |

### Redis

| Key Pattern | Classification | Encryption Tier | Notes |
|---|---|---|---|
| `session:*` | Restricted | LUKS volume + TLS | Session tokens containing user identity |
| `cache:incidents:*` | Confidential | LUKS volume + TLS | Cached incident data; no raw PII |
| `queue:*` | Internal | LUKS volume + TLS | Job queue entries; no sensitive payload |
| `ratelimit:*` | Internal | LUKS volume + TLS | IP and user rate limit counters |

### MinIO

| Bucket | Classification | Encryption Tier | Notes |
|---|---|---|---|
| `socioprophet-artifacts` | Confidential | SSE-KMS (default) | Parquet/Arrow datasets; processed data |
| `socioprophet-restricted-data` | Restricted | SSE-KMS (mandatory) | PII-containing datasets; DLP controls active |
| `socioprophet-audit-archive` | Restricted | SSE-KMS + WORM | Audit log long-term archive |
| `socioprophet-backups` | Confidential | SSE-KMS | Database backup archives |
| `socioprophet-es-snapshots` | Confidential | SSE-KMS | Elasticsearch snapshot repository |

### RocksDB

| Key Prefix | Classification | Encryption Tier | Notes |
|---|---|---|---|
| `session:` | Restricted | Block encryption (AES-256-CTR) | Short-lived session state |
| `job:` | Internal | Block encryption (AES-256-CTR) | Worker job metadata |
| `cache:` | Confidential | Block encryption (AES-256-CTR) | Cached results |

---

## Encryption Requirements by Classification

| Classification | Encryption at Rest | Encryption in Transit | Field-Level Encryption |
|---|---|---|---|
| Public | Not required | TLS 1.3 recommended | Not required |
| Internal | Storage-level (AES-256-XTS volume) | TLS 1.3 required | Not required |
| Confidential | Storage engine AES-256-GCM | TLS 1.3 + mTLS | Not required |
| Restricted | Storage engine AES-256-GCM + field-level where PII present | TLS 1.3 + mTLS | Required for PII fields |
| Secret | Storage engine AES-256-GCM + mandatory field-level | TLS 1.3 + mTLS | Required for all fields |

---

## Masking and Tokenization Requirements

### Masking Rules

PII fields must be masked in all non-production environments and in query results returned to callers without `restricted_data_access` permission:

| PII Type | Masking Pattern | Example Input | Example Output |
|---|---|---|---|
| Email address | Preserve domain; mask local part | `alice@example.com` | `a***@example.com` |
| Phone number | Last 4 digits only | `+1-555-867-5309` | `***-***-5309` |
| Full name | First initial + masked surname | `Alice Wonderland` | `A. W*********` |
| IP address | Last octet masked | `192.168.1.42` | `192.168.1.***` |
| Credit card | First 6 + last 4 (BIN masking) | `4111111111111111` | `411111******1111` |
| SSN / NIN | Last 4 only | `123-45-6789` | `***-**-6789` |

### Tokenization

For Restricted data referenced across systems (e.g., a user identity used in both PostgreSQL and Elasticsearch), tokenization replaces the real PII value with a non-reversible token that is consistent within the platform:

```python
# Tokenization via Vault Transform Secrets Engine
import hvac

client = hvac.Client(url='https://vault.internal:8200', token=vault_token)

# Tokenize an email address
result = client.secrets.transform.encode_value(
    role_name='pii-tokenizer',
    value='alice@example.com',
    transformation='email-tokenization',
    tweak='',
)
token = result['data']['encoded_value']
# Store token in cross-system references; never store plaintext PII in non-primary stores
```

### De-identification for Analytics

For analytics pipelines consuming Restricted data, a de-identification step is required before data leaves the primary system:

1. Replace direct identifiers (name, email, SSN) with opaque tokens.
2. Generalize quasi-identifiers (age → age range, exact location → region).
3. Apply k-anonymity (k≥5) for any dataset released to the analytics layer.
4. Document the de-identification method and parameters in the data pipeline registry.

---

## PII Handling Procedures

### PII Inventory

A PII inventory must be maintained and updated whenever new PII-containing data assets are introduced:

| Asset | PII Types | System | Classification | Retention | Owner |
|---|---|---|---|---|---|
| User profiles | Name, email, phone | PostgreSQL, MongoDB | Restricted | Account lifetime + 2 years | Identity Team |
| Incident reporters | Name, email, org | PostgreSQL | Restricted | 7 years | Platform DBA Team |
| Session tokens | User ID, IP, user agent | Redis | Restricted | Session TTL (24h max) | API Team |
| Audit logs | User identity, IP | OpenSearch, MinIO | Restricted | 7 years | Security Engineering |

### PII Access Request Process

1. **Request:** Submitter documents the business purpose and specific fields required.
2. **Review:** Data owner and Security Engineering review within 5 business days.
3. **Approval:** CISO or designated approver authorizes access.
4. **Grant:** Vault role updated; database permission granted with 90-day expiry.
5. **Audit:** Access is logged from the point of grant; quarterly review of active grants.
6. **Revocation:** Access revoked at expiry or when business purpose ends.

### Data Subject Rights (GDPR / Privacy)

When a data subject invokes the right to erasure or portability:

1. Locate all records for the data subject across all six systems using the PII inventory.
2. For erasure: replace PII fields with NULL or a deletion marker; do not delete rows (referential integrity).
3. For portability: export all PII fields in JSON format; encrypt the export archive under the subject's provided key.
4. Log the erasure/export event to the audit trail.
5. Verify that audit logs retain only the event record (not the PII itself) per AU-11 requirements.

---

## Data Lifecycle Management

| Phase | Trigger | Action | Responsible Team |
|---|---|---|---|
| Creation | New record inserted | Assign classification label; apply encryption | Application / Data owner |
| Active use | Within retention window | Full controls per classification level | Platform DBA Team |
| Archival | End of hot retention | Move to cold storage; verify encryption key accessibility | Platform DBA Team |
| Retention expiry | After minimum retention period | Initiate destruction review | Security Engineering |
| Destruction | Approved destruction order | Cryptographic erasure (key deletion); verify | Security Engineering + CISO |

### Cryptographic Erasure

For media that cannot be physically destroyed (cloud storage, SSDs), cryptographic erasure is the required destruction method:

1. Rotate the encryption key covering the data to be destroyed to a new key.
2. Purge the old key version from Vault (all versions of the key path).
3. Verify with a read attempt that the data is inaccessible.
4. Document the destruction event with key version details in the audit trail.

---

## Cross-System Data Flow Classification

When data flows between systems, the classification of the combined data flow must be the highest classification of any data element in the flow.

| Source System | Target System | Data Type | Classification | Controls |
|---|---|---|---|---|
| PostgreSQL | Elasticsearch | Incident content (no PII) | Confidential | TLS 1.3; field exclusion policy in indexer |
| PostgreSQL | Redis | Session tokens | Restricted | TLS 1.3; TTL enforcement; masked in logs |
| MongoDB | MinIO | Exported documents | Confidential | TLS 1.3; SSE-KMS on upload |
| PostgreSQL | MinIO | Backup archives | Confidential | Encrypted by `pg_basebackup`; SSE-KMS in MinIO |
| Elasticsearch | OpenSearch (cross-cluster) | Search indices | Confidential | CCR over TLS 1.3 |
| Redis | Application cache | Deserialized objects | Restricted | In-memory only; never logged |

---

## Labeling Requirements

### Database Object Labeling

Labels are applied using native database mechanisms where available:

```sql
-- PostgreSQL: SECURITY LABEL
SECURITY LABEL FOR classification ON TABLE incident_reporters IS 'RESTRICTED';
SECURITY LABEL FOR classification ON COLUMN users.email IS 'RESTRICTED';
```

```bash
# MinIO: bucket tags
mc tag set myminio/socioprophet-restricted-data \
  "classification=RESTRICTED" \
  "pii=true" \
  "owner=platform-dba"
```

```javascript
// MongoDB: collection-level metadata (via admin database)
db.adminCommand({
  setCollectionOptions: "user_profiles",
  validationLevel: "strict",
  validator: { $jsonSchema: {
    properties: {
      _classification: { enum: ["RESTRICTED"] }
    },
    required: ["_classification"]
  }}
});
```

### Elasticsearch Index Naming Convention

Restricted indices must include the classification tier in the index alias:

```
restricted-incidents-2026.01
confidential-search-2026.01
internal-metrics-2026.01
```

---

## Access Control Requirements by Classification

| Classification | Authentication | Authorization | MFA |
|---|---|---|---|
| Public | None required | None | Not required |
| Internal | Any valid database user | Authenticated database role | Not required |
| Confidential | SCRAM-SHA-256 / x.509 mTLS | Named role with explicit grant | Not required |
| Restricted | SCRAM-SHA-256 / x.509 mTLS | Named role with explicit grant; MFA for direct query | Required for direct operator access |
| Secret | x.509 mTLS only | Named break-glass role; dual authorization | Required; CISO notification |

---

## Audit Requirements by Classification

| Classification | Reads Logged | Writes Logged | Retention | Real-Time Alert |
|---|---|---|---|---|
| Public | No | No | N/A | No |
| Internal | No | Yes (schema changes only) | 1 year | No |
| Confidential | No (bulk SELECT not logged; parameterized queries logged) | Yes | 3 years | No |
| Restricted | Yes (all reads logged) | Yes (full record) | 7 years | No (alert on anomaly only) |
| Secret | Yes (every access) | Yes (every access) | 7 years + legal hold | Yes (every access triggers alert) |
