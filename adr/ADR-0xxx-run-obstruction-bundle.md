# ADR-0xxx: Run Obstruction Bundle as Canonical Control-Plane Artifact

## Status
Proposed

## Date
2026-04-09

## Context

SocioProphet separates standards, workspace control, execution control, transport,
and platform delivery across dedicated repositories.

This separation is desirable, but it leaves the effective truth of a governed run
distributed across:
- workspace manifests and locks
- descriptors / capability declarations
- lifecycle events
- policy decisions
- evidence artifacts
- replay receipts
- evaluation outputs
- promotion state
- negative evidence / retractions

We need one canonical artifact that makes the full obstruction/evidence surface
of a run explicit.

## Decision

We define a canonical control-plane artifact called the **Run Obstruction Bundle**.

A Run Obstruction Bundle is the minimum replayable object required before a governed
run may be treated as more than merely executed.

It joins:
- descriptor identity
- workspace identity
- lane / execution slice
- lifecycle transitions
- policy references and verdicts
- evidence references
- replay receipt references
- evaluation result references
- promotion state
- negative-evidence / retraction references

The Run Obstruction Bundle is normative at the standards layer and emitted by the
execution control plane.

## Consequences

### Positive
- a run becomes inspectable as one governed object rather than many loose fragments
- promotion criteria become explicit and testable
- replay and evaluation become attached to the same canonical object
- negative evidence and retractions become first-class

### Negative
- runners must emit more structured metadata
- promotion logic must be formalized rather than inferred from logs
- legacy execution paths will need shims during migration

## Promotion Rule

Execution completion does NOT imply promotion.

Promotion requires descriptor validation, coherent lifecycle, required policy gates,
required evidence, replay/receipt satisfaction, and no unresolved blocking negative evidence.

## Negative Evidence Rule

Negative evidence is a first-class control-plane object and MUST support contradiction,
invalidation, revocation, supersession, retraction, and downgrade implications.
