# 134 — IFC Theoretical Foundations

## Purpose
Record the original theoretical basis for the Incidence Fabric Contract (IFC) so that the standards framework remains anchored to its semantic rationale rather than only to implementation artifacts.

## Core claim
IFC is based on the claim that the correct semantic nucleus for our graph/fabric work is not the ordinary property graph and not the ordinary set-style hypergraph, but a richer **incidence-first** structure.

The decisive reason is that many operationally important facts live at the level of **participation**:
- role,
- order,
- multiplicity,
- provenance scope,
- policy scope,
- contradiction visibility,
- obligation propagation.

If participation is not first-class, these semantics are either lost or awkwardly smeared onto the wrong objects.

## The original distinction
The initial theory separated four different operations that are often wrongly conflated:

1. **Incidence-preserving lowering**
   - relation-instance identity remains explicit,
   - participation identity remains explicit,
   - higher-order structure is recoverable.

2. **Star expansion / reified lowering**
   - higher-order relations are represented through explicit relation nodes or bipartite structures,
   - often acceptable operationally,
   - still requires explicit preservation of participation payload when role/order/policy/provenance matter.

3. **Dyadic projection**
   - higher-order structure is collapsed into pairwise links,
   - generally lossy,
   - acceptable only for bounded tasks under explicit loss certification.

4. **Embedding compression**
   - graph or hypergraph structure is compressed into vectors for ML tasks,
   - this is not a structural equivalence claim and must never be treated as the normative truth layer.

## Why property graphs and hypergraphs were both insufficient alone
### Property graph limitation
A property graph is operationally strong but natively binary. Higher-order semantics must be reified or projected into it.

### Set-style hypergraph limitation
A set-style hypergraph captures higher-order membership directly, but without incidence-first structure it still under-models participation-specific semantics.

### IFC move
IFC therefore takes the stronger view:
- entities are first-class,
- relation instances are first-class,
- incidences / participations are first-class when semantics require them,
- compiled views are allowed, but only with explicit recoverability and governance posture.

## Why this matters for governance
The theory was never only about expressiveness. It matters because governance failures often occur exactly at the boundary where rich semantics are projected into lower-order views.

That is why IFC requires:
- projection taxonomy,
- loss certificates,
- contradiction-aware query posture,
- delegation and obligation controls,
- backend capability profiles,
- conformance fixtures.

These are not bolt-ons. They are the operational consequence of the original theory.

## Working interpretation for standards work
The standards repo should therefore treat IFC as:
1. a semantic contract grounded in incidence-first structure,
2. a governance contract controlling projection and use,
3. a conformance contract that tests whether adapters and backends preserve the intended posture.

## Relationship to the current repo surfaces
- Standard 132 states the IFC contract.
- Standard 133 states backend capability profile requirements.
- The `schemas/ifc/` directory states machine-readable governance and projection surfaces.
- The `benchmarks/workloads/ifc/` directory states how conformance and certification will be tested.

## Follow-on work
This note should eventually be linked from the root graph-layer and governance indexes so the original theory remains visible to implementers and reviewers.
