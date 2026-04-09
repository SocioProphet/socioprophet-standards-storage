# IFC Index

## Purpose
Provide one in-repo entry point for the Incidence Fabric Contract (IFC) standards, schemas, fixtures, and certification artifacts.

## Standards
- `docs/standards/132-incidence-fabric-contract.md`
- `docs/standards/133-ifc-backend-capability-profiles.md`
- `docs/standards/134-ifc-theoretical-foundations.md`
- `docs/standards/governance/agentplane-ifc-governance.md`

## Schemas and examples
Located under `schemas/ifc/` and `schemas/ifc/examples/`.

Current schema families include:
- loss certificate
- query IR
- backend capability profile
- authorization grammar
- merge conflict
- contradiction and competing-claim
- delegation and obligation
- fixture result

## Conformance fixtures
Located under `benchmarks/workloads/ifc/fixtures/`.

Current fixture families include:
- projection downgrade
- contradiction visibility
- obligation propagation

## Certification artifacts
Located under `docs/benchmarks/certifications/` and `benchmarks/workloads/ifc/results/`.

Current artifacts include:
- certification template
- reference-stack provisional certification note
- Neo4j operational serving provisional certification note
- GraphDB semantic publication provisional certification note
- reference-stack provisional result
- Neo4j provisional result
- GraphDB provisional result

## Reading order
Suggested reading order for implementers and reviewers:
1. `132-incidence-fabric-contract.md`
2. `134-ifc-theoretical-foundations.md`
3. `133-ifc-backend-capability-profiles.md`
4. `docs/standards/governance/agentplane-ifc-governance.md`
5. `schemas/ifc/`
6. `benchmarks/workloads/ifc/fixtures/`
7. `docs/benchmarks/certifications/`
8. `benchmarks/workloads/ifc/results/`

## Status
This is an index note only. As IFC artifacts evolve, this file SHOULD be kept current so the repo remains navigable.
