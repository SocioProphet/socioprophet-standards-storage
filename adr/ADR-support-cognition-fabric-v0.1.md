# ADR: Support Cognition Fabric v0.1

## Status
Proposed

## Context
We are defining the baseline object model and service contract for an evidence-first, zero-trust, graph-grounded support system. The baseline must support:
- typed case/session/turn state
- replayable Cairn checkpoints
- ranked route and assignment decisions
- claim-to-span evidence packets
- policy-gated execution and promotion
- benchmark-gated release discipline

## Decision
We adopt a canonical logical IDL for the support cognition fabric and derive downstream JSON Schema, CloudEvents mappings, and Protobuf service contracts from it.

We standardize the first-class entities:
- Case
- CaseSession
- Turn
- Cairn
- Asset
- AssetUse
- Recommendation
- RouteDecision
- AssignmentDecision
- EvidencePacket
- BenchmarkRun
- ConfidenceObject

We require these invariants:
1. no action without policy
2. no cross-tenant asset joins without explicit delegation
3. every claim backed or explicitly marked as a gap
4. every state transition emits a Cairn
5. asset promotion requires review
6. route and assignment preserve ranked alternatives
7. verification failure blocks execution and promotion

## Consequences
### Positive
- Strong replay and auditability
- Stable control-plane contracts across services
- Better support for evidence-backed operator workflows
- Clear promotion and execution gates
- Easier benchmark and policy enforcement

### Negative
- More initial schema and event discipline
- Higher implementation overhead at the start
- Requires graph and benchmark layers early

## Repo Placement
- `socioprophet-standards-storage`: canonical logical IDL, source standards packs, fixtures, and ADRs
- `TriTRPC`: protobuf and event transport mappings
- `agentplane`: implementation-facing docs and landing notes
- identity/entitlement surface: actor, role, tenant, and entitlement bindings

## Minimal Deployable Slice
1. Builder Studio contract store
2. Knowledge Intake
3. Policy Sentinel
4. Retrieval Controller
5. Verifier
6. Route/Assignment scoring
7. Support Console evidence view
8. Cairn emission
9. Benchmark gates

## Open Questions
- Which graph substrate should own case + asset + product graph families?
- Which benchmark harness should own component vs scenario vs confidentiality suites?
- How should generated schemas be versioned and released across repos?
