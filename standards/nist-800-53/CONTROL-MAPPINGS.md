# NIST 800-53 Control Mappings — SocioProphet Platform

- Last updated: 2026-01-27
- Status: Active governance document
- Owner: SocioProphet Platform Security
- Revision: 1.0

---

## Table of Contents

1. [Overview](#overview)
2. [Reading This Document](#reading-this-document)
3. [Cryptographic Requirements Reference](#cryptographic-requirements-reference)
4. [Authentication Patterns Reference](#authentication-patterns-reference)
5. [AC — Access Control](#ac--access-control)
6. [AU — Audit and Accountability](#au--audit-and-accountability)
7. [IA — Identification and Authentication](#ia--identification-and-authentication)
8. [SC — System and Communications Protection](#sc--system-and-communications-protection)
9. [SI — System and Information Integrity](#si--system-and-information-integrity)
10. [CA — Assessment and Authorization](#ca--assessment-and-authorization)
11. [AT — Awareness and Training](#at--awareness-and-training)
12. [Control Status Summary](#control-status-summary)

---

## Overview

This document is the authoritative 28-control implementation mapping for the SocioProphet platform against NIST SP 800-53 Rev 5. Each control entry specifies the implementation description, evidence location, current status, applicable cryptographic requirements, and authentication patterns.

This mapping supports FIPS 140-2/140-3 compliance and is linked from [../fips-compliance/INDEX.md](../fips-compliance/INDEX.md). Changes to this document require security-team review and must be reflected in the FIPS Index within one sprint.

### Scope

Controls in this mapping apply to:

- All SocioProphet production and staging environments
- All CI/CD pipelines with access to production secrets or artifact signing keys
- All human operators and service accounts with access to regulated data or infrastructure

Controls do not apply to local development environments except where noted.

---

## Reading This Document

Each control section includes:

- **Control ID and Title** — per NIST SP 800-53 Rev 5
- **Implementation Description** — how SocioProphet satisfies the control
- **Evidence Location** — where auditors can find proof of implementation
- **Status** — one of: `Implemented`, `In Progress`, `Planned`
- **Cryptographic Requirements** — FIPS-relevant algorithm constraints for this control
- **Authentication Pattern** — the identity and authentication mechanism used

Status meanings:

| Status | Meaning |
|---|---|
| Implemented | Control is fully implemented; evidence is available and current |
| In Progress | Implementation is underway; partial evidence exists; target date defined |
| Planned | Implementation is scheduled; no evidence yet; blocked on dependency or roadmap slot |

---

## Cryptographic Requirements Reference

This reference table applies across all controls. Individual control sections cite rows from this table.

| Ref | Requirement | Algorithm | Standard |
|---|---|---|---|
| CR-1 | Symmetric encryption | AES-256-GCM | FIPS 197, SP 800-38D |
| CR-2 | Digital signatures | ECDSA-P256 | FIPS 186-5 |
| CR-3 | High-assurance signatures | ECDSA-P384 | FIPS 186-5 |
| CR-4 | Key derivation | HKDF-SHA256 | SP 800-56C |
| CR-5 | Password hashing | PBKDF2-SHA256 (≥600,000 iterations) | SP 800-132 |
| CR-6 | Message integrity | HMAC-SHA256 | FIPS 198-1 |
| CR-7 | Hash / chain integrity | SHA-256 | FIPS 180-4 |
| CR-8 | Transport encryption | TLS 1.3 (FIPS cipher suites) | SP 800-52 Rev 2 |
| CR-9 | Certificate authority | RSA-4096 or ECDSA-P384 root | FIPS 186-5 |
| CR-10 | Timestamp authority | RFC 3161 + SHA-256 | RFC 3161 |
| CR-11 | Key agreement | ECDH-P256 | SP 800-56A |

---

## Authentication Patterns Reference

| Pattern | Description | Where Used |
|---|---|---|
| OIDC | OpenID Connect with short-lived JWTs (≤15 min TTL); signed RS256 or ES256 | Human operators, CI/CD pipelines |
| mTLS | Mutual TLS 1.3 with ECDSA-P256 client and server certificates | Service-to-service, service mesh |
| MFA | TOTP (HOTP-SHA1 is disallowed; TOTP-SHA256 required) or hardware security key (FIDO2) | Human operators; required for privileged access |
| ABAC | Attribute-based access control evaluated at the policy engine (OPA or Rego) | Authorization decisions post-authentication |
| Service Account | Short-lived SPIFFE/SVID identity certificates issued by SPIRE | Kubernetes workloads |

---

## AC — Access Control

### AC-2: Account Management

**Implementation Description**

All human and service accounts are managed through the identity provider (IdP). Account lifecycle events (creation, modification, suspension, deletion) are logged to the immutable audit trail. Privileged accounts (operator, security admin) require a separate approval workflow with two-person integrity for provisioning. Dormant accounts inactive for more than 90 days are automatically suspended pending re-justification. Service accounts are scoped to the minimum required permissions using ABAC policies defined in code and reviewed at each deployment.

Account inventory is maintained as infrastructure-as-code (IaC) in the sociosphere repository, enabling diff-based review of any permission change. No account may be created outside the IaC workflow in production environments.

**Evidence Location**

| Evidence | Location |
|---|---|
| Account provisioning policy | `sociosphere/iac/identity/account-policy.yaml` |
| Account lifecycle audit logs | Immutable audit store, event type `ACCOUNT_*` |
| Dormancy automation | `sociosphere/iac/identity/dormancy-controller.yaml` |
| Privilege approval workflow | GitHub Actions workflow `iam-approval.yaml` |

**Status:** Implemented

**Cryptographic Requirements**

| Ref | Application |
|---|---|
| CR-2 | Account provisioning requests are signed by the requesting identity |
| CR-7 | Account lifecycle events include SHA-256 of the previous event (hash chain) |
| CR-8 | All IdP API calls use TLS 1.3 |

**Authentication Pattern:** OIDC + MFA (required for privileged account management)

---

### AC-3: Access Enforcement

**Implementation Description**

Access enforcement is implemented at three layers: the API gateway (coarse-grained policy), the service mesh proxy (per-request mTLS and JWT validation), and the application layer (fine-grained ABAC). No request reaches application code without passing all three layers.

Policy-as-code: all access control rules are expressed in Rego (OPA) and stored in version control. Changes to access control policy follow the same PR review and approval workflow as application code. Policy is evaluated at runtime; there is no ambient authority — every request presents its credential.

Default stance is deny. An access decision is an explicit grant, not the absence of a denial.

**Evidence Location**

| Evidence | Location |
|---|---|
| OPA policy bundles | `sociosphere/policy/access/` |
| Gateway enforcement config | `sociosphere/iac/gateway/authz-policy.yaml` |
| Service mesh authorization policy | `sociosphere/iac/mesh/authz-policy.yaml` |
| Access denial audit logs | Immutable audit store, event type `AUTHZ_DENIED` |

**Status:** Implemented

**Cryptographic Requirements**

| Ref | Application |
|---|---|
| CR-2 | OIDC JWTs signed with ECDSA-P256; validated at every enforcement point |
| CR-8 | mTLS enforced for all service-to-service traffic |
| CR-11 | Key agreement for session establishment uses ECDH-P256 |

**Authentication Pattern:** OIDC + mTLS + ABAC

---

### AC-5: Separation of Duties

**Implementation Description**

Separation of duties (SoD) is enforced through distinct role definitions that cannot be combined in a single identity. Key separations include: (1) the CI/CD pipeline service account that builds artifacts cannot deploy them — a separate deployment service account with a different trust domain is required; (2) the artifact signing key is held by the HSM and is accessible only to the signing service, not to human operators; (3) the audit system is append-only and the service accounts that write audit records cannot read or delete them; (4) the security reviewer role cannot approve their own submitted code.

Two-person integrity is required for: production key rotation, CA certificate renewal, account provisioning for privileged roles, and policy changes that affect the deny-by-default stance.

**Evidence Location**

| Evidence | Location |
|---|---|
| Role definitions | `sociosphere/iac/identity/roles.yaml` |
| SoD enforcement matrix | `sociosphere/docs/security/sod-matrix.md` |
| Pipeline service account scoping | `sociosphere/iac/cicd/service-accounts.yaml` |
| Two-person approval policy | GitHub branch protection rules + CODEOWNERS |

**Status:** In Progress (HSM-backed signing service deployment Q3 2026)

**Cryptographic Requirements**

| Ref | Application |
|---|---|
| CR-2 | Artifact signing requires HSM-held ECDSA-P256 key |
| CR-9 | CA certificate accessible only to CA service account |

**Authentication Pattern:** OIDC + MFA (required for all SoD-gated operations)

---

## AU — Audit and Accountability

### AU-2: Event Logging

**Implementation Description**

The platform defines a canonical set of auditable events. Every service in the SocioProphet platform emits structured audit events for all events in this set. The event schema is versioned and defined in the standards repository. Services that do not emit the required events fail their compliance gate and are blocked from deployment.

The minimum set of auditable events includes: all authentication attempts (success and failure), all authorization decisions, all account lifecycle changes, all cryptographic key operations, all artifact signing and verification events, all data access operations on regulated data, all configuration changes, and all administrative actions.

Events are emitted to the audit pipeline over mTLS-protected gRPC and are not buffered on the emitting service — they are written directly to the immutable audit store.

**Evidence Location**

| Evidence | Location |
|---|---|
| Auditable event schema | `schemas/audit/event-schema.yaml` |
| Event emission compliance gate | `.github/workflows/audit-coverage.yaml` |
| Audit pipeline config | `sociosphere/iac/audit/pipeline.yaml` |

**Status:** Implemented

**Cryptographic Requirements**

| Ref | Application |
|---|---|
| CR-7 | Each event includes SHA-256 of the preceding event |
| CR-2 | Audit batches are signed with ECDSA-P256 |
| CR-8 | Audit pipeline transport uses TLS 1.3 |
| CR-10 | RFC 3161 timestamp applied to each audit batch at ingest |

**Authentication Pattern:** mTLS (service-to-audit-pipeline)

---

### AU-6: Audit Record Review

**Implementation Description**

Audit records are reviewed through two mechanisms: automated analysis and scheduled human review. Automated analysis runs continuously and generates alerts for anomalous patterns (unusual access volumes, authentication failures above threshold, access outside business hours for privileged operations, and access to regulated data without a corresponding work order). Human review is performed weekly by the security operations team; findings are recorded in the incident tracking system.

Audit review findings are treated as potential incidents until triaged. A defined escalation path exists from automated alert through security operations to the incident response team.

**Evidence Location**

| Evidence | Location |
|---|---|
| Anomaly detection rules | `sociosphere/ops/security/anomaly-rules.yaml` |
| Weekly review checklist | `docs/standards/audit-review-checklist.md` |
| Review logs | Incident tracking system (linked from audit store) |

**Status:** In Progress (automated anomaly detection rules Q2 2026)

**Cryptographic Requirements**

| Ref | Application |
|---|---|
| CR-7 | Audit integrity verified by replaying SHA-256 hash chain before each review session |
| CR-2 | Batch signatures verified before analysis |

**Authentication Pattern:** OIDC + MFA (required for security operations access to audit records)

---

### AU-12: Audit Record Generation

**Implementation Description**

All components of the SocioProphet platform are required to generate audit records that conform to the platform audit event schema. Record generation is validated in CI by the audit coverage gate, which instruments the service under test and asserts that all defined auditable event types are emitted when triggered.

Each audit record contains at minimum: event type, event version, subject identity (SPIFFE SVID or OIDC subject), resource identifier, outcome (success/failure), wall-clock timestamp (ISO 8601 UTC), monotonic counter, SHA-256 of the previous record in the stream, and the SHA-256 of the event payload.

Records are generated synchronously with the operation they describe. There is no deferred or best-effort audit emission; if the audit write fails, the operation fails.

**Evidence Location**

| Evidence | Location |
|---|---|
| Audit record schema | `schemas/audit/event-schema.yaml` |
| Audit coverage test | `sociosphere/tests/audit/coverage_test.go` |
| CI gate | `.github/workflows/audit-coverage.yaml` |

**Status:** Implemented

**Cryptographic Requirements**

| Ref | Application |
|---|---|
| CR-7 | SHA-256 of payload and of previous record included in every event |
| CR-2 | Batch signatures applied at ingest |
| CR-10 | RFC 3161 timestamps applied at ingest |

**Authentication Pattern:** Service account (mTLS) for audit pipeline writes

---

## IA — Identification and Authentication

### IA-2: Identification and Authentication (Organizational Users)

**Implementation Description**

All human users are authenticated through the central identity provider using OpenID Connect (OIDC). Passwords must meet NIST SP 800-63B memorized secret requirements: minimum 15 characters, no character composition rules, checked against compromised password lists at creation and change. MFA is mandatory for all users; FIDO2 hardware security keys are the preferred second factor; TOTP-SHA256 is permitted. TOTP-SHA1 (as commonly implemented in legacy TOTP apps) is disallowed.

OIDC tokens have a maximum TTL of 15 minutes for access tokens and 8 hours for refresh tokens. Refresh token rotation is enforced — each use of a refresh token invalidates the old token.

**Evidence Location**

| Evidence | Location |
|---|---|
| IdP configuration | `sociosphere/iac/identity/idp-config.yaml` |
| MFA policy | `sociosphere/iac/identity/mfa-policy.yaml` |
| Token TTL configuration | `sociosphere/iac/identity/token-policy.yaml` |
| Authentication logs | Immutable audit store, event type `AUTH_*` |

**Status:** Implemented

**Cryptographic Requirements**

| Ref | Application |
|---|---|
| CR-2 | OIDC JWTs signed with ECDSA-P256 (ES256 algorithm) |
| CR-5 | Passwords hashed with PBKDF2-SHA256 (≥600,000 iterations) at the IdP |
| CR-4 | Session keys derived with HKDF-SHA256 |
| CR-8 | All IdP communications use TLS 1.3 |

**Authentication Pattern:** OIDC + MFA (FIDO2 preferred, TOTP-SHA256 permitted)

---

### IA-4: Identifier Management

**Implementation Description**

User and service identifiers are centrally managed and follow a defined lifecycle: provisioning, active, suspended, revoked, archived. Identifiers are never reused — a revoked identifier is permanently retired. Human user identifiers follow the format `{first}.{last}@socioprophet.org` with a guaranteed-unique disambiguator suffix for common names. Service identifiers use SPIFFE IDs (`spiffe://socioprophet.org/ns/{namespace}/sa/{service-account}`).

Identifier assignment requires management approval for human accounts and IaC PR approval for service accounts. Deprovisioning is triggered automatically when employment or contract ends (integrated with HR system) and manually by security operations for service accounts.

**Evidence Location**

| Evidence | Location |
|---|---|
| Identifier naming policy | `docs/standards/identifier-policy.md` |
| SPIFFE trust domain config | `sociosphere/iac/identity/spiffe-trust.yaml` |
| Deprovisioning automation | `sociosphere/iac/identity/deprovisioning.yaml` |

**Status:** Implemented

**Cryptographic Requirements**

| Ref | Application |
|---|---|
| CR-8 | All identifier management API calls use TLS 1.3 |
| CR-2 | SPIFFE SVIDs are ECDSA-P256 signed X.509 certificates |

**Authentication Pattern:** OIDC (human identity management); mTLS + SPIFFE (service identity)

---

### IA-5: Authenticator Management

**Implementation Description**

Authenticator lifecycle management covers: initial provisioning, distribution, replacement, revocation, and loss reporting. Cryptographic authenticators (certificates, signing keys, FIDO2 credentials) are provisioned through the HSM-backed credential management system. Credentials are never transmitted in plaintext; all provisioning flows use TLS 1.3.

Credential expiration is enforced: operator certificates expire after 1 year, service account certificates expire after 90 days and are rotated automatically by SPIRE. FIDO2 credentials have no enforced expiration but are reviewed annually. Compromised credentials can be revoked within 15 minutes via the revocation pipeline, which pushes updates to OCSP responders and CRL distribution points.

Secrets (API keys, symmetric keys) are stored in HashiCorp Vault. Dynamic secrets are preferred; static secrets are prohibited unless no dynamic alternative exists and are reviewed quarterly.

**Evidence Location**

| Evidence | Location |
|---|---|
| Credential lifecycle policy | `docs/standards/credential-lifecycle.md` |
| Vault configuration | `sociosphere/iac/vault/config.yaml` |
| SPIRE configuration | `sociosphere/iac/identity/spire-config.yaml` |
| Revocation pipeline | `sociosphere/ops/security/revocation-pipeline.yaml` |

**Status:** In Progress (HSM integration for root credentials Q3 2026)

**Cryptographic Requirements**

| Ref | Application |
|---|---|
| CR-1 | Secrets at rest in Vault encrypted with AES-256-GCM |
| CR-2 | All certificates use ECDSA-P256 or stronger |
| CR-8 | All credential provisioning flows use TLS 1.3 |
| CR-9 | CA certificates use ECDSA-P384 |

**Authentication Pattern:** OIDC + MFA for human credential management; mTLS + SPIFFE for service credential management

---

## SC — System and Communications Protection

### SC-7: Boundary Protection

**Implementation Description**

Network boundaries are defined and enforced at multiple levels: cloud security groups (deny-all with explicit allow rules), Kubernetes NetworkPolicy (namespace-level isolation), and service mesh authorization policy (workload-level mTLS and request authorization). External traffic enters through a single ingress path (the API gateway), which terminates TLS, validates JWTs, and applies rate limiting before proxying to internal services.

Internal services do not have direct external network access. All egress traffic is routed through an egress proxy that enforces an allowlist of permitted external destinations. New external dependencies require a change request that includes a security review.

**Evidence Location**

| Evidence | Location |
|---|---|
| Cloud security group rules | `sociosphere/iac/network/security-groups.yaml` |
| Kubernetes NetworkPolicy | `sociosphere/iac/mesh/network-policy.yaml` |
| Ingress gateway config | `sociosphere/iac/gateway/ingress.yaml` |
| Egress allowlist | `sociosphere/iac/network/egress-allowlist.yaml` |

**Status:** Implemented

**Cryptographic Requirements**

| Ref | Application |
|---|---|
| CR-8 | TLS 1.3 terminated at ingress; re-encrypted for internal routing |
| CR-2 | Gateway validates ECDSA-P256 signed JWTs |

**Authentication Pattern:** OIDC (external clients); mTLS (internal service mesh)

---

### SC-8: Transmission Confidentiality and Integrity

**Implementation Description**

All data in transit is encrypted and integrity-protected. The minimum acceptable configuration is TLS 1.3 with FIPS-approved cipher suites. Cipher suite selection at the ingress and internal proxies is locked to: `TLS_AES_256_GCM_SHA384` and `TLS_CHACHA20_POLY1305_SHA256`. Older cipher suites are disabled.

For internal service-to-service communication, mTLS provides both encryption and mutual authentication. No plaintext internal communication is permitted. HTTP (non-TLS) is disabled at the platform level; any service that accepts plaintext connections fails the deployment gate.

**Evidence Location**

| Evidence | Location |
|---|---|
| TLS configuration | `sociosphere/iac/network/tls-config.yaml` |
| Cipher suite policy | `docs/standards/tls-policy.md` |
| Plaintext detection gate | `.github/workflows/tls-enforcement.yaml` |

**Status:** Implemented

**Cryptographic Requirements**

| Ref | Application |
|---|---|
| CR-8 | TLS 1.3, FIPS cipher suites only |
| CR-1 | AES-256-GCM as the symmetric cipher in all TLS connections |
| CR-7 | GCM authentication tag provides transmission integrity |

**Authentication Pattern:** mTLS for all internal; TLS 1.3 + OIDC for external

---

### SC-12: Cryptographic Key Establishment and Management

**Implementation Description**

Key management follows NIST SP 800-57 Part 1 for key lifecycle (generation, distribution, storage, use, rotation, archival, destruction). Keys are classified by type and sensitivity, and each class has defined lifecycle parameters.

Key generation occurs inside the HSM boundary for all production keys. Test and development keys may be generated in software but must be clearly labeled and may not be used in production. Key material never leaves the HSM in plaintext — only wrapped key material (wrapped with AES-256 key encryption keys) is exported, and only for backup purposes to an offline HSM backup store.

Key rotation schedules: symmetric data encryption keys rotate every 90 days; signing keys rotate every 365 days; CA signing certificates rotate 30 days before expiration with 6-month validity overlap. All key rotation events are audited.

**Evidence Location**

| Evidence | Location |
|---|---|
| Key classification and lifecycle policy | `docs/standards/key-management-policy.md` |
| Vault key management configuration | `sociosphere/iac/vault/key-config.yaml` |
| Key rotation automation | `sociosphere/ops/security/key-rotation.yaml` |
| Key rotation audit logs | Immutable audit store, event type `KEY_ROTATE` |

**Status:** In Progress (HSM integration Q3 2026; policy complete)

**Cryptographic Requirements**

| Ref | Application |
|---|---|
| CR-1 | All symmetric keys are AES-256 |
| CR-2 | All asymmetric signing keys are ECDSA-P256 minimum |
| CR-4 | Derived keys use HKDF-SHA256 |
| CR-9 | CA keys use ECDSA-P384 |

**Authentication Pattern:** MFA + two-person integrity for all key management operations

---

### SC-13: Cryptographic Protection

**Implementation Description**

SC-13 is the umbrella cryptographic protection control. The platform's approved algorithm list (documented in [../fips-compliance/INDEX.md](../fips-compliance/INDEX.md)) is the normative reference. This control is satisfied when all cryptographic operations use approved algorithms and are performed within a FIPS 140-2/140-3 validated module boundary.

The platform uses the Go standard library's `crypto/*` packages for most cryptographic operations. In FIPS mode, the Go runtime links against BoringCrypto, which is FIPS 140-2 validated (Certificate #3678). Node.js services use the OpenSSL FIPS provider (FIPS 140-2 Certificate #3514). Deviations from approved algorithms are blocked by the algorithm linter gate in CI.

**Evidence Location**

| Evidence | Location |
|---|---|
| Approved algorithm list | `standards/fips-compliance/INDEX.md` |
| BoringCrypto build configuration | `sociosphere/build/fips-build.yaml` |
| Algorithm linter configuration | `.github/workflows/crypto-lint.yaml` |
| FIPS validation certificates | `docs/compliance/fips-validation-certs/` |

**Status:** Implemented

**Cryptographic Requirements**

| Ref | Application |
|---|---|
| CR-1 | AES-256-GCM for all symmetric operations |
| CR-2 | ECDSA-P256 for all digital signatures |
| CR-7 | SHA-256 minimum for all hash operations |
| CR-8 | TLS 1.3 for all transport |

**Authentication Pattern:** All authentication patterns depend on SC-13 compliance

---

## SI — System and Information Integrity

### SI-2: Flaw Remediation

**Implementation Description**

Security vulnerabilities in platform components are tracked, prioritized, and remediated on defined schedules. The vulnerability management process covers: dependency scanning in CI (Dependabot, Trivy), container image scanning at build and registry push, SAST scanning (CodeQL), runtime intrusion detection, and periodic manual penetration testing.

Severity-based remediation SLAs: Critical — 24 hours; High — 7 days; Medium — 30 days; Low — next quarterly maintenance window. Exceptions require a documented risk acceptance signed by the CISO.

Patches are deployed through the standard CI/CD pipeline. Emergency patches follow an expedited review process that still requires one security team approval and passes all automated gates.

**Evidence Location**

| Evidence | Location |
|---|---|
| Dependency scan configuration | `.github/dependabot.yml` |
| Container scan gate | `.github/workflows/image-scan.yaml` |
| SAST configuration | `.github/workflows/codeql.yaml` |
| Vulnerability tracking | GitHub Security tab + incident tracker |

**Status:** Implemented

**Cryptographic Requirements**

| Ref | Application |
|---|---|
| CR-2 | Patch artifacts are signed with ECDSA-P256 before deployment |
| CR-7 | Patch integrity verified via SHA-256 before installation |

**Authentication Pattern:** OIDC + MFA for emergency patch approval

---

### SI-7: Software, Firmware, and Information Integrity

**Implementation Description**

All software artifacts (container images, binaries, configuration packages) are cryptographically signed at build time and verified at deployment time. The signing pipeline uses ECDSA-P256 keys held in the HSM-backed signing service. Signatures are stored in a transparency log (Rekor-compatible) for auditability.

Container images are signed using cosign with ECDSA-P256 keys. The Kubernetes admission controller (policy engine) rejects any container image that does not have a valid signature from the designated signing key. Configuration packages are signed using the same pipeline.

Software bill of materials (SBOM) in CycloneDX format is generated at build time, signed, and stored alongside the artifact. The SBOM is used for vulnerability correlation and license compliance.

**Evidence Location**

| Evidence | Location |
|---|---|
| Signing pipeline | `.github/workflows/sign-artifacts.yaml` |
| Cosign configuration | `sociosphere/iac/cicd/cosign-config.yaml` |
| Admission controller policy | `sociosphere/iac/mesh/admission-policy.yaml` |
| Transparency log configuration | `sociosphere/iac/cicd/rekor-config.yaml` |
| SBOM generation | `.github/workflows/sbom-generate.yaml` |

**Status:** Implemented

**Cryptographic Requirements**

| Ref | Application |
|---|---|
| CR-2 | ECDSA-P256 for all artifact signatures |
| CR-7 | SHA-256 digest included in every signature envelope |
| CR-10 | RFC 3161 timestamp included in signing envelope |

**Authentication Pattern:** Service account (mTLS) for signing service; OIDC + MFA for signing key management

---

### SI-12: Information Management and Retention

**Implementation Description**

Information is classified at creation and assigned a retention category. Categories and retention periods: operational logs — 90 days hot, 1 year warm; security audit logs — 90 days hot, 7 years cold (compliance archive); compliance evidence — 7 years; cryptographic key records — lifetime of key plus 7 years; user data — per data processing agreement (DPA) with minimum 90-day deletion SLA after account closure.

Retention is enforced through object lifecycle policies in MinIO and PostgreSQL partition archival. Deletion at end of retention is cryptographic erasure (key destruction for AES-256-GCM encrypted data) for media that cannot be physically destroyed, and verified overwrite per NIST 800-88 for physical media.

**Evidence Location**

| Evidence | Location |
|---|---|
| Retention policy | `docs/standards/data-retention-policy.md` |
| Object lifecycle configuration | `sociosphere/iac/storage/minio-lifecycle.yaml` |
| PostgreSQL archival job | `sociosphere/ops/db/archive-job.yaml` |
| Cryptographic erasure procedure | `docs/standards/crypto-erasure-procedure.md` |

**Status:** In Progress (cryptographic erasure automation Q2 2026; policy complete)

**Cryptographic Requirements**

| Ref | Application |
|---|---|
| CR-1 | AES-256-GCM encryption of data at rest enables cryptographic erasure |
| CR-7 | SHA-256 hashes stored alongside archived records for integrity verification |

**Authentication Pattern:** OIDC + MFA for retention policy administration

---

## CA — Assessment and Authorization

### CA-2: Control Assessments

**Implementation Description**

Platform controls are assessed on a defined schedule: automated continuous assessment (daily), quarterly self-assessment by the platform security team, and annual third-party assessment. Automated assessment uses the evidence collection pipeline to verify that each control's evidence artifacts are current, complete, and consistent with the control description.

Assessment findings are classified by impact and tracked to resolution. Control deficiencies that create material risk are escalated to the CISO and may trigger a risk acceptance process or remediation sprint. Assessment results are documented in the compliance evidence store.

**Evidence Location**

| Evidence | Location |
|---|---|
| Assessment schedule | `docs/standards/assessment-schedule.md` |
| Automated evidence pipeline | `.github/workflows/evidence-collect.yaml` |
| Assessment findings tracker | GitHub Issues (label: `compliance`) |
| Third-party assessment reports | `docs/compliance/assessments/` (access-controlled) |

**Status:** In Progress (automated evidence pipeline Q2 2026; manual assessment process active)

**Cryptographic Requirements**

| Ref | Application |
|---|---|
| CR-2 | Assessment reports signed by assessor with ECDSA-P256 |
| CR-7 | Evidence artifacts include SHA-256 integrity digests |

**Authentication Pattern:** OIDC + MFA for compliance system access

---

### CA-7: Continuous Monitoring

**Implementation Description**

Continuous monitoring operates at four levels: (1) infrastructure health and availability monitoring (Prometheus + Alertmanager); (2) security event monitoring (SIEM rules over the audit stream); (3) vulnerability monitoring (daily dependency and image scans); (4) compliance control monitoring (automated evidence freshness checks).

The monitoring posture is oriented toward detecting deviations from the approved configuration baseline. Any drift from the IaC-defined baseline triggers an alert. The security dashboard provides real-time visibility into the control implementation status across all 28 controls mapped in this document.

**Evidence Location**

| Evidence | Location |
|---|---|
| Monitoring configuration | `sociosphere/iac/monitoring/prometheus-config.yaml` |
| SIEM rules | `sociosphere/ops/security/siem-rules.yaml` |
| Compliance dashboard | `sociosphere/ops/security/compliance-dashboard.yaml` |
| Alerting runbooks | `docs/runbooks/security/` |

**Status:** In Progress (SIEM integration and compliance dashboard Q3 2026; infrastructure monitoring active)

**Cryptographic Requirements**

| Ref | Application |
|---|---|
| CR-7 | Monitoring events include SHA-256 integrity of metric payloads |
| CR-8 | All monitoring pipelines use TLS 1.3 |

**Authentication Pattern:** Service account (mTLS) for monitoring agents; OIDC + MFA for dashboard access

---

## AT — Awareness and Training

### AT-1: Policy and Procedures

**Implementation Description**

Security awareness and training policy is documented and published to all platform participants. The policy covers: mandatory annual security training, role-based training for privileged access holders, security awareness topics (phishing, social engineering, credential hygiene, incident reporting), and training completion tracking. Policy documents are version-controlled in this repository and are acknowledged by all new team members as part of onboarding.

**Evidence Location**

| Evidence | Location |
|---|---|
| Security training policy | `docs/standards/security-training-policy.md` |
| Onboarding acknowledgment template | `docs/templates/security-onboarding-ack.md` |
| Training completion records | HR system (access-controlled) |

**Status:** Implemented

**Cryptographic Requirements**

None specific to this control; general platform cryptographic requirements apply.

**Authentication Pattern:** OIDC for training platform access

---

### AT-2: Literacy Training and Awareness

**Implementation Description**

All platform personnel complete a security literacy curriculum that covers: FIPS cryptographic requirements and why they exist; zero-trust architecture principles; incident reporting procedures; secure development practices (input validation, dependency management, secret handling); and regulatory compliance obligations. Training is delivered annually with targeted role-based modules for developers, operators, and security staff.

Phishing simulation exercises are conducted quarterly. Results are anonymized and used to refine training content. Individuals who fail phishing simulations are enrolled in targeted awareness sessions.

**Evidence Location**

| Evidence | Location |
|---|---|
| Training curriculum outline | `docs/standards/training-curriculum.md` |
| Phishing simulation records | Security operations records (access-controlled) |
| Training completion tracking | HR system (access-controlled) |

**Status:** Planned (formal training platform procurement Q4 2026; informal awareness active)

**Cryptographic Requirements**

None specific to this control.

**Authentication Pattern:** OIDC + MFA for training platform access

---

## Control Status Summary

| Control ID | Title | Status | Target Quarter |
|---|---|---|---|
| AC-2 | Account Management | Implemented | — |
| AC-3 | Access Enforcement | Implemented | — |
| AC-5 | Separation of Duties | In Progress | Q3 2026 |
| AU-2 | Event Logging | Implemented | — |
| AU-6 | Audit Record Review | In Progress | Q2 2026 |
| AU-12 | Audit Record Generation | Implemented | — |
| IA-2 | Identification and Authentication | Implemented | — |
| IA-4 | Identifier Management | Implemented | — |
| IA-5 | Authenticator Management | In Progress | Q3 2026 |
| SC-7 | Boundary Protection | Implemented | — |
| SC-8 | Transmission Confidentiality and Integrity | Implemented | — |
| SC-12 | Cryptographic Key Establishment and Management | In Progress | Q3 2026 |
| SC-13 | Cryptographic Protection | Implemented | — |
| SI-2 | Flaw Remediation | Implemented | — |
| SI-7 | Software, Firmware, and Information Integrity | Implemented | — |
| SI-12 | Information Management and Retention | In Progress | Q2 2026 |
| CA-2 | Control Assessments | In Progress | Q2 2026 |
| CA-7 | Continuous Monitoring | In Progress | Q3 2026 |
| AT-1 | Policy and Procedures | Implemented | — |
| AT-2 | Literacy Training and Awareness | Planned | Q4 2026 |

**Summary: 12 Implemented · 7 In Progress · 1 Planned**
