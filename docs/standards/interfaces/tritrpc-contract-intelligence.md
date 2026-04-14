# TritRPC Contract Intelligence Interface Standard

## Purpose

This document defines the initial **cross-repo interface standard** for contract-intelligence services.

It is the normative interface layer for services that ingest, route, parse, extract, review, benchmark, and promote contract-intelligence artifacts.

This standard is intentionally neutral with respect to any single domain runtime implementation. Contract-domain canon remains in `SocioProphet/contractforge`, while this document defines the shared interface posture used across implementations.

## Scope

This standard covers:

- command-plane service boundaries
- query-plane service boundaries
- evaluation-plane service boundaries
- idempotency and replay requirements
- artifact identity and version expectations
- event-emission expectations
- profile-resolution expectations

This standard does **not** define the full contract-domain schema family itself.

## Naming

The canonical cross-repo family name for this service surface is:

- **family**: `contract_intelligence`
- **protobuf package**: `socioprophet.contract_intelligence.v1`
- **service names**:
  - `ContractIntelligenceService`
  - `ContractIntelligenceQueryService`
  - `ContractIntelligenceEvaluationService`

## Architectural posture

Contract intelligence MUST follow a CQRS-like split.

- **Query plane**: stable retrieval surface for versioned artifacts and benchmark results
- **Command plane**: owning service surface for mutations and re-computation
- **Evaluation plane**: benchmark, comparison, replay, and promotion surface

## Artifact identity invariants

Every contract-intelligence artifact MUST support:

- `artifact_type`
- `artifact_id`
- `version`
- `tenant_id` where applicable
- `story_id` where applicable
- `utc_timestamp`
- stable provenance references

Canonical query interfaces MUST be able to address artifacts by `(artifact_type, artifact_id, version)`.

## Command plane

### Service

`ContractIntelligenceService`

### Required methods

#### `IngestDocument`

Accepts a raw or referenced contract/regulatory document and produces a canonical document artifact.

#### `ResolveProfile`

Resolves the processing profile across:

- language
- jurisdiction / region
- domain
- subdomain
- schema pack
- pattern pack
- model pack

#### `ParseDocument`

Produces structural parsing artifacts from a canonical document artifact.

#### `ExtractClauses`

Produces clause-like structural units and associated typing where applicable.

#### `ExtractObligations`

Produces semantic contractual artifacts such as obligations, prohibitions, rights, exceptions, conditions, and temporal dependencies.

#### `ApplyReviewerFeedback`

Applies human review or adjudication feedback to previously produced artifacts.

#### `RecomputeExtraction`

Re-runs extraction against a specified artifact/version using explicit pack versions.

### Command-plane requirements

- commands SHOULD be idempotent where possible
- accepted commands MUST emit downstream availability/change events
- commands MUST capture pack versions used
- commands MUST support replay with explicit artifact and pack references

## Query plane

### Service

`ContractIntelligenceQueryService`

### Required methods

#### `GetDocumentArtifact`
Retrieve a canonical document artifact by id/version.

#### `GetClauseSet`
Retrieve a clause artifact set by document/version.

#### `GetObligationSet`
Retrieve a semantic extraction set by document/version.

#### `GetInterpretationEvidence`
Retrieve explanation/evidence artifacts associated with a document or semantic artifact.

#### `ListArtifactsByStory`
List artifacts associated with a story or processing lineage.

#### `ListArtifactsByTimeWindow`
List artifacts by time window and artifact family.

#### `ListArtifactsByProfile`
List artifacts filtered by resolved language / jurisdiction / domain / subdomain profile dimensions.

### Query-plane requirements

- query results MUST be version-aware
- query results MUST preserve tenant boundaries where applicable
- query results SHOULD provide stable pagination or cursor semantics
- query results MUST surface artifact lineage when requested

## Evaluation plane

### Service

`ContractIntelligenceEvaluationService`

### Required methods

#### `RunBenchmark`
Execute benchmark suites against specified pattern packs and model packs.

#### `CompareModelVersions`
Compare two or more model pack versions against a benchmark suite.

#### `ComparePatternPackVersions`
Compare two or more pattern pack versions against a benchmark suite.

#### `ApprovePromotion`
Record approval of a pack version for promotion.

#### `ReplayRun`
Replay a prior run with identical inputs and explicit pack versions.

### Evaluation-plane requirements

- benchmark runs MUST record pack versions and dataset references
- replay MUST preserve explicit pack and artifact references
- promotion MUST be separable for pattern packs and model packs

## Event emission

Contract-intelligence services MUST emit typed events for accepted mutations and material artifact availability changes.

Minimum event families SHOULD include:

- document ingested
- profile resolved
- structure parsed
- clauses extracted
- obligations extracted
- reviewer feedback applied
- benchmark completed
- pack promoted

Event payloads MUST carry enough identity to re-query resulting artifacts.

## Profile resolution requirements

Profile resolution is a first-class interface concern.

It MUST NOT be hidden inside opaque extraction code.

A conforming implementation MUST be able to represent and inspect:

- language decision
- jurisdiction / region decision
- domain decision
- subdomain decision
- selected schema pack
- selected pattern pack
- selected model pack
- resolver evidence and confidence

## Replay and determinism

A conforming implementation MUST support replayability over:

- canonical document artifact version
- profile resolution output
- pattern pack version
- model pack version

If exact determinism is not possible, the implementation MUST surface the source of nondeterminism.

## Recommended message families

This standard expects shared transport messages to include at least:

- `DocumentArtifact`
- `ProfileResolution`
- `ClauseSet`
- `ObligationSet`
- `InterpretationEvidence`
- `ReviewerFeedback`
- `BenchmarkCase`
- `EvaluationReport`

## Relationship to adjacent repositories

- `SocioProphet/contractforge` owns the contract-domain canon and schema family
- `SocioProphet/api-contracts` owns protobuf / Buf / Connect transport packages implementing this standard
- domain-specialization repos may publish profile-specific pattern packs and mappings against this standard

## Status

This document defines **v0.1** of the TritRPC contract-intelligence interface standard.