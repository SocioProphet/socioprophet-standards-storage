# IFC Example Relational Ledger Canonical Truth Run Report

## Purpose
Provide a concrete evidence artifact referenced by an executed-result style example for the relational IFC ledger as the canonical truth layer.

## Fixture
- Fixture ID: `ifc-fixture-contradiction-visibility-001`
- Category: contradiction visibility

## Target
- Backend: `relational_ifc_ledger`
- Type: backend
- Version: `provisional-example`

## Evaluated change
A contradiction-aware canonical query was evaluated over competing validated claims stored in the relational IFC ledger.

## Reviewed artifacts
- `schemas/ifc/examples/backend-profile.relational-ledger.example.json`
- `docs/benchmarks/certifications/relational-ledger-canonical-truth-provisional.md`
- `benchmarks/workloads/ifc/fixtures/contradiction-visibility.fixture.yaml`

## Result
- Status: `pass`
- Reason: the canonical ledger preserved contradiction visibility and grouped competing validated claims without flattening them into a single truth answer.
- No downgrade or obligation weakening was involved in this run.

## Notes
This report is an example evidence artifact only. It demonstrates the shape of a canonical-truth evidence attachment, not a final production certification run.
