# NIST SP 800-53 Rev. 5 Control Mappings

**Status:** Active  
**Authority:** SocioProphet/socioprophet-standards-storage  
**Last Reviewed:** 2026-04-06  
**Next Review:** 2026-07-01  
**Reference:** https://csrc.nist.gov/publications/detail/sp/800-53/rev-5/final

---

## Overview

This document maps NIST SP 800-53 Rev. 5 security controls to their implementation locations
within the SocioProphet platform. Each control entry specifies the implementation description,
evidence location, compliance status, cryptographic bindings required, and audit event
specifications.

This document uses RFC 2119 language: **MUST**, **SHOULD**, **MAY**.

---

## Control Status Key

| Symbol | Meaning |
|--------|---------|
| ✅ Implemented | Control is fully implemented with evidence |
| 📋 Planned | Control is designed and scheduled for implementation |
| ❌ Not Started | Control has not been addressed |
| 🔍 Review Required | Control needs assessment against current implementation |

---

## AC – Access Control

### AC-2 — Account Management

| Field | Value |
|-------|-------|
| **Status** | 📋 Planned |
| **Implementation** | OIDC-based identity management via workspace controller. Service accounts provisioned through the sociosphere manifest system. Account lifecycle events (create, modify, disable, delete) emitted as immutable audit records. |
| **Evidence Location** | `sociosphere/auth/oidc.py`, `sociosphere/docs/GLOSSARY-FIPS.md` |
| **Cryptographic Binding** | ECDSA P-256 token signing; HKDF-SHA-256 session key derivation |
| **Audit Events** | `AccountCreated`, `AccountModified`, `AccountDisabled`, `AccountDeleted`, `AccountReviewed` |

### AC-3 — Access Enforcement

| Field | Value |
|-------|-------|
| **Status** | 📋 Planned |
| **Implementation** | Policy engine enforces access decisions on every API call. No implicit trust; every request evaluated against current policy state. Decisions logged as `AccessGranted` or `AccessDenied` events. |
| **Evidence Location** | `sociosphere/policy/engine.py`, `docs/standards/050-security-oidc-policy.md` |
| **Cryptographic Binding** | JWT verification with ECDSA P-256; mTLS for service-to-service channels |
| **Audit Events** | `AccessGranted`, `AccessDenied`, `PolicyEvaluated` |

### AC-6 — Least Privilege

| Field | Value |
|-------|-------|
| **Status** | ✅ Implemented |
| **Implementation** | Workspace controller scopes OIDC tokens to minimum required permissions per operation. Build execution tokens include only the build-scoped claims. Manifest fetch tokens are read-only. |
| **Evidence Location** | `sociosphere/ontologies/sociosphere-fips-schema.jsonld`, `sociosphere/ontologies/sociosphere-fips.ttl` |
| **Cryptographic Binding** | ECDSA P-256 token claims; scope enforcement in JWT `scp` field |
| **Audit Events** | `TokenIssued` (with scope), `PrivilegeEscalationAttempt`, `ScopeViolation` |

### AC-17 — Remote Access

| Field | Value |
|-------|-------|
| **Status** | 📋 Planned |
| **Implementation** | All remote access **MUST** use TLS 1.3 (RFC 8446) with FIPS-approved cipher suites. Remote sessions authenticated via OIDC; MFA required for privileged operations. Session tokens expire after 60 minutes; refresh tokens after 24 hours. |
| **Evidence Location** | `sociosphere/transport/tls.py` |
| **Cryptographic Binding** | TLS 1.3 with AES-256-GCM, ECDHE-P256; no TLS < 1.2 permitted |
| **Audit Events** | `RemoteSessionStarted`, `RemoteSessionTerminated`, `MFAChallengeIssued`, `MFAChallengeCompleted` |

---

## AU – Audit and Accountability

### AU-2 — Event Logging

| Field | Value |
|-------|-------|
| **Status** | 📋 Planned |
| **Implementation** | All security-relevant events **MUST** be logged. Log entries include: timestamp (RFC 3161 TSA token), principal identity, action, outcome, and correlation ID. Log entries are cryptographically signed with ECDSA P-256. |
| **Evidence Location** | `sociosphere/audit/logger.py` |
| **Cryptographic Binding** | ECDSA P-256 per-entry signature; SHA-256 hash chain linking entries |
| **Audit Events** | All events below; see [NIST-800-88.md](../audit-forensics/NIST-800-88.md) |

### AU-3 — Content of Audit Records

| Field | Value |
|-------|-------|
| **Status** | 📋 Planned |
| **Implementation** | Each audit record **MUST** contain: event type, timestamp (ISO 8601 + RFC 3161 token), source IP/identity, object acted upon, action taken, outcome, session/correlation ID, and node identity. |
| **Evidence Location** | `sociosphere/audit/schema.py` |
| **Cryptographic Binding** | ECDSA P-256 signature covering full record JSON; previous-entry hash |
| **Audit Events** | Audit record schema enforced at emission time |

### AU-9 — Protection of Audit Information

| Field | Value |
|-------|-------|
| **Status** | 📋 Planned |
| **Implementation** | Audit logs stored on WORM (Write-Once-Read-Many) storage. Append-only; modification and deletion operations rejected. Access to audit logs restricted to authorized audit roles; access itself logged. |
| **Evidence Location** | `sociosphere/audit/storage.py` |
| **Cryptographic Binding** | AES-256-GCM encryption at rest; HMAC-SHA-256 integrity seals |
| **Audit Events** | `AuditLogAccessed`, `AuditLogExportRequested`, `AuditIntegrityViolation` |

### AU-10 — Non-Repudiation

| Field | Value |
|-------|-------|
| **Status** | 📋 Planned |
| **Implementation** | Every action by a principal is bound to a cryptographic proof. ECDSA P-256 signatures on all records. RFC 3161 trusted timestamps prevent backdating. See also [NIST-800-88.md](../audit-forensics/NIST-800-88.md). |
| **Evidence Location** | `sociosphere/audit/non_repudiation.py` |
| **Cryptographic Binding** | ECDSA P-256 per-action signature; RFC 3161 TSA token |
| **Audit Events** | `ActionCommitted` (signed), `SignatureVerified`, `TimestampTokenIssued` |

### AU-11 — Audit Record Retention

| Field | Value |
|-------|-------|
| **Status** | 📋 Planned |
| **Implementation** | Audit records **MUST** be retained for a minimum of 3 years (or applicable regulatory period). Records archived to WORM object storage with integrity verification on retrieval. |
| **Evidence Location** | `sociosphere/audit/retention.py` |
| **Cryptographic Binding** | AES-256-GCM for archival; SHA-256 content hashes for retrieval verification |
| **Audit Events** | `AuditRecordArchived`, `RetentionPolicyApplied`, `RetentionViolation` |

### AU-12 — Audit Record Generation

| Field | Value |
|-------|-------|
| **Status** | 📋 Planned |
| **Implementation** | All components **MUST** emit audit records via the platform-standard audit library. Records generated at the point of action; never buffered in a way that could result in loss. |
| **Evidence Location** | `sociosphere/audit/emitter.py` |
| **Cryptographic Binding** | HMAC-SHA-256 message authentication on transport |
| **Audit Events** | Per-component event catalog maintained in `sociosphere/audit/events/` |

---

## IA – Identification and Authentication

### IA-2 — Identification and Authentication (Organizational Users)

| Field | Value |
|-------|-------|
| **Status** | ✅ Implemented |
| **Implementation** | All users and service accounts authenticated via OIDC/OAuth 2.0. MFA required for all human users accessing privileged operations. Token claims include identity, roles, and scope. |
| **Evidence Location** | `sociosphere/ontologies/sociosphere-fips-schema.jsonld` (OIDC binding section), `sociosphere/docs/GLOSSARY-FIPS.md` |
| **Cryptographic Binding** | ECDSA P-256 ID token signing; PKCE for authorization code flow |
| **Audit Events** | `UserAuthenticated`, `MFAChallengeCompleted`, `AuthenticationFailed`, `TokenIssued` |

### IA-5 — Authenticator Management

| Field | Value |
|-------|-------|
| **Status** | 📋 Planned |
| **Implementation** | Credentials managed through centralized identity provider. Secrets stored only in approved HSM or secrets management system; never in source code. Credential rotation enforced on schedule (90-day maximum). |
| **Evidence Location** | `sociosphere/secrets/manager.py` |
| **Cryptographic Binding** | AES-256-GCM for credential storage; HKDF-SHA-256 for key derivation |
| **Audit Events** | `CredentialRotated`, `CredentialRevoked`, `CredentialExpiryWarning` |

### IA-8 — Identification and Authentication (Non-Organizational Users)

| Field | Value |
|-------|-------|
| **Status** | 📋 Planned |
| **Implementation** | External systems authenticated via mTLS client certificates or OIDC service tokens. Client certificates **MUST** use ECDSA P-256 or RSA-4096. Certificate validity verified on every connection. |
| **Evidence Location** | `sociosphere/transport/mtls.py` |
| **Cryptographic Binding** | mTLS with ECDSA P-256 client certificates; OCSP stapling for revocation |
| **Audit Events** | `ExternalSystemAuthenticated`, `CertificateValidationFailed`, `CertificateRevoked` |

---

## SC – System and Communications Protection

### SC-8 — Transmission Confidentiality and Integrity

| Field | Value |
|-------|-------|
| **Status** | 📋 Planned |
| **Implementation** | All network communication **MUST** use TLS 1.3. Approved cipher suites: `TLS_AES_256_GCM_SHA384`, `TLS_CHACHA20_POLY1305_SHA256`. No plaintext channels for any sensitive data. |
| **Evidence Location** | `sociosphere/transport/tls.py` |
| **Cryptographic Binding** | TLS 1.3; AES-256-GCM or ChaCha20-Poly1305; ECDHE-P256 key exchange |
| **Audit Events** | `TLSHandshakeCompleted`, `TLSHandshakeFailed`, `WeakCipherAttempt` |

### SC-12 — Cryptographic Key Establishment and Management

| Field | Value |
|-------|-------|
| **Status** | 📋 Planned |
| **Implementation** | Cryptographic keys generated in FIPS 140-2 Level 2 (or higher) HSM. Key lifecycle managed per NIST SP 800-57. Keys never exported in plaintext. Root keys rotated annually; session keys per-session. |
| **Evidence Location** | `sociosphere/crypto/key_management.py` |
| **Cryptographic Binding** | ECDSA P-256 signing keys; AES-256 wrapping keys; HKDF-SHA-256 derivation |
| **Audit Events** | `KeyGenerated`, `KeyRotated`, `KeyRevoked`, `KeyExportAttempt` |

### SC-13 — Cryptographic Protection

| Field | Value |
|-------|-------|
| **Status** | 📋 Planned |
| **Implementation** | Only FIPS-approved algorithms permitted (see [INDEX.md](../fips-compliance/INDEX.md) algorithm table). Algorithm selection enforced by policy; violations cause build/deploy failure. |
| **Evidence Location** | `sociosphere/crypto/policy.py`, `sociosphere/tools/validator/fips-compliance-checker.py` |
| **Cryptographic Binding** | Policy-enforced algorithm allowlist |
| **Audit Events** | `DisallowedAlgorithmDetected`, `CryptoOperationCompleted`, `PolicyViolation` |

### SC-17 — Public Key Infrastructure Certificates

| Field | Value |
|-------|-------|
| **Status** | 📋 Planned |
| **Implementation** | Certificates issued by approved CA. Certificate policies include: key usage constraints, SANs, validity periods (max 397 days for TLS), OCSP must-staple. Only ECDSA P-256 or RSA-4096 permitted. |
| **Evidence Location** | `sociosphere/pki/certificate_policy.py` |
| **Cryptographic Binding** | ECDSA P-256 or RSA-4096; SHA-256 certificate fingerprints |
| **Audit Events** | `CertificateIssued`, `CertificateRenewed`, `CertificateRevoked`, `OCSPQueryMade` |

### SC-28 — Protection of Information at Rest

| Field | Value |
|-------|-------|
| **Status** | 📋 Planned |
| **Implementation** | All sensitive data encrypted at rest using AES-256-GCM. Encryption keys stored in HSM; data keys wrapped with master key. Audit logs additionally protected with HMAC-SHA-256 integrity seals. |
| **Evidence Location** | `sociosphere/storage/encryption.py` |
| **Cryptographic Binding** | AES-256-GCM data encryption; RSA-4096 or ECDH P-256 key wrapping |
| **Audit Events** | `DataEncryptionApplied`, `DataDecryptionPerformed`, `EncryptionKeyAccessed` |

---

## SI – System and Information Integrity

### SI-3 — Malicious Code Protection

| Field | Value |
|-------|-------|
| **Status** | ❌ Not Started |
| **Implementation** | Dependency scanning integrated into CI/CD pipeline. Container images scanned for known vulnerabilities before deployment. Supply-chain integrity enforced via sigstore/cosign. |
| **Evidence Location** | `sociosphere/.github/workflows/security-scan.yml` (planned) |
| **Cryptographic Binding** | cosign ECDSA P-256 image signatures; SBOM attestation |
| **Audit Events** | `MaliciousCodeDetected`, `ScanCompleted`, `VulnerabilityFound` |

### SI-4 — System Monitoring

| Field | Value |
|-------|-------|
| **Status** | 📋 Planned |
| **Implementation** | Continuous monitoring of system behaviour. Anomaly detection based on baseline profiles. Real-time alerting on deviations. See [ZERO-TRUST-ARCHITECTURE.md](../nist-800-207/ZERO-TRUST-ARCHITECTURE.md) §Continuous Monitoring. |
| **Evidence Location** | `sociosphere/monitoring/anomaly_detector.py` |
| **Cryptographic Binding** | HMAC-SHA-256 integrity on monitoring data streams |
| **Audit Events** | `AnomalyDetected`, `BaselineDeviation`, `AlertTriggered`, `MonitoringGapDetected` |

### SI-7 — Software, Firmware, and Information Integrity

| Field | Value |
|-------|-------|
| **Status** | 📋 Planned |
| **Implementation** | All software artifacts signed with ECDSA P-256 at build time. Signature verification at deploy time. SBOM generated per build; stored in immutable audit trail. |
| **Evidence Location** | `sociosphere/build/integrity.py` |
| **Cryptographic Binding** | ECDSA P-256 artifact signatures; SHA-256 content hashes in SBOM |
| **Audit Events** | `ArtifactSigned`, `SignatureVerified`, `IntegrityViolationDetected` |

### SI-10 — Information Input Validation

| Field | Value |
|-------|-------|
| **Status** | 📋 Planned |
| **Implementation** | All external inputs validated against strict schemas before processing. Input validation failures logged and trigger rate-limiting. Validated input schemas published in `schemas/` directory of this repository. |
| **Evidence Location** | `schemas/`, `sociosphere/validation/input_validator.py` |
| **Cryptographic Binding** | Schema validation does not require cryptographic binding; used alongside signed manifests |
| **Audit Events** | `InputValidationFailed`, `MalformedInputReceived`, `SchemaViolation` |

---

## Cryptographic Requirements Table

| Use Case | Algorithm | Key Size | Mode | Standard |
|---------|-----------|----------|------|---------|
| Data encryption at rest | AES | 256-bit | GCM | FIPS 197, NIST SP 800-38D |
| Data encryption in transit | TLS 1.3 AES | 256-bit | GCM | RFC 8446 |
| Digital signatures | ECDSA | P-256 | — | FIPS 186-5 |
| Key agreement | ECDH | P-256 | — | NIST SP 800-56A Rev. 3 |
| Key derivation | HKDF | SHA-256 | — | RFC 5869, NIST SP 800-56C |
| Message authentication | HMAC | SHA-256 | — | FIPS 198-1 |
| Hashing (general) | SHA | 256-bit | — | FIPS 180-4 |
| Hashing (high-assurance) | SHA | 384-bit | — | FIPS 180-4 |

---

## Authentication Implementation Patterns

### OIDC (OpenID Connect) — Human Users

```
User → [Browser/Client]
        ↓  Authorization Code + PKCE
[OIDC Provider]
        ↓  ID Token (ECDSA P-256 signed)
[Workspace Controller]
        ↓  Token verified, scope enforced
[Resource / API]
```

**Requirements:**
- PKCE (RFC 7636) **MUST** be used for all public clients
- ID tokens **MUST** be short-lived (≤ 60 minutes)
- Refresh tokens **MUST** expire after 24 hours
- MFA **MUST** be required for privileged operations

### mTLS — Service-to-Service

```
Service A → [TLS 1.3 + Client Certificate]
             ↓  mTLS handshake (ECDSA P-256)
Service B  → [Verify client certificate]
             ↓  Authorize via policy engine
[Resource]
```

**Requirements:**
- Client certificates **MUST** use ECDSA P-256 or RSA-4096
- OCSP stapling **MUST** be enabled
- Certificates **MUST** include explicit key usage constraints

### MFA — Multi-Factor Authentication

MFA **MUST** be enforced for:
- All human users accessing production systems
- Build execution operations
- Key management operations
- Audit log access

Approved second factors: TOTP (RFC 6238), hardware security keys (FIDO2/WebAuthn).

---

## Audit and Accountability Specifications

See [standards/audit-forensics/NIST-800-88.md](../audit-forensics/NIST-800-88.md) for the full specification.

**Mandatory audit fields per record:**

| Field | Type | Description |
|-------|------|-------------|
| `event_id` | UUID v4 | Unique record identifier |
| `event_type` | string | Enumerated event type |
| `timestamp` | ISO 8601 | Wall clock timestamp (UTC) |
| `tsa_token` | base64 | RFC 3161 trusted timestamp token |
| `principal_id` | string | Authenticated identity of actor |
| `source_ip` | string | Source IP or service identifier |
| `resource` | string | Object acted upon |
| `action` | string | Action performed |
| `outcome` | enum | `success` \| `failure` \| `error` |
| `session_id` | UUID v4 | Correlation identifier |
| `prev_hash` | SHA-256 hex | Hash of preceding log entry |
| `signature` | base64 | ECDSA P-256 signature over this record |

---

## Boundary Protection and Micro-Segmentation

The platform is divided into four trust domains. All cross-domain traffic **MUST** be
explicitly authorized. See [ZERO-TRUST-ARCHITECTURE.md](../nist-800-207/ZERO-TRUST-ARCHITECTURE.md)
for the full micro-segmentation specification.

| Domain | Description | Trust Level |
|--------|-------------|-------------|
| Control Plane | Policy engine, identity provider, manifest store | Highest |
| Build Plane | Build executors, artifact stores | High |
| Data Plane | Storage backends, databases | High |
| Operations Plane | Monitoring, alerting, audit sinks | Medium |

Cross-domain communication: always TLS 1.3 + mTLS client authentication + policy-engine authorization.

---

## Control Status Summary by Category

| Control | Title | Status |
|---------|-------|--------|
| AC-2 | Account Management | 📋 Planned |
| AC-3 | Access Enforcement | 📋 Planned |
| AC-6 | Least Privilege | ✅ Implemented |
| AC-17 | Remote Access | 📋 Planned |
| AU-2 | Event Logging | 📋 Planned |
| AU-3 | Content of Audit Records | 📋 Planned |
| AU-9 | Protection of Audit Information | 📋 Planned |
| AU-10 | Non-Repudiation | 📋 Planned |
| AU-11 | Audit Record Retention | 📋 Planned |
| AU-12 | Audit Record Generation | 📋 Planned |
| IA-2 | Identification and Authentication (Users) | ✅ Implemented |
| IA-5 | Authenticator Management | 📋 Planned |
| IA-8 | Identification and Authentication (Non-Org) | 📋 Planned |
| SC-8 | Transmission Confidentiality and Integrity | 📋 Planned |
| SC-12 | Cryptographic Key Establishment and Management | 📋 Planned |
| SC-13 | Cryptographic Protection | 📋 Planned |
| SC-17 | Public Key Infrastructure Certificates | 📋 Planned |
| SC-28 | Protection of Information at Rest | 📋 Planned |
| SI-3 | Malicious Code Protection | ❌ Not Started |
| SI-4 | System Monitoring | 📋 Planned |
| SI-7 | Software, Firmware, and Information Integrity | 📋 Planned |
| SI-10 | Information Input Validation | 📋 Planned |

---

## Compliance Evidence and Assessment Procedures

### Evidence Collection

For each ✅ Implemented control:
1. Locate evidence files at the paths listed in the "Evidence Location" column.
2. Run the FIPS compliance checker: `python3 sociosphere/tools/validator/fips-compliance-checker.py`
3. Verify audit log integrity by replaying hash chain.
4. Confirm MFA and OIDC tokens are correctly scoped.

### Assessment Schedule

| Activity | Frequency |
|---------|-----------|
| Automated compliance scan (CI) | Every commit |
| Internal control review | Quarterly |
| External audit | Annually |
| Penetration test | Annually (Q4) |

---

## References

| Standard | URL |
|---------|-----|
| NIST SP 800-53 Rev. 5 | https://csrc.nist.gov/publications/detail/sp/800-53/rev-5/final |
| NIST SP 800-57 (Key Mgmt) | https://csrc.nist.gov/publications/detail/sp/800-57-part-1/rev-5/final |
| NIST SP 800-56A Rev. 3 | https://csrc.nist.gov/publications/detail/sp/800-56a/rev-3/final |
| NIST SP 800-56C Rev. 2 | https://csrc.nist.gov/publications/detail/sp/800-56c/rev-2/final |
| FIPS 140-2/140-3 | https://csrc.nist.gov/projects/cryptographic-module-validation-program/ |
| RFC 8446 (TLS 1.3) | https://tools.ietf.org/html/rfc8446 |
| RFC 7636 (PKCE) | https://tools.ietf.org/html/rfc7636 |
| RFC 6238 (TOTP) | https://tools.ietf.org/html/rfc6238 |
| RFC 3161 (TSP) | https://tools.ietf.org/html/rfc3161 |
| RFC 5869 (HKDF) | https://tools.ietf.org/html/rfc5869 |
| DISA STIGs | https://public.cyber.mil/stigs/ |
