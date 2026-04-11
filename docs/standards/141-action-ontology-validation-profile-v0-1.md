# 141. Action Ontology Validation Profile (v0.1)

## Purpose

This note defines the bootstrap validation posture for portable Action Ontology bundles.

## Validation layers

The bootstrap package uses two validation layers.

### 1. Structural bundle checks

Structural checks verify that a bundle has the required top-level arrays and that basic references are coherent.

Current bootstrap tool:

- `tools/action_ontology_bundle_check.py`

### 2. Pattern-semantic checks

Pattern-semantic checks verify that a bundle is not merely well-shaped but also satisfies protocol expectations for a named coordination pattern.

Current bootstrap tool:

- `tools/action_ontology_pattern_check.py`

## Initial pattern profiles

### Contract Net profile

A valid Contract Net bootstrap bundle SHOULD include:

- at least one `cfp` trace with `taskId`
- at least one `bid` trace for that `taskId`
- at least one `award` action
- at least one `executeTask` action
- at least one `done` trace that references an `executeTask` action via `refAction`

### Pub/Sub profile

A valid Pub/Sub bootstrap bundle SHOULD include:

- at least one `publish` trace with `topicId` and `messageId`
- at least one `consume` action
- at least one `ack` trace for the same topic/message pair
- the `ack` trace SHOULD reference the `consume` action via `refAction`

## Scope note

These bootstrap validators are intentionally lightweight and example-oriented.

They are not yet a replacement for deeper ontology/SHACL promotion gates or future runtime-level protocol verification.

## Summary

The bootstrap Action Ontology validation profile makes the package executable enough to reject obvious structural and protocol drift while the broader standards surface is still stabilizing.