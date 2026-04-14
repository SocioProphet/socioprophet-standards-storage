# Contract Intelligence Interface Standard

## Purpose

This document defines the **cross-repository normative interface standard** for contract intelligence flows in the SocioProphet stack.

It exists to ensure that:

- contract and regulatory document ingestion is interoperable across services,
- routing and extraction behavior are replayable and benchmarkable,
- query and command responsibilities are separated cleanly,
- domain-specific contract intelligence work can be specialized in product/domain repos without fragmenting the platform-wide interface surface.

This document is intentionally **transport-neutral at the normative layer**.
Typed language bindings and service-specific protobuf definitions may be published separately in shared typed-contract repositories, but MUST conform to the requirements in this standard.

---

## Scope

This standard applies to services and pipelines that perform one or more of the following:

- ingest contract, policy, or regulatory documents,
- resolve processing profile by language / jurisdiction / domain / subdomain,
- parse structural document boundaries,
- extract contractual semantics,
- emit explanation, feedback, or adjudication artifacts,
- benchmark or promote model packs / pattern packs used in contract intelligence.

This standard does **not** define contract-domain product canon such as contractual economics, settlement lifecycle, or amendment policy. Those remain product/domain concerns.

---

## Canonical interaction model

Contract intelligence MUST follow a CQRS-like separation.

### Query plane

The query plane is the stable retrieval surface for versioned artifacts.
It MUST support retrieval by artifact identity, time window, and profile dimensions where applicable.

### Command plane

The command plane is the owning-service mutation surface.
It MUST accept mutation requests, apply idempotency semantics where possible, emit change events, and make resulting artifacts available to the query plane.

### Event plane

The event plane is the authoritative asynchronous change log for accepted mutations and downstream derivations.

---

## Required canonical artifacts

### 1. DocumentArtifact

Represents the canonicalized form of an ingested source document.

Required fields:

- `artifact_id`
- `artifact_type`
- `version`
- `tenant_id`
- `story_id` when applicable
- `source_ref`
- `content_hash`
- `mime_type`
- `canonical_text`
- `normalization_log[]`
- `created_at`

Recommended fields:

- `layout_refs`
- `section_spans`
- `paragraph_spans`
- `sentence_spans`
- `language_hint`
- `jurisdiction_hint`

### 2. ProfileResolution

Represents the routing decision used to select the applicable schema, pattern, and model packs.

Required fields:

- `document_id`
- `language`
- `jurisdiction`
- `domain`
- `subdomain`
- `confidence`
- `selected_schema_pack`
- `selected_pattern_pack`
- `selected_model_pack`

Recommended fields:

- `region`
- `resolver_evidence[]`
- `ambiguity_flags[]`

### 3. BenchmarkCase

Represents a golden fixture used for routing, parsing, semantic extraction, replay, or governance evaluation.

Required fields:

- `case_id`
- `document_ref`
- `difficulty`
- `slice_tags[]`

Recommended fields:

- `gold_profile`
- `gold_structure`
- `gold_semantics`
- `notes`

### 4. EvaluationReport

Represents the results of a benchmark or comparison run.

Required fields:

- `run_id`
- `subject_ref`
- `metrics`
- `generated_at`

Recommended fields:

- `slice_metrics`
- `error_buckets`
- `regressions`
- `promotion_recommendation`

### 5. ReviewerFeedback

Represents human adjudication or correction of a previously produced artifact.

Required fields:

- `feedback_id`
- `artifact_ref`
- `reviewer_id`
- `label`
- `timestamp`

Recommended fields:

- `span_refs[]`
- `rationale`
- `supersedes_feedback_id`

---

## Required command operations

The owning contract-intelligence service MUST define operations equivalent to the following logical commands:

- `IngestDocument`
- `ResolveProfile`
- `ParseStructure`
- `ExtractSemantics`
- `ApplyReviewerFeedback`
- `RecomputeExtraction`

Optional but recommended operations:

- `PromotePatternPack`
- `PromoteModelPack`
- `ReplayRun`

### Command requirements

Commands MUST:

- accept an idempotency key when feasible,
- accept a policy / governance snapshot reference when the environment requires one,
- emit events for accepted mutations,
- preserve sufficient provenance for replay and audit,
- produce outputs that are retrievable via the shared query plane.

---

## Required query capabilities

The shared query plane MUST support retrieval of resulting artifacts without requiring read proxying through every owning service.

Minimum required retrieval patterns:

- retrieve by `(artifact_type, artifact_id, version)`
- retrieve by `story_id`
- retrieve by time window
- retrieve by `tenant_id` where multi-tenant operation exists

Recommended retrieval patterns:

- retrieve by `(language, jurisdiction, domain, subdomain)`
- retrieve by `selected_pattern_pack`
- retrieve by `selected_model_pack`

---

## Event requirements

Every accepted command that changes availability of an artifact MUST emit an event.

Minimum logical event types:

- `document_ingested`
- `profile_resolved`
- `structure_parsed`
- `semantics_extracted`
- `feedback_applied`
- `evaluation_completed`
- `pattern_pack_promoted`
- `model_pack_promoted`

Event payloads MUST:

- identify the subject artifact or run,
- provide event time in UTC,
- provide stable type naming,
- preserve a path to explanation / provenance where applicable.

---

## Evaluation harness alignment

Any compliant implementation SHOULD align to the following harness families:

### Routing harness

Measures correctness of language / jurisdiction / domain / subdomain resolution.

### Structure harness

Measures extraction quality for sections, clauses, definitions, exhibits, schedules, and cross-references.

### Semantic harness

Measures extraction quality for obligations, prohibitions, rights, exceptions, conditions, triggers, and timeframes.

### Ambiguity harness

Measures the system’s ability to surface competing interpretations with evidence rather than collapsing all uncertainty into a single answer.

### Replay and idempotency harness

Measures replay determinism, duplicate command handling, and lineage stability.

### Governance harness

Measures feedback application, promotion gating, and visibility of mutation outputs through the query plane.

---

## Packaging model

This standard distinguishes three layers:

1. **Normative standard layer** — this repository
2. **Typed service binding layer** — shared typed API-contract repositories
3. **Product / domain canon layer** — product/domain repositories such as ContractForge

Implementations MUST NOT collapse these ownership boundaries casually.

---

## Conformance notes

A contract-intelligence implementation conforms to this standard when it:

- produces the required artifact families,
- preserves the command/query/event separation,
- exposes outputs through a shared query plane,
- emits events for accepted mutations,
- supports routing and extraction replay,
- participates in benchmark-driven evaluation.

---

## Initial recommended next artifacts

The following concrete schema documents SHOULD be added after this standard is accepted:

- `document-artifact.schema.json`
- `profile-resolution.schema.json`
- `benchmark-case.schema.json`
- `evaluation-report.schema.json`
- `reviewer-feedback.schema.json`

The following workload definitions SHOULD also be added:

- `contract-intelligence-routing.yaml`
- `contract-intelligence-structure.yaml`
- `contract-intelligence-semantics.yaml`
- `contract-intelligence-ambiguity.yaml`
- `contract-intelligence-replay.yaml`
