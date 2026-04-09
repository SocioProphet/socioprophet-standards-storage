# 110 — Ghost Control Plane

## Status
Draft v0.1

## Purpose
This standard defines the minimum interoperable contract for the Ghost control plane across the SocioProphet stack.

The Ghost control plane standardizes:
- typed Ghost event envelopes
- canonical hashing of payload-bearing events
- signed governance artifacts
- registry update proof bundles
- correlated control-plane reporting

## Ownership boundaries
- `socioprophet-standards-storage` owns normative schemas and standards text.
- `TriTRPC` owns method naming, transport fixtures, and replay vectors.
- `prophet-platform` owns runtime harnesses and CI workflows.

## Core rule
Ghostspace may interpret.
Identity Is Prime must decide.
TriTRPC must replay.
Telemetry must prove what happened.

## Canonical primitives
- `GhostEventV2`
- `GhostSignatureEnvelopeV0_2`
- `GovernanceAttestationV0_1`
- `RegistryUpdateProofBundleV0_1`
- `ControlPlaneCorrelatedReportV0_1`

## Canonical hashing
For a payload-bearing Ghost event, `canonical_hash` MUST equal:

`sha256(canonical_json(event_without_canonical_hash))`

with:
- UTF-8 encoding
- sorted object keys
- compact separators
- preserved array order
- top-level `canonical_hash` excluded from the hash scope

## Result lattice
Implementations MUST distinguish:
- `ADMITTED`
- `ADMITTED_WITH_WARNING`
- `BLOCKED`

Malformed artifacts are transport/validation failures and MUST NOT be silently recast as semantic `BLOCKED` outcomes.

## Runtime lane
A minimal runtime lane SHOULD be able to emit and validate:
- queued / started / succeeded Ghost layer-touch events
- contradiction fracture events on failure
- signed governance attestations
- signed registry update bundles

## Control-plane correlation
A complete control-plane run SHOULD be representable as one correlated report joining:
- trust-root lifecycle
- governance quorum
- registry update admission
- runtime fracture lane
- final validation outcome

## Conformance note
This is a draft interoperability contract. Implementations SHOULD treat these schemas as the source of truth for new work and maintain backward compatibility once promoted to stable.
