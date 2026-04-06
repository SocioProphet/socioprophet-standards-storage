# FIPS Compliance Index — SocioProphet Platform

- Last updated: 2026-01-27
- Status: Active governance document
- Owner: SocioProphet Platform Security

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Cross-Repository Mapping](#cross-repository-mapping)
3. [Cryptographic Standards Summary](#cryptographic-standards-summary)
4. [Disallowed Algorithms](#disallowed-algorithms)
5. [NIST 800-53 Control Implementation Status](#nist-800-53-control-implementation-status)
6. [Zero-Trust Architecture Overview](#zero-trust-architecture-overview)
7. [NIST 800-88 Forensics Requirements Summary](#nist-800-88-forensics-requirements-summary)
8. [Integration Roadmap](#integration-roadmap)
9. [Repository Coherence Status](#repository-coherence-status)
10. [Document Registry](#document-registry)

---

## Executive Summary

The SocioProphet platform adopts FIPS 140-2 (transitioning to FIPS 140-3) as its foundational cryptographic compliance framework. All cryptographic modules used in authentication, data protection, key management, and secure communications must operate within validated boundaries defined by the National Institute of Standards and Technology (NIST).

This index governs cryptographic policy across three repository layers:

- **sociosphere** — the primary application and workspace orchestration layer
- **socioprophet-standards-storage** — this repository; the governance and policy layer
- **socioprophet-standards-knowledge** — the knowledge engineering standards layer

The compliance posture is defense-in-depth: each layer independently enforces FIPS-approved algorithms, and cross-layer interactions are governed by explicit interface contracts validated at merge time.

### Compliance Objectives

- All symmetric and asymmetric cryptographic operations use only FIPS 140-2/140-3 approved algorithms.
- Authentication flows implement OIDC with FIPS-approved token signing and mTLS for service-to-service communication.
- Audit records are cryptographically signed, time-stamped via RFC 3161, and stored in write-once append-only stores.
- Key management follows NIST SP 800-57 key lifecycle requirements, with HSM-backed roots of trust for production environments.
- Zero-trust network architecture (NIST SP 800-207) is applied at all service boundaries.
- All 28 mapped NIST 800-53 controls are implemented or in active implementation with tracked evidence.

### Applicability

This policy applies to:

- All production and staging deployments of sociosphere services
- All CI/CD pipelines that build, sign, or distribute artifacts
- All operators and contributors with access to cryptographic material or production infrastructure
- All third-party integrations that exchange data with the SocioProphet platform

---

## Cross-Repository Mapping

The SocioProphet ecosystem spans multiple repositories. Each has a defined role in the FIPS compliance posture.

| Repository | Category | FIPS Role | Integration Status |
|---|---|---|---|
| sociosphere | Application | Consumes cryptographic primitives; enforces auth and audit | Integrated |
| socioprophet-standards-storage | Standards/Governance | Defines policy, controls, and evidence requirements | Authoritative |
| socioprophet-standards-knowledge | Standards/Knowledge | Inherits platform-wide cryptographic invariants | Pending alignment |
| prophet-cli | Tooling | Signs and verifies artifacts; consumes OIDC tokens | In Progress |
| socioprophet-docs | Documentation | Vendors pinned standards; no cryptographic operations | Planned |

### Policy Inheritance Chain

```
socioprophet-standards-storage  (authoritative policy)
         │
         ├── socioprophet-standards-knowledge  (inherits; adds knowledge-specific controls)
         │
         └── sociosphere  (implements; emits evidence)
                  │
                  └── prophet-cli  (tooling; artifact signing)
```

### Cross-Repository Artifact References

Pinned commit references between repositories must be updated via automated PRs that include:

1. A diff of the changed policy sections.
2. Evidence that all downstream validation gates still pass.
3. A sign-off from the platform security owner.

See [INTEGRATION-MAP.md](../INTEGRATION-MAP.md) for the full cross-repository status matrix.

---

## Cryptographic Standards Summary

Only FIPS 140-2/140-3 approved algorithms are permitted in any SocioProphet component. The following table is the authoritative approved algorithm list.

### Approved Symmetric Algorithms

| Algorithm | Key Size | Mode | Use Case | FIPS Reference |
|---|---|---|---|---|
| AES | 256 bits | GCM | Bulk data encryption, envelope encryption | FIPS 197, SP 800-38D |
| AES | 256 bits | CBC+HMAC-SHA256 | Legacy compatibility (must transition to GCM) | FIPS 197 |
| AES | 128/256 bits | CTR | Streaming encryption (with explicit nonce management) | FIPS 197, SP 800-38A |

AES-256-GCM is the **MUST** standard for all new implementations. GCM provides authenticated encryption (AEAD) eliminating the need for separate MAC operations.

### Approved Asymmetric Algorithms

| Algorithm | Parameters | Use Case | FIPS Reference |
|---|---|---|---|
| ECDSA | P-256 (secp256r1) | Digital signatures, artifact signing | FIPS 186-5 |
| ECDSA | P-384 (secp384r1) | High-assurance signatures, CA certificates | FIPS 186-5 |
| ECDH | P-256 / P-384 | Key agreement | SP 800-56A |
| RSA | 3072-bit minimum | Legacy interoperability only | FIPS 186-5 |

ECDSA-P256 is the **MUST** standard for artifact signing. ECDSA-P384 is required for CA-level certificates and high-assurance contexts.

### Approved Hash Functions

| Algorithm | Output | Use Case | FIPS Reference |
|---|---|---|---|
| SHA-256 | 256 bits | General integrity, HMAC, hash chains | FIPS 180-4 |
| SHA-384 | 384 bits | Certificate digests, high-assurance contexts | FIPS 180-4 |
| SHA-512 | 512 bits | Long-term archive integrity | FIPS 180-4 |
| SHA-3-256 | 256 bits | Post-quantum readiness (supplementary) | FIPS 202 |

SHA-1 and MD5 are explicitly disallowed (see below). SHA-256 is the minimum for all new hash operations.

### Approved Key Derivation Functions

| Algorithm | Hash | Use Case | FIPS Reference |
|---|---|---|---|
| HKDF | SHA-256 | Session key derivation, token binding | SP 800-56C |
| HKDF | SHA-384 | High-assurance key derivation | SP 800-56C |
| PBKDF2 | SHA-256 | Password-based key derivation (≥600,000 iterations) | SP 800-132 |

### Approved Transport Protocols

| Protocol | Version | Configuration | Use Case |
|---|---|---|---|
| TLS | 1.3 | MUST; FIPS-approved cipher suites only | All service-to-service and client-to-service |
| TLS | 1.2 | SHOULD NOT; permitted only for legacy interop with approved suites | Legacy clients only |
| mTLS | 1.3 | MUST for service mesh and internal RPC | All internal service communication |

TLS 1.0 and 1.1 are explicitly disallowed. TLS 1.2 is permitted only with a documented exception and must be scheduled for deprecation.

---

## Disallowed Algorithms

The following algorithms are **explicitly prohibited** across all SocioProphet components. Any use must be flagged as a critical finding in security review and blocked from merging.

| Algorithm | Reason | Replacement |
|---|---|---|
| MD5 | Cryptographically broken; collision attacks demonstrated | SHA-256 |
| SHA-1 | Collision attacks demonstrated (SHAttered, 2017) | SHA-256 |
| DES | 56-bit key; exhaustive search attacks trivial | AES-256-GCM |
| 3DES (Triple-DES) | Sweet32 birthday attacks; NIST deprecated 2017 | AES-256-GCM |
| RC4 | Multiple statistical biases; prohibited by RFC 7465 | AES-256-GCM |
| AES-ECB | Deterministic; patterns visible in ciphertext | AES-256-GCM |
| AES-CBC without MAC | Padding oracle attacks without authentication | AES-256-GCM |
| RSA < 2048-bit | Insufficient margin; NIST deprecated < 2048 | ECDSA-P256 or RSA-3072 |
| DSA (any key size) | NIST deprecated after 2023 | ECDSA-P256 |
| Diffie-Hellman < 2048-bit | Logjam attack; insufficient security margin | ECDH-P256 |
| TLS 1.0 / 1.1 | Protocol-level vulnerabilities (POODLE, BEAST) | TLS 1.3 |

Linters and static analysis gates in the CI/CD pipeline scan for use of disallowed algorithms using pattern matching and dependency analysis. Violations block merge.

---

## NIST 800-53 Control Implementation Status

The SocioProphet platform maps 20 baseline controls across seven control families, with 8 additional enhanced and supplemental controls targeted for Q3–Q4 2026 (bringing the full set to 28). Full implementation details are in [../nist-800-53/CONTROL-MAPPINGS.md](../nist-800-53/CONTROL-MAPPINGS.md).

### Control Family Summary (20 Baseline Controls)

| Family | Controls Mapped | Implemented | In Progress | Planned |
|---|---|---|---|---|
| AC — Access Control | 3 | 2 | 1 | 0 |
| AU — Audit & Accountability | 3 | 2 | 1 | 0 |
| IA — Identification & Authentication | 3 | 2 | 1 | 0 |
| SC — System & Communications Protection | 4 | 3 | 1 | 0 |
| SI — System & Information Integrity | 3 | 2 | 1 | 0 |
| CA — Assessment & Authorization | 2 | 1 | 1 | 0 |
| AT — Awareness & Training | 2 | 1 | 0 | 1 |
| **Total (baseline)** | **20** | **13** | **6** | **1** |

> Expansion target: 8 additional enhanced and supplemental controls (AC-6, AU-9, IA-8, SC-28, SI-3, SI-4, SA-9, CP-9) are planned for Q3–Q4 2026, bringing total coverage to 28 controls. See CONTROL-MAPPINGS.md for the current baseline mapping.

### High-Priority Controls

The following controls are classified as critical path for FIPS 140-2/140-3 compliance:

- **SC-13** (Cryptographic Protection) — governs algorithm selection; fully implemented
- **SC-12** (Cryptographic Key Establishment) — governs key lifecycle; in progress (HSM integration Q3 2026)
- **IA-5** (Authenticator Management) — governs credential lifecycle; implemented
- **AU-12** (Audit Record Generation) — governs event capture; implemented
- **SI-7** (Software & Information Integrity) — governs artifact signing; implemented

---

## Zero-Trust Architecture Overview

The SocioProphet platform implements zero-trust network architecture (ZTNA) per NIST SP 800-207. The core principle is that no implicit trust is granted to any subject, resource, or network path regardless of physical or logical location.

Full architecture documentation is in [../nist-800-207/ZERO-TRUST-ARCHITECTURE.md](../nist-800-207/ZERO-TRUST-ARCHITECTURE.md).

### Core Principles Applied

| Principle | Application in SocioProphet |
|---|---|
| Never Implicit Trust | Default-deny at all service boundaries; every request is authenticated |
| Continuous Verification | OIDC tokens with short TTLs (≤15 minutes); periodic re-authentication for long-lived sessions |
| Least Privilege | Scoped service accounts; no wildcard permissions; attribute-based access control (ABAC) |
| Assume Breach | Micro-segmentation; blast radius containment; immutable audit trails |

### Identity Plane

All service-to-service communication uses mTLS with certificates issued by the platform CA (backed by HSM root of trust). Human operator access uses OIDC with MFA enforced at the identity provider.

### Data Plane

Traffic is routed through the service mesh (Istio or Linkerd) with per-request authorization policy evaluated by the policy engine. Connections that do not present a valid certificate and a valid authorization token are rejected at the proxy layer before reaching application code.

---

## NIST 800-88 Forensics Requirements Summary

Audit records and forensic artifacts are governed by NIST SP 800-88 (Guidelines for Media Sanitization) and the platform's immutable audit trail requirements.

Full documentation is in [../audit-forensics/NIST-800-88.md](../audit-forensics/NIST-800-88.md).

### Key Requirements

| Requirement | Standard | Implementation |
|---|---|---|
| Write-Once storage | NIST 800-88 | WORM-enabled object storage (MinIO with object locking) |
| Hash chain integrity | FIPS 180-4 | SHA-256 chain across sequential log entries |
| Digital signatures | FIPS 186-5 | ECDSA-P256 per audit batch |
| Timestamps | RFC 3161 | Trusted timestamp authority integration |
| Retention | Platform policy | 7-year compliance archive; 90-day hot tier |
| Sanitization | NIST 800-88 | Cryptographic erasure for end-of-life media |

### Audit Event Categories

All authentication events, authorization decisions, cryptographic operations, system configuration changes, and data access operations are captured with the minimum fields: event type, subject identity, resource, outcome, timestamp (RFC 3161), and the SHA-256 of the previous record.

---

## Integration Roadmap

### Q2 2026 — Foundation

| Milestone | Target | Owner |
|---|---|---|
| FIPS-validated TLS 1.3 enforced across all services | All services | Platform Security |
| AES-256-GCM migration complete for data at rest | sociosphere, PostgreSQL | Backend |
| ECDSA-P256 artifact signing in CI/CD pipeline | prophet-cli, GitHub Actions | DevSecOps |
| WORM audit storage operational | MinIO | Infrastructure |
| NIST 800-53 control evidence collection automated | All services | Platform Security |

### Q3 2026 — Hardening

| Milestone | Target | Owner |
|---|---|---|
| HSM integration for key roots of trust | HashiCorp Vault + HSM | Infrastructure |
| HKDF-SHA256 session key derivation | sociosphere | Backend |
| SC-12 full implementation (key lifecycle management) | Vault | Infrastructure |
| RFC 3161 timestamp integration for audit chain | Audit service | Backend |
| Zero-trust service mesh deployment | Istio / Linkerd | Infrastructure |
| socioprophet-standards-knowledge alignment | standards-knowledge | Security Lead |

### Q4 2026 — Attestation & Validation

| Milestone | Target | Owner |
|---|---|---|
| First formal FIPS 140-3 validation submission | Platform Security | CISO |
| Continuous monitoring dashboard live | All services | DevSecOps |
| Cross-repository policy coherence audit | All repos | Platform Security |
| NIST 800-53 full 28-control evidence package complete | All services | Platform Security |
| Penetration test with FIPS scope | External assessor | CISO |

---

## Repository Coherence Status

Repository coherence means that the policies defined in this repository are faithfully reflected in the implementation repositories and that evidence of compliance is continuously collected and verifiable.

| Coherence Dimension | Status | Notes |
|---|---|---|
| Algorithm policy documented | ✅ Complete | This document + CONTROL-MAPPINGS.md |
| Algorithm policy enforced in CI | 🔄 In Progress | Linter gates for disallowed algorithms |
| Key management policy documented | ✅ Complete | CONTROL-MAPPINGS.md SC-12 |
| Key management implemented | 🔄 In Progress | Vault integration Q3 2026 |
| Audit trail policy documented | ✅ Complete | NIST-800-88.md |
| Audit trail implemented | 🔄 In Progress | WORM storage Q2 2026 |
| Zero-trust policy documented | ✅ Complete | ZERO-TRUST-ARCHITECTURE.md |
| Zero-trust implemented | 🔄 In Progress | Service mesh Q3 2026 |
| Cross-repo pin automation | 📋 Planned | Q2 2026 |
| External validation | 📋 Planned | Q4 2026 |

---

## Document Registry

All governance documents in the `standards/` directory tree are listed below. This registry is the canonical index; any document not listed here is not authoritative.

### FIPS Compliance

| Document | Path | Status | Description |
|---|---|---|---|
| FIPS Index (this document) | `standards/fips-compliance/INDEX.md` | Active | Master index and executive summary |

### NIST 800-53

| Document | Path | Status | Description |
|---|---|---|---|
| Control Mappings | `standards/nist-800-53/CONTROL-MAPPINGS.md` | Active | 28-control implementation matrix |

### NIST 800-207

| Document | Path | Status | Description |
|---|---|---|---|
| Zero-Trust Architecture | `standards/nist-800-207/ZERO-TRUST-ARCHITECTURE.md` | Active | ZTA design and implementation |

### Audit & Forensics

| Document | Path | Status | Description |
|---|---|---|---|
| NIST 800-88 Audit Requirements | `standards/audit-forensics/NIST-800-88.md` | Active | Immutable audit trail requirements |

### Integration

| Document | Path | Status | Description |
|---|---|---|---|
| Integration Map | `standards/INTEGRATION-MAP.md` | Active | Cross-repository status matrix |

### Related ADRs

| ADR | Path | Relevance |
|---|---|---|
| ADR-010 | `adr/ADR-010-storage-portfolio.md` | Storage selection; affects audit storage |
| ADR-020 | `adr/ADR-020-graph-store-abstraction.md` | Graph store; provenance and audit graph |
| ADR-030 | `adr/ADR-030-knowledge-context-repo-split.md` | Standards repo split; policy inheritance |
