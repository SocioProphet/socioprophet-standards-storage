# Data Layer FIPS 140-2/140-3 Governance Index

- Last updated: 2026-01-27
- Status: Active governance document
- Owner: SocioProphet Platform Security
- Standard references: FIPS 140-2, FIPS 140-3, NIST SP 800-57, NIST SP 800-53, NIST SP 800-111

---

## Table of Contents

1. [Introduction](#introduction)
2. [Systems Covered](#systems-covered)
3. [Document Registry](#document-registry)
4. [Compliance Status Summary](#compliance-status-summary)
5. [Cryptographic Standards Applied](#cryptographic-standards-applied)
6. [Disallowed Algorithms](#disallowed-algorithms)
7. [Implementation Timeline](#implementation-timeline)
8. [Roles and Responsibilities](#roles-and-responsibilities)
9. [Governance and Review Cadence](#governance-and-review-cadence)

---

## Introduction

This index governs the FIPS 140-2 and FIPS 140-3 compliance posture for all persistent data layer components deployed within the SocioProphet platform. It serves as the authoritative entry point for data-layer security policy, referencing dedicated standards documents for each control domain.

The SocioProphet data layer comprises six primary storage systems, each handling distinct data access patterns: relational state, document collections, full-text search, in-memory caching, object storage, and embedded key-value storage. Because these systems span different threat models, authentication protocols, and encryption capabilities, each requires a tailored compliance treatment aligned to the shared cryptographic policy inherited from the parent FIPS compliance framework at `standards/fips-compliance/INDEX.md`.

### Compliance Philosophy

The data layer compliance program is grounded in three principles:

1. **Cryptographic uniformity** — Every system encrypts data at rest with AES-256-GCM and enforces TLS 1.3+ for all in-transit communication, regardless of whether that communication is client-facing or internal cluster traffic.
2. **Least privilege by default** — Every database user, service account, and operator role receives only the permissions explicitly required for its function, enforced through native RBAC mechanisms supplemented by OIDC-federated identity.
3. **Auditability at all layers** — Every access event, schema change, privileged operation, and authentication event produces a structured, tamper-evident log record retained for a minimum of seven years.

### Relationship to Parent Governance

This directory extends the platform-wide FIPS governance defined in `standards/fips-compliance/INDEX.md`. Where this document and its siblings conflict with the parent index, the more restrictive requirement applies. Data layer maintainers must review the parent index before changing any cryptographic configuration.

---

## Systems Covered

The following storage systems are in scope for this governance document set:

| System | Role in Platform | Version Baseline | FIPS Module Status |
|---|---|---|---|
| **PostgreSQL** | Relational system-of-record (incident state, tenancy, policy, audit, relational mappings) | PostgreSQL 15+ | OpenSSL 3.x FIPS provider required |
| **MongoDB** | High-variability domain documents with schema churn and change-stream workflows | MongoDB 7.0+ (Enterprise) | MongoDB Enterprise FIPS mode; OpenSSL FIPS |
| **Elasticsearch** | Full-text search, faceted retrieval, rebuildable index (also referenced as OpenSearch) | Elasticsearch 8.x / OpenSearch 2.x | X-Pack Security with FIPS JVM; Bouncy Castle FIPS |
| **Redis** | In-memory caching, session state, ephemeral queues | Redis 7.2+ | TLS via OpenSSL FIPS; ACL enforcement |
| **MinIO** | Object storage for binary artifacts, columnar datasets (Parquet/Arrow IPC), encrypted backups | MinIO RELEASE.2024+ | SSE-KMS with HashiCorp Vault; TLS 1.3 |
| **RocksDB** | Embedded key-value store used in internal services for high-throughput local state | RocksDB 8.x | Encryption-at-rest plugin; application-level FIPS wrapper |

### Out-of-Scope Systems

The following are explicitly out of scope for this document set but are governed by separate standards:

- **pgvector** — governed as a PostgreSQL extension under the PostgreSQL policies in this set.
- **OpenSearch kNN indexes** — governed under the Elasticsearch/OpenSearch policies in this set.
- **Triplestore / graph store** — governed by `standards/nist-800-207/` pending adoption decision.

---

## Document Registry

All files in this directory and their governing scope:

| File | Domain | Status |
|---|---|---|
| `INDEX.md` (this file) | Overview, timeline, cryptographic standards | Active |
| `ENCRYPTION-AT-REST.md` | Encryption-at-rest configuration for all six systems | Active |
| `ENCRYPTION-IN-TRANSIT.md` | TLS 1.3+ configuration, certificate management, cipher suites | Active |
| `AUDIT-LOGGING.md` | Per-system audit logging, centralized aggregation, retention | Active |
| `ACCESS-CONTROL.md` | RBAC, least privilege, MFA, OIDC integration | Active |
| `DATA-CLASSIFICATION.md` | Sensitivity levels, encryption thresholds, PII handling | Active |
| `BACKUP-RECOVERY.md` | Encrypted backups, RTO/RPO targets, disaster recovery | Active |
| `HARDENING.md` | Network isolation, configuration hardening, vulnerability management | Active |
| `INTEGRATION-CHECKLIST.md` | Per-system compliance checklist with pass/fail items | Active |
| `COMPLIANCE-VALIDATION.md` | Automated and manual validation procedures, CI/CD integration | Active |

---

## Compliance Status Summary

The table below reflects the compliance posture as of the document date. Items marked 🔄 are in active implementation. Items marked ✅ are verified and tested. Items marked ❌ are scheduled but not yet started.

| Control Domain | PostgreSQL | MongoDB | Elasticsearch | Redis | MinIO | RocksDB |
|---|---|---|---|---|---|---|
| Encryption at rest | 🔄 | 🔄 | ✅ | 🔄 | ✅ | ❌ |
| Encryption in transit | ✅ | ✅ | ✅ | 🔄 | ✅ | 🔄 |
| Audit logging | 🔄 | 🔄 | ✅ | 🔄 | 🔄 | ❌ |
| Access control / RBAC | ✅ | ✅ | ✅ | 🔄 | ✅ | ❌ |
| Backup encryption | 🔄 | 🔄 | ✅ | ❌ | ✅ | ❌ |
| Hardening | 🔄 | 🔄 | ✅ | 🔄 | ✅ | ❌ |
| OIDC integration | 🔄 | 🔄 | ✅ | ❌ | 🔄 | N/A |
| Key rotation | 🔄 | 🔄 | 🔄 | 🔄 | 🔄 | ❌ |

### Legend

- ✅ Implemented and validated via automated compliance check
- 🔄 In active implementation; target completion per timeline below
- ❌ Scheduled; implementation not yet started
- N/A Not applicable to this system's architecture

---

## Cryptographic Standards Applied

All cryptographic operations across the data layer must use only FIPS 140-2 or FIPS 140-3 approved algorithms. The following table defines the approved algorithm set.

### Approved Symmetric Algorithms

| Algorithm | Mode | Key Length | Use Case |
|---|---|---|---|
| AES | GCM | 256-bit | Data at rest encryption, TLS record encryption |
| AES | CBC with PKCS7 | 256-bit | Legacy compatibility layer (migration only; no new use) |
| AES | CTR | 256-bit | Streaming encryption in RocksDB blocks |
| AES | KW (Key Wrap) | 256-bit | Key encryption key (KEK) wrapping in Vault |
| ChaCha20-Poly1305 | AEAD | 256-bit | TLS 1.3 cipher suite (TLS_CHACHA20_POLY1305_SHA256) |

### Approved Asymmetric Algorithms

| Algorithm | Key Size | Use Case |
|---|---|---|
| RSA | 3072-bit minimum (4096-bit preferred) | Certificate signing, key transport |
| ECDSA | P-256, P-384 | TLS certificates, code signing |
| ECDH | P-256, P-384 | TLS 1.3 key exchange |
| Ed25519 | 256-bit | SSH keys for operator access (where FIPS mode permits) |

### Approved Hash Functions

| Algorithm | Digest Length | Use Case |
|---|---|---|
| SHA-256 | 256-bit | General-purpose integrity, audit log chaining |
| SHA-384 | 384-bit | TLS cipher suite (TLS_AES_256_GCM_SHA384) |
| SHA-512 | 512-bit | Long-term archive integrity, HKDF derivation |
| HMAC-SHA-256 | 256-bit | Audit record authentication, backup integrity |
| HKDF-SHA-256 | Variable | Key derivation from master key material |

### Approved Key Derivation Functions

| KDF | Standard | Use Case |
|---|---|---|
| HKDF | RFC 5869 / NIST SP 800-56C | Database encryption key derivation from Vault master |
| PBKDF2-SHA-256 | NIST SP 800-132 | Password-based key derivation (operator key material) |
| SP 800-108 CTR-KDF | NIST SP 800-108 | Counter-mode KDF for subkey generation |

### TLS Protocol Requirements

| Parameter | Required Value |
|---|---|
| Minimum TLS version | TLS 1.3 |
| Approved cipher suites | `TLS_AES_256_GCM_SHA384`, `TLS_CHACHA20_POLY1305_SHA256` |
| Certificate signature algorithm | ECDSA P-256 or P-384, RSA-PSS with SHA-256/384 |
| Minimum RSA certificate key size | 3072-bit |
| Minimum ECDSA certificate key size | P-256 |
| Perfect Forward Secrecy | Required (ECDHE key exchange in all suites) |
| Certificate revocation | OCSP stapling required; CRL as fallback |

---

## Disallowed Algorithms

The following algorithms are **explicitly prohibited** across all data layer components. Any configuration, library, or driver that enables these algorithms must be remediated before production deployment.

| Algorithm / Protocol | Reason for Prohibition |
|---|---|
| DES, 3DES | NIST deprecated; insufficient key length; Sweet32 vulnerability |
| RC4 | Statistically weak; FIPS non-compliant |
| MD5 | Collision attacks; FIPS non-compliant for security applications |
| SHA-1 | Collision attacks demonstrated; NIST deprecated after 2030 but prohibited here immediately |
| SSLv2, SSLv3 | Protocol-level vulnerabilities (POODLE, DROWN) |
| TLS 1.0, TLS 1.1 | Protocol-level vulnerabilities; NIST SP 800-52 Rev 2 disallows |
| RSA PKCS#1 v1.5 encryption | Padding oracle attacks (Bleichenbacher); use RSA-OAEP or ECDH instead |
| DSA | NIST deprecated in FIPS 186-5 |
| Diffie-Hellman < 3072-bit | Insufficient security margin |
| ECB mode (any block cipher) | No semantic security; deterministic ciphertext |
| Non-FIPS random number generators | Must use CTR-DRBG or Hash-DRBG per NIST SP 800-90A |
| Blowfish, Twofish, CAST | Non-FIPS approved |

---

## Implementation Timeline

### Q2 2026 (April–June)

| Milestone | Systems | Owner | Target Date |
|---|---|---|---|
| PostgreSQL pgcrypto + TDE baseline | PostgreSQL | Platform DBA Team | 2026-04-15 |
| MongoDB WiredTiger encryption enabled | MongoDB | Platform DBA Team | 2026-04-15 |
| Redis TLS 1.3 enforcement | Redis | Infrastructure Team | 2026-04-30 |
| HashiCorp Vault KMIP integration (all systems) | All | Security Engineering | 2026-05-15 |
| pgaudit deployment and centralized log forwarding | PostgreSQL | Security Engineering | 2026-05-31 |
| MongoDB audit log + Fluentd pipeline | MongoDB | Security Engineering | 2026-05-31 |
| RocksDB encryption-at-rest plugin integration | RocksDB | Application Teams | 2026-06-30 |

### Q3 2026 (July–September)

| Milestone | Systems | Owner | Target Date |
|---|---|---|---|
| OIDC federation for PostgreSQL + MongoDB | PostgreSQL, MongoDB | Identity Team | 2026-07-31 |
| Redis ACL hardening + OIDC bridge | Redis | Infrastructure Team | 2026-07-31 |
| MinIO OIDC integration completion | MinIO | Infrastructure Team | 2026-07-31 |
| Automated key rotation (all systems, 90-day cycle) | All | Security Engineering | 2026-08-15 |
| Backup encryption validation and quarterly restore test | All | Platform DBA Team | 2026-08-31 |
| Compliance validation CI/CD pipeline (Phase 1) | All | DevSecOps Team | 2026-09-30 |

### Q4 2026 (October–December)

| Milestone | Systems | Owner | Target Date |
|---|---|---|---|
| RocksDB RBAC + audit framework | RocksDB | Application Teams | 2026-10-31 |
| Full compliance validation CI/CD pipeline (Phase 2) | All | DevSecOps Team | 2026-10-31 |
| Third-party penetration test (data layer scope) | All | External Auditor | 2026-11-15 |
| FIPS 140-3 module inventory final certification check | All | Security Engineering | 2026-11-30 |
| Annual compliance audit report | All | CISO / Security Engineering | 2026-12-15 |
| DR tabletop exercise (data layer focus) | All | Platform DBA Team + Ops | 2026-12-31 |

---

## Roles and Responsibilities

| Role | Responsibilities |
|---|---|
| **Platform DBA Team** | Day-to-day database configuration, encryption key rotation, backup scheduling, restore testing |
| **Security Engineering** | Cryptographic standard definition, Vault configuration, audit pipeline, compliance automation |
| **Infrastructure Team** | Network isolation, certificate management, TLS termination, firewall rules |
| **Identity Team** | OIDC provider configuration, service account lifecycle, MFA enforcement |
| **DevSecOps Team** | CI/CD compliance gates, automated validation scripts, drift detection |
| **Application Teams** | RocksDB integration, application-level audit hooks, service account credential rotation |
| **CISO / Security** | Policy ownership, audit report sign-off, escalation authority |

---

## Governance and Review Cadence

| Activity | Frequency | Owner |
|---|---|---|
| Compliance checklist review | Quarterly | Security Engineering |
| Key rotation verification | Monthly (automated) / Quarterly (manual audit) | Platform DBA Team |
| Audit log completeness check | Monthly | Security Engineering |
| Penetration testing | Annual (external) + Semi-annual (internal) | CISO |
| Disaster recovery testing | Quarterly tabletop; Annual full exercise | Platform DBA Team + Ops |
| Certificate expiry review | Monthly (automated) / 30-day pre-expiry alert | Infrastructure Team |
| Algorithm sunset review | Annual; triggered by NIST advisories | Security Engineering |
| Document review and update | Quarterly | Document owner (listed per file) |

All governance exceptions must be approved by the CISO and documented with a risk acceptance record in `standards/audit-forensics/`. No permanent exceptions are permitted for disallowed algorithms.
