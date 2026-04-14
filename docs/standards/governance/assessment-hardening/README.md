# Assessment Hardening — Lessons Applied

This document records generalized hardening lessons derived from recent investigation and exploit-analysis work.

It belongs in the public standards repository because it focuses on reusable control-surface improvements rather than case-specific exhibits, theories, or evidentiary artifacts.

## Hardening lessons

### 1. Distribution-friction measurement needs a governed schema anchor

Distribution-run capture and friction scoring should begin with a governed schema and deterministic rollup spec, not an ad hoc pile of artifacts.

**Hardening action:** add a generic distribution-measurement schema stub once a second case confirms the pattern is stable.

### 2. Claim graduation needs an explicit reproducibility gate

Summary-grade findings should not be publishable unless reproducibility and claim-grade rules are codified and machine-checkable.

**Hardening action:** add a claim-graduation policy that defines how evidence moves from raw capture to publishable finding.

### 3. Deterministic rollups must be repo-native before publication

If rollup logic is not checked into the repository and covered by fixture tests, findings are not independently reproducible.

**Hardening action:** require summary-grade rollups to live under `scripts/` and be exercised by CI fixture tests.

### 4. Schemas, fixtures, and validators must be co-located

Keeping the schema, example, and validation surfaces in one repository layout reduces interpretation drift and strengthens auditability.

**Hardening action:** use a co-located layout for all future investigation-derived hardening packs.

### 5. Summary schemas and executors must be versioned together

A summary schema change without a matching executor change creates silent inconsistency.

**Hardening action:** add a co-versioning convention for schema+executor pairs.

## Status

- Generic hardening lessons recorded.
- Case-specific artifacts should remain outside the public standards surface.
- Follow-on standards work should bind these lessons into the generic evidence-native assessment model already emerging across storage, knowledge, and policy layers.
