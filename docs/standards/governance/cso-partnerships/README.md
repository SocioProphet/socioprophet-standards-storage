# Governed CSO Partnership Pack

This subtree adds a governed civil-society partnership execution pack to the standards repository.

## Fit within this repository
This package belongs here because the repository already carries standards, contracts, measurement, governance, and interoperability guidance. The CSO pack adds governance and execution controls for partnership selection, instrument choice, safeguarding, data handling, incident escalation, and evidence-pack discipline.

## Layout
- `framework.md` - operating standard
- `field-sheet.md` - compact operator sheet
- `templates/` - operator-facing markdown forms
- `services-kit/` - customer and service-delivery operating kit derived from the canonical governed CSO standard
- `../../../schemas/governance/cso-partnerships/` - machine-readable record schemas
- `../../../examples/governance/cso-partnerships/` - example records

## Run it
- `make cso-governance-validate` - run positive schema checks plus negative and markdown-hygiene checks.
- `make cso-governance-scaffold CSO_GOVERNANCE_OUTPUT=build/cso-governance-demo` - generate a starter pack with copied templates, starter records, and local placeholder files.
- `../../../examples/governance/cso-partnerships/golden-example/` - checked-in golden example of the scaffolded structure.

## Notes
These materials are implementation aids and source-controlled working documents. They do not substitute for binding policy, local legal review, or any formal approval flow.
