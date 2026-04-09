# 133 — IFC Backend Capability Profiles v0.1

## Status
Draft standard.

## Purpose
Define the machine-readable backend capability profile required for any storage, serving, publication, or analytical substrate that claims conformance with the Incidence Fabric Contract (IFC).

This standard exists so that backend suitability, loss posture, and safe-use boundaries can be declared explicitly instead of being implied by product marketing or adapter code.

## Required profile dimensions
Every IFC backend profile MUST declare at least the following dimensions:

### Identity and relation support
- entity identity support
- relation-instance identity support
- incidence / participation identity support
- identity merge / split support class

### Structural support
- native higher-order support
- native binary / LPG support
- named role support
- ordering support
- multiplicity support
- incidence-property support
- relation-property support
- entity-property support

### Semantic support
- contradiction-aware storage support
- lifecycle-state support
- scenario / world support
- provenance support
- policy support
- obligation propagation support
- delegation-boundary support
- native reasoning support

### Operational support
- transactions / consistency posture
- version / branch / merge posture
- query model(s)
- projection risks
- recommended projection kind
- recoverability claims
- best role in stack

## Required top-level fields
A compliant backend profile SHOULD include fields equivalent to:

- `backend_name`
- `backend_family`
- `substrate_class`
- `closest_semantic_fit_to_ifc`
- `best_role_in_stack`
- `query_models`
- `native_higher_order_support`
- `native_reasoning_support`
- `best_projection_kind`
- `projection_risk`
- `recoverability_notes`
- `supports`
- `forbids`
- `review_required_for`
- `safe_task_classes`
- `unsafe_task_classes`

## Substrate classes
Recommended `substrate_class` values include:

- `operational_lpg`
- `semantic_graph`
- `embedded_analytical_graph`
- `higher_order_reasoning`
- `graph_overlay`
- `versioned_knowledge_store`
- `analytical_projection_engine`
- `multimodel_document_graph`

## Semantics of fit
`closest_semantic_fit_to_ifc` MUST NOT be interpreted as a raw product score. It is a declaration of how closely the backend’s native model aligns with IFC’s incidence-first, governance-aware posture.

Recommended values:
- `high`
- `medium`
- `low`

A backend with strong operational value but low semantic fit MAY still be a preferred serving target if the projection kind and loss modes are explicit.

## Safe-use requirement
Every backend profile MUST declare:
- the task classes for which it is considered safe,
- the task classes for which it is considered unsafe or review-required,
- the projection kinds under which those claims hold.

## Governance requirement
No backend may be called `lossless` in an IFC workflow without:
- a backend capability profile,
- an applicable projection declaration,
- no contradictory loss modes for the relevant task class.

## Initial reference intent
This standard is designed to support initial certification of:
- reified-LPG serving layers,
- semantic publication / governance layers,
- embedded local graph runtimes,
- typed reasoning substrates,
- graph-over-existing-data overlays.

## Follow-on work
This standard should be accompanied by:
1. backend profile schema examples,
2. per-backend certification notes,
3. adapter-specific conformance results,
4. loss-certificate compatibility checks.
