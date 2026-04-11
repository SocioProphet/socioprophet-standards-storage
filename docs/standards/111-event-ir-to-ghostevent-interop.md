# Event-IR → GhostEvent Interop Specification v1

## Status
Draft v1.0

## Purpose
This specification defines the normative mapping from canonical Event-IR records into `GhostEvent`
artifacts. It is the semantic bridge between the Identity-Is-Prime kernel and the Ghost control plane.

This specification is intentionally narrow. It standardizes:
- the semantic payload derived from Event-IR
- the canonical prime-vector encoding
- the binding to a Prime Topic Registry state
- the canonical hash scope
- the minimum fields required for replayable validation

## Ownership boundaries
- The Prime Topic Registry and its governance are authoritative for topic identity and basis order.
- Event-IR is authoritative for raw/derived evidence semantics.
- GhostEvent is authoritative for telemetry, transition, fracture, and runtime replay semantics.
- TriTRPC is authoritative for deterministic transport and fixture conformance.

## Normative language
The key words MUST, MUST NOT, SHOULD, SHOULD NOT, and MAY are normative.

## Source object: Event-IR
An Event-IR object is assumed to be a typed intermediate record carrying:
- primitive evidence
- derived facts
- scope/context
- actor/interaction/observer references
- topic-factorization state or enough evidence to derive it

This spec does not redefine Event-IR. It defines how Event-IR is projected into GhostEvent.

## Target object: GhostEvent
A GhostEvent is the minimum replayable telemetry artifact for the Ghost control plane.
Every GhostEvent MUST be:
- schema-valid
- canonically hashable
- optionally signed
- basis-bound to an explicit registry state when prime-topic semantics are present

## Required semantic fields added by this spec
A GhostEvent derived from Event-IR MUST carry the following additional fields when prime-topic semantics are present:
- `prime_registry_ref`
- `prime_registry_state_hash`
- `event_ir_hash`
- `prime_vector`

### `prime_registry_ref`
A stable identifier for the registry and version used to interpret the event.

### `prime_registry_state_hash`
The hash of the exact registry state used for this event. This MUST allow replay against the same basis,
even if the registry evolves later.

### `event_ir_hash`
A canonical hash pointer to the Event-IR source payload. This is the semantic provenance anchor for the
Ghost event.

### `prime_vector`
The canonical sparse representation of the event’s topic factorization under the referenced registry.

## Canonical prime-vector representation
The normative representation of `prime_vector` is a sparse ordered list of entries:

```json
[
  { "basis_index": 0, "topic_id": "topic:identity_prime", "prime": 2, "exponent": 1 },
  { "basis_index": 4, "topic_id": "topic:witness",        "prime": 11, "exponent": 2 }
]
```

### Invariants
1. Entries MUST be sorted by ascending `basis_index`.
2. `basis_index` MUST match the referenced registry state.
3. `topic_id` MUST match the referenced registry state.
4. `prime` MUST match the referenced registry state.
5. `exponent` MUST be a non-negative integer.
6. Zero-exponent entries MUST NOT be included.
7. Duplicate `basis_index` entries MUST NOT appear.

### Optional scalar encoding
Implementations MAY also derive a scalar encoding:

`prime_encoding = Π prime_i ^ exponent_i`

If present, the scalar encoding MUST decode to the same sparse vector under the referenced registry state.
The sparse vector remains the normative representation.

## Triadic mapping
Every GhostEvent derived from Event-IR SHOULD preserve the triadic semantics:

- `source_ref`
- `interaction_ref`
- `observer_ref`

If the Event-IR source contains enough information to construct the triad, then:
- `triad_assert` events MUST carry those three references explicitly
- other event types SHOULD retain them in payload or artifact references where possible

## Event-type mapping
The following minimum mapping is normative.

### `layer_touch`
Use when Event-IR indicates a stable transition or touch into a semantic layer without contradiction.

### `triad_assert`
Use when Event-IR supports an explicit `(source, interaction, observer)` assertion.

### `metric_snapshot`
Use when Event-IR is being used as the source for a derived metric emission.

### `projection_attempt`
Use when Event-IR is being lifted into a higher-order interpreted state and admission is not yet final.

### `projection_commit`
Use when a projected state is admitted and linked to a final validation outcome.

### `contradiction_fracture`
Use when Event-IR plus policy/registry constraints imply an inadmissible or contradictory state.

### `entanglement_marker`
Use only when a measurable coupling criterion is met. This event type MUST NOT be emitted from
pure narrative interpretation alone.

## Canonical hash scope
For any payload-bearing GhostEvent, `canonical_hash` MUST equal:

`sha256(canonical_json(event_without_canonical_hash))`

Canonical JSON in this specification means:
- UTF-8 encoding
- sorted object keys
- compact separators
- preserved array order
- no inclusion of the top-level `canonical_hash` field in the hash scope

The following fields MUST be included in hash scope:
- event metadata
- `prime_registry_ref`
- `prime_registry_state_hash`
- `event_ir_hash`
- `prime_vector`
- payload

If a signature envelope is present, the signature MUST bind this canonical hash.

## Registry binding rules
A GhostEvent that includes prime semantics MUST be rejected if:
- `prime_registry_ref` cannot be resolved
- `prime_registry_state_hash` does not match the resolved registry state
- any `prime_vector` entry does not match the resolved registry state
- deprecated/retired topics are used in a mode disallowed by policy

## Validation error classes
At minimum, validators SHOULD distinguish:

### Malformed
- invalid schema
- invalid canonical hash
- invalid signature envelope
- duplicate vector indices
- bad data types

### Blocked
- unresolved registry
- registry state hash mismatch
- invalid topic/prime/basis mapping
- forbidden deprecated or retired topic usage
- contradiction fracture conditions
- missing migration artifact for cross-version projection

### Warning
- deprecated topic usage permitted by policy
- precision loss
- approve-with-note governance
- cross-version projection admitted under explicit migration rules

## Conformance
An implementation is conformant with this spec only if it:
1. emits the required registry-binding fields
2. emits canonical sparse prime vectors
3. computes canonical hashes according to this spec
4. validates registry state and vector consistency
5. preserves malformed vs blocked distinction
