# 138. Evidence Receipt Spine (v0.1)

## Status

Proposed baseline for implementation.

## Purpose

This standard defines the first normalized receipt family for the evidence plane.

It exists to ensure that custody, validation, promotion, publication, execution, and replay can be linked through one common receipt structure rather than by ad hoc per-repo objects.

## Scope

This standard defines:

- the common receipt envelope,
- typed receipts for the first knowledge/evidence lifecycle,
- the minimum shared fields required for cross-repo interoperability.

This standard does **not** redefine:

- raw blob custody,
- transport framing,
- knowledge object taxonomy,
- execution artifact schemas.

## Typed receipt family

The first canonical receipt kinds SHALL be:

1. `ObservationReceipt`
2. `ValidationReceipt`
3. `PromotionReceipt`
4. `PublicationReceipt`
5. `ExecutionReceipt`
6. `ReplayReceipt`

## Shared fields

Every receipt SHALL carry:

- `id`
- `kind`
- `specVersion`
- `subjectRef`
- `issuedTimeUtc`
- `scopeRef`
- `policyWitnessThreshold`
- `witnesses`

When applicable, a receipt SHOULD also carry:

- `contentSpaceRef`
- `provenanceRootRef`
- `evidenceRefs`
- `upstreamReceiptIds`

## Receipt roles

### `ObservationReceipt`
Records that a source observation, acquisition, or local evidence intake occurred.

### `ValidationReceipt`
Records that a subject passed or failed validation checks and binds the result to validation evidence.

### `PromotionReceipt`
Records the governed act of promoting or refusing to promote a candidate into a more durable status.

### `PublicationReceipt`
Records that a validated object was published into a canonical content space or comparable governed publication surface.

### `ExecutionReceipt`
Records that a governed runtime action executed and binds the execution lane to the resulting evidence artifacts.

### `ReplayReceipt`
Records the replay boundary and the minimum inputs required to recompute or verify a prior execution path.

## Cross-repo intent

This receipt spine is intended to be consumed by:

- knowledge-state lifecycle records in the Knowledge Context standards package,
- runtime artifacts in execution/control-plane repos,
- platform services that normalize or surface governed receipts.

## Bootstrap note

These receipt schemas live temporarily in the evidence bootstrap subtree. They are expected to move into the future dedicated evidence contracts repo family when repo creation is available.
