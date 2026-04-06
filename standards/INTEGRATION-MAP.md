# Cross-Repository Integration Map

**Status:** Living Document — updated as integrations progress  
**Authority:** SocioProphet/socioprophet-standards-storage  
**Last Updated:** 2026-04-06  
**Next Review:** 2026-07-01

---

## Overview

This document is the authoritative tracking record for FIPS 140-2/140-3 and NIST compliance
integration across all SocioProphet repositories. It records which repositories are integrated,
which are pending, and the compliance checklist status for each.

---

## Current Integration Status Matrix

| Repository | Role | FIPS Crypto | NIST 800-53 | Zero-Trust | Audit Trail | Semantic Ontology | Status |
|-----------|------|:-----------:|:-----------:|:----------:|:-----------:|:-----------------:|--------|
| SocioProphet/sociosphere | Workspace controller | ✅ | 📋 | 📋 | 📋 | ✅ | 🔄 In Progress |
| SocioProphet/socioprophet-standards-storage | Standards authority | ✅ | ✅ | ✅ | ✅ | 📋 | ✅ Integrated |
| SocioProphet/socioprophet-standards-knowledge | Knowledge semantics | 📋 | 📋 | 📋 | 📋 | 📋 | 📋 Planned |

Legend: ✅ Integrated · 📋 Planned · 🔄 In Progress · ❌ Not Started

---

## Integration Checklist Per Repository

### SocioProphet/socioprophet-standards-storage (Standards Authority)

This repository — the compliance standards authority.

- [x] FIPS cryptographic algorithm policy defined ([standards/fips-compliance/INDEX.md](fips-compliance/INDEX.md))
- [x] NIST 800-53 control mapping matrix ([standards/nist-800-53/CONTROL-MAPPINGS.md](nist-800-53/CONTROL-MAPPINGS.md))
- [x] Zero-trust architecture specification ([standards/nist-800-207/ZERO-TRUST-ARCHITECTURE.md](nist-800-207/ZERO-TRUST-ARCHITECTURE.md))
- [x] Immutable audit trail requirements ([standards/audit-forensics/NIST-800-88.md](audit-forensics/NIST-800-88.md))
- [x] Cross-repository integration map (this document)
- [ ] Semantic ontology alignment with socioprophet-standards-knowledge
- [ ] JSON-LD context for FIPS/NIST concepts published in `schemas/jsonld/contexts/`

### SocioProphet/sociosphere (Workspace Controller)

Primary implementation repository.

- [x] FIPS cryptographic compliance — `docs/GLOSSARY-FIPS.md` (controlled vocabulary)
- [x] Semantic ontology — `ontologies/sociosphere-fips-schema.jsonld` (JSON-LD)
- [x] Semantic ontology — `ontologies/sociosphere-fips.ttl` (RDF/Turtle)
- [ ] NIST 800-53 control alignment — `ontologies/FIPS-COMPLIANCE-GUIDE.md`
- [ ] Zero-trust binding enforcement — `ontologies/zero-trust-govt-bindings.jsonld`
- [ ] Immutable audit trail support — `audit/` module with WORM + hash chain
- [ ] TriTRPC FIPS specification — `protocol/tritrpc-fips-spec.md`
- [ ] FIPS compliance checker (CI) — `tools/validator/fips-compliance-checker.py`
- [ ] Authentication module — `auth/oidc.py` (OIDC + PKCE + MFA)
- [ ] Policy engine — `policy/engine.py` (AC-3, AU-12 enforcement)
- [ ] Key management — `crypto/key_management.py` (HSM integration)

Cross-references from sociosphere to this repository:
- `docs/GLOSSARY-FIPS.md` → [standards/fips-compliance/INDEX.md](fips-compliance/INDEX.md)
- `ontologies/` → [standards/nist-800-53/CONTROL-MAPPINGS.md](nist-800-53/CONTROL-MAPPINGS.md) (AC-6, IA-2)
- (planned) `audit/` → [standards/audit-forensics/NIST-800-88.md](audit-forensics/NIST-800-88.md)
- (planned) `auth/oidc.py` → [standards/nist-800-53/CONTROL-MAPPINGS.md](nist-800-53/CONTROL-MAPPINGS.md) AC-2, IA-2
- (planned) `ontologies/zero-trust-govt-bindings.jsonld` → [standards/nist-800-207/ZERO-TRUST-ARCHITECTURE.md](nist-800-207/ZERO-TRUST-ARCHITECTURE.md)

### SocioProphet/socioprophet-standards-knowledge (Knowledge Semantics)

Semantic vocabulary and ontology authority.

- [ ] FIPS cryptographic compliance — shared vocabulary with standards-storage
- [ ] NIST 800-53 control alignment — ontology mapping to control families
- [ ] Zero-trust binding enforcement — semantic definitions for ZTA patterns
- [ ] Immutable audit trail support — audit event ontology
- [ ] Semantic ontology coherence — alignment with sociosphere JSON-LD + RDF
- [ ] Cross-links to standards-storage authority documents

---

## Governance Checkpoints

All integration work **MUST** pass the following checkpoints before a repository is considered
fully integrated.

### Checkpoint 1: Cryptographic Compliance

- [ ] Only FIPS-approved algorithms used in all security-sensitive code paths.
- [ ] Disallowed algorithms (MD5, SHA-1, DES, RC4) absent from codebase.
- [ ] FIPS compliance checker reports 0 violations in CI.

### Checkpoint 2: NIST 800-53 Control Alignment

- [ ] All applicable controls from the [CONTROL-MAPPINGS.md](nist-800-53/CONTROL-MAPPINGS.md) matrix addressed.
- [ ] Evidence locations populated for all ✅ Implemented controls.
- [ ] No control in ❌ Not Started state for critical control families (AC, AU, IA, SC).

### Checkpoint 3: Zero-Trust Enforcement

- [ ] No implicit trust granted on any API endpoint.
- [ ] All cross-domain calls authenticated via mTLS + scoped token.
- [ ] Micro-segmentation boundary rules documented and enforced.
- [ ] Anomaly detection baselines established.

### Checkpoint 4: Immutable Audit Trail

- [ ] All security events emitted via audit library with hash chaining.
- [ ] Audit storage WORM-configured; deletion operations blocked.
- [ ] Hash chain integrity verified in weekly scheduled job.
- [ ] RFC 3161 TSA tokens included on all audit records.

### Checkpoint 5: Semantic Ontology Coherence

- [ ] JSON-LD context published and resolvable.
- [ ] RDF/Turtle representation aligned with JSON-LD.
- [ ] Cross-links from ontology to standards documents accurate.
- [ ] Vocabulary aligned between sociosphere and standards-knowledge.

---

## Artifact Cross-References

The following table maps implementation artifacts in sociosphere to the defining
standards documents in socioprophet-standards-storage.

| sociosphere Artifact | Standard Defined In | Status |
|---------------------|-------------------|--------|
| `docs/GLOSSARY-FIPS.md` | [fips-compliance/INDEX.md](fips-compliance/INDEX.md) | ✅ |
| `ontologies/sociosphere-fips-schema.jsonld` | [nist-800-53/CONTROL-MAPPINGS.md](nist-800-53/CONTROL-MAPPINGS.md) AC-6, IA-2 | ✅ |
| `ontologies/sociosphere-fips.ttl` | [nist-800-53/CONTROL-MAPPINGS.md](nist-800-53/CONTROL-MAPPINGS.md) AC-6, IA-2 | ✅ |
| `ontologies/zero-trust-govt-bindings.jsonld` | [nist-800-207/ZERO-TRUST-ARCHITECTURE.md](nist-800-207/ZERO-TRUST-ARCHITECTURE.md) | 📋 |
| `protocol/tritrpc-fips-spec.md` | [fips-compliance/INDEX.md](fips-compliance/INDEX.md) | 📋 |
| `tools/validator/fips-compliance-checker.py` | [fips-compliance/INDEX.md](fips-compliance/INDEX.md) | 📋 |
| `ontologies/FIPS-COMPLIANCE-GUIDE.md` | [nist-800-53/CONTROL-MAPPINGS.md](nist-800-53/CONTROL-MAPPINGS.md) | 📋 |
| `auth/oidc.py` | [nist-800-53/CONTROL-MAPPINGS.md](nist-800-53/CONTROL-MAPPINGS.md) AC-2, IA-2 | 📋 |
| `audit/logger.py` | [audit-forensics/NIST-800-88.md](audit-forensics/NIST-800-88.md) | 📋 |
| `crypto/key_management.py` | [nist-800-53/CONTROL-MAPPINGS.md](nist-800-53/CONTROL-MAPPINGS.md) SC-12 | 📋 |
| `policy/engine.py` | [nist-800-53/CONTROL-MAPPINGS.md](nist-800-53/CONTROL-MAPPINGS.md) AC-3 | 📋 |
| `transport/tls.py` | [nist-800-53/CONTROL-MAPPINGS.md](nist-800-53/CONTROL-MAPPINGS.md) SC-8 | 📋 |
| `pki/certificate_policy.py` | [nist-800-53/CONTROL-MAPPINGS.md](nist-800-53/CONTROL-MAPPINGS.md) SC-17 | 📋 |

---

## Next Phase Targets

### Phase 2 — Data Layer (Q3 2026)

| Repository | Technology | Integration Scope |
|-----------|-----------|-----------------|
| PostgreSQL operator | Relational DB | FIPS TLS, encryption at rest, audit hooks |
| MongoDB operator | Document DB | FIPS TLS, encryption at rest, audit hooks |
| Elasticsearch operator | Search / analytics | FIPS TLS, index encryption, audit log shipping |
| Redis operator | Cache / pub-sub | FIPS TLS, AUTH, no plaintext |
| MinIO operator | Object storage | FIPS TLS, SSE-S3 (AES-256-GCM), WORM for audit logs |

### Phase 3 — Orchestration Layer (Q3–Q4 2026)

| Repository | Technology | Integration Scope |
|-----------|-----------|-----------------|
| KinD cluster configs | Kubernetes in Docker | FIPS node images, admission webhooks |
| minikube profiles | Local Kubernetes | FIPS mode enabled, OIDC API server |
| kubefed configuration | Kubernetes Federation | Cross-cluster zero-trust policies |
| Helm chart library | Helm packaging | FIPS defaults, security context defaults |

### Phase 4 — P2P and Distributed Systems (Q4 2026)

| Repository | Technology | Integration Scope |
|-----------|-----------|-----------------|
| Hypercore integration | Append-only log | Hash chain alignment with audit trail |
| Hyperdrive integration | Distributed FS | Encryption at rest, access control |
| Dat ecosystem connectors | P2P data layer | Identity binding, integrity verification |

### Phase 5 — Knowledge Graph and ML (2027)

| Repository | Technology | Integration Scope |
|-----------|-----------|-----------------|
| Egeria connector | Metadata catalog | FIPS TLS, audit trail integration |
| KBPedia adapter | Knowledge base | Ontology alignment with standards-knowledge |
| Kubeflow integration | ML pipelines | SBOM generation, model signing |
| TensorFlow operators | ML framework | Artifact integrity, supply-chain security |

---

## Integration Timeline

```
Q2 2026 (Apr–Jun):  ■■■■■■■■░░  Core governance (this PR)
Q3 2026 (Jul–Sep):  ░░░░░░░░░░  Data layer + sociosphere control implementation
Q4 2026 (Oct–Dec):  ░░░░░░░░░░  Orchestration + external audit
2027 Q1-Q2:         ░░░░░░░░░░  P2P systems + knowledge graph + ML
```

---

## Governance

### Bi-Weekly Coherence Review

Every two weeks, the following must be assessed:
- New artifacts created since last review — are they cross-linked?
- Any ✅ statuses need to move to 📋 due to refactoring?
- Any new repositories integrated that need to be added to this map?
- Compliance checker findings from CI — any new violations?

### Quarterly Attestation

Each quarter, the [ZERO-TRUST-ARCHITECTURE.md](nist-800-207/ZERO-TRUST-ARCHITECTURE.md) attestation
checklist **MUST** be completed and recorded in the audit trail.

### Change Management

Changes to this document **MUST**:
1. Be reviewed by at least one standards authority member.
2. Include an updated `Last Updated` date.
3. Reference the PR or issue that prompted the change.
4. Not remove existing ✅ entries without a documented architectural rationale.
