# IFC Reference Stack — Provisional Certification Note

## Target
Canonical relational ledger + reified-LPG operational serving + semantic publication layer.

## Stack posture
- Canonical truth layer: relational IFC ledger
- Operational serving layer: reified-LPG adapter
- Semantic publication layer: statement-oriented semantic adapter

## Certification basis
This note is based on the current IFC standards and the following fixture families:
- projection downgrade
- contradiction visibility
- obligation propagation

## Current status
**Status:** provisional

This stack is considered provisionally certifiable because the required fixture categories now exist and the stack posture is aligned with the standards repo’s intended reference architecture.

## Conditions
The stack MUST NOT be treated as fully certified until:
1. executable results are attached for the fixture files,
2. backend capability profiles are present for each concrete backend in the stack,
3. loss certificates exist for all downgrades,
4. contradiction handling and obligation propagation are verified with actual adapter outputs.

## Current expected outcomes
- Projection downgrade: review-required when moving from incidence-preserving truth storage to dyadic projection.
- Contradiction visibility: competing validated claims MUST remain grouped or visible under contradiction-aware query modes.
- Obligation propagation: publication artifacts MUST retain governed obligations from source claim and derivation chains.

## Decision
The reference stack is suitable as the primary candidate for first end-to-end certification work.

## Next evidence required
- executable fixture runs
- backend-specific profile attachments
- adapter-specific certification notes
- review records for any downgraded projections
