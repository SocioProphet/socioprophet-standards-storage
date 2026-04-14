# Golden Example — Governed CSO Partnership Pack

This directory is a checked-in example of the scaffolded structure produced by `scripts/scaffold_cso_partnership_pack.py`.

## Contents
- `records/partner-profile.json`
- `records/incident-record.json`
- `records/evidence-pack.yaml`
- `local/` placeholder evidence files
- `templates/` copied operator forms

## How to reproduce
Run:

`make cso-governance-scaffold CSO_GOVERNANCE_OUTPUT=build/cso-governance-demo`

Then compare the generated pack with this checked-in example and run `make cso-governance-validate`.
