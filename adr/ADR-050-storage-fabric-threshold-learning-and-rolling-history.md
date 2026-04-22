# ADR-050: Storage-Fabric Threshold Learning and Rolling History

## Status
Accepted

## Context

Storage benchmark interpretation needs to separate ordinary benchmark movement from decision-relevant drift.

## Decision

Storage-fabric benchmark methodology should use rolling history, noise bands, minimum practical effect size, and explicit trend classification when interpreting benchmark movement.

## Consequences

- benchmark reports must expose enough metadata to explain trend classification
- `noise` is distinct from `stable`
- a single small movement should not be treated as a storage-fabric regression without supporting evidence
