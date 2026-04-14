# 139. Action Ontology Contracts and Pattern Surfaces (v0.1)

## Purpose

This note defines the portable bootstrap contract surface for Action Ontology instances used in examples, fixtures, and early integration work.

## Core object surface

The minimum portable object set is:

- `Agent`
- `ActionType`
- `State`
- `Action`
- `Trace`
- `Preference`

## Required semantics

### Action

An `Action` SHOULD provide at minimum:

- actor / performer reference
- action type reference
- from-state reference
- to-state reference
- timestamp

### State

A `State` SHOULD declare at least one affordance.

### Trace

A `Trace` SHOULD declare:

- pattern
- trace kind
- medium
- timestamp

## Pattern families in scope for bootstrap

The bootstrap package is deliberately not a one-note pattern surface. The initial family is:

- Contract Net
- Pub/Sub
- Blackboard
- Workflow

## Validation posture

The bootstrap package supports two validation layers:

1. structural shape checks
2. pattern-specific invariant checks

## Ontology relationship

Normative semantic terms belong in `SocioProphet/ontogenesis`.
This bootstrap standards package exists so portable examples and early validation surfaces can evolve without coupling runtime consumers directly to ontology-source internals.

## Summary

The bootstrap Action Ontology package standardizes a small but expressive cross-pattern object surface suitable for agentic coordination, swarm communication, and governed replay-oriented examples.