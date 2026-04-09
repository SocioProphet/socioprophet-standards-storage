# Relational IFC Ledger Canonical Truth Layer — Provisional IFC Certification Note

## Target
Relational IFC Ledger used as the canonical truth and replay layer.

## Intended role in stack
- Canonical truth layer
- Audit and replay layer
- Identity, lifecycle, contradiction, and governance anchor

The relational IFC ledger is **not** treated here as an operational serving layer and **not** as an embedding-oriented analysis surface.

## Certification basis
This note is evaluated against:
- IFC standard posture
- backend capability profile expectations
- projection downgrade fixture
- contradiction visibility fixture
- obligation propagation fixture

## Declared projection posture
- Preferred projection kind: `incidence_preserving`
- Recoverability posture: intended to be the canonical loss-minimizing truth layer
- Review required for any export or adapter path that weakens contradiction visibility, obligation propagation, or identity/lifecycle semantics

## Current status
**Status:** provisional

## Expected pass/review posture
### Expected to pass
- canonical truth storage
- replay and audit
- identity and lifecycle tracking
- governance control anchoring
- contradiction-aware canonical query posture

### Expected to require review
- any downgrade export to dyadic or embedding-oriented views
- any obligation weakening during derivation or publication
- identity merge or split decisions
- contradiction visibility changes

### Expected to fail if attempted without additional controls
- unlogged identity reconciliation
- canonical storage that bypasses lifecycle or contradiction tracking
- exports that claim losslessness without explicit certification

## Conditions for full certification
The relational ledger can only move from provisional to certified when:
1. fixture evidence is attached for projection downgrade, contradiction visibility, and obligation propagation,
2. canonical relation-instance and incidence tracking are implemented and evidenced,
3. identity and lifecycle transitions are recorded under governed control,
4. all downgraded exports carry explicit loss posture and review state.

## Decision
The relational IFC ledger is the leading candidate for initial **canonical truth certification** and remains the anchor surface against which serving and publication layers should be evaluated.
