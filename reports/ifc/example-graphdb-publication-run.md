# IFC Example GraphDB Semantic Publication Run Report

## Purpose
Provide a concrete evidence artifact referenced by an executed-result style example for the GraphDB semantic publication layer.

## Fixture
- Fixture ID: `ifc-fixture-obligation-propagation-001`
- Category: obligation propagation

## Target
- Backend: `graphdb_semantic_publication`
- Type: backend
- Version: `provisional-example`

## Evaluated change
A statement-oriented publication export derived governed claim material into a semantic publication view.

## Reviewed artifacts
- `schemas/ifc/examples/backend-profile.graphdb.example.json`
- `docs/benchmarks/certifications/graphdb-semantic-publication-provisional.md`
- `benchmarks/workloads/ifc/fixtures/obligation-propagation.fixture.yaml`

## Result
- Status: `review_required`
- Reason: publication is acceptable only when propagated obligations remain attached and contradiction visibility is not weakened.
- Review-gated concerns remain:
  - higher-order to statement-shaped reduction
  - weakening of propagated obligations
  - contradiction visibility suppression

## Notes
This report is an example evidence artifact only. It demonstrates the shape of a semantic-publication evidence attachment, not a final production certification run.
