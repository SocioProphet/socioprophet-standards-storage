# Identity Control Plane Composition (Normative)

This document uses RFC 2119 language: **MUST**, **SHOULD**, **MAY**.

## 1. Purpose
This standard defines the normative composition of the SourceOS identity control plane.
It exists to prevent three recurring design failures:
1. conflating workload identity with human semantic identity,
2. treating export readiness as if it were identity,
3. smearing runtime authorization semantics across transport, policy, and business logic layers.

## 2. Identity planes
### 2.1 Workload identity plane
- Workload/service principals **MUST** be represented by `spiffe_id` plus short-lived credentials.
- Workload identity issuance, rotation, and federation **MUST** be owned by the TSI/SPIFFE/SPIRE lane.
- Workload identity **MUST NOT** be used as a substitute for human semantic identity.

### 2.2 Semantic human/event identity plane
- Human/event semantic identity **MUST** be expressed through Event-IR or a compatible future standard derived from Event-IR.
- Prime-topic vectors, encodings, and merge-admissibility judgments **MUST** remain semantic artifacts, not session credentials.
- Merge or disclosure admissibility decisions **SHOULD** be accompanied by a replayable proof artifact or a signed reference to one.

### 2.3 Human artifact readiness/export plane
- Ω states and export/repair decisions **MUST** remain separate from semantic identity decisions.
- A human-centric artifact crossing a trust boundary **MUST** pass an HDT-style readiness/export decision point before export.
- Ω labels **MUST NOT** be treated as ontologies of the human.

### 2.4 Runtime grant/policy plane
- Concrete runtime authorization **MUST** be expressed in `Grant` and `PolicyDecision` objects, with evidence anchored by `AttestationBundle` and `LedgerEvent` where applicable.
- Runtime grant identity **MUST** bind to the canonical principal tuple.

## 3. Canonical principal tuple
Every privileged runtime action **MUST** be attributable to:
- `spiffe_id`
- `aum_digest`
- optional `session_id`

Interpretation:
- `spiffe_id` identifies the acting workload or signer.
- `aum_digest` identifies the software/configuration bundle.
- `session_id` narrows authorization to a bounded interaction when required.

## 4. Repo-to-role map
The following role mapping is normative:
- `trusted-service-identity` **MUST** own workload identity issuance and federation.
- `identity-is-prime-reference` **MUST** own Event-IR semantics, prime-topic reasoning, constrained ER, and proof generation for semantic human/event identity.
- `human-digital-twin` **MUST** own Ω readiness/export evaluation.
- `mcp-a2a-zero-trust` **MUST** own the canonical governance schema family for grants, attestations, decisions, quorum proofs, and ledger events.
- `TriTRPC` **MUST** own deterministic transport framing, canonical verification expectations, and receipt semantics.
- `agentplane` **MUST** own execution validation, evidence creation, and replay semantics.
- `socioprophet-standards-storage` **MUST** publish the normative standards, ADRs, conformance profiles, and schema indexes.

## 5. Decision sequencing
### 5.1 Semantic decisions before export decisions
- If an action involves human identity reasoning, semantic admissibility **MUST** be decided before export readiness.
- Prime identity and HDT **MUST** remain separate decision points.

### 5.2 Export decisions before grant issuance for egress
- If an action exports or projects human-centric artifacts outside a trust boundary, the export/readiness decision **MUST** be evaluated before issuing a grant for the export step.

### 5.3 Runtime authorization after identity/policy binding
- Runtime authorization **MUST** operate on bindings that already include the canonical principal tuple and any relevant proof or decision references.

## 6. A2A and MCP implications
- A2A and MCP implementations **MUST NOT** invent alternate identity models when the identity control plane already supplies the canonical bindings.
- A2A and MCP adapters **SHOULD** consume grants, policy decisions, and attestation references through the standardized governance schema family.
- A2A and MCP runtimes **MAY** cache validated proof references, but the cache key **MUST** include at least `policy_hash`, the principal tuple, and the referenced artifact hash.

## 7. Publication and versioning
- All standards and schemas named in this document **MUST** be versioned and indexed in standards-storage.
- Breaking changes **MUST** increment a major version and publish migration notes.
- Each normative object family **MUST** publish at least one cross-language example fixture.
