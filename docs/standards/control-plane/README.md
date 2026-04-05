# Agentic Control Matrix v3 — canonical seed package

This directory seeds the canonical standards package for the Agentic Control Matrix.

## What this package is

The Agentic Control Matrix is the governance/control constitution for agentic execution across the SocioProphet ecosystem. It defines a control-cell model keyed by state dimensions such as:

- phase
- connector
- authority
- memory class
- objective
- failure mode
- principal
- environment tier
- trust zone
- data class
- resource type
- approval mode
- execution mode
- dependency state
- tenant scope
- concurrency profile
- monitor health

The v3 seed package currently includes:

- 187 reachable rows
- 16 denied rows
- 1177 generated tests
- 686 generated monitors
- 8 exceptions
- 12 incidents

## Canonical ownership

This standards repository owns the **normative** package:

- schemas
- ADRs
- canonical manifest
- example compiled bundles
- reference compiler surface

Runtime repos such as `agentplane` should consume a released bundle from here rather than redefining the ontology locally.

## Package layout

- `schemas/control-matrix/` — schema and compiler contract
- `docs/standards/control-plane/` — explanatory standards docs
- `examples/control-matrix/v3/` — seed manifest and example compiled bundles
- `adr/` — canonical-home and related architecture decisions

## Ecosystem placement

- standards canon: `socioprophet-standards-storage`
- runtime consumer: `agentplane`
- transport implications: `TriTRPC`
- deployment pinning: `prophet-platform`
- docs / academy / inventory: umbrella docs surfaces and `socioprophet`

## Current limits

This is still a reference control package. It is not yet bound to a live topology export or a live policy engine.
