# Neo4j Operational Serving Layer — Provisional IFC Certification Note

## Target
Neo4j used as the operational serving layer in a reified-LPG posture.

## Intended role in stack
- Operational serving layer
- Graph application query surface
- Traversal and exploration layer

Neo4j is **not** treated here as the canonical truth layer.

## Certification basis
This note is evaluated against:
- IFC standard posture
- backend capability profile expectations
- projection downgrade fixture
- contradiction visibility fixture
- obligation propagation fixture

## Declared projection posture
- Preferred projection kind: `star_expansion`
- Recoverability posture: acceptable when relation instances and incidence payload are explicitly preserved
- Review required for dyadic projections and embedding-only exports

## Current status
**Status:** provisional

## Expected pass/review posture
### Expected to pass
- operational serving over reified relation nodes
- graph application queries over serving view
- retrieval and exploration tasks where no stronger governance claim is made

### Expected to require review
- any downgrade from reified/star-expansion serving to dyadic projection
- policy reasoning over projected views
- provenance audit over projected views without supporting ledger references
- exports that weaken propagated obligations

### Expected to fail if attempted without additional controls
- claiming canonical truth equivalence to the relational IFC ledger
- claiming native lossless higher-order semantics without explicit reification
- flattening contradiction-aware reads into a single truth answer by default

## Conditions for full certification
Neo4j serving can only move from provisional to certified when:
1. the concrete adapter preserves relation-instance and incidence payload explicitly,
2. fixture runs are attached for projection downgrade, contradiction visibility, and obligation propagation,
3. the serving adapter references the canonical relational ledger for truth/audit authority,
4. loss certificates are present for all downgraded exports.

## Decision
Neo4j is the leading candidate for initial **operational serving certification**, not for canonical truth certification.
