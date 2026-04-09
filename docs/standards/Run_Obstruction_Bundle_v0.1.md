# Run Obstruction Bundle v0.1

## Purpose

Define the minimum replayable control-plane object required before a governed run
may be treated as more than merely executed.

## Canonical members

A Run Obstruction Bundle joins:
- descriptor identity
- workspace identity
- lane / execution slice
- lifecycle transitions
- policy references / verdicts
- evidence references
- receipt references
- evaluation references
- promotion state
- negative evidence / retraction references

## Promotion rule

Execution completion does NOT imply promotion.

Promotion requires:
- descriptor validation
- coherent lifecycle
- required policy gates
- required evidence
- receipt / replay satisfaction
- no unresolved blocking negative evidence
