# Semantic Control Plane (SCP) — Specification v0.1

## Status

Bootstrap spec pack. This is a standards-side contract landing that defines the minimum stable semantics required for a provenance + evidence control plane.

## Purpose

SCP defines a canonical data model and rulepack for connecting:

- intent (policies, documentation claims, feature constraints)
- implementation (artifacts, versions, optional OO traceability hooks)
- operations (deployments, observations, incidents)

The goal is mechanical auditability: every claim about compliance, quality, release readiness, or incident causality must be expressible as a traversal over typed objects with time semantics and evidence references.

## Non-goals

- SCP does not store customer payload data.
- Documentation is treated as claim-bearing evidence, not ground truth.
- Telemetry completeness is not assumed; sampling and missingness must be represented.

## Canonical design commitments

- Append-only event ledger (EventEnvelope) is the source of truth.
- Entities are projections; queries must support time-travel (as-of).
- Evidence objects are typed, reference concrete artifacts/observations/events, and support integrity metadata.
- Project-specific configuration/documentation are preserved as artifacts; normalized facts/claims are extracted with explicit provenance.

## Directory layout

- `schemas/scp/0.1.0/` — machine schemas (JSON Schema 2020-12)
- `rules/scp/0.1.0/` — OPA/Rego rule packs + tests
- `docs/specs/scp/v0.1/` — narrative spec, state machines, API skeletons, examples

## Validation expectations

The spec pack is designed to be validated in CI:

- JSON Schema validity checks for all `schemas/scp/0.1.0/*.json`
- `opa test` against `rules/scp/0.1.0/` to prevent rule regressions

## Versioning

- Schemas and rules are versioned by directory and by `$id`.
- Breaking changes require a new minor line (e.g., 0.2.0) and explicit migration notes.

## References (normative where applicable)

- Canonical JSON hashing: RFC 8785 (JCS)
- Policy language: OPA/Rego
- Telemetry transport: OTLP
- Attestations: in-toto Attestation Framework
- Signing/transparency pattern: Sigstore Cosign
- SBOM formats: CycloneDX, SPDX
