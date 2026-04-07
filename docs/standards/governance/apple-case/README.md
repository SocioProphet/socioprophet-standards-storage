# Apple Case Evidence Pack (staging note)

This directory anchors the Apple-case evidence-pack work inside the standards repository.

## Why this belongs here

This repository already carries standards, contracts, measurement guidance, governance packs, and validation-oriented scaffolding. The Apple-case work fits that surface because it is not a product feature; it is a standards-and-evidence package for measuring distribution friction, interoperability parity, privacy-control behavior, packet-level corroboration, and summary-grade publication constraints.

## Current model surface prepared outside the repo

The current pack includes these machine-readable objects and supporting specs:

- distribution-run
- distribution-summary
- interoperability-run
- interoperability-summary
- privacy-run
- privacy-summary
- packet-run
- destination-attribution
- privacy rollup generator spec

The current local bundle also includes a fixture pack with valid and invalid examples plus a minimal privacy-summary rollup implementation.

## Intended repository layout

- `schemas/governance/apple-case/` — JSON Schemas for raw runs, helper attribution, and summary objects
- `examples/governance/apple-case/` — valid / invalid example objects and sample rollup inputs
- `scripts/` — validation and deterministic summary generation helpers
- `docs/standards/governance/apple-case/` — operator and standards notes for the evidence model

## Immediate next integration steps

1. Promote the schema bundle into `schemas/governance/apple-case/`.
2. Promote the fixture pack and validator helpers into `examples/governance/apple-case/` and `scripts/`.
3. Add CI validation for schema fixtures and rollup determinism.
4. Add distribution and interoperability rollup implementations so all three evidence lanes share one execution model.

## Status

- Branch anchor created.
- Repo path selected.
- Full schema bundle and fixture pack currently exist in the active working session and are ready to be promoted in follow-on commits.
