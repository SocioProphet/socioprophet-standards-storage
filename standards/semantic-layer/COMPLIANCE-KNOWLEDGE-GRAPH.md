# FIPS Compliance Knowledge Graph

## Purpose

This document specifies the semantic knowledge graph for FIPS compliance in the SocioProphet platform. It defines the taxonomies, instance data, and SPARQL query patterns used with KBPedia, Blazegraph, and WebProtégé to enable automated reasoning, compliance discovery, and evidence generation.

---

## FIPS Control Taxonomy

The `SecurityControl` hierarchy follows NIST SP 800-53 Rev 5 control families. Only the controls most relevant to FIPS 140-2/140-3 cryptographic and data-protection requirements are listed here as normative entries; additional controls MUST be added via the WebProtégé ontology workflow.

```
SecurityControl
├── AccessControl (AC)
│   ├── AC-2: Account Management
│   ├── AC-3: Access Enforcement
│   ├── AC-6: Least Privilege
│   ├── AC-17: Remote Access
│   └── AC-18: Wireless Access
├── AuditAndAccountability (AU)
│   ├── AU-2: Event Logging
│   ├── AU-3: Content of Audit Records
│   ├── AU-9: Protection of Audit Information
│   ├── AU-11: Audit Record Retention
│   └── AU-12: Audit Record Generation
├── CryptographicAndKeyManagement (SC)
│   ├── SC-8: Transmission Confidentiality and Integrity
│   ├── SC-12: Cryptographic Key Establishment and Management
│   ├── SC-13: Cryptographic Protection
│   ├── SC-17: Public Key Infrastructure Certificates
│   ├── SC-28: Protection of Information at Rest
│   └── SC-39: Process Isolation
├── IdentificationAndAuthentication (IA)
│   ├── IA-2: Identification and Authentication (Organizational Users)
│   ├── IA-3: Device Identification and Authentication
│   ├── IA-5: Authenticator Management
│   └── IA-8: Identification and Authentication (Non-Organizational Users)
└── ConfigurationManagement (CM)
    ├── CM-2: Baseline Configuration
    ├── CM-6: Configuration Settings
    └── CM-7: Least Functionality
```

### Control Instance Properties

Every control instance in the knowledge graph MUST carry:

| Property | Type | Description |
|---|---|---|
| `controlId` | string | NIST identifier (e.g., `AC-2`) |
| `controlFamily` | string | Short family code (e.g., `AC`) |
| `controlName` | string | Human-readable name |
| `fipsRelevance` | enum | `required`, `recommended`, `not-applicable` for FIPS 140-3 context |
| `requiresCryptography` | boolean | True if the control mandates a specific algorithm |
| `requiredAlgorithms` | list of IRI | Links to `CryptographicAlgorithm` instances when `requiresCryptography = true` |

---

## Cryptographic Algorithm Taxonomy

```
CryptographicAlgorithm
├── ApprovedFIPS140 (MUST use; any other algorithm is non-compliant)
│   ├── SymmetricEncryption
│   │   └── AES-256-GCM         (primary approved cipher)
│   ├── AsymmetricEncryption
│   │   ├── ECDSA-P256
│   │   └── ECDSA-P384
│   ├── KeyDerivation
│   │   ├── HKDF-SHA256
│   │   └── PBKDF2-SHA256       (for password-based keys only)
│   ├── HashFunctions
│   │   ├── SHA-256
│   │   ├── SHA-384
│   │   └── SHA-512
│   ├── MessageAuthenticationCode
│   │   └── HMAC-SHA256
│   └── KeyAgreement
│       ├── ECDH-P256
│       └── ECDH-P384
└── DisallowedOrDeprecated (MUST NOT use; presence triggers a compliance violation)
    ├── HashFunctions
    │   ├── MD5
    │   └── SHA-1
    ├── SymmetricEncryption
    │   ├── DES
    │   ├── 3DES
    │   ├── RC4
    │   └── Blowfish
    ├── AsymmetricEncryption
    │   └── RSA-1024             (key size below NIST minimum)
    └── KeyDerivation
        └── MD5-crypt
```

### Algorithm Instance Properties

| Property | Type | Description |
|---|---|---|
| `algorithmId` | string | Short identifier (e.g., `AES-256-GCM`) |
| `fipsStatus` | enum | `approved`, `disallowed`, `deprecated` |
| `fipsDocument` | string | Governing FIPS publication (e.g., `FIPS 197`, `FIPS 186-5`) |
| `keyLengthBits` | integer | Minimum key length in bits (when applicable) |
| `deprecationDate` | ISO-8601 date | Date deprecated or disallowed (when applicable) |
| `replacedBy` | IRI | Link to the approved replacement algorithm |

---

## Zero-Trust Principles Taxonomy

```
ZeroTrustPrinciple
├── NeverImplicitTrust
│   ├── DefaultDenyNetworkPolicy
│   └── ExplicitAuthorizationRequired
├── ContinuousVerification
│   ├── PeriodicReAuthentication
│   └── ContinuousSessionMonitoring
├── LeastPrivilege
│   ├── MinimalPermissionGrants
│   ├── JustInTimeAccess
│   └── ScopeRestrictedTokens
└── AssumeBreach
    ├── BlastRadiusContainment
    ├── LateralMovementPrevention
    └── EncryptionAtRestAndInTransit
```

### Zero-Trust Mapping to NIST Controls

| Principle | Primary Controls | Enforcement Mechanism |
|---|---|---|
| `NeverImplicitTrust` | AC-3, AC-17 | Default-deny network policy; mTLS between services |
| `ContinuousVerification` | IA-2, IA-5, AU-2 | Short-lived tokens; continuous session audit |
| `LeastPrivilege` | AC-6, AC-2 | Role-scoped credentials; JIT access workflows |
| `AssumeBreach` | SC-8, SC-28, AU-9 | Full encryption at rest and in transit; isolated audit log store |

---

## Semantic Query Examples (SPARQL)

The following SPARQL 1.1 queries MUST be executable against the Blazegraph instance storing the compliance graph. Prefix `fips:` refers to the platform FIPS ontology namespace.

### Find All Systems Implementing AC-2

```sparql
PREFIX fips: <https://socioprophet.io/ontology/fips#>

SELECT ?system ?controlStatus
WHERE {
  ?system a fips:System ;
          fips:implements ?control .
  ?control fips:controlId "AC-2" ;
           fips:complianceStatus ?controlStatus .
}
ORDER BY ?system
```

### Find Systems Using Disallowed Algorithms

```sparql
PREFIX fips: <https://socioprophet.io/ontology/fips#>

SELECT ?system ?algorithm
WHERE {
  ?system a fips:System ;
          fips:uses ?algo .
  ?algo a fips:DisallowedOrDeprecated ;
        fips:algorithmId ?algorithm .
}
ORDER BY ?system
```

### Find Controls Without Recent Audit Events (Stale)

```sparql
PREFIX fips: <https://socioprophet.io/ontology/fips#>
PREFIX xsd:  <http://www.w3.org/2001/XMLSchema#>

SELECT ?system ?control
WHERE {
  ?system fips:implements ?control .
  FILTER NOT EXISTS {
    ?event a fips:AuditEvent ;
           fips:verifies ?control ;
           fips:timestamp ?ts .
  FILTER ( ?ts > NOW() - "P30D"^^xsd:duration )
  }
}
ORDER BY ?system ?control
```

### Find Controls Missing Evidence

```sparql
PREFIX fips: <https://socioprophet.io/ontology/fips#>

SELECT ?system ?control
WHERE {
  ?system fips:implements ?control .
  FILTER NOT EXISTS {
    ?impl a fips:Implementation ;
          fips:evidence ?control .
  }
}
ORDER BY ?system ?control
```

### Find All Systems Classified FIPS-Compliant

```sparql
PREFIX fips: <https://socioprophet.io/ontology/fips#>

SELECT ?system ?owner ?lastVerified
WHERE {
  ?system a fips:System ;
          fips:complianceStatus "implemented" ;
          fips:owner ?owner ;
          fips:lastVerifiedDate ?lastVerified .
}
ORDER BY DESC(?lastVerified)
```

### Verify All Required Cryptographic Controls Are Met

```sparql
PREFIX fips: <https://socioprophet.io/ontology/fips#>

SELECT ?system ?control ?requiredAlgo ?usedAlgo
WHERE {
  ?system fips:implements ?control .
  ?control fips:requiresCryptography true ;
           fips:requiredAlgorithms ?requiredAlgo .
  OPTIONAL {
    ?system fips:uses ?usedAlgo .
  }
  FILTER ( !BOUND(?usedAlgo) || ?usedAlgo != ?requiredAlgo )
}
```

---

## Ontology Management (WebProtégé)

All changes to the FIPS compliance ontology MUST follow the WebProtégé governance workflow.

### Change Workflow

1. **Propose**: contributor opens a change proposal in WebProtégé with rationale and reference to the governing NIST/FIPS publication.
2. **Review**: at least one security subject-matter expert and one data architect review the proposal.
3. **Approve**: both reviewers must approve; no change is merged with an open objection.
4. **Merge**: the approved change is merged to the `main` ontology version and tagged with a semver bump.
5. **Publish**: the updated ontology is loaded into Blazegraph and the Egeria type registry is updated.

### Versioning

- Ontology versions MUST follow semantic versioning (`MAJOR.MINOR.PATCH`).
- Adding a new class or property is a `MINOR` bump.
- Removing or renaming a class or property is a `MAJOR` bump (breaking change; requires migration plan).
- Correcting a label or adding a comment is a `PATCH` bump.

---

## GLOSSARY-FIPS Integration

The FIPS compliance knowledge graph MUST be anchored to the GLOSSARY-FIPS controlled vocabulary.

### Vocabulary Requirements

- Every ontology class and property MUST have a corresponding GLOSSARY-FIPS term definition.
- Term definitions MUST be NIST-aligned (referenced to a specific NIST SP, FIPS publication, or CNSS instruction).
- Synonyms, narrower terms, and broader terms MUST be recorded in GLOSSARY-FIPS using SKOS relations (`skos:altLabel`, `skos:narrower`, `skos:broader`).
- Every change to a term definition MUST be recorded in the GLOSSARY-FIPS audit trail (who changed what, when, and why).

### SKOS Mappings

```turtle
@prefix skos:  <http://www.w3.org/2004/02/skos/core#> .
@prefix fips:  <https://socioprophet.io/ontology/fips#> .
@prefix nist:  <https://csrc.nist.gov/glossary/term/> .

fips:AES-256-GCM
    a skos:Concept ;
    skos:prefLabel "AES-256-GCM"@en ;
    skos:altLabel "Advanced Encryption Standard 256-bit GCM"@en ;
    skos:broader fips:SymmetricEncryption ;
    skos:exactMatch nist:aes .

fips:SecurityControl
    a skos:Concept ;
    skos:prefLabel "Security Control"@en ;
    skos:definition "A safeguard or countermeasure prescribed for an information system to protect the confidentiality, integrity, and availability of the system and its information."@en ;
    skos:exactMatch nist:security_control .
```

---

## Normative References

- NIST SP 800-53 Rev 5 — Security and Privacy Controls for Information Systems and Organizations
- FIPS 140-2 / FIPS 140-3 — Security Requirements for Cryptographic Modules
- FIPS 197 — Advanced Encryption Standard (AES)
- FIPS 186-5 — Digital Signature Standard (DSS)
- NIST SP 800-207 — Zero Trust Architecture
- W3C SPARQL 1.1 — https://www.w3.org/TR/sparql11-query/
- W3C SKOS — https://www.w3.org/TR/skos-reference/
- standards/semantic-layer/ARCHITECTURE.md — Ontology structure and reasoning rules
- standards/semantic-layer/EGERIA-COMPLIANCE.md — Egeria governance specification
- docs/standards/070-graph-rdf-hypergraph.md — Graph store abstraction standard
