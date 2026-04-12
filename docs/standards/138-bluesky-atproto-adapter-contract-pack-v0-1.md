# 138. Bluesky (ATProto) Adapter Contract Pack (v0.1)

## Status

Draft, implementable contract pack.

## Purpose

Define the first governed contract pack for a **social connector** (Bluesky / ATProto) that is compatible with the Prophet / New Hope control-plane invariants:

- no ambient connector power
- rail separation (mirror / live / action)
- staged ingestion lanes + quarantine
- outbox-only writes
- deterministic receipts + ledgered audit events
- bounded backfill + explicit rate budgets
- delete / forget propagation

This pack is designed to be copied into future dedicated connector repositories without semantic change.

## Scope

This standard covers:

1. The adapter contract surface (capabilities + rail split).
2. The minimal schema set required to represent grants, root bindings, staged objects, carriers, receipts, and audit events.
3. A conformance test checklist to prevent “connector drift” and silent privilege expansion.

Non-goals:

- prescribing a single ATProto endpoint, SDK, or auth implementation
- shipping runtime code (runtime belongs in `sociosphere` / `prophet-platform`)

## Normative requirements

### 138.1 Authorization and isolation

The adapter SHALL reject mirror and action operations unless a valid `CapabilityGrant` is presented and bound to a valid `RootBinding`.

The adapter SHALL scope every ingestion namespace to a `RootBinding` such that content and derived artifacts cannot escape the binding without explicit policy.

### 138.2 Rail separation

The adapter SHALL expose separate connector rails:

- Mirror rail: ingest into local durable stores; eligible for indexing.
- Live rail: read-through fetch for UI; SHALL NOT write to indexes.
- Action rail: write operations; SHALL be executed only via an Outbox workflow.

### 138.3 Lane state machine

Every ingested object SHALL exist in exactly one lane:

`ingested | analyzed | problematic | published`

Promotion and quarantine actions SHALL emit ledger events.

### 138.4 Deterministic receipts

Mirror transformations SHALL emit receipts containing:

- input hash set
- output hash set
- stage identifier + version
- policy decisions applied
- errors and quarantine decisions

Receipts SHOULD be stable for identical inputs and stage versions.

### 138.5 Auditability

The adapter SHALL emit audit events for at least:

- grant issuance and root binding
- ingest accepted/rejected
- mirror sync started/completed/failed
- stage completed/failed
- object quarantined/promoted
- outbox requested/approved/denied/completed/failed
- throttling and protective pause (circuit) state changes

### 138.6 Resilience and bounded ingestion

The adapter SHALL implement per-root rate budgets and bounded backfill windows.

The adapter SHOULD prioritize live rail over mirror rail under contention.

### 138.7 Privacy and deletion propagation

A delete/forget request SHALL remove derived artifacts (indexes, caches, summaries) and SHALL be ledgered.

## Artifact locations (this repo)

### Normative text
- `docs/standards/138-bluesky-atproto-adapter-contract-pack-v0-1.md` (this file)
- `docs/standards/connectors/bsky/blue-sky-adapter-pattern-v0.1.md`
- `docs/standards/connectors/bsky/bluesky-atproto-adapter-contract-v0.1.md`
- `docs/standards/connectors/bsky/bsky-runtime-skeleton-plan-v0.1.md`

### Conformance checklist
- `docs/conformance/bsky-adapter-conformance-tests-v0.1.md`

### Schemas
- `schemas/connectors/bsky/v0.1/core/*.json`
- `schemas/connectors/bsky/v0.1/bsky/*.json`

### Examples
- `examples/connectors/bsky/v0.1/*.json`

## Related standards

- `030-service-interfaces-tritrpc.md` — typed RPC contract expectations.
- `050-security-oidc-policy.md` — baseline authorization posture.
- `136-evidence-fabric-bootstrap-temp-landing.md` — temporary landing posture for contract packs.
- `137-evidence-broker-local-ingest-manifest-v0-1.md` — custody-first ingestion discipline.

## Implementation evidence (expected)

Runtime implementations SHOULD link back to this standard and provide:

- a conformance runner that executes the conformance checklist
- example receipts and audit events
- documentation of per-root rate budgets and backfill ceilings
