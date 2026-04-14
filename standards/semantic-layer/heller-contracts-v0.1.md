# Heller v1 Event and State Contracts

## Purpose

This document seeds a first-pass contract family for Heller-domain event envelopes and state snapshots.

## Scope

The artifacts in this change set define:

- Avro contracts for event and state payloads
- JSON Schema mirrors for validation and examples
- a compact event catalog for Heller lifecycle operations
- sample JSON instances for baseline interoperability checks

## Canonical artifacts

- `schemas/avro/heller/v1/heller_event_envelope.avsc`
- `schemas/avro/heller/v1/heller_state_snapshot.avsc`
- `schemas/jsonschema/heller/v1/heller_event_envelope.schema.json`
- `schemas/jsonschema/heller/v1/heller_state_snapshot.schema.json`
- `events/heller/v0/heller-events.v0.1.yaml`
- `examples/heller/v1/sample_event_envelope_v1.json`
- `examples/heller/v1/sample_state_snapshot_v1.json`

## Notes

This is an initial standards seed, not yet the final conformance profile.

- The Avro contracts are the normative payload contracts in this patch.
- The JSON Schema mirrors exist to support validation, examples, and developer ergonomics.
- Transport-bound byte fixtures and Protocol Buffers siblings belong in the TriTRPC repository.

## Follow-on work

- add schema evolution guidance and compatibility tests
- register stable schema labels / IDs where transport bindings require them
- add round-trip verification in CI against a standard Avro runtime
