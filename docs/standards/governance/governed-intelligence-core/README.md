# Governed Intelligence Core v0.1

This package stages the governed-intelligence control-plane companion for SocioProphet’s standards repository.

## Why this package belongs here

`SocioProphet/socioprophet-standards-storage` already owns platform-wide standards, contracts, schemas, benchmark framing, and governance-oriented operating packs. This package extends that role into the public-safe governed-intelligence lane: conformance, core objects, authorization and policy, events and lineage, proof-bearing execution, and surface-promotion governance.

## Relation to existing standards

This package is intentionally **complementary** to the existing semantic-proof core.

- `docs/standards/semantic-proof/` remains the canonical home for proof-object canon, proof fixtures, replay-hash rules, and generic proof verification vocabulary.
- `docs/standards/governance/governed-intelligence-core/` adds the broader governed-execution layer: decision requests, relationship tuples, policy bundles, canonical events, control-matrix rows, incident records, replay-result handling, and governance/promotion gates.

This avoids duplicating proof canon while still making proof-bearing governance and replay obligations explicit.

## Layout

- `framework.md` — condensed working framework for the v0.1 governed-intelligence standards corpus.
- `validation.md` — current validation posture and known gaps.
- `conformance-control-matrix.seed.summary.json` — initial machine-readable control summary.
- `../../../schemas/governance/governed-intelligence-core/v0/` — package-specific schema seed set.
- `../../../examples/governance/governed-intelligence-core/v0/records/` — example records for schema validation.
- `../../../examples/governance/governed-intelligence-core/v0/scenarios/` — scenario fixtures for transition-rich policy and governance paths.
- `../../../scripts/validate_governed_intelligence_core_examples.py` — local validation harness.

## Validation

Run the package validator directly:

```bash
python3 scripts/validate_governed_intelligence_core_examples.py
```

The harness validates example records against the package schemas and checks that invalid fixtures fail as expected.

## Current scope

v0.1 focuses on the strongest public-safe layer:

- typed event ingress and canonical event recording
- first-class scope and policy state handling
- explicit authorization decision requests and relationship tuples
- policy bundles and promotion/rollback semantics
- proof-bearing decisions and replay-result handling
- control-matrix rows, incident records, and surface-conformance records

## Current status

This package is a seeded standards lane, not a finished final authority. It is intended to make the governed-intelligence layer source-controlled, testable, and reviewable while future work tightens schema coverage, semantic invariants, control ownership, and release automation.
