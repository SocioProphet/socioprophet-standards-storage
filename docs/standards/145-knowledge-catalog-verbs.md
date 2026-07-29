# Knowledge Catalog Verbs and Promotion Gates

This document uses RFC 2119 language: **MUST**, **SHOULD**, **MAY**.

## 1. Purpose

This standard defines a portable contract for a **knowledge catalog as a control plane**, where the catalog enumerates not only assets but also the **verbs** (operations) that can be executed over knowledge objects.

The intent is to prevent the common failure mode where a catalog becomes a passive metadata UI while operational semantics, policy, and evidence drift into proprietary pipelines.

## 2. Scope

This standard covers:
- verb registration and versioning
- promotion gates for schema, mappings, and semantic decisions
- match + disambiguation recordkeeping
- data-quality (DQ) rules as first-class governed objects
- class-aware access control
- required evidence and audit bindings for all action-bearing operations

It does not define a full ontology; it defines the governance and interface substrate that makes ontologies and catalogs operational and auditable.

## 3. Terms

### 3.1 Knowledge object
A **knowledge object** is any cataloged entity that can be referenced, governed, and acted upon, including:
- assets (documents, datasets, model artifacts)
- schema objects (classes, relations, taxonomies)
- mappings (source ↔ semantic)
- match candidates and resolution decisions
- policies and DQ rules

### 3.2 Catalog verb
A **catalog verb** is a typed, versioned capability that defines an allowed operation over one or more knowledge objects (for example: propose mapping, resolve entity, promote schema change).

### 3.3 Promotion gate
A **promotion gate** is the explicit transition rule from a non-authoritative state (draft, candidate, suggestion) into an authoritative state (published schema, accepted mapping, committed resolution).

## 4. Requirements

### 4.1 Verb-first catalog
- The catalog MUST treat verbs as first-class objects, not only assets.
- Each verb MUST have:
  - a stable identifier
  - a semantic description of intent
  - versioned input and output schema references
  - declared risk class
  - declared idempotency expectations
  - declared policy requirements
  - declared evidence outputs (receipt + audit bindings)

### 4.2 Typed interfaces and required headers
- All catalog verbs exposed over the network MUST comply with `030-service-interfaces-tritrpc.md`.
- Every verb invocation MUST carry standard metadata headers at minimum:
  - `trace_id`, `span_id`
  - `tenant_id`
  - `actor_id` or equivalent acting principal
  - `model_id` + `model_version` when model-influenced
  - `artifact_hash` references for any external payloads

### 4.3 Evidence by construction
- Every successful verb invocation MUST emit an operation receipt.
- Receipts MUST bind to:
  - stable input hashes
  - stable output hashes
  - the policy hash or policy snapshot consumed
  - referenced evidence objects (assets/chunks/claims)
- Receipts MUST follow the binding rules in `060-governance-artifacts-and-bindings.md`.

### 4.4 Draft → promoted lifecycle
- Knowledge objects that mutate the shared semantic model (schema, taxonomy, mapping, resolution decisions) MUST follow an explicit lifecycle:
  - `draft` → `candidate` → `reviewed` → `promoted` → `deprecated`
- A system MUST NOT promote a new authoritative semantic object without an explicit promotion gate decision recorded in an auditable form.

### 4.5 Schema evolution
- Schema objects (classes/relations/taxonomies) MUST be versioned.
- Schema changes MUST be represented as proposals prior to promotion.
- A promoted schema change MUST include migration impact notes or a declared compatibility posture.

### 4.6 Match and disambiguation record
- Entity/term resolution MUST preserve both lexical and semantic evidence.
- A resolution decision MUST record, at minimum:
  - candidate set identifiers
  - scores and/or ranking signals for string match and semantic match
  - disambiguation rationale
  - taxonomy/type constraints used
  - any human override that changed the outcome

### 4.7 Data-quality rules
- DQ rules MUST be first-class knowledge objects.
- DQ rules MUST be attachable to semantic classes/relations/fields, not only raw tables.
- DQ execution MUST emit results that are referenceable by receipts and audits.
- Bypassing a failing DQ rule MUST require an explicit policy decision.

### 4.8 Class-aware access control
- Access control MUST be meaning-aware (class-aware), not solely file/path-based.
- Access policy evaluation MUST comply with `050-security-oidc-policy.md`.
- Any access decision that gates a verb execution MUST be recorded (directly or by reference) in the operation receipt.

### 4.9 Governance and fact posture
- Systems MUST distinguish between:
  - claims (candidate statements)
  - facts (promoted/authoritative statements)
- Promotion of a claim into a fact MUST be represented as a promotion gate decision.
- Audits MUST be able to reconstruct:
  - who initiated the operation
  - which evidence was used
  - which policy snapshot governed it
  - which human overrides occurred

## 5. Interface families (non-exhaustive)

A compliant implementation SHOULD expose verb families analogous to:
- `catalog.verb.register`, `catalog.verb.list`, `catalog.verb.deprecate`
- `schema.change.propose`, `schema.change.approve`, `schema.change.apply`
- `mapping.propose`, `mapping.validate`, `mapping.promote`
- `match.candidates`, `match.resolve`, `match.rollback`
- `dq.rule.register`, `dq.evaluate`, `dq.enforce`
- `policy.evaluate` (for gate checks)

## 6. Failure modes this standard prevents

This standard exists to prevent:
- catalogs that cannot explain how a semantic decision was made
- schema drift without promotion decisions
- invisible human overrides that create undeclared authority
- policy decisions that cannot be linked to specific operations
- access control that cannot follow semantic meaning
- DQ checks that exist only as folklore or scattered scripts

## 7. Related standards

- `010-storage-contexts.md`
- `020-data-formats.md`
- `030-service-interfaces-tritrpc.md`
- `040-observability-otel.md`
- `050-security-oidc-policy.md`
- `060-governance-artifacts-and-bindings.md`
- `070-graph-rdf-hypergraph.md`
- `080-knowledge-context.md`

## 8. Implementation evidence

Implementations SHOULD add a "Complies with Standards" section that links back to this file and identifies:
- the verb registry implementation location
- the receipt/audit emission implementation location
- the policy engine integration location
- the schema/mapping promotion workflow implementation location
