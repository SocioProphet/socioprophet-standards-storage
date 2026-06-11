# Agentic Control Matrix v3 — canonical seed package

This directory seeds the canonical standards package for the Agentic Control Matrix and related control-plane standards.

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
- control-plane security standards

Runtime repos such as `agentplane` should consume a released bundle from here rather than redefining the ontology locally.

## Package layout

- `schemas/control-matrix/` — schema and compiler contract
- `docs/standards/control-plane/` — explanatory standards docs
- `docs/standards/control-plane/vendor-adapter-security/` — vendor-adapter and local-model-gateway security standard package
- `examples/control-matrix/v3/` — seed manifest and example compiled bundles
- `adr/` — canonical-home and related architecture decisions

## Control-plane packages

### Agentic Control Matrix

The Agentic Control Matrix defines the high-dimensional control-cell model for agentic execution and monitoring.

### Vendor Adapter Security

The `vendor-adapter-security` package defines the required hardening controls for vendor adapters, local model gateways, tool-calling inference bridges, and attached administrative/debug surfaces.

Package entry point:

```text
docs/standards/control-plane/vendor-adapter-security/README.md
```

The package includes:

- normative standard
- implementation hardening spec
- local model gateway baseline
- machine-checkable controls checklist
- JSON Schema for the checklist
- verification matrix
- cross-repository adoption map

## Ecosystem placement

- standards canon: `socioprophet-standards-storage`
- runtime consumer: `agentplane`
- transport implications: `TriTRPC`
- deployment pinning: `prophet-platform`
- workspace registry and compliance tracking: `sociosphere`
- SourceOS local/operator consumers: `sourceos-spec`, `sourceos-devtools`
- AgentOS assembly consumer: `agentos-spine`
- docs / academy / inventory: umbrella docs surfaces and `socioprophet`

## Current limits

This is still a reference control package. It is not yet bound to a live topology export or a live policy engine.

The vendor-adapter security package now has verification artifacts and an adoption map, but downstream runtime consumers still need to pin and enforce the controls.
