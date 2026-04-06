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
