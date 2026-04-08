# FIPS 140-2/140-3 and NIST Compliance Standard

This document uses RFC 2119 language: **MUST**, **SHOULD**, **MAY**.

## 1. Overview and Authority

This standard defines the cryptographic and security requirements for all SocioProphet platform components to achieve FIPS 140-2 Level 2 / FIPS 140-3 compliance and government-grade security posture, aligned with:

- **FIPS 140-2/140-3** — Cryptographic module security requirements
- **NIST SP 800-53 Rev. 5** — Security and privacy controls (28 critical controls)
- **NIST SP 800-207** — Zero-trust architecture principles
- **NIST SP 800-88** — Media sanitization and forensic-ready audit trails

## 2. Approved Cryptographic Algorithms

All cryptographic operations MUST use FIPS 140-2/140-3 validated algorithms only.

### 2.1 Symmetric Encryption
- Encryption at rest and in transit MUST use **AES-256-GCM** (FIPS 197, SP 800-38D).
- 3DES, RC4, DES, and any export-restricted ciphers MUST NOT be used.

### 2.2 Asymmetric Cryptography and Key Exchange
- Digital signatures MUST use **ECDSA with P-256** (NIST curve, FIPS 186-4) or **RSA-4096**.
- Key exchange MUST use **ECDH with P-256** or **X25519** (when operating outside strict FIPS mode).
- DSA and RSA-1024/2048 MUST NOT be used for new implementations.

### 2.3 Hash Functions
- All cryptographic hashes MUST use **SHA-256** or stronger (SHA-384, SHA-512) from the SHA-2 family (FIPS 180-4).
- MD5 and SHA-1 MUST NOT be used for cryptographic purposes.
- MD5 and SHA-1 MAY be used only for non-security checksums where explicitly documented.

### 2.4 Transport Layer Security
- All network connections MUST require **TLS 1.3** (RFC 8446).
- TLS 1.2 MAY be permitted only for legacy system compatibility with documented exceptions.
- TLS 1.1 and below MUST NOT be enabled.
- Cipher suites MUST be limited to AEAD suites (e.g., `TLS_AES_256_GCM_SHA384`, `TLS_CHACHA20_POLY1305_SHA256`).

### 2.5 Message Authentication
- HMAC MUST use **HMAC-SHA-256** or stronger (FIPS 198-1).
- Unauthenticated encryption modes MUST NOT be used.

### 2.6 Random Number Generation
- All cryptographic randomness MUST be sourced from a FIPS 140-2 approved DRBG (Deterministic Random Bit Generator) per SP 800-90A.
- `/dev/urandom` or OS-provided CSPRNG MUST be used; `Math.random()` or language-level pseudo-RNG MUST NOT be used for security purposes.

## 3. Key Management

- Cryptographic keys MUST be managed by a dedicated secrets management system (e.g., HashiCorp Vault).
- Key rotation MUST occur at least every **90 days** for symmetric keys and **1 year** for asymmetric keys.
- Key custody records MUST be maintained for audit purposes.
- Key material MUST NOT be stored in version control, configuration files, or unencrypted environment variables.
- Key Encryption Keys (KEKs) MUST be stored in an HSM or Vault-backed storage.

## 4. Authentication Requirements

- All user and service identities MUST authenticate using **OIDC/OAuth2** (see `050-security-oidc-policy.md`).
- Multi-factor authentication (MFA) MUST be enforced for all human users.
- Service-to-service authentication MUST use **mTLS** (mutual TLS with client certificates).
- Credential lifetime MUST NOT exceed 24 hours for short-lived tokens; 90 days for service accounts.
- Default credentials MUST be changed before deployment; hardcoded credentials MUST NOT be used.

## 5. Access Control (Least Privilege)

- All access MUST be governed by Role-Based Access Control (RBAC) with least-privilege principles.
- Service accounts MUST have only the permissions required for their specific function.
- Privileged access (e.g., DBA, cluster-admin) MUST be separated from application accounts.
- Quarterly access reviews MUST be conducted to validate and prune access grants.

## 6. Audit Logging Requirements

All systems MUST emit structured audit events for:
- Authentication events (login, logout, failure, MFA)
- Authorization decisions (allow/deny)
- Configuration changes (create, update, delete)
- Data access events (read, write, delete) for sensitive data
- Cryptographic key operations (creation, rotation, deletion)

Audit logs MUST:
- Be immutable once written (append-only or WORM storage)
- Include cryptographic signatures (ECDSA-P256 per entry or per batch)
- Include RFC 3161 trusted timestamps
- Be retained for a minimum of **7 years** for compliance purposes
- Be centralized to a tamper-evident log store (e.g., Elasticsearch, syslog-ng with signing)

Audit logs MUST NOT:
- Contain plaintext passwords, secrets, or PII beyond what is necessary
- Be deletable by the system being audited (separation of duty)

## 7. Encryption at Rest

All persistent data stores containing sensitive data MUST use encryption at rest:
- Symmetric cipher: AES-256-GCM
- Key management: Vault-managed KEK with per-tenant DEKs
- See `094-data-layer-fips-compliance.md` for per-system requirements

## 8. Certificate Management

- TLS certificates MUST use minimum **RSA-4096** or **ECDSA-P-256** keys.
- Certificates MUST be rotated before expiry with automated alerting at 30 days before expiration.
- Certificate Revocation MUST be supported via OCSP Stapling or CRL distribution.
- Certificate Transparency (CT) logs MUST be used for public-facing certificates.
- Internal PKI (cert-manager or Vault PKI) SHOULD be used for internal service certificates.

## 9. Compliance Verification

- Automated compliance checks MUST run on every CI/CD pipeline run.
- A daily automated compliance scan MUST verify cryptographic configuration of all services.
- Deviation from these standards MUST generate an alert within 5 minutes of detection.
- Annual third-party FIPS 140-2/140-3 assessment MUST be conducted by an NIST-accredited auditor.

## 10. Prohibited Practices

The following MUST NOT be used in any production or pre-production environment:
- Non-FIPS cryptographic libraries without explicit written exception
- Self-signed certificates on external-facing endpoints
- Static long-lived service account tokens without rotation
- Unauthenticated internal service endpoints
- Cleartext storage of any credentials or key material

## Related Standards

- `050-security-oidc-policy.md` — Identity, authorization, and policy
- `091-nist-800-53-control-mappings.md` — NIST 800-53 control-to-implementation mapping
- `092-zero-trust-nist-800-207.md` — Zero-trust architecture (NIST 800-207)
- `093-forensic-audit-nist-800-88.md` — Forensic-ready audit trails (NIST 800-88)
- `094-data-layer-fips-compliance.md` — Data layer FIPS compliance (6 database systems)
- `095-orchestration-fips-compliance.md` — Orchestration/Kubernetes FIPS compliance

## Implementation Evidence

- FIPS controls implemented in: `SocioProphet/sociosphere/auth/oidc.py`
- mTLS enforcement: `SocioProphet/sociosphere/mesh/mtls-policy.yaml`
- Key management: `SocioProphet/sociosphere/vault/vault-config.hcl`
- Certificate automation: `SocioProphet/sociosphere/k8s/cert-manager/`
- Audit log pipeline: `SocioProphet/sociosphere/observability/audit-pipeline.yaml`
