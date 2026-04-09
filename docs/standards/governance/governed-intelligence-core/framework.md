# Governed Intelligence Core v0.1 — Working Framework

## Purpose

This framework turns the public-safe SocioProphet governed-intelligence architecture into a checkable standards layer. It captures the minimum normative surface needed to make controlled execution, proof-bearing transitions, replayability, and surface governance testable rather than merely aspirational.

## Scope

This v0.1 working framework covers five layers:

1. conformance and terms
2. core object model
3. authorization and policy
4. events, lineage, and proofs
5. governance and surface promotion

It does **not** attempt to solve every semantic or epistemic question in v0.1.

## Relation to semantic-proof core

This framework composes with `docs/standards/semantic-proof/`.

- semantic-proof remains the home for proof-object canon, canonicalization, replay-hash rules, generic proof fixtures, and proof failure codes;
- governed-intelligence-core adds the broader control-plane and governance semantics around those proofs.

## 00 — Conformance and terms

### Status
This document is a working draft for the public-safe canonical standards layer of governed intelligence in SocioProphet.

### Requirement language
The key words **MUST**, **MUST NOT**, **REQUIRED**, **SHALL**, **SHALL NOT**, **SHOULD**, **SHOULD NOT**, **RECOMMENDED**, **MAY**, and **OPTIONAL** are interpreted in the BCP 14 sense when written in all capitals.

### Conformance classes
The minimum conformance classes are:
- Producer
- Evaluator
- Consumer
- Verifier
- Surface Integrator

### Publication model
Every normative section SHOULD exist in two forms:
- a human-readable standards document; and
- a machine-readable companion artifact.

### Shared object envelope
Every canonical object MUST include:
- `object_type`
- `object_id`
- `spec_version`
- `schema_uri`
- `emitted_at`
- `emitter_ref`

## 10 — Core object model

### Minimum v0.1 object families
The minimum canonical object families are:
- `event_ir`
- `scope`
- `entity`
- `link`
- `proof_artifact`
- `policy_state`
- `export_rule`
- `channel_provenance`

### Event ingress
`event_ir` is the typed ingress record for consequential observations and MUST carry enough structure for replay, policy evaluation, provenance, and later graph materialization.

### Required invariants
The minimum invariants are:
- no silent collapse of incompatible contexts into one ambient identity;
- no consequential decision without proof production;
- no export widening solely because merge confidence increased;
- no protected-context widening without admissibility and required witness/review paths;
- no irreversible merge without a reversal path;
- no promoted graph output without channel provenance.

## 20 — Authorization and policy

### Canonical decision request
Every consequential authorization evaluation MUST be representable as:
- `principal_ref`
- `action_ref`
- `resource_ref`
- `context`

### Relationship tuples
Authorization-relevant relations are represented as:
- `subject_ref`
- `relation`
- `object_ref`

### Policy bundles
A policy bundle is the distributable unit of policies, policy data, validation metadata, and manifest material. Bundles MUST be versioned, attributable, and activation-safe.

### Required evaluation outcomes
The minimum evaluation outcomes are:
- `allow`
- `deny`
- `review_required`
- `witness_required`
- `error`

### Separation rules
Merge validity and export validity are separate authorization questions. Verification success is also separate from policy permission.

## 30 — Events, lineage, and proofs

### Canonical events
A canonical event is a named occurrence at an instant in time. Event names SHOULD be low-cardinality, dot-delimited, and semantically stable.

### Required event families
The minimum event families are:
- `sp.event.ingest.*`
- `sp.policy.evaluation.*`
- `sp.capability.routing.*`
- `sp.execution.*`
- `sp.evidence.emission.*`
- `sp.review.*`
- `sp.promotion.*`
- `sp.reversal.*`
- `sp.export.*`
- `sp.proof.*`

### Lineage facets
Lineage facets are additive metadata blocks for policy, proof, model, export, review, reversal, surface, and channel lineage. They MUST use immutable schema references.

### Proof verification
Proof-bearing objects MUST be independently verifiable using the information the applicable profile declares necessary. Verification success MUST NOT be treated as policy permission.

### Replay
Replay MUST preserve enough information to reconstruct requests, policy bundles, evidence, proofs, transitions, and any review/witness/promotion/reversal steps. Divergent replay results MUST be recorded explicitly.

## 40 — Governance and surface promotion

### Governance functions
Every control SHOULD map to at least one governance function:
- `govern`
- `map`
- `measure`
- `manage`

### Control matrix
Every control matrix row MUST identify:
- control identifier and source
- governance function
- owner class
- evidence source
- validation method
- review cadence
- release gate
- reversal or exception path

### Owner classes
The minimum owner classes are:
- `spec_owner`
- `schema_owner`
- `policy_owner`
- `verification_owner`
- `surface_owner`
- `release_owner`
- `incident_owner`
- `records_owner`

### Release gates
The minimum release gates are:
- `schema_gate`
- `policy_gate`
- `proof_gate`
- `replay_gate`
- `surface_gate`
- `governance_gate`

### Surface promotion criteria
A surface MUST NOT be promoted to first-class public status unless it has:
- public landing surface
- product docs
- trust or policy context when relevant
- clear CTA and routing
- explicit auth/capability relationship when relevant
- ownership and maturity expectations

### Incident and reversal governance
Rollback and reversal are governance actions, not ad hoc edits. Reversal MUST NOT erase the evidence needed to understand both the original action and the corrective action.

## Seed artifact inventory

This seeded package includes:
- standalone schema seeds for decision requests, tuples, bundles, events, control rows, surface reports, incident records, and replay results;
- example records for validation;
- scenario fixtures for merge/export separation, review/witness gates, reversal after proof invalidation, surface-promotion denial, and replay divergence;
- a local validation harness.

## Known gaps

This seed intentionally leaves some future work open:
- richer semantic invariants beyond JSON Schema
- stronger cross-object transition validation
- a fuller claim and narrative layer
- tighter integration with release automation and repository-wide validation
- governance adjudication of owner/evidence/gate assignments

## Use

This framework is a source-controlled working aid. It is meant to make governed-intelligence work inspectable, repeatable, and testable in the standards repository. It does not replace local legal review, institutional approval, or restricted operational controls.