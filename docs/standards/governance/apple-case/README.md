# Apple Case — Lessons Learned

This document records the system-hardening lessons drawn from the Apple-case investigation. The evidence pack, schemas, fixtures, and rollup helpers developed during that work belong in the **shining-apple** repository. What belongs here are the generalised standards and control-surface improvements that should propagate across the broader system.

## Lessons learned

### 1. Distribution-friction measurement belongs in governance standards

The Apple-case work revealed that distribution-run capture and friction scoring lack a shared schema anchor. Any future investigation of a similar kind should begin with a governed schema and a deterministic rollup spec, not an ad hoc accumulation of artefacts.

**Hardening action:** Add a `distribution-measurement` schema stub to `schemas/governance/` once a second case confirms the pattern is stable.

### 2. Privacy-control evidence needs a reproducibility gate

During the Apple-case work, a publication-grade finding could not be issued without a reproducibility rating. That gate was improvised rather than codified. The `claim_grade` and `reproducibility` fields need to be part of a documented claim-graduation policy.

**Hardening action:** Extend `docs/standards/governance/` with a claim-graduation policy document that codifies how evidence moves from raw capture to a publishable finding.

### 3. Deterministic rollup logic must be repo-native before a finding is published

The privacy-summary rollup was implemented in the active working session and validated there. That is a gap: if the rollup logic is not repo-native and CI-verified, findings cannot be independently reproduced.

**Hardening action:** Any summary-grade rollup used to support a finding must live under `scripts/` and be covered by a CI fixture test before the finding is published.

### 4. Schema, fixture, and validator surfaces must be co-located

The Apple-case work produced schemas, valid/invalid fixtures, and a validator as separate artefacts in separate locations. Co-location and cross-referencing in a single repository layout reduces interpretation drift.

**Hardening action:** Follow the layout established for `cso-partnerships/` (schema in `schemas/governance/`, fixtures in `examples/governance/`, docs in `docs/standards/governance/`) for all future investigation packs.

### 5. Rollup executor and summary schema must be versioned together

A privacy-summary schema change that is not paired with a matching rollup-executor change produces silent inconsistency. The two must be versioned as a unit.

**Hardening action:** Add a `CHANGELOG` convention for co-versioned schema+executor pairs in `docs/standards/`.

## Status

- Lessons recorded.
- Evidence pack and full artifact set live in the **shining-apple** repository.
- Hardening actions above are candidates for follow-on standards work in this repository.
