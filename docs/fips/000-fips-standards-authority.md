# FIPS Standards Authority: NIST/FIPS 140-2/140-3 Foundation

This document uses RFC 2119 language: **MUST**, **SHOULD**, **MAY**.

---

## 1. Scope and applicability

All SocioProphet services that handle cryptographic key material, authenticate users or services, or protect data at rest or in transit MUST comply with the controls in this document.

This standard maps to:

- **FIPS 140-2 / FIPS 140-3** — Security Requirements for Cryptographic Modules
- **NIST SP 800-53 Rev 5** — Security and Privacy Controls (28 selected controls)
- **NIST SP 800-57** — Key Management Recommendations

---

## 2. Approved cryptographic algorithms

| Category | Approved | Prohibited |
|----------|----------|------------|
| Symmetric encryption | AES-128, AES-256 (GCM, CBC) | DES, 3DES, RC4, Blowfish |
| Hashing | SHA-256, SHA-384, SHA-512, SHA-3 | MD5, SHA-1 |
| Asymmetric / key exchange | RSA-2048+, ECDSA P-256/P-384, ECDH P-256/P-384 | RSA < 2048, DSA < 2048 |
| MAC | HMAC-SHA-256, HMAC-SHA-512, CMAC-AES | HMAC-MD5, HMAC-SHA-1 |
| Key derivation | PBKDF2, HKDF, SP 800-108 KDF | Custom/non-NIST KDFs |
| Random number generation | NIST SP 800-90A DRBG (CTR_DRBG, Hash_DRBG) | /dev/random (unvalidated), custom PRNGs |

Implementations MUST use FIPS-validated cryptographic modules (CMVP certificate required for production).

---

## 3. Key management requirements

- Cryptographic keys MUST be managed by a FIPS-validated secrets authority (HashiCorp Vault with FIPS-validated backend, AWS KMS, or equivalent).
- Key material MUST NOT be stored in source code, environment variables, or unencrypted configuration files.
- Key rotation MUST be automated: data-encryption keys rotated every 90 days; signing keys rotated annually.
- Key escrow and backup procedures MUST be documented and tested quarterly.
- Key access MUST be logged as immutable audit events.

---

## 4. Transport security

- All service-to-service communication MUST use TLS 1.2+ with FIPS-approved cipher suites.
- TLS 1.3 is RECOMMENDED; TLS 1.0/1.1 MUST be disabled.
- Mutual TLS (mTLS) MUST be enforced for all internal service mesh traffic.
- Certificate lifetimes SHOULD NOT exceed 90 days for service certificates; MUST NOT exceed 397 days for all certificates.

---

## 5. Data protection

- Data at rest MUST be encrypted with AES-256 using FIPS-validated modules.
- Database-level encryption MUST be enabled for all six canonical stores (PostgreSQL, MongoDB, Elasticsearch, Redis, MinIO, RocksDB).
- Backup data MUST be encrypted with the same controls as primary data.
- Data minimization MUST be applied: fields not required for a given context MUST be excluded from payloads.

---

## 6. Authentication and access control

- All human access to production systems MUST use multi-factor authentication (MFA).
- Service identities MUST use short-lived certificates or tokens (maximum TTL: 24 hours).
- Role-based access control (RBAC) MUST be implemented; least-privilege is the default.
- Access decisions MUST be centralized in a policy service and logged as immutable events.

---

## 7. Audit logging

- All cryptographic operations MUST generate audit log entries.
- Audit logs MUST be tamper-evident (append-only, cryptographically signed).
- Log retention MUST be a minimum of 12 months online, 7 years archived.
- Logs MUST include: timestamp (UTC), actor identity, operation type, resource identifier, outcome (success/failure).

---

## 8. Vulnerability and patch management

- FIPS-validated cryptographic modules MUST be updated within 30 days of a CMVP advisory.
- Operating system and runtime patches rated Critical or High MUST be applied within 14 days.
- A software bill of materials (SBOM) MUST be maintained and reviewed quarterly.

---

## 9. NIST 800-53 control mapping

The following 28 controls are in-scope for the FIPS certification programme:

| Control ID | Family | Title | STEP |
|------------|--------|-------|------|
| AC-2 | Access Control | Account Management | 1 |
| AC-3 | Access Control | Access Enforcement | 1 |
| AC-17 | Access Control | Remote Access | 3 |
| AU-2 | Audit and Accountability | Event Logging | 2 |
| AU-3 | Audit and Accountability | Content of Audit Records | 2 |
| AU-9 | Audit and Accountability | Protection of Audit Information | 2 |
| AU-12 | Audit and Accountability | Audit Record Generation | 2 |
| CA-2 | Assessment | Control Assessments | 7 |
| CA-7 | Assessment | Continuous Monitoring | 10 |
| CM-6 | Configuration Management | Configuration Settings | 3 |
| CM-7 | Configuration Management | Least Functionality | 3 |
| IA-2 | Identification and Authentication | Multi-Factor Authentication | 1 |
| IA-5 | Identification and Authentication | Authenticator Management | 1 |
| IA-8 | Identification and Authentication | Non-Organizational Users | 1 |
| MA-4 | Maintenance | Non-Local Maintenance | 9 |
| MP-5 | Media Protection | Media Transport | 2 |
| PE-3 | Physical and Environmental | Physical Access Control | 7 |
| PL-8 | Planning | Security and Privacy Architectures | 1 |
| RA-5 | Risk Assessment | Vulnerability Monitoring and Scanning | 8 |
| SA-9 | System and Services Acquisition | External System Services | 6 |
| SC-8 | System and Communications | Transmission Confidentiality and Integrity | 3 |
| SC-12 | System and Communications | Cryptographic Key Establishment and Management | 2 |
| SC-13 | System and Communications | Cryptographic Protection | 2 |
| SC-17 | System and Communications | Public Key Infrastructure Certificates | 3 |
| SC-28 | System and Communications | Protection of Information at Rest | 2 |
| SI-2 | System and Information Integrity | Flaw Remediation | 8 |
| SI-3 | System and Information Integrity | Malicious Code Protection | 8 |
| SI-7 | System and Information Integrity | Software, Firmware, and Information Integrity | 8 |

---

## 10. Compliance validation

- Automated FIPS compliance checks MUST run on every CI/CD commit.
- The FIPS validator tool MUST gate merges: non-compliant commits MUST be blocked.
- Compliance status MUST be surfaced in a dashboard visible to the governance committee.
- Third-party FIPS audit MUST be conducted in STEP 7 (Weeks 13–16).

---

## 11. Definitions

| Term | Definition |
|------|------------|
| CMVP | Cryptographic Module Validation Program (NIST/CCCS) |
| FIPS | Federal Information Processing Standard |
| FIPS 140-2 | Standard for cryptographic module security requirements |
| FIPS 140-3 | Successor to FIPS 140-2 (ISO/IEC 19790-based) |
| mTLS | Mutual TLS — both parties present certificates |
| RBAC | Role-Based Access Control |
| SBOM | Software Bill of Materials |
| TTL | Time to Live — maximum validity period of a credential |
| Zero-Trust | Security model: never implicit trust, always verify |

---

**Document version**: 1.0
**Status**: Active
**Effective**: Q2 2026
**Next review**: After STEP 7 audit (Q3/Q4 2026)
