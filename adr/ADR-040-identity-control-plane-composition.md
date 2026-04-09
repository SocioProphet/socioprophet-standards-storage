# ADR-040 — Identity Control Plane Composition

## Status
Accepted (draft publication overlay)

## Context
The current SourceOS / SocioProphet stack already separates concerns across several repositories, but the boundaries have been implicit rather than normative.

Publicly visible lanes already exist:
- `trusted-service-identity` — workload/service identity and federation
- `identity-is-prime-reference` — semantic identity, Event-IR, proof artifacts, policy vetoes
- `human-digital-twin` — export/readiness state and decisioning
- `mcp-a2a-zero-trust` — grants, policy decisions, attestation bundles, ledger events
- `TriTRPC` — deterministic transport, receipts, carrier discipline
- `agentplane` — validate → run → evidence → replay execution control plane

Without a published composition contract, these lanes risk drifting or re-encoding overlapping concepts under different names.

## Decision
We publish a canonical identity control plane composition with the following split:

1. **Workload identity lane**
   - canonical principal anchor: `spiffe_id`
   - primary issuer/federation home: `trusted-service-identity`

2. **Semantic identity lane**
   - canonical semantic input: `Event-IR`
   - canonical semantic output: `ProofArtifact`
   - primary reference home: `identity-is-prime-reference`

3. **Export/readiness lane**
   - canonical export/readiness output: `HDTDecisionSummary`
   - primary home: `human-digital-twin`

4. **Runtime governance lane**
   - canonical runtime artifacts: `Grant`, `PolicyDecision`, `AttestationBundle`, `LedgerEvent`
   - primary home: `mcp-a2a-zero-trust`

5. **Transport / receipt lane**
   - canonical carrier and receipt discipline: `TriTRPC`
   - policy/evidence refs travel as carriage references, not full embedded artifacts by default

6. **Execution / replay lane**
   - canonical runtime enforcement/evidence plane: `agentplane`

## Consequences
- Identity is no longer treated as one blob.
- The canonical principal tuple is:
  - `spiffe_id`
  - `aum_digest`
  - optional `session_id`
- Semantic proofs and export/readiness decisions become referenceable upstream artifacts.
- Runtime authorization decisions can be replayed and audited across repos.
- Standards publication moves first; repo wiring follows second.

## Follow-on work
- publish Event-IR and ProofArtifact schemas in standards-storage
- publish HDT decision summary schema
- extend runtime governance schemas with proof refs
- define TriTRPC AUX carriage profile for policy/evidence refs
- wire agentplane to validate and replay the full chain
