# ADR: Canonical home for the Agentic Control Matrix and control bundles

- Status: Accepted (seed decision)
- Date: 2026-04-05
- Owners: SocioProphet standards + agentplane maintainers

## Context

The Agentic Control Matrix has grown beyond a worksheet. It now defines:

- control-cell ontology
- inheritance rules
- reachability model
- risk and review semantics
- exceptions/incidents/change-log linkage
- compiled policy, monitor, and test bundles
- a reference compiler surface

The current v3 seed package contains:

- 187 reachable rows
- 16 denied-by-construction rows
- 1177 generated tests
- 686 generated monitors
- 8 exceptions
- 12 incidents

This control package spans standards, runtime enforcement, transport implications, and deployment.

## Decision

The **canonical normative home** for the Agentic Control Matrix is the SocioProphet standards lane.

For the current repository topology, the canonical seed package lives in:

- `SocioProphet/socioprophet-standards-storage`

Runtime consumers MUST treat the standards lane as the source of truth and import a released bundle/manifest rather than redefine the ontology locally.

## Repository responsibilities

### Canonical standards home: `socioprophet-standards-storage`

This repository owns:

- control-cell ontology and schema
- inheritance order and reachability semantics
- versioned manifests and example bundles
- ADRs and benchmark / conformance expectations
- reference compiler contract

### Runtime consumer: `agentplane`

`agentplane` consumes released control bundles and binds them to:

- policy enforcement
- monitor generation / ingestion
- generated test harnesses
- evidence emission and reconciliation

`agentplane` is **not** the canonical standards home.

### Transport implications: `TriTRPC`

`TriTRPC` owns only the transport-level consequences of this package, such as:

- control events
- evidence envelopes
- typed runtime messages
- fixture implications for wire compatibility

### Deployment / pinning: `prophet-platform`

`prophet-platform` pins and deploys released bundle versions into real platform lanes.

### Knowledge / distribution: `socioprophet`, docs surfaces

Umbrella inventory, RACI, operator docs, and academy material should point at the released standards package and the consuming runtime lane.

## Consequences

### Positive

- one canonical home for governance semantics
- avoids standards drift across runtime repos
- allows runtime repos to remain thin consumers
- preserves durable organizational memory in a standards package
- supports later extraction into a dedicated control-standards repository if the object model keeps growing

### Negative / tradeoffs

- requires explicit release discipline between standards and runtime lanes
- import/pinning metadata must be maintained in consumer repos
- some artifacts will exist in both places: canonical source vs imported runtime bundle

## Follow-on work

1. Keep schemas and example bundles versioned in the standards repo.
2. Import the released bundle manifest into `agentplane`.
3. Add runtime adapters in `agentplane` for policy / monitor / test consumption.
4. Later, if the control package outgrows the current standards repository, promote it into a dedicated `socioprophet-standards-control` repository without changing the architectural split.

## Status note

This ADR seeds the canonical-home decision. It does **not** yet imply that the reference package is bound to a live topology or active policy engine.
