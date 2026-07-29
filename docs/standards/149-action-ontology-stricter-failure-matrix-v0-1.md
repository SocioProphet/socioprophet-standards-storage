# 149. Action Ontology Stricter Failure Matrix (v0.1)

## Purpose

This note extends the bootstrap failure matrix beyond the first obvious protocol violations.

## Additional failure cases in scope

### Pub/Sub

The bootstrap profile now treats these as failures:

- duplicate `publish` traces for the same `(topicId, messageId)` pair
- duplicate `ack` traces for the same `(topicId, messageId)` pair
- missing `ack`
- `ack.refAction` that does not resolve to a consume action

### Contract Net

The bootstrap profile now treats these as failures:

- missing `bid` for the `cfp.taskId`
- missing `done`
- missing `done.refAction`

### ContractNet↔PubSub bridge

The bridge profile now treats these as failures:

- missing publish bridge for a ContractNet `taskId`
- publish bridge present but carrying the wrong `taskId`

## Intent

These checks are still bootstrap-grade and intentionally small. They exist to increase confidence that the Action Ontology examples are not merely descriptive, but actually reject common coordination and replay drift conditions.
