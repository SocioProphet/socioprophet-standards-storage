# ADR-040: Adopt a multi-plane identity control plane for agent and human-governed operations
- Date: 2026-04-03
- Status: Proposed
- Decision owner: SocioProphet
- Contexts affected: identity, governance, artifacts, rpc, graphs, policy, execution, publication

## Context
The public SourceOS/SocioProphet stack now shows a clear split across several repositories:
- `trusted-service-identity` handles workload identity issuance, attestation, and federation.
- `identity-is-prime-reference` handles semantic human/event identity decomposition, constrained entity resolution, and proof-bearing policy veto.
- `human-digital-twin` handles human artifact export/readiness decisions via the Ω lattice and explicit policy gates.
- `mcp-a2a-zero-trust` defines grants, attestations, policy decisions, and ledger events for runtime authorization and audit.
- `TriTRPC` provides deterministic transport framing, canonical verification expectations, and receipt-oriented transport semantics.
- `agentplane` is positioned as the execution control plane (`bundle→validate→run→evidence→replay`).
- `socioprophet-standards-storage` is the existing standards/ADR/publication home.

Today, these lanes are intellectually aligned but not yet normalized into a single, normative composition contract.
The risk is not lack of ideas. The risk is semantic drift:
- the same concept represented differently in multiple repos,
- runtime enforcement happening without stable proof inputs,
- transport receipts and semantic proofs being conflated,
- workload identity being confused with human semantic identity.

We need a single decision that freezes the split and makes the composition normative.

## Decision
Adopt a **multi-plane identity control plane** with the following normative split:

1. **Workload identity plane**
   - Principal form: `spiffe_id` plus short-lived workload credentials.
   - Owning repo/lane: `trusted-service-identity`.
   - Purpose: answer “which workload or service is acting?”

2. **Semantic human/event identity plane**
   - Principal semantic forms: Event-IR, prime-topic vectors/encodings, merge-admissibility proofs.
   - Owning repo/lane: `identity-is-prime-reference`.
   - Purpose: answer “what identity-relevant meaning is present, and is a merge/inference/disclosure admissible?”

3. **Human artifact readiness/export plane**
   - Principal forms: Ω state, export/repair decisions, readiness summaries.
   - Owning repo/lane: `human-digital-twin`.
   - Purpose: answer “is this outward-facing human artifact allowed to cross a boundary?”

4. **Runtime grant/policy plane**
   - Principal forms: `Grant`, `PolicyDecision`, `AttestationBundle`, `LedgerEvent`, optional `session_id`.
   - Owning repo/lane: `mcp-a2a-zero-trust`.
   - Purpose: answer “is this concrete action allowed right now, under which constraints, and with which evidence?”

5. **Transport/receipt plane**
   - Principal forms: canonical frame bytes, AUX bundle profile, transport receipts.
   - Owning repo/lane: `TriTRPC`.
   - Purpose: answer “what exact bytes were exchanged, and can we verify/replay them?”

6. **Execution/evidence plane**
   - Principal forms: validated bundles, execution records, evidence packs, replay handles.
   - Owning repo/lane: `agentplane`.
   - Purpose: answer “what actually ran, under which identity/policy inputs, and can we replay it?”

`socioprophet-standards-storage` becomes the single normative publication and conformance home for the composition across these planes.

## Options considered
1) Collapse all identity work into a single repository and model.
2) Leave the current split informal and document it ad hoc in per-repo READMEs.
3) Preserve the split, but publish a normative composition contract in standards-storage.

## Tradeoffs
- Correctness / consistency
  - Option 3 improves consistency by freezing interfaces without flattening distinct identity concerns.
  - Option 1 would reduce repo count but conflate workload, semantic, and export governance semantics.
- Query expressiveness
  - Option 3 preserves rich semantic identity reasoning while still allowing simple runtime authorization.
- Throughput / p95/p99 latency
  - Separating planes lets hot-path runtime checks remain compact while deeper semantic checks stay asynchronous or cached.
- Operational complexity
  - More interfaces exist, but each interface becomes explicit and testable.
- Cost profile
  - Lower long-term integration cost than repeated bespoke adapters.
- Failure and recovery semantics
  - Replay/evidence boundaries become clearer, especially once execution and transport are separated from semantic proof generation.

## Measurement plan
Success is measured by the following outcomes:
1. standards-storage publishes normative docs for the multi-plane composition.
2. zero-trust schemas can reference prime-identity proofs and HDT decision summaries without schema ambiguity.
3. TriTRPC gains a documented policy/evidence AUX profile.
4. agentplane can execute and emit replayable evidence tied to grants, policies, and identities.
5. Cross-repo conformance tests exist for canonical bindings and object references.

## Consequences
What becomes easier:
- Explaining the identity model to engineers and auditors.
- Wiring A2A/MCP runtimes to a stable policy substrate.
- Separating human semantic identity from workload/service identity.
- Producing evidence and replay artifacts that are meaningful rather than decorative.

What becomes harder:
- We must version and validate more schemas explicitly.
- Some repos will need small adapter layers instead of continuing to improvise local object shapes.

What must be built next:
- Standards `050`, `060`, and `070`.
- HDT decision-summary contract.
- Zero-trust schema extensions for semantic/export proof references.
- TriTRPC AUX profile.
- agentplane evidence binding.
