# Telemetry Schema Package

This directory contains the initial machine-readable contract surface for the transparent telemetry model.

## Contents
- `event_manifest.schema.json` — contract for event-family manifests
- `receipt.schema.json` — contract for telemetry decision receipts
- `control.schema.json` — contract for user/operator control objects
- `policy_outcome.schema.json` — contract for policy engine decisions

## Intended use
These schemas are the enforcement substrate for:
- `docs/standards/041-transparent-telemetry.md`
- `docs/standards/042-live-telemetry-inspector.md`

## Notes
This is an initial scaffold. Follow-on work should add:
- plane registry schema
n- retention/deletion schema
- example manifests for the reference slice
- CI validation rules and sample fixtures
