# Polycentric Observer-Control Standards

This package captures the canonical **polycentric observer-control model** for the SocioProphet organization.

## Purpose

The goal is to define one normative doctrine for:

- bounded participants as first-class entities
- multi-party interactions as typed envelopes / hyperedges
- scoped state, memory, artifacts, and views
- trust, delegation, information flow, and policy decisions
- consistency, retention, revocation, and replay boundaries
- surface contracts across browser, terminal, IDE, search, DevSecOps, CI/CD, NixOS ops, and the agent plane

## Canonical ownership model

This repository owns the **normative doctrine, invariants, and ADRs**.

Downstream authoritative homes are split by role:

- `SourceOS-Linux/sourceos-spec` — machine-readable schemas, examples, OpenAPI / AsyncAPI / semantic overlays
- `SocioProphet/socioprophet-standards-knowledge` — knowledge-context and ontology companion material
- `SocioProphet/prophet-platform-standards` — operational bindings for DevSecOps, CI/CD, observability, RBAC, and audit
- `SocioProphet/TriTRPC` — transport bindings only
- `SocioProphet/agentplane` — execution/evidence bindings only
- `SocioProphet/prophet-platform` — runtime adoption tracking and standards lock / rollout coordination

## Package contents

- `010-reference-model.md`
- `020-state-lattice.md`
- `030-entity-interaction-view.md`
- `040-trust-flow.md`
- `050-retention-revocation.md`
- `060-consistency-matrix.md`
- `ORG_CAPTURE_PLAN.md`

## Non-goal

This package is **not** the machine-readable schema source of truth. It defines the normative upstream doctrine that downstream contract repositories must implement and reference.
