# IFC Example Projection Downgrade Run Report

## Purpose
Provide a concrete evidence artifact referenced by the executed-result style example for IFC projection downgrade handling.

## Fixture
- Fixture ID: `ifc-fixture-projection-downgrade-001`
- Category: projection downgrade

## Target
- Backend: `neo4j_reified_lpg_serving`
- Type: backend
- Version: `5.x-example`

## Evaluated change
A serving export path moved from an incidence-preserving / reified representation to a dyadic projection for a bounded retrieval workflow.

## Reviewed artifacts
- `schemas/ifc/examples/backend-profile.neo4j.example.json`
- `schemas/ifc/examples/loss-certificate.example.json`
- `benchmarks/workloads/ifc/fixtures/projection-downgrade.fixture.yaml`

## Result
- Status: `review_required`
- Reason: the downgrade is acceptable only for bounded task classes such as retrieval and exploration.
- Explicitly forbidden uses remain:
  - policy reasoning
  - provenance audit
  - identity resolution

## Notes
This report is an example evidence artifact only. It demonstrates the shape of an executed-result attachment, not a final production certification run.
