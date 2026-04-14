# GraphDB Semantic Publication Layer — Provisional IFC Certification Note

## Target
GraphDB used as the semantic publication and governance-facing statement layer.

## Intended role in stack
- Semantic publication layer
- Statement metadata layer
- Governance-facing interoperability surface

GraphDB is **not** treated here as the canonical truth layer and **not** as the operational serving layer.

## Certification basis
This note is evaluated against:
- IFC standard posture
- backend capability profile expectations
- contradiction visibility fixture
- obligation propagation fixture

## Declared projection posture
- Preferred projection kind: `semantic_statement`
- Recoverability posture: acceptable for publication and governance-facing statement views when higher-order semantics are explicitly mapped and bounded
- Review required for any weakening of contradiction visibility or obligation propagation

## Current status
**Status:** provisional

## Expected pass/review posture
### Expected to pass
- semantic publication of governed claims and derivations
- statement-level metadata publication
- governance-facing interoperability and review

### Expected to require review
- projection of role-rich incidence data into statement-shaped exports
- contradiction visibility changes that hide competing validated claims
- publication flows that weaken propagated obligations

### Expected to fail if attempted without additional controls
- claiming native incidence-first canonical storage equivalence
- treating publication views as complete operational truth surfaces
- suppressing contradiction-aware visibility by default

## Conditions for full certification
GraphDB publication can only move from provisional to certified when:
1. contradiction-aware query posture is demonstrated with fixture evidence,
2. obligation propagation to derived publication artifacts is demonstrated,
3. the publication adapter is anchored to the canonical relational ledger for truth authority,
4. any higher-order-to-statement reduction is covered by explicit loss posture and review.

## Decision
GraphDB is the leading candidate for initial **semantic publication certification**, not for canonical truth certification.
