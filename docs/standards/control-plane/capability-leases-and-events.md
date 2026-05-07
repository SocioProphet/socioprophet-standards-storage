# Capability Leases and Control-Plane Events

This note introduces the first additive control-plane contract tranche for the Matrix / MCP / A2A / broker-governed control surface.

## Purpose

The goal of this tranche is to define portable, reviewable contract surfaces for:

- short-lived capability leases
- lease lifecycle events
- Matrix room-pivot records
- moderation decision records

These contracts are implementation-neutral. They are intended to be consumed by runtime repos and broker/enforcement repos without making this standards repository the runtime owner.

## Ownership split

- normative operating posture: `prophet-platform-standards`
- contract and schema layer: `socioprophet-standards-storage`
- broker / registry / enforcement implementation: `mcp-a2a-zero-trust`
- runtime and deployment topology: `prophet-platform`
- workspace/controller placement and ownership: `sociosphere`

## Included schemas in this tranche

- `schemas/control-plane/capability-lease.schema.json`
- `schemas/control-plane/lease-issued.avsc`
- `schemas/control-plane/matrix-room-pivot.avsc`
- `schemas/control-plane/moderation-decision.avsc`

## Non-goals

This tranche does not define:

- transport protocol behavior
- Keycloak or IdP configuration
- Matrix deployment layout
- runtime service implementation
- broker execution semantics

Those concerns belong in the owning runtime and standards repositories.
