# Apple Case Kit

## Purpose

This kit is the evidence-model surface for the Apple-case work. It is designed to carry the work from raw captures to publication-safe findings without ad hoc interpretation drift.

## Current kit layers

1. **Raw capture schemas**
   - distribution-run
   - interoperability-run
   - privacy-run
   - packet-run
2. **Helper attribution**
   - destination-attribution
3. **Summary rollups**
   - distribution-summary
   - interoperability-summary
   - privacy-summary
4. **Deterministic rollup logic**
   - privacy rollup generator spec
   - local privacy rollup implementation already validated in the active working session
5. **Fixture and validator surface**
   - valid and invalid fixtures for each schema
   - sample privacy and packet inputs
   - schema validator

## Why this belongs in this repository

This repository already defines standards, governance packages, machine-readable contracts, validation helpers, and benchmark surfaces. The Apple-case work is the same kind of object: a standards-and-evidence pack rather than an app feature.

## Execution plan

### Phase 1 — anchor and fit
- create the repo path
- record why the work belongs here
- pin the intended layout
- open a PR so follow-on work has a stable landing zone

### Phase 2 — promote the kit
- promote schemas into `schemas/governance/apple-case/`
- promote fixtures into `examples/governance/apple-case/`
- promote validator and rollup helpers into `scripts/`
- add CI validation for fixtures and deterministic rollups

### Phase 3 — extend the execution model
- implement distribution-summary rollup
- implement interoperability-summary rollup
- unify all three lanes under one deterministic summary pattern

## Intended repository layout

- `docs/standards/governance/apple-case/` — operator notes, kit notes, rollup spec
- `schemas/governance/apple-case/` — JSON Schemas for capture, attribution, and summary objects
- `examples/governance/apple-case/` — valid and invalid fixtures plus generated examples
- `scripts/` — validator and deterministic rollup helpers

## Current local artifacts already prepared

- schema bundle
- fixture and validator pack
- generated privacy summary example
- staging PR and branch in this repository

## Immediate next promotion order

1. schemas
2. fixtures
3. validator and rollup helpers
4. CI workflow
5. distribution and interoperability rollup executables
