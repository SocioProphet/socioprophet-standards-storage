# Semantic Retrieval and Structural Mapping v1

This document uses RFC 2119 language: **MUST**, **SHOULD**, **MAY**.

## 1. Purpose
Define the normative standard for fast candidate retrieval and evidence-based structural mapping across heterogeneous platform data artifacts.

This standard exists to prevent the platform from depending on surface names alone. Different artifacts MAY encode the same underlying structure. Similar labels do not prove structural equivalence, and weak lexical overlap does not rule it out.

## 2. Scope
This v1 standard covers **tabular artifacts** as the pilot object class.

Covered artifacts:
- tables
- views
- materialized views
- CSV / Parquet / Iceberg / Delta datasets represented as tabular assets

Deferred to later versions:
- event schemas
- APIs
- documents
- graph substructures
- multimodal artifacts

## 3. Core doctrine
- Retrieval MUST be separated from verification.
- Retrieval MUST optimize recall and bounded cost.
- Verification MUST optimize structural correctness and explainability.
- Mappings MUST be stored as first-class reusable objects.
- Confidence MUST be explicit, versioned, and reviewable.
- Evidence from names alone MUST NOT be treated as sufficient for canonicalization.

## 4. Required pipeline stages
Every compliant implementation MUST implement the following stages:

1. **Profile extraction**
   - Extract lexical, value-profile, structural, and usage / lineage views for each tabular artifact.
2. **Compact retrieval encoding**
   - Encode each view into a compact retrieval representation suitable for approximate nearest-neighbor or Hamming-neighborhood search.
3. **Candidate generation**
   - Retrieve candidate peers, candidate families, candidate joins, and candidate unions.
4. **Structural verification**
   - Score candidates with a verifier that uses cross-view evidence and hard incompatibility checks.
5. **Decision recording**
   - Persist match proposals, accepted mappings, rejected mappings, and confidence explanations as first-class records.
6. **Transfer application**
   - Apply approved canonical schema mappings, quality rules, governance tags, and transformation hints.

## 5. Required views
Each tabular artifact MUST expose the following views.

### 5.1 Lexical view
The lexical view MUST include:
- artifact name
- column names
- normalized token set
- optional descriptions / docs
- optional alias dictionary

### 5.2 Value-profile view
The value-profile view MUST include, per column when applicable:
- inferred primitive type
- null ratio
- uniqueness ratio
- cardinality estimate
- representative regex / pattern family
- length statistics for text
- numeric range statistics for numeric fields
- temporal granularity where applicable
- domain exemplars or sketches where privacy policy permits

### 5.3 Structural view
The structural view MUST include:
- candidate key columns
- composite key candidates
- foreign-key / inclusion-dependency candidates
- row grain hypothesis
- partitioning or clustering hints where present
- column co-dependency signals where measurable

### 5.4 Usage / lineage view
The usage / lineage view MUST include when available:
- upstream artifact references
- downstream artifact references
- join neighborhoods
- query or job access frequency buckets
- transformation lineage hints
- governance / policy attachment hints

Implementations MAY omit unavailable fields, but MUST record omission explicitly.

## 6. Retrieval encoding requirements
- Implementations MUST support multi-view retrieval.
- A single global hash or embedding for the entire artifact SHOULD NOT be the only retrieval representation.
- Retrieval codes MAY be binary semantic hashes, dense embeddings, or a hybrid.
- If binary semantic hashes are used, the implementation MUST support bounded-radius Hamming retrieval.
- If dense embeddings are used, the implementation MUST still preserve the four-view decomposition at scoring time.

## 7. Family profiles
The system MUST support family-level or archetype-level structural hubs.

Examples include:
- `customer_master`
- `order_header`
- `order_line_fact`
- `invoice_header`
- `gl_transaction`
- `sensor_measurement`
- `entity_dimension`
- `support_ticket`

Each family profile MUST define:
- expected slots
- optional slots
- key expectations
- grain expectation
- unit / domain expectations where relevant
- common join neighborhoods
- common quality rules

## 8. Verification requirements
The verifier MUST consume evidence from more than one view.

The verifier MUST evaluate at least:
- lexical compatibility
- value-profile compatibility
- structural compatibility
- lineage / usage compatibility when available
- hard incompatibilities

Hard incompatibilities MUST include, when applicable:
- impossible type clashes
- mutually incompatible grain
- incompatible key structure
- impossible unit or domain clashes
- severe coverage gaps against required family slots

A verifier MUST NOT accept a mapping solely because one column name or table name appears similar.

## 9. Decision object requirements
Every proposed or accepted mapping MUST be materialized as a versioned decision object containing:
- source artifact reference
- target family or artifact reference
- proposed field mappings
- confidence score
- explanation vector or reason list
- verifier version
- profile extraction version
- reviewer identity or automation identity
- accepted / rejected / superseded state
- timestamps

## 10. Transfer requirements
Once a mapping is accepted, the implementation SHOULD transfer:
- canonical field names
- canonical data types
- join recommendations
- deduplication and normalization hints
- data-quality expectations
- governance and policy tags
- lineage annotations

The transfer layer MUST keep inherited material distinguishable from observed source facts.

## 11. Explainability requirements
The platform MUST expose why a candidate was proposed.

Explanation output MUST identify the strongest positive and negative factors, such as:
- high domain overlap
- high uniqueness compatibility
- strong join-neighborhood similarity
- grain conflict
- null-rate mismatch
- weak slot coverage

## 12. Privacy and security constraints
- Retrieval and verification MUST honor access controls.
- Protected values SHOULD be summarized via sketches, histograms, or privacy-preserving statistics rather than raw exemplars where feasible.
- Sensitive columns MUST support redacted or policy-constrained profiling.

## 13. Minimum evaluation metrics
Any compliant implementation MUST report, at minimum:
- candidate generation recall@k
- verifier precision / recall / F1
- join suggestion precision@k
- union suggestion precision@k
- mean and p95 candidate generation latency
- mean and p95 verification latency
- explanation completeness rate
- accepted-mapping reuse rate over time

## 14. Recommended first implementation
The recommended first implementation is:
- pilot object class: tables
- retrieval: hybrid multi-view binary + dense retrieval
- verifier: constrained family-slot alignment plus hard incompatibility checks
- persistence: first-class mapping records with acceptance workflow

## 15. Related standards
- `000-platform-standards.md`
- `005-design-philosophy.md`
- `020-data-formats.md`
- `060-storage-decision-guidance.md`
- `070-graph-rdf-hypergraph.md`

## 16. Implementation evidence
Initial implementation targets are expected to land in:
- `SocioProphet/prophet-platform` for runtime services
- `SocioProphet/ontogenesis` for ontology / family definitions
- `SocioProphet/sociosphere` for orchestration and evidence routing

This standards repository is the normative authority for the doctrine, schemas, and benchmark contract.