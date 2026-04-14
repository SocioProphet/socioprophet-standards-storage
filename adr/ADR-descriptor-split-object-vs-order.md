# ADR: Split descriptor contracts into object and order forms

- Status: Proposed
- Date: 2026-04-05
- Decision owners: SocioProphet standards and platform stewards

## Context

The platform now spans knowledge objects, reusable assets, policy-governed publication, Matrix ChatOps workflows, and governed execution through agentplane.

The current repo boundaries already imply different responsibilities:
- `socioprophet-standards-storage` owns normative contracts and storage standards.
- `socioprophet-standards-knowledge` owns knowledge semantics and validation gates.
- `TriTRPC` owns deterministic typed transport.
- `agentplane` owns execution control, run evidence, and replay.

A single universal descriptor would blur object semantics and action lifecycle, increase coupling, and make execution contracts harder to reason about.

## Decision

We split descriptors into two first-class contracts:

1. `GeneralDescriptor`
   - describes a reusable or governed object
   - carries identity, source, relationships, policy bindings, provenance, stewardship, and human-facing projections

2. `OrderDescriptor`
   - describes governed work requested against one or more objects
   - carries action, targets, lifecycle, validation gates, policy pack refs, and output artifact expectations

## Consequences

### Positive
- preserves a clean separation between object semantics and governed work
- allows agentplane to stay focused on execution rather than knowledge catalog semantics
- allows the commons runtime to manage knowledge assets without becoming a second execution plane
- gives TriTRPC a stable typed surface for both object registration and governed work

### Negative
- introduces one more explicit contract family to maintain
- requires bridge mappings from orders to execution bundles where governed execution is needed

## Non-goals
- replacing agentplane bundle or evidence schemas
- collapsing PARA into the canonical ontology
- putting imperative executor logic into knowledge object descriptors

## Follow-on work
- publish `general-descriptor.v0.1.json`
- publish `order-descriptor.v0.1.json`
- publish initial event contracts
- define bridge rules from `OrderDescriptor` to `agentplane Bundle`
