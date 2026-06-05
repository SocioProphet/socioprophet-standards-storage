# Cloud Vendor Strategy v1.1

Status: Draft-for-execution
Decision record: EDR-CVSP-2026-06-05-002
Owning issue: #91

## Thesis

Prophet uses one canonical commercial and entitlement spine, projected outward through thin marketplace adapters for AWS, Azure, and Google Cloud. AWS is first activation rail, Azure is enterprise workflow rail, and Google Cloud is data, knowledge, and agent rail.

## Non-negotiable invariants

1. No cloud-specific offer exists without a canonical plan mapping.
2. No entitlement mutation grants access unless the canonical lifecycle state allows it.
3. Paid-but-not-entitled is severity 1.
4. Entitled-but-not-paid is severity 1 after grace policy expires.
5. Marketplace event handling must be idempotent, replay-safe, auditable, and reconcilable.
6. Adapter logic must remain thin; product truth lives in canonical files.
7. Runtime bindings may be cloud-specific, but commercial semantics remain canonical.

## Directory map

- `canonical/planspec.v1.yaml` — plan ladder, entitlements, add-ons.
- `canonical/capabilities.v1.yaml` — stable capability registry.
- `canonical/lifecycle-state-machine.v1.yaml` — vendor-neutral lifecycle.
- `schemas/marketplace.event.v1.schema.json` — normalized marketplace event envelope.
- `adapters/aws/offer-map.stub.yaml` — AWS Marketplace mapping stub.
- `adapters/azure/offer-map.stub.yaml` — Microsoft Marketplace mapping stub.
- `adapters/gcp/offer-map.stub.yaml` — Google Cloud Marketplace mapping stub.
- `conformance/fixtures/` — golden event fixtures for adapter validation.
- `marketplace-readiness-kit/gates.v1.md` — blocking gates for listing readiness.

## Cloud roles

| Cloud | Role | Motion |
|---|---|---|
| AWS | OpenAI timing, enterprise AI procurement, Bedrock, Codex, managed agents | First activation rail |
| Azure | Microsoft enterprise workflow, identity, Teams, GitHub, Foundry | Enterprise workflow rail |
| Google Cloud | Data, knowledge graph, analytics, agent grounding | Data / knowledge / agent rail |

## Promotion rule

This repository stores normative standards and mapping contracts. Runtime implementations belong in platform/runtime repositories only after these standards are frozen and referenced by issue or ADR.
