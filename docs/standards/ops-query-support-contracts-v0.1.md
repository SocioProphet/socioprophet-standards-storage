# Ops, Query, and Support Contract Standard v0.1

## Status
Draft v0.1

## Purpose

This standard defines the contract layer for governed query, support, premium-support, and operations-domain intelligence across the SocioProphet platform.

It is downstream of semantic authority in `ontogenesis` and upstream of runtime implementations in `sherlock-search`, `global-devsecops-intelligence`, `memory-mesh`, `prophet-platform`, and `agentplane`.

This document standardizes:

- transport and envelope expectations
- minimum typed payload shapes
- cross-context portability requirements
- storage/profile expectations for query, support, and ops-domain records
- evidence and provenance requirements

## Authority boundaries

### Owned here

- base transport invariants
- envelope structure
- schema/profile guidance
- interface expectations for typed RPC and event topics
- storage portability guidance
- measurement-oriented retention/profile expectations

### Not owned here

- semantic meaning of classes and relationships (`ontogenesis`)
- operations-domain specialization (`global-devsecops-intelligence`)
- runtime API hosting (`prophet-platform`)
- bounded execution and replay (`agentplane`)
- long-horizon retained memory semantics (`memory-mesh`)
- curriculum/pedagogy semantics (`alexandrian-academy`)

## Canonical contract families

The following payload families MUST exist in typed form.

### Query contracts

- `QueryRequest`
- `QueryPlan`
- `QueryResultSet`
- `ActionSuggestion`
- `EscalationPacket`

### Support contracts

- `SupportInteraction`
- `SupportComment`
- `SupportRecommendation`
- `SupportOpsContext`
- `ResolutionOutcome`
- `PremiumOverlayRef`

### Ops-domain contracts

- `LogEvent`
- `TelemetryEvent`
- `TicketEvent`
- `ChatOpsEvent`
- `AnomalyFinding`
- `IncidentStory`
- `MeterRecord`
- `OpsRecommendation`
- `OpsEvidenceArtifact`

### Memory and learning link contracts

- `MemoryRecordRef`
- `LearningObjectiveRef`
- `CurriculumObjectRef`
- `ObservationEvent`
- `ImprovementProposal`

## Required formats

### Event contracts

Event contracts SHOULD be modeled in Avro for asynchronous flows.

### Analytic payloads

High-volume meter, anomaly, and operational measurement outputs SHOULD support Arrow and Parquet representations.

### Semantic overlays

JSON-LD SHOULD be used when semantic provenance or ontology-aligned exchange is needed.

### Service interfaces

TritRPC SHOULD be the typed service interface default for query, support orchestration, and operational intelligence lookup.

## Envelope requirements

Every contract family MUST support an envelope containing at minimum:

- `message_id`
- `schema_ref`
- `semantic_class_ref`
- `producer_ref`
- `produced_at`
- `policy_tags`
- `provenance_refs`
- `trace_ref`
- `support_tier` when support semantics apply

No runtime may discard envelope provenance when translating between transports.

## Storage context guidance

### System-of-record

Relational system-of-record persistence SHOULD be available for:

- support interactions
- promotion decisions
- escalation records
- contract registration

### Search and retrieval

Search-oriented indexing SHOULD support:

- textual lookup
- citation and evidence lookup
- support history retrieval
- incident-story retrieval
- recommendation lookup

### Graph / semantic context

Graph or semantic overlays SHOULD support:

- relationship traversal between support, assets, incidents, and evidence
- premium-overlay inheritance
- ontology-aligned discovery

### Measurement context

Analytic stores SHOULD support:

- meter time series
- anomaly scoring history
- recommendation acceptance/rejection trends
- time-to-resolution and support-load metrics
- asset reuse and runbook effectiveness metrics

## Minimum payload fields

### QueryRequest

MUST include:

- query identifier
- requesting principal or service
- requested support tier
- query text or structured query body
- allowed planes/sources
- policy bundle refs
- time scope when applicable

### QueryResultSet

MUST include:

- result set identifier
- linked query identifier
- typed result items
- citations or evidence handles
- policy flags
- confidence summary

### SupportInteraction
n
MUST include:

- interaction identifier
- support tier
- resolved or requested domain/category
- principal/customer/tenant reference where applicable
- linked assets or result refs
- outcome state

### AnomalyFinding

MUST include:

- anomaly identifier
- scope / service or incident binding
- confidence and severity
- detection rationale
- evidence references
- produced timestamp

### MeterRecord

MUST include:

- meter identifier
- measured target ref
- metric name
- metric value
- unit when applicable
- time window
- provenance/tracing handle

## Evidence and explainability requirements

1. Support recommendations MUST be explainable and traceable.
2. Ops recommendations MUST link to evidence handles or incident stories.
3. Premium-support results MUST preserve policy flags and overlay provenance.
4. Query results MUST preserve the distinction between raw source, normalized ops-domain object, memory context, and recommendation layer.

## Compatibility rule

Any implementation repo claiming compliance with this standard MUST include a README section or doc reference that states:

- which contract families are implemented
- which transports are supported
- which storage contexts are used
- whether support-tier semantics and provenance envelopes are preserved end-to-end

## Immediate implementation targets

- `sherlock-search`
- `global-devsecops-intelligence`
- `memory-mesh`
- `prophet-platform`
- `agentplane`

## Future follow-on

A follow-on version SHOULD add concrete schema files under `schemas/` for the above payloads once the ontology tranche and repo-native runtime surfaces stabilize.
