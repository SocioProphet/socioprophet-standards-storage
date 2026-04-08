# Control matrix repository topology

This document explains how the Agentic Control Matrix should land across the SocioProphet repository ecosystem.

## Principle

Keep the **canon** separate from the **consumer**.

The control matrix is cross-cutting governance. It should not be owned solely by a runtime repo because:

- runtime repos should be able to import and pin released governance bundles
- the standards package needs durable memory independent of one executor/control-plane implementation
- transport, deployment, and docs lanes all consume the same canon in different ways

## Split

### 1. Canonical standards home

Repository: `socioprophet-standards-storage`

Owns the normative objects:

- schema
- ADRs
- manifests
- example bundles
- reference compiler contract

### 2. Runtime consumer

Repository: `agentplane`

Owns the executable integration lane:

- imported bundle manifest
- imported policy / monitor / test bundles
- runtime adapters
- evidence emission and reconciliation logic

### 3. Transport implications

Repository: `TriTRPC`

Owns only on-wire implications of control and evidence events.

### 4. Deployment pinning

Repository: `prophet-platform`

Owns version pinning, rollout wiring, and infra adoption.

### 5. Organizational memory

Repositories / surfaces: umbrella docs, academy material, `socioprophet`

Owns human-readable maps, operator docs, and cross-repo inventory.

## Upgrade path

If the control package becomes large enough, promote it into a dedicated standards-control repository while preserving the same split between canon and consumer.
