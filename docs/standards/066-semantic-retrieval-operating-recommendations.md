# Semantic Retrieval Operating Recommendations v1

This document is an implementation companion to `065-semantic-retrieval-and-structural-mapping.md`.

It uses RFC 2119 language where a recommendation becomes a platform requirement.

## 1. Philosophy
The platform MUST treat data artifacts as evidence-bearing structures, not as filenames, table names, or text labels.

The central design principle is:

> use compact semantic routing to find candidates, then use structural verification to decide what the candidate means.

This revives three useful older ideas in a modern platform form:
- semantic hashing / compact retrieval for fast neighborhood search
- schema matching and model management for reusable mappings
- dataspace-style incremental integration where mappings improve over time

## 2. Anti-patterns
The platform MUST avoid the following anti-patterns:

1. **Embedding-only canonicalization**
   - A dense vector hit is a candidate, not a proof.
2. **Name-only mapping**
   - Similar field names are weak evidence unless type, value profile, grain, and usage agree.
3. **One global schema too early**
   - The platform SHOULD accumulate accepted mappings before imposing broad canonical schemas.
4. **Unstored human corrections**
   - Reviewer feedback MUST become durable mapping evidence.
5. **Unexplained automation**
   - Every proposed family, join, or union MUST expose reason codes.
6. **Raw-value leakage**
   - Sensitive datasets SHOULD use sketches, redaction, or policy-constrained profiling.

## 3. Recommended architecture
A compliant first implementation SHOULD use this architecture:

```text
Tabular artifact
  -> profile extractor
  -> four-view profile
      lexical
      value-profile
      structural
      usage / lineage
  -> multi-view compact retrieval index
  -> candidate families / joins / unions / similar artifacts
  -> structural verifier
  -> mapping decision object
  -> transfer layer
      canonical fields
      quality rules
      governance tags
      lineage annotations
```

## 4. First-class objects
The implementation SHOULD materialize at least these objects:

- `TableArtifactProfile`
- `FamilyProfile`
- `RetrievalCandidate`
- `MappingDecision`
- `TransferApplicationRecord`

Each object SHOULD be content-addressable or at least version-addressable.

## 5. Retrieval recommendations
Implementations SHOULD start with hybrid retrieval:

- lexical sparse or token-based retrieval for obvious matches
- binary compact hashes for bounded-radius multi-view retrieval
- dense vectors for semantic description and documentation retrieval
- optional MinHash / SimHash for near-duplicate and column-set similarity

The retrieval layer SHOULD prefer recall over precision. The verifier owns precision.

## 6. Verifier recommendations
The verifier SHOULD operate as a constrained alignment problem.

Recommended score components:

```text
score =
  lexical_score * w_lexical
+ value_profile_score * w_value
+ structural_score * w_structure
+ lineage_usage_score * w_lineage
+ family_slot_coverage * w_slots
- hard_incompatibility_penalty
```

Recommended hard penalties:
- incompatible grain
- incompatible key structure
- incompatible primitive type for required slots
- impossible unit or currency mismatch
- severe required-slot coverage failure

## 7. Human and automation review
Mappings MAY be accepted by automation only when:
- confidence exceeds the configured family threshold
- no hard incompatibilities are present
- explanation completeness is above threshold
- the source artifact policy allows automated transfer

All other cases SHOULD be routed for human or governed-agent review.

## 8. Feedback loop
Every accepted, rejected, or superseded mapping MUST feed future candidate ranking.

The platform SHOULD maintain:
- accepted mapping memory
- rejected mapping memory
- reviewer correction history
- family-profile drift history
- versioned verifier performance reports

## 9. Transfer recommendations
Transfer MUST preserve provenance boundaries.

Inherited facts SHOULD be tagged as inherited. Observed facts SHOULD be tagged as observed. Inferred facts SHOULD be tagged as inferred.

Recommended transfer outputs:
- canonical field aliases
- semantic family tag
- join hints
- union hints
- data-quality rules
- deduplication hints
- governance / sensitivity tags
- transformation recipes

## 10. Implementation order
The recommended implementation order is:

1. table profile schema
2. family profile schema
3. retrieval candidate schema
4. mapping decision schema
5. deterministic reference implementation
6. benchmark fixtures and metrics
7. runtime service in the platform
8. ontology-backed family library in the semantic layer
9. acceptance workflow and feedback loop

## 11. Cross-repo placement
- Standards and schemas: `SocioProphet/socioprophet-standards-storage`
- Runtime service and API surface: `SocioProphet/prophet-platform`
- Ontology-backed family library: `SocioProphet/ontogenesis`
- Workspace and evidence routing: `SocioProphet/sociosphere`
- Execution placement / replay: `SocioProphet/agentplane`

## 12. Acceptance criteria
The first production-quality version SHOULD pass these criteria:

- candidate generation recall@20 >= 0.95 on benchmark fixtures
- verifier precision@1 >= 0.90 on accepted benchmark families
- join suggestion precision@10 >= 0.85 on benchmark fixtures
- union suggestion precision@10 >= 0.85 on benchmark fixtures
- p95 retrieval latency reported for configured corpus size
- p95 verification latency reported for configured candidate set size
- every accepted mapping has reason codes and versioned evidence
- rejected mappings are stored and reduce repeated false positives
