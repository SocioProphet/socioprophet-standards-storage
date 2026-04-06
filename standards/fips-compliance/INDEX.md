# FIPS 140-2/140-3 Compliance Standards Index

**Status:** Active  
**Authority:** SocioProphet/socioprophet-standards-storage  
**Last Reviewed:** 2026-04-06  
**Next Review:** 2026-07-01

---

## Overview

This document is the master index for FIPS 140-2/140-3 compliance, NIST cryptographic standards,
and related security frameworks across the SocioProphet platform. It defines what constitutes
FIPS/NIST compliance, maps controls to implementations, and establishes governance checkpoints.

All repositories that process, transmit, or store sensitive data **MUST** reference this index
and implement the controls described herein. This document uses RFC 2119 language: **MUST**,
**SHOULD**, **MAY**.

---

## FIPS 140-2 / FIPS 140-3 Framework

FIPS 140-2 (and its successor FIPS 140-3, aligned to ISO/IEC 19790:2012) define security
requirements for cryptographic modules used by federal agencies. The SocioProphet platform
**MUST** use only FIPS-validated cryptographic modules for all sensitive operations.

### Approved Cryptographic Algorithms

| Algorithm | Purpose | Minimum Key Length | Standard |
|-----------|---------|-------------------|---------|
| AES-256-GCM | Symmetric encryption | 256-bit | FIPS 197, NIST SP 800-38D |
| ECDSA P-256 | Digital signatures | 256-bit (equivalent) | FIPS 186-5 |
| ECDH P-256 | Key agreement | 256-bit | NIST SP 800-56A Rev. 3 |
| SHA-256 / SHA-384 | Hashing | 256-bit output minimum | FIPS 180-4 |
| HKDF-SHA-256 | Key derivation | 256-bit | RFC 5869, NIST SP 800-56C |
| RSA-4096 | Asymmetric encryption / sig | 4096-bit | FIPS 186-5 |
| HMAC-SHA-256 | Message authentication | 256-bit | FIPS 198-1 |

### Prohibited Algorithms

The following **MUST NOT** be used in any security-sensitive context:

- MD5, SHA-1 (broken collision resistance)
- DES, 3DES (deprecated by NIST 2024)
- RC4, RC2 (stream cipher weaknesses)
- RSA < 2048-bit (insufficient key strength)
- EC curves other than P-256, P-384, P-521

---

## Cross-Repository Mapping

| Repository | Role | FIPS Integration Status |
|-----------|------|------------------------|
| [SocioProphet/sociosphere](https://github.com/SocioProphet/sociosphere) | Workspace controller — primary implementation | ✅ Ontologies created; controls in progress |
| [SocioProphet/socioprophet-standards-storage](https://github.com/SocioProphet/socioprophet-standards-storage) | Standards authority — this repository | ✅ Active |
| [SocioProphet/socioprophet-standards-knowledge](https://github.com/SocioProphet/socioprophet-standards-knowledge) | Knowledge semantics — vocabulary and ontologies | 📋 Planned Q2 2026 |

### Implementation Artifacts in sociosphere

| Artifact | Path | Description |
|---------|------|-------------|
| FIPS Glossary | `docs/GLOSSARY-FIPS.md` | Controlled vocabulary, NIST 800-53 terminology |
| JSON-LD Ontology | `ontologies/sociosphere-fips-schema.jsonld` | Formal FIPS ontology definitions |
| RDF/Turtle Ontology | `ontologies/sociosphere-fips.ttl` | RDF semantic representation |
| Zero-Trust Bindings | `ontologies/zero-trust-govt-bindings.jsonld` | Interaction pattern specifications |
| TriTRPC FIPS Spec | `protocol/tritrpc-fips-spec.md` | Framework-level FIPS requirements |
| Compliance Checker | `tools/validator/fips-compliance-checker.py` | Automated CI/CD validation tool |
| Compliance Guide | `ontologies/FIPS-COMPLIANCE-GUIDE.md` | Executive guidance and control mappings |

---

## Standards Documents in This Repository

| Document | Path | Description |
|---------|------|-------------|
| NIST 800-53 Control Mappings | [standards/nist-800-53/CONTROL-MAPPINGS.md](../nist-800-53/CONTROL-MAPPINGS.md) | 28-control implementation matrix |
| Zero-Trust Architecture | [standards/nist-800-207/ZERO-TRUST-ARCHITECTURE.md](../nist-800-207/ZERO-TRUST-ARCHITECTURE.md) | NIST SP 800-207 deep-dive specification |
| Audit Trails & Forensics | [standards/audit-forensics/NIST-800-88.md](../audit-forensics/NIST-800-88.md) | NIST SP 800-88 forensic audit requirements |
| Integration Map | [standards/INTEGRATION-MAP.md](../INTEGRATION-MAP.md) | Cross-repository coherence tracking |

---

## NIST SP 800-53 Control Implementation Summary

| Control Family | Controls | Implemented | Planned | Not Started |
|---------------|---------|-------------|---------|-------------|
| AC – Access Control | AC-2, AC-3, AC-6, AC-17 | 1 | 3 | 0 |
| AU – Audit & Accountability | AU-2, AU-3, AU-9, AU-10, AU-11, AU-12 | 0 | 6 | 0 |
| IA – Identification & Authentication | IA-2, IA-5, IA-8 | 1 | 2 | 0 |
| SC – System & Comms Protection | SC-8, SC-12, SC-13, SC-17, SC-28 | 0 | 5 | 0 |
| SI – System & Info Integrity | SI-3, SI-4, SI-7, SI-10 | 0 | 3 | 1 |

Full control details: [standards/nist-800-53/CONTROL-MAPPINGS.md](../nist-800-53/CONTROL-MAPPINGS.md)

---

## NIST SP 800-207 Zero-Trust Principles

The platform **MUST** implement all five core zero-trust tenets as defined in NIST SP 800-207:

1. **Never Trust, Always Verify** — No implicit trust granted based on network location.
2. **Continuous Verification** — Authentication and authorization evaluated on every request.
3. **Least Privilege** — Access scoped to minimum permissions required for each operation.
4. **Assume Breach** — Design assumes adversary presence; limit blast radius.
5. **Micro-Segmentation** — Network and service boundaries enforced at the workload level.

Full specification: [standards/nist-800-207/ZERO-TRUST-ARCHITECTURE.md](../nist-800-207/ZERO-TRUST-ARCHITECTURE.md)

---

## NIST SP 800-88 Forensic Requirements Summary

All audit-trail implementations **MUST** satisfy:

- **Immutability** — Write-Once-Read-Many (WORM) storage; no deletion or modification.
- **Hash chaining** — Each entry includes the SHA-256 hash of the previous entry.
- **Digital signatures** — Every audit record signed with ECDSA P-256.
- **Trusted timestamps** — RFC 3161 TSA tokens on every write.
- **Chain of custody** — Documented preservation and evidence-handling procedures.

Full specification: [standards/audit-forensics/NIST-800-88.md](../audit-forensics/NIST-800-88.md)

---

## Integration Roadmap

### Q2 2026 (Current)

| Deliverable | Status | Repository |
|------------|--------|-----------|
| FIPS Glossary (GLOSSARY-FIPS.md) | ✅ Implemented | sociosphere |
| JSON-LD + RDF Ontologies | ✅ Implemented | sociosphere |
| Standards Index (this document) | ✅ Implemented | socioprophet-standards-storage |
| NIST 800-53 Control Mappings | ✅ Implemented | socioprophet-standards-storage |
| Zero-Trust Architecture spec | ✅ Implemented | socioprophet-standards-storage |
| Audit Trail spec (NIST 800-88) | ✅ Implemented | socioprophet-standards-storage |
| Integration Map | ✅ Implemented | socioprophet-standards-storage |
| Zero-Trust Bindings JSON-LD | 📋 Planned | sociosphere |
| TriTRPC FIPS Specification | 📋 Planned | sociosphere |
| FIPS Compliance Checker (CI) | 📋 Planned | sociosphere |

### Q3 2026

| Deliverable | Status |
|------------|--------|
| NIST 800-53 control evidence in sociosphere | 📋 Planned |
| Immutable audit trail implementation | 📋 Planned |
| Cryptographic key management (HSM integration) | 📋 Planned |
| CI/CD compliance validation pipeline | 📋 Planned |
| Standards-knowledge semantic alignment | 📋 Planned |

### Q4 2026

| Deliverable | Status |
|------------|--------|
| Third-party FIPS certification audit | 📋 Planned |
| Penetration testing & vulnerability assessment | 📋 Planned |
| Annual compliance review | 📋 Planned |
| Final documentation & certification package | 📋 Planned |

---

## Repository Coherence Status

| Repository | FIPS Crypto | NIST 800-53 | Zero-Trust | Audit Trail | Semantic Ontology |
|-----------|:-----------:|:-----------:|:----------:|:-----------:|:-----------------:|
| SocioProphet/sociosphere | ✅ | 📋 | 📋 | 📋 | ✅ |
| SocioProphet/socioprophet-standards-storage | ✅ | ✅ | ✅ | ✅ | 📋 |
| SocioProphet/socioprophet-standards-knowledge | 📋 | 📋 | 📋 | 📋 | 📋 |

Legend: ✅ Integrated · 📋 Planned · ❌ Not Started

---

## Compliance Checkpoints

Every artifact published in the SocioProphet platform **MUST** satisfy:

- ✅ References to applicable NIST standards (with CSRC URLs)
- ✅ Specific implementation locations in relevant repositories
- ✅ Status indicators (Implemented / Planned / Not Started)
- ✅ Cross-links to related controls and documents
- ✅ Government compliance context (FIPS, NIST, DISA, DoD)

---

## References

| Standard | URL |
|---------|-----|
| FIPS 140-2 | https://csrc.nist.gov/publications/detail/fips/140/2/final |
| FIPS 140-3 | https://csrc.nist.gov/publications/detail/fips/140/3/final |
| NIST SP 800-53 Rev. 5 | https://csrc.nist.gov/publications/detail/sp/800-53/rev-5/final |
| NIST SP 800-207 (Zero Trust) | https://csrc.nist.gov/publications/detail/sp/800-207/final |
| NIST SP 800-88 Rev. 1 | https://csrc.nist.gov/publications/detail/sp/800-88/rev-1/final |
| CMVP (Validated Modules) | https://csrc.nist.gov/projects/cryptographic-module-validation-program/ |
| FIPS 197 (AES) | https://csrc.nist.gov/publications/detail/fips/197/final |
| FIPS 186-5 (DSA/ECDSA) | https://csrc.nist.gov/publications/detail/fips/186/5/final |
| FIPS 180-4 (SHA) | https://csrc.nist.gov/publications/detail/fips/180/4/final |
| FIPS 198-1 (HMAC) | https://csrc.nist.gov/publications/detail/fips/198/1/final |
| RFC 5869 (HKDF) | https://tools.ietf.org/html/rfc5869 |
| RFC 3161 (TSP) | https://tools.ietf.org/html/rfc3161 |
| RFC 8446 (TLS 1.3) | https://tools.ietf.org/html/rfc8446 |
| DISA STIGs | https://public.cyber.mil/stigs/ |
