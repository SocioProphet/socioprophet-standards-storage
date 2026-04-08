# Semantic Layer Architecture

## Purpose

This document is the normative master reference for the SocioProphet semantic layer: the collection of machine-readable knowledge representations that enable automated compliance reasoning, evidence generation, and governance across all platform systems.

The semantic layer provides a shared, vendor-neutral vocabulary and graph of FIPS compliance concepts. Tooling (Egeria, KBPedia, WebProtégé, Blazegraph) builds on top of these stable contracts — the contracts, not the tools, are the product.

---

## Ontology Structure

The FIPS compliance ontology is rooted at `FIPSCompliance` and branches into six major concept groups.

```
FIPSCompliance (root)
├── CryptographicStandard
│   ├── AES-256-GCM
│   ├── ECDSA-P256
│   ├── ECDSA-P384
│   ├── HKDF-SHA256
│   └── ... (see COMPLIANCE-KNOWLEDGE-GRAPH.md for full taxonomy)
├── SecurityControl
│   ├── AccessControl (AC family)
│   ├── AuditAndAccountability (AU family)
│   ├── CryptographicAndKeyManagement (SC family)
│   └── ... (see COMPLIANCE-KNOWLEDGE-GRAPH.md for full taxonomy)
├── ZeroTrustPrinciple
│   ├── NeverImplicitTrust
│   ├── ContinuousVerification
│   ├── LeastPrivilege
│   └── AssumeBreach
├── AuditEvent
│   ├── AuthenticationEvent
│   ├── AuthorizationEvent
│   └── DataAccessEvent
├── System
│   ├── Database
│   ├── OrchestrationService
│   └── APIService
└── Implementation
    ├── CodeLocation
    └── ConfigurationEntry
```

---

## Relationships

The ontology defines the following normative relationships between concepts.

| Relationship | Domain | Range | Semantics |
|---|---|---|---|
| `system:implements` | `System` | `SecurityControl` | Which NIST 800-53 control does the system implement? |
| `control:requires` | `SecurityControl` | `CryptographicStandard` | Which cryptographic algorithm does the control mandate? |
| `system:uses` | `System` | `CryptographicStandard` | Which cryptographic algorithm does the system actually use? |
| `implementation:evidence` | `Implementation` | `SecurityControl` | This code location or configuration is evidence for the control. |
| `auditEvent:verifies` | `AuditEvent` | `SecurityControl` | This audit event proves the control is operating correctly. |

### Relationship Constraints

- A `System` MUST be linked to every `SecurityControl` it claims to implement via `system:implements`.
- A `SecurityControl` that `control:requires` a `CryptographicStandard` is not satisfied unless the `System` also satisfies `system:uses` the same algorithm (or an approved superset).
- An `Implementation` that supplies `implementation:evidence` for a control MUST reference a verifiable artifact (file path, configuration key, or audit log identifier).

---

## Properties

Every instance in the ontology carries the following normative properties.

### Compliance Status

| Property | Type | Allowed Values | Required |
|---|---|---|---|
| `complianceStatus` | enum | `implemented`, `planned`, `not-started` | MUST |
| `implementationDate` | ISO-8601 date | — | SHOULD (when status = `implemented`) |
| `lastVerifiedDate` | ISO-8601 date | — | SHOULD (when status = `implemented`) |
| `riskLevel` | enum | `critical`, `high`, `medium`, `low` | MUST |
| `evidenceLocation` | string (path or URI) | — | SHOULD (when status = `implemented`) |
| `owner` | string (team or individual identifier) | — | MUST |

### Metadata

| Property | Type | Notes |
|---|---|---|
| `createdAt` | ISO-8601 datetime | Set on first assertion |
| `updatedAt` | ISO-8601 datetime | Updated on every change |
| `version` | semver string | Ontology version that defined this instance |
| `sourceSystem` | string | Egeria, Blazegraph, CI pipeline, etc. |

---

## Reasoning Rules

The following normative inference rules govern automated compliance assessment. Implementations using Blazegraph or any OWL/SWRL-capable reasoner MUST encode these rules.

### Rule 1 — System Compliance

```
IF  system S implements every SecurityControl C
    AND for each C, no required CryptographicStandard is missing
    AND each C has at least one Implementation with evidence
THEN  S is compliant
```

### Rule 2 — Algorithm Mismatch

```
IF  control C requires CryptographicStandard A
    AND system S implements C
    AND system S uses CryptographicStandard B
    AND B ≠ A  (and B is not an approved superset of A)
THEN  control C is NOT satisfied for system S
```

### Rule 3 — Stale Audit Signal

```
IF  control C is implemented by system S
    AND no AuditEvent with auditEvent:verifies C exists
        within the last 30 calendar days
THEN  raise alert: possible control failure for C on S
```

### Rule 4 — Missing Evidence

```
IF  system S asserts system:implements C
    AND no Implementation with implementation:evidence C exists
THEN  raise alert: evidence required for C on S
```

---

## Integration Points

| System | Role |
|---|---|
| **Egeria** | Authoritative metadata store; asset classification; governance workflows; audit trail (see EGERIA-COMPLIANCE.md) |
| **KBPedia** | Knowledge ontology; taxonomy management; semantic search and reasoning (see COMPLIANCE-KNOWLEDGE-GRAPH.md) |
| **WebProtégé** | Visual ontology editing; collaborative development; version control and approval workflows |
| **Blazegraph** | RDF triple store; SPARQL query engine; full-text search; inference and reasoning |
| **GLOSSARY-FIPS** | Controlled vocabulary; NIST-aligned term definitions; synonyms/narrower/broader relations; audit trail of term changes |

---

## Normative References

- NIST SP 800-53 Rev 5 — Security and Privacy Controls for Information Systems
- FIPS 140-2 / FIPS 140-3 — Security Requirements for Cryptographic Modules
- NIST SP 800-207 — Zero Trust Architecture
- W3C OWL 2 — Web Ontology Language
- W3C SPARQL 1.1 — Query Language for RDF
- W3C PROV-O — Provenance Ontology
- docs/standards/050-security-oidc-policy.md — Platform security standard
- docs/standards/070-graph-rdf-hypergraph.md — Graph store abstraction standard
