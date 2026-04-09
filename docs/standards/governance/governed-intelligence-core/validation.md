# Governed Intelligence Core v0.1 — Validation Summary

## Current starter-pack posture

This package was seeded from a stricter local implementation starter and reduced into a repository-friendly governance package.

The source starter pack validated:
- expected-valid examples passing;
- expected-invalid examples failing;
- schema reference resolution;
- replay-result and policy-state structural correctness;
- scenario presence for merge/export separation, review/witness gates, reversal, promotion denial, and replay divergence.

## Validation goals for this repository package

This package is considered healthy when:
- package schemas parse and validate;
- example records validate against their package schemas;
- explicitly invalid examples fail as expected;
- scenario fixtures remain present and JSON-parseable;
- the package remains composition-safe with `docs/standards/semantic-proof/` rather than redefining its proof canon.

## Known gaps

The current seeded package still has known limits:
- ownership, evidence, and release-gate assignments remain seed-level and need governance review;
- schema validation cannot enforce every graph-level business rule or higher-order semantic invariant;
- scenario fixtures describe transition-rich paths but do not yet exhaustively execute them end-to-end;
- repository-wide automation wiring is not yet attached to Makefile or CI.

## Minimum expected outcomes

A local validation pass SHOULD show:
- valid seed records pass;
- invalid seed records fail;
- no silent schema resolution errors;
- no confusion between proof verification success and policy permission;
- no collapse of merge validity into export validity.

## Follow-on tightening

The next useful tightening steps are:
1. expand the record set to cover more transition paths;
2. add graph/business-rule checks beyond JSON Schema;
3. bind the package to release gates and repository-wide validation automation;
4. promote the control-matrix summary into an adjudicated governance registry.
