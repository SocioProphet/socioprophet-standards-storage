# Standards Index

This directory contains normative standards for the SocioProphet platform. Requirements use **MUST/SHOULD/MAY** language to define portable, vendor-neutral expectations.

## Current standards
- `000-platform-standards.md` — versioning, compatibility, and publishing rules.
- `010-storage-contexts.md` — canonical storage contexts and boundaries.
- `020-data-formats.md` — contract formats (Avro, Arrow/Parquet, JSON-LD).
- `030-interfaces.md` — RPC and eventing interface expectations.
- `040-measurement.md` — measurement, benchmarking, and reporting rules.
- `090-fips-governance-activation-rollout.md` — FIPS 140-2/140-3 governance activation and rollout coordination plan (10-step roadmap, phases, KPIs, risk management).

## Authoring guidance
When adding a new standard:
1. Start with a brief rationale.
2. Use unambiguous MUST/SHOULD/MAY statements.
3. Include versioning impact and migration notes.
