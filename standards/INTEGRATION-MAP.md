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
# Integration Map — SocioProphet Ecosystem

- Last updated: 2026-01-27
- Status: Living document — updated with each cross-repository standards change
- Owner: SocioProphet Platform Security
- Review cadence: Quarterly

---

## Table of Contents

1. [Overview](#overview)
2. [Repository Status Matrix](#repository-status-matrix)
3. [Compliance Checkpoints Per Repository](#compliance-checkpoints-per-repository)
4. [Governance Procedures for Cross-Repository Standards](#governance-procedures-for-cross-repository-standards)
5. [Cross-Repository Artifact References](#cross-repository-artifact-references)
6. [Repository Categories](#repository-categories)
7. [Next Phase Targets](#next-phase-targets)
8. [Change Management Process](#change-management-process)

---

## Overview

This living document tracks the integration status of every repository in the SocioProphet ecosystem against the platform governance standards defined in this repository (socioprophet-standards-storage). It is the operational companion to [fips-compliance/INDEX.md](fips-compliance/INDEX.md).

A repository is **integrated** when:

1. It consumes the current pinned version of these standards.
2. Its CI/CD pipeline enforces the compliance checkpoints defined in this document.
3. It emits audit events that conform to the platform audit schema.
4. A human reviewer on the platform security team has verified the above.

A repository is **pending** when integration work has begun but is not yet complete. A repository is **planned** when it is identified for future integration but work has not started.

### How to Use This Document

- Repository owners: check your repository's compliance checkpoint status and address any gaps.
- Security reviewers: use the checkpoint table to structure compliance reviews.
- External auditors: use the status matrix and checkpoint tables as the starting point for scope definition.
- Platform team: update this document within 5 business days of any integration status change.

---

## Repository Status Matrix

### Application Repositories

| Repository | Role | Integration Status | Pinned Standards Version | Last Verified |
|---|---|---|---|---|
| sociosphere | Primary application; workspace orchestration | Integrated | `standards-storage@main` (pin Q2 2026) | 2026-01-27 |
| prophet-cli | CLI tooling; artifact signing | In Progress | Not yet pinned | — |
| socioprophet-web | Web portal; static mode initially | Planned | Not yet pinned | — |
| socioprophet-docs | Documentation site | Planned | Not yet pinned | — |

### Standards Repositories

| Repository | Role | Integration Status | Relationship |
|---|---|---|---|
| socioprophet-standards-storage (this repo) | Authoritative governance and policy | Authoritative | N/A |
| socioprophet-standards-knowledge | Knowledge engineering standards | Pending alignment | Inherits from standards-storage |

### Data Repositories / Infrastructure

| Component | Category | Integration Status | Notes |
|---|---|---|---|
| PostgreSQL | Relational (system of record) | In Progress | AES-256-GCM at-rest encryption; audit logging |
| MongoDB | Document store (optional) | Planned | Pending specialization trigger benchmark |
| Elasticsearch / OpenSearch | Full-text search | In Progress | TLS 1.3 enforced; audit trail for index changes |
| Redis | Cache / session store | In Progress | TLS 1.3 enforced; no sensitive data at rest in non-WORM tier |
| MinIO | Object store; WORM audit store | In Progress | Object Locking (Compliance mode) for audit bucket |
| RocksDB | Embedded key-value (embedded in services) | Planned | AES-256-GCM at-rest encryption required |

### Orchestration Infrastructure

| Component | Category | Integration Status | Notes |
|---|---|---|---|
| Kubernetes | Container orchestration | In Progress | NetworkPolicy default-deny; RBAC configured |
| kubefed | Federation control plane | Planned | Multi-cluster ZTA extension planned |
| KinD | Local development clusters | Planned | Development-only; compliance requirements reduced |
| minikube | Local development | Planned | Development-only; compliance requirements reduced |
| Istio | Service mesh | In Progress | mTLS enforcement; authorization policy |
| Linkerd | Service mesh (alternative) | Planned | Evaluated as Istio alternative |
| HashiCorp Vault | Secrets and key management | In Progress | AES-256-GCM; ECDSA-P256 transit keys; HSM integration Q3 2026 |

### P2P Infrastructure

| Component | Category | Integration Status | Notes |
|---|---|---|---|
| Hypercore | Append-only log (P2P) | Planned | Audit chain integration; crypto alignment |
| Hyperdrive | P2P file system | Planned | Encryption layer alignment with AES-256-GCM |
| Dat | P2P data sharing | Planned | Depends on Hypercore integration |
| multifeed | Multi-writer Hypercore | Planned | Depends on Hypercore integration |
| kappa-core | Kappa architecture over Hypercore | Planned | Depends on Hypercore + multifeed |

P2P components are isolated in the P2P zone (see [nist-800-207/ZERO-TRUST-ARCHITECTURE.md](nist-800-207/ZERO-TRUST-ARCHITECTURE.md)) and communicate with the application zone only through a dedicated authenticated proxy. The proxy enforces mTLS, validates SVID identities, and logs all inter-zone traffic to the audit pipeline.

### ML/AI Infrastructure

| Component | Category | Integration Status | Notes |
|---|---|---|---|
| Ray Core | Distributed Python runtime | Planned | Crypto alignment; audit integration |
| Ray Serve | Model serving | Planned | mTLS for serving endpoints; OIDC for API access |
| Ray Tune | Hyperparameter tuning | Planned | Isolated in ML zone; audit events for training runs |
| Ray Train | Distributed training | Planned | Isolated in ML zone; data access auditing |
| Ray Data | Distributed data processing | Planned | Data classification and access control integration |

Ray components are isolated in the ML/AI zone. Access from the application zone passes through the ML/AI proxy, which enforces authentication and logs all access. Training data access is audited per DATA_READ event requirements.

### Semantic / Knowledge Infrastructure

| Component | Category | Integration Status | Notes |
|---|---|---|---|
| Apache Egeria | Open metadata / governance | Planned | Governance metadata integration with standards-storage |
| KBPedia | Knowledge graph | Planned | Read-only access; no audit event modification |
| WebProtégé | Ontology editor | Planned | Edit events audited; OIDC authentication |
| Blazegraph | Triplestore | Planned | TLS 1.3 for SPARQL endpoint; audit for query logs |

---

## Compliance Checkpoints Per Repository

This section defines the compliance checkpoints that each repository must satisfy before receiving `Integrated` status. Checkpoints are evaluated by the platform security team as part of the integration review.

### Checkpoint Categories

| Category | Code | Description |
|---|---|---|
| Cryptographic | CRYPTO | Use of approved algorithms only; no disallowed algorithms |
| Transport | TRANS | All network communication over TLS 1.3 minimum |
| Identity | IDENT | OIDC or SPIFFE/SVID for all service and user identities |
| Audit | AUDIT | Audit event emission conforming to platform schema |
| Storage | STORE | Data at rest encrypted with AES-256-GCM |
| Signing | SIGN | Artifacts signed with ECDSA-P256 |
| Scanning | SCAN | CI/CD includes dependency, container, and SAST scanning |
| Policy | POLICY | Access control policies defined as code; reviewed |

### Application Repositories

#### sociosphere

| Checkpoint | Status | Evidence Location | Notes |
|---|---|---|---|
| CRYPTO | ✅ Implemented | `sociosphere/build/fips-build.yaml` | BoringCrypto in FIPS mode |
| TRANS | ✅ Implemented | `sociosphere/iac/network/tls-config.yaml` | TLS 1.3 enforced |
| IDENT | 🔄 In Progress | `sociosphere/iac/identity/` | OIDC done; SPIFFE in progress |
| AUDIT | ✅ Implemented | `sociosphere/tests/audit/coverage_test.go` | All required event types |
| STORE | ✅ Implemented | `sociosphere/iac/storage/encryption.yaml` | AES-256-GCM |
| SIGN | ✅ Implemented | `.github/workflows/sign-artifacts.yaml` | ECDSA-P256 via cosign |
| SCAN | ✅ Implemented | `.github/workflows/codeql.yaml` | CodeQL + Dependabot + Trivy |
| POLICY | 🔄 In Progress | `sociosphere/policy/access/` | OPA policies; ABAC in progress |

#### prophet-cli

| Checkpoint | Status | Evidence Location | Notes |
|---|---|---|---|
| CRYPTO | 🔄 In Progress | TBD | BoringCrypto integration planned |
| TRANS | 🔄 In Progress | TBD | TLS 1.3 enforced for API calls |
| IDENT | 📋 Planned | TBD | OIDC integration planned |
| AUDIT | 📋 Planned | TBD | Audit emission planned |
| STORE | ✅ N/A | — | CLI does not persist data at rest |
| SIGN | 🔄 In Progress | TBD | Artifact signing core feature |
| SCAN | 📋 Planned | TBD | Scanning setup planned |
| POLICY | ✅ N/A | — | CLI does not define access policy |

### Data Infrastructure

#### PostgreSQL

| Checkpoint | Status | Notes |
|---|---|---|
| CRYPTO | 🔄 In Progress | pgcrypto with AES-256 configured; GCM mode required |
| TRANS | ✅ Implemented | TLS 1.3 client connections enforced via `ssl_min_protocol_version` |
| IDENT | 🔄 In Progress | Certificate authentication for service accounts; LDAP for humans |
| AUDIT | 🔄 In Progress | pgaudit extension; event forwarding to audit pipeline |
| STORE | 🔄 In Progress | Tablespace encryption with AES-256-GCM |
| SIGN | ✅ N/A | Database engine; not an artifact |
| SCAN | 🔄 In Progress | Minor version patching automation |
| POLICY | 🔄 In Progress | Row-level security policies defined |

#### MinIO (Audit Store)

| Checkpoint | Status | Notes |
|---|---|---|
| CRYPTO | ✅ Implemented | SSE-S3 with AES-256-GCM; Vault KMS integration |
| TRANS | ✅ Implemented | TLS 1.3 enforced; plaintext disabled |
| IDENT | ✅ Implemented | IAM policies; service account access only for audit bucket |
| AUDIT | ✅ Implemented | MinIO audit log forwarded to secondary audit stream |
| STORE | ✅ Implemented | AES-256-GCM with per-bucket DEK |
| SIGN | ✅ N/A | Object store; not an artifact |
| SCAN | 🔄 In Progress | MinIO version update automation |
| POLICY | ✅ Implemented | Bucket policies: audit bucket write-only for pipeline accounts |

---

## Governance Procedures for Cross-Repository Standards

### Standards Version Pinning

Every consuming repository must pin to a specific commit SHA of this repository, not to a branch or tag that can be moved. Pinned references are stored in:

- `standards-pin.yaml` in the root of the consuming repository (defined format below)
- The consuming repository's CI/CD configuration, which validates the pin at build time

```yaml
# standards-pin.yaml format
standards:
  storage:
    repository: socioprophet/socioprophet-standards-storage
    commit: abc123def456...   # full SHA; not a tag or branch
    verified_by: security-team
    verified_at: 2026-01-27
    next_review: 2026-04-27
  knowledge:
    repository: socioprophet/socioprophet-standards-knowledge
    commit: null              # not yet pinned
```

### Update Process for Consuming Repositories

When the standards repository is updated:

1. The standards repository maintainer opens an update PR in each consuming repository, bumping the pinned commit SHA.
2. The PR includes a diff summary of what changed in the standards between the old and new commit.
3. The consuming repository's CI validates that all compliance checkpoints still pass against the new standards.
4. A platform security team member reviews and approves the update PR.
5. The update PR is merged. The consuming repository's integration status is updated in this document within 5 business days.

### Breaking Changes

A breaking change to the standards is one that requires consuming repositories to make code or configuration changes to remain compliant. Breaking changes are signaled by:

- A major version bump in the standards repository's `VERSION` file.
- A notice in the `CHANGELOG.md` flagging the breaking change.
- A migration guide added to `docs/migrations/`.
- Direct notification to all consuming repository owners.

Breaking changes are not applied on the same timeline as non-breaking updates. Consuming repositories are given a minimum 30-day migration window, with a maximum of one breaking change per quarter.

### Standards Review Gate

Before any PR is merged to this standards repository that changes a normative requirement, the following approvals are required:

1. Platform security owner (cryptographic and policy changes)
2. Platform architecture lead (infrastructure and integration changes)
3. At least one consuming repository owner (confirming they have reviewed the change impact)

---

## Cross-Repository Artifact References

This table tracks the specific versioned artifacts that flow between repositories.

### Standards Artifacts Consumed by sociosphere

| Artifact | Source | Version / Pin | Format | Validation |
|---|---|---|---|---|
| Audit event schema | standards-storage `schemas/audit/event-schema.yaml` | Pinned commit | YAML / JSON Schema | CI gate: schema conformance test |
| Approved algorithm list | standards-storage `standards/fips-compliance/INDEX.md` | Pinned commit | Markdown (normative) | CI gate: algorithm linter |
| OPA base policies | standards-storage `standards/nist-800-53/` | Pinned commit | Rego | CI gate: policy unit tests |
| SPIFFE trust domain config | standards-storage `standards/nist-800-207/` | Pinned commit | YAML | CI gate: SPIFFE conformance |

### Standards Artifacts Consumed by standards-knowledge

| Artifact | Source | Version / Pin | Format | Validation |
|---|---|---|---|---|
| Platform cryptographic requirements | standards-storage `standards/fips-compliance/INDEX.md` | Pinned commit | Markdown (normative) | Manual review at pin update |
| Control mapping template | standards-storage `standards/nist-800-53/CONTROL-MAPPINGS.md` | Pinned commit | Markdown | Manual review |

### Artifact Signing Cross-Reference

All artifacts produced by the CI/CD pipeline are signed with the platform artifact signing key and recorded in the transparency log. The transparency log entry cross-references:

- Source repository and commit SHA
- Build pipeline run ID
- Signer certificate SPIFFE ID
- SBOM CycloneDX document hash

This enables any relying party to trace any deployed artifact back to its source commit and verify its integrity.

---

## Repository Categories

### Application

Repositories that implement end-user or operator features. They are consumers of standards, not producers.

| Repository | Description | Primary Languages | Key Interfaces |
|---|---|---|---|
| sociosphere | Workspace orchestration; primary platform application | Go, TypeScript | gRPC (triRPC), REST, OIDC |
| prophet-cli | Command-line interface for operators and developers | Go | CLI, artifact signing, OIDC |
| socioprophet-web | Web portal; initially static reference viewer | TypeScript, React | REST, OIDC |

### Standards

Repositories that define governance requirements. They are producers of standards.

| Repository | Description | Authority Level |
|---|---|---|
| socioprophet-standards-storage (this repo) | Platform-wide governance, storage, and security standards | Authoritative |
| socioprophet-standards-knowledge | Knowledge engineering standards | Inherits from standards-storage |

### Data

Data stores and their integration requirements.

| Component | Technology | Data Sensitivity | Encryption Requirement |
|---|---|---|---|
| PostgreSQL | Relational | High (system of record) | AES-256-GCM at rest, TLS 1.3 in transit |
| MongoDB | Document | Medium (domain documents) | AES-256-GCM at rest, TLS 1.3 in transit |
| Elasticsearch / OpenSearch | Search index | Medium (derived) | TLS 1.3 in transit; at-rest per cloud provider |
| Redis | Cache | Low (ephemeral) | TLS 1.3 in transit; no sensitive data at rest |
| MinIO | Object store | Variable (artifact + audit) | AES-256-GCM with Vault KMS |
| RocksDB | Embedded KV | Medium (embedded in services) | AES-256-GCM via application-layer encryption |

### Orchestration

Infrastructure components that operate the platform.

| Component | Role | Security Notes |
|---|---|---|
| Kubernetes | Container orchestration | RBAC + NetworkPolicy + PodSecurity |
| kubefed | Federation | Cross-cluster identity and policy propagation |
| KinD | Dev/test clusters | Compliance requirements relaxed for development |
| minikube | Local development | Compliance requirements relaxed for development |
| Istio | Service mesh | mTLS enforcement; authorization policy; Envoy sidecar |
| Linkerd | Service mesh (alternative) | Evaluated; selected based on operational fit |
| HashiCorp Vault | Secrets + key management | HSM integration; AES-256-GCM; ECDSA-P256 transit |

### P2P

Peer-to-peer infrastructure for decentralized data sharing.

| Component | Protocol | Integration Notes |
|---|---|---|
| Hypercore | Append-only log | Hash-chain alignment with platform audit model |
| Hyperdrive | P2P file system | Encryption layer alignment; FIPS algorithm compliance |
| Dat | Data sharing | Depends on Hypercore + Hyperdrive |
| multifeed | Multi-writer Hypercore | Concurrent write model; coordination with audit sequencing |
| kappa-core | Kappa architecture | View materialization over P2P logs; access control model |

P2P components introduce specific security considerations due to their decentralized nature. Key requirements:
- All data stored in P2P components must be encrypted at the application layer using AES-256-GCM before entering the P2P network.
- The P2P network is treated as untrusted; no plaintext sensitive data.
- Access to P2P content from the application zone is mediated by the P2P proxy, which enforces authentication and audit logging.

### ML/AI

Machine learning and AI infrastructure.

| Component | Role | Integration Notes |
|---|---|---|
| Ray Core | Distributed runtime | Service account identity (SVID); task audit logging |
| Ray Serve | Model serving | mTLS endpoints; OIDC for inference API |
| Ray Tune | Hyperparameter tuning | Isolated in ML zone; training run audit |
| Ray Train | Distributed training | Training data access audited; model artifact signed |
| Ray Data | Data processing | Data classification enforcement; lineage audit |

### Semantic

Semantic web and knowledge graph infrastructure.

| Component | Role | Integration Notes |
|---|---|---|
| Apache Egeria | Open metadata governance | Platform governance metadata; cross-repo traceability |
| KBPedia | Reference knowledge graph | Read-only; no write audit required; cache invalidation |
| WebProtégé | Ontology editor | OIDC authentication; edit history audited |
| Blazegraph | SPARQL triplestore | TLS 1.3 endpoint; query log forwarded to audit pipeline |

---

## Next Phase Targets

### Q2 2026 Targets

| Target | Repository / Component | Success Criteria | Owner |
|---|---|---|---|
| sociosphere SPIFFE integration | sociosphere | All pods have SVID; mTLS enforced in mesh | Backend |
| prophet-cli OIDC integration | prophet-cli | Signing operations authenticated via OIDC | DevSecOps |
| MinIO WORM audit store | MinIO | Object Locking (Compliance) active; replication to secondary | Infrastructure |
| PostgreSQL audit forwarding | PostgreSQL | pgaudit events flowing to audit pipeline | Infrastructure |
| Standards pin automation | All repositories | Automated PRs opened when standards pin needs updating | Platform Security |
| Algorithm linter gate | sociosphere, prophet-cli | CI blocks merge on disallowed algorithm usage | DevSecOps |

### Q3 2026 Targets

| Target | Repository / Component | Success Criteria | Owner |
|---|---|---|---|
| HSM integration | HashiCorp Vault | Root CA and signing keys in HSM; software fallback removed | Infrastructure |
| Full service mesh | Istio | All production namespaces in mesh; mTLS enforced; authz policy active | Infrastructure |
| OPA policy engine | sociosphere | ABAC policies evaluated at mesh; all access decisions in audit | Backend |
| SIEM integration | Audit pipeline | SIEM rules active; alert thresholds configured; runbooks published | Security Operations |
| standards-knowledge alignment | standards-knowledge | standards-knowledge pinned to standards-storage; checkpoints pass | Security Lead |
| Ray Core zone isolation | Ray | ML zone isolated; P2P proxy for ML zone active | Infrastructure |

### Q4 2026 Targets

| Target | Repository / Component | Success Criteria | Owner |
|---|---|---|---|
| External FIPS 140-3 validation submission | Platform | Formal validation submitted to NIST CMVP | CISO |
| Penetration test | All production | External assessor with FIPS scope; findings remediated | CISO |
| Full 28-control evidence package | standards-storage | All evidence artifacts current, signed, and accessible | Platform Security |
| Cross-repo coherence audit | All repositories | Annual coherence audit complete; findings tracked | Platform Security |
| WebProtégé audit integration | WebProtégé | Edit events flowing to audit pipeline | Backend |
| Blazegraph TLS enforcement | Blazegraph | TLS 1.3 enforced; query log forwarded | Infrastructure |
| Egeria governance integration | Egeria | Platform governance metadata surfaced in Egeria catalog | Architecture |

---

## Change Management Process

### Types of Changes

| Change Type | Examples | Approval Requirements | Lead Time |
|---|---|---|---|
| Normative policy change | New algorithm requirement; revised retention period | Security owner + architecture lead + consuming repo owner | 30 days minimum notice |
| Additive documentation | New control mapping; new evidence pointer | Security owner | Same sprint |
| Status update | Integration status change; checkpoint update | Document owner (self-service) | Same day |
| Breaking change | Requirement that forces consuming repo code changes | Full review committee; 60-day notice | 60 days minimum |
| Emergency change | Active incident response; critical vulnerability | Security owner + on-call lead; document within 24 hours | Immediate |

### Change Request Process

1. **Open an issue** in this repository describing the proposed change, its rationale, and its impact on consuming repositories.
2. **Label the issue** with the appropriate change type (`normative-policy`, `additive`, `status-update`, `breaking`, `emergency`).
3. **Notify stakeholders:** @-mention the platform security owner, architecture lead, and owners of affected consuming repositories.
4. **Wait for the required notice period** before merging normative or breaking changes.
5. **Open a PR** with the change. Include: the change itself, an update to this INTEGRATION-MAP.md (if integration status is affected), and a CHANGELOG entry.
6. **Obtain required approvals** per the table above.
7. **Merge and propagate:** After merging, open update PRs in all consuming repositories to update their pinned commit SHA.

### Emergency Changes

In the event of an active security incident or critical vulnerability discovery that requires an immediate standards update:

1. The on-call security lead may apply the change immediately with a single approver.
2. The change must be documented in the incident tracking system with a reference to the standards commit.
3. A post-incident review must ratify the change within 5 business days and update this document.
4. Consuming repositories must update their pins within 24 hours of an emergency change.

### CHANGELOG

All normative changes are recorded in `CHANGELOG.md` at the repository root with:

- Date
- Change type
- Summary of what changed
- Impact on consuming repositories
- Migration instructions (for breaking changes)

The CHANGELOG is itself version-controlled and its history is part of the compliance evidence record.
