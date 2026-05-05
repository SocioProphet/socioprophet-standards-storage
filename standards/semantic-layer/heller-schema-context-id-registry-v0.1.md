# Heller Schema + Context ID Registry (v0.1)

This registry freezes the first string labels used to derive 32-byte Heller schema and context identifiers.

Derivation rule:

```text
ID = SHA3-256(label)
```

## Event envelope Avro payload schema

- Label: `HELLER_EVENT_AVRO_v1`
- SCHEMA_ID: `69de72bfc1ff283618ff01dc8ad0d64c7254076db286a7ea0154be57e9851c58`
- Canonical paths:
  - `schemas/avro/heller/v1/heller_event_envelope.avsc`
  - `schemas/jsonschema/heller/v1/heller_event_envelope.schema.json`

## State snapshot Avro payload schema

- Label: `HELLER_STATE_AVRO_v1`
- SCHEMA_ID: `038609da12e4c7b6ace729ab53b73eb20654e3f86cb4ffb88944e3da4663290d`
- Canonical paths:
  - `schemas/avro/heller/v1/heller_state_snapshot.avsc`
  - `schemas/jsonschema/heller/v1/heller_state_snapshot.schema.json`

## Shared Heller transport / context label

- Label: `HELLER_CONTEXT_v1`
- CONTEXT_ID: `5f7bb0541e2e79bd3d38f3d561df91ffc5135611543fa0cc65bc41214f8c5052`
- Canonical paths:
  - `events/heller/v0/heller-events.v0.1.yaml`
  - `standards/semantic-layer/heller-contracts-v0.1.md`
  - transport binding material in `SocioProphet/TriTRPC`

## Change control

- Labels MUST NOT be renamed.
- Breaking changes MUST mint new labels, for example `HELLER_EVENT_AVRO_v2`.
- Avro contracts are the normative payload contracts for this seed.
- JSON Schema mirrors are validation and developer ergonomics surfaces.
- Transport bindings MUST reference these labels before claiming canonical TriTRPC frame conformance.
