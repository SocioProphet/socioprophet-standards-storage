# Governance Artifacts and Bindings (Normative)

This document uses RFC 2119 language: **MUST**, **SHOULD**, **MAY**.

## 1. Purpose
This standard defines how semantic identity artifacts, export/readiness decisions, runtime grants, attestations, and ledger events bind together.

## 2. Canonical artifacts
### 2.1 Event-IR
- Event-IR **MUST** remain the baseline semantic event representation for human/event identity reasoning.
- At minimum, an Event-IR document **MUST** carry `version` and an `events` array.
- Each event **MUST** include `ts`, `actor`, `scope`, `action`, `primes`, and `attrs`, matching the current public schema family. 
- Event-IR documents **SHOULD** be content-addressed.

### 2.2 ProofArtifact
- Proof artifacts **MUST** carry `claim`, `status`, `inputs`, `domains`, and `diagnostics`.
- Supported baseline statuses are `PROVED`, `VIOLATION`, and `INCONCLUSIVE`.
- Proof artifacts **SHOULD** include `violations`, `counterexample`, `witnesses`, and `precision` when available.
- Proof artifacts consumed by runtime policy **MUST** bind to a policy version and stable input hashes.

### 2.3 HDT Decision Summary
A compact HDT decision summary **MUST** be introduced as a shared contract.
It **MUST** contain at least:
- `subject_ref`
- `omega_state`
- `allow_export`
- `repair_required`
- `policy_hash`
- `evidence_hashes[]`
- `issued_at`
- `issuer`

The summary **MUST NOT** be treated as a replacement for raw HDT traces; it is the portable boundary contract.

## 3. Runtime governance bindings
### 3.1 AttestationBundle binding
- `AttestationBundle.subject` **MUST** include `spiffe_id` and `aum_digest`.
- Runtime admission **SHOULD** reject attestations whose subject tuple does not match the acting runtime principal tuple.

### 3.2 Grant binding
- `Grant.binding` **MUST** include `spiffe_id` and `aum_digest`; it **MAY** include `session_id`.
- `Grant.policy_hash` **MUST** identify the policy state under which the grant was issued.
- For identity-sensitive or human-exporting actions, a grant **SHOULD** reference:
  - a semantic proof artifact hash/reference,
  - an HDT decision summary hash/reference when export is involved.

### 3.3 PolicyDecision binding
- `PolicyDecision.policy_hash` **MUST** align with the grant or runtime evaluation that consumed it.
- `PolicyDecision.constraints` **MUST** remain the runtime-operational constraint container.
- The policy decision **MAY** include references to semantic proofs and HDT summaries, but those references **MUST NOT** replace the decision itself.

### 3.4 LedgerEvent binding
- `LedgerEvent.actor` **MUST** contain `spiffe_id`; it **SHOULD** contain `aum_digest` when meaningful.
- `payload_hash` and `policy_hash` **MUST** remain stable semantic/governance hashes.
- Identity-sensitive events **SHOULD** include references to any semantic proof artifact and HDT decision summary that materially influenced the decision.

## 4. Required reference semantics
Whenever a runtime object references a semantic or export artifact, the reference **MUST** be one of:
1. a content-addressed full artifact,
2. a content-addressed artifact reference,
3. a signed summary object with its own stable content hash.

Ephemeral local pointers **MUST NOT** be the only reference form across trust boundaries.

## 5. Signed-bytes rule
Any signed governance artifact **MUST** declare, directly or by profile, the exact bytes that are signed.
Implementations **MUST NOT** rely on implementation-defined serializer behavior as the sole definition of signed bytes.
Cross-language test vectors **MUST** be published for each signed artifact family.

## 6. Non-goals
- This standard does not define the internal semantics of prime-topic inference.
- This standard does not define the internal math of the Ω lattice.
- This standard does not define transport framing; that belongs to TriTRPC.
