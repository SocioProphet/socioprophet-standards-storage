# Triune Agent Mesh Framework

Status: initial integrated landing document

This repository is the normative prose and registry home for the Triune Agent Mesh framework spanning:
- agent lifecycle and governance
- phase-gated operations across CLOSED, GUARDED, OPEN
- Jinja messaging, sealing, storage, rollback, backup
- learning, inheritance, federation, HPO, distillation
- vector-space contracts, telemetry feature ontology, non-private telemetry fabric
- distributional semantics packs, semantic tombstones, drift and method-of-moments checks
- cohort tracking, experience geometry, fractal and fracture analysis
- template architecture packs for translation, transformer LLMs, and RL

## Canonical repo split

The framework is intentionally split across orgs and repos:

- `SocioProphet/socioprophet-standards-storage`
  - normative prose, ADR-style standards, registries, rollout guidance
- `SocioProphet/socioprophet-standards-knowledge`
  - machine-readable schema inventory: Avro, JSON Schema, JSON-LD
- `SocioProphet/ontogenesis`
  - ontology classes, semantic relations, typed capability and lifecycle graph
- `SourceOS-Linux/sourceos-spec`
  - implementation-facing typed contracts: OpenAPI, AsyncAPI, JSON Schemas, ADR integration notes
- `SocioProphet/sociosphere`
  - runtime/controller/workbench/backlog and telemetry integration
- `SociOS-Linux/os`
  - downstream OS/image integration, packaging, and first-boot hooks

## Initial framework modules

1. Agent lifecycle and promotion / demotion / rollback
2. Template-rendered messaging with Jinja + Seal/Unseal + WORM storage
3. Telemetry, metering, privacy-preserving aggregation, and vector encoding
4. Learning manifests, birth records, umbilical plans, and inheritance
5. Distributional semantics packs before purge / destruction
6. Drift suite, MoM checks, periodic sampling, semantic fingerprints
7. Cohort Tracking Fabric and Experience Index
8. Fractal Core Kit and fracture geometry metrics
9. GPT/model profiling, model cards, distillation, adapter deltas, RL/DPO/PPO
10. Template Architecture Pack for translation, LLM small/large, and RL

## Immediate follow-on work

This file is the anchor point for the first integrated commit. Follow-on commits should add:
- detailed standards docs under this subtree
- registry JSON documents for vector spaces, fingerprint methods, and XI weights
- schema references into standards-knowledge
- ontology bindings into ontogenesis
- contract bindings into sourceos-spec
- runtime rollout registration in sociosphere
- OS integration notes in SociOS-Linux/os

## Core invariants

- deterministic, replayable, content-addressed artifacts
- no update without snapshot
- no external egress in CLOSED
- privacy-preserving telemetry only, no user identifiers in shared aggregates
- append-only vector space evolution; no axis reordering
- all promotions governed by measurable gates and evidence trails
