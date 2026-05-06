# ADR-030: Commons Data Model and Map Log Canon

## Status

Accepted for v0.1 bootstrap.

## Date

2026-05-06

## Decision

We establish the **Commons Data Model / Commons Data Map / Map Log** canon as the vendor-neutral, non-enterprise semantic spine for shared data, evidence, provenance, knowledge, agent observations, and projection surfaces across the SocioProphet / SourceOS / SociOS estate.

This repository, `SocioProphet/socioprophet-standards-storage`, owns the normative storage/event/map/projection doctrine. It does **not** silently fork the machine-readable contract layer owned by `SourceOS-Linux/sourceos-spec`.

The base runtime envelope in `SourceOS-Linux/sourceos-spec` is already named `EventEnvelope` and is described there as the universal wrapper for AsyncAPI channel messages. Therefore CDM must align with `EventEnvelope` rather than replacing it casually.

The CDM event contract will be expressed as a constrained profile over `EventEnvelope` unless a later cross-repo ADR explicitly promotes a new base envelope. In this ADR, the documentation term **CDM Event** means an `EventEnvelope`-compatible event carrying one of the CDM payload kinds: observation, transition, projection, audit, or dead-letter.

## Context

Earlier working diagrams used enterprise and Watson-shaped vocabulary, including `EDM`, `EDF`, `Enterprise Data Map`, `WKC`, `WKS`, and `WDS`. Those names import assumptions that are incorrect for the platform we are building. The target system is not only for enterprise users. It must serve personal, civic, research, commons, agentic, field, organizational, and platform contexts with one coherent semantic spine.

The estate already contains partial substrates:

- `socioprophet-standards-storage` defines storage contexts, event stream posture, graph/search/vector/storage standards, benchmark methodology, and shared storage contracts.
- `SourceOS-Linux/sourceos-spec` defines machine-readable JSON Schema, OpenAPI, AsyncAPI, JSON-LD / Hydra overlays, examples, and an existing `EventEnvelope` schema.
- `SocioProphet/ontogenesis` owns RDF/OWL/JSON-LD ontology modules, SHACL gates, module registry, ledgers, release validation, and semantic promotion governance.
- `SocioProphet/socioprophet-standards-knowledge` owns knowledge atoms such as Note, Claim, Annotation, MeriotopographicEdge, ProvenanceRecord, semantic overlays, Avro payloads, fixtures, and round-trip verification.
- `SocioProphet/socioprophet-agent-standards` owns agent-facing normative profiles, conformance, evidence, replay, control, gating, and compatibility overlays.
- `SocioProphet/prophet-platform-standards` owns DevSecOps, CI/CD, GitOps, RBAC/audit, OTEL, and enforcement templates.

The missing piece is the cross-repo CDM canon that states which repo owns which layer and how the shared semantics propagate without duplication.

## Canonical vocabulary

The canonical vocabulary is:

- **Commons Data Model (CDM-Model):** structural and semantic model for Data Objects, Facets, Relationships, Provenance, Policy Hooks, Evidence References, Time, and Identity.
- **Commons Data Map (CDM-Map):** current assembled state derived from accepted transition events.
- **Map Log (CDM-Log):** append-only ordered transition stream from which the CDM-Map and projections can be rebuilt.
- **Data Object:** addressable thing represented in the map, including files, datasets, records, people, agents, devices, concepts, policies, runs, claims, annotations, services, artifacts, or external resources.
- **Facet:** typed attribute bundle attached to a Data Object.
- **Relationship:** typed link between Data Objects.
- **CDM Event:** `EventEnvelope`-compatible message whose payload is a CDM observation, transition, projection, audit, or dead-letter payload.
- **Observation Payload:** idempotent assertion of observed objects, facets, relationships, evidence references, and provenance.
- **Transition Payload:** ordered mutation applied to the map log.
- **Projection Payload:** event describing the creation/update/rebuild of a derived read model such as search, graph, catalog, vector, or materialized view.

## Banned or deprecated vocabulary

The following terms MUST NOT be used for new canonical schema names, API names, normative labels, or diagrams:

- `EDM`
- `EDF`
- `Enterprise Data Map`
- `Enterprise Data Model`
- `Enterprise Data Frame`
- `WKC`
- `WKS`
- `WDS`
- `Watson`

The word `enterprise` MAY appear in historical migration notes, external citations, or market-context prose, but MUST NOT define core platform semantics.

## Event-envelope alignment decision

`SourceOS-Linux/sourceos-spec/schemas/EventEnvelope.json` already defines an envelope with these required fields: `eventId`, `eventType`, `specVersion`, `occurredAt`, `actor`, `objectId`, and `payload`.

CDM v0.1 will therefore profile this model rather than creating an unrelated `CommonEvent` base. The profile rules are:

1. `eventId` MUST follow the `urn:srcos:event:` prefix until SourceOS adopts an additional CDM-specific prefix.
2. `eventType` MUST encode the CDM event class and operator, for example:
   - `cdm.observation.recorded`
   - `cdm.transition.object_upserted`
   - `cdm.transition.facet_added`
   - `cdm.transition.relationship_added`
   - `cdm.transition.retracted`
   - `cdm.transition.objects_merged`
   - `cdm.transition.object_split`
   - `cdm.transition.snapshot_recorded`
   - `cdm.projection.upserted`
3. `objectId` MUST reference the primary affected Data Object, map partition, projection target, or stable synthetic object for aggregate events.
4. `payload.kind` MUST be one of `OBSERVATION`, `TRANSITION`, `PROJECTION`, `AUDIT`, or `DEADLETTER`.
5. `payload` MUST conform to the CDM profile schemas once those schemas are landed.
6. `integrity.eventHash` SHOULD be the canonical digest of the normalized event payload and provenance anchors.
7. `integrity.signature` SHOULD be used for release, audit, evidence, and cross-boundary event transport.

## Physical channel policy

Non-segmented messaging means one semantic envelope and one coherent event family. It does **not** require one physical topic for all events.

Physical channels MAY be separated for throughput, retention, locality, replay, security, or governance reasons. Recommended logical channels are:

- `cdm.observations`
- `cdm.transitions`
- `cdm.projections`
- `cdm.audit`
- `cdm.deadletter`

Implementations MAY multiplex these over one event bus, but they MUST preserve CDM envelope/profile semantics.

## Ordering and replay policy

Map transitions are not just messages; they are ordered mutations. Implementations MUST define:

- partition key rules,
- map sequence number or equivalent monotonic order,
- idempotency key for observations,
- duplicate-detection semantics,
- conflict handling,
- retry and dead-letter policy,
- snapshot boundary rules,
- replay determinism checks,
- projection rebuild equivalence checks.

Projection conformance requires that incremental projection results equal rebuild-from-log results for the same map version and schema/profile version.

## Ownership map

| Layer | Owning repository | Rule |
| --- | --- | --- |
| Normative CDM doctrine, map log, storage/projection conformance | `SocioProphet/socioprophet-standards-storage` | This ADR and follow-on standard are canonical here. |
| Machine-readable base JSON Schemas, OpenAPI/AsyncAPI, examples | `SourceOS-Linux/sourceos-spec` | CDM profile must align with existing `EventEnvelope`; no silent fork. |
| RDF/OWL/JSON-LD/SHACL vocabulary and semantic registry | `SocioProphet/ontogenesis` | Ontology owns semantic IRIs and SHACL gates, not the event bus. |
| Knowledge atom profile | `SocioProphet/socioprophet-standards-knowledge` | Note/Claim/Annotation/Edge/ProvenanceRecord profile CDM, not redefine it. |
| Agent-facing emission/evidence/replay profile | `SocioProphet/socioprophet-agent-standards` | Agents import CDM and impose evidence/conformance obligations. |
| CI/CD, RBAC/audit, OTEL, GitOps enforcement | `SocioProphet/prophet-platform-standards` | Enforcement consumes CDM; it does not own CDM semantics. |
| Workspace orchestration and drift validation | `SocioProphet/sociosphere` | Sociosphere validates and propagates; it is not the standards authority. |

## Consequences

Positive consequences:

- CDM becomes a portable, non-enterprise, non-vendor semantic spine.
- Existing `EventEnvelope` work is preserved instead of forked.
- Storage, ontology, knowledge, agent, platform, and workspace concerns remain cleanly separated.
- Projections become testable through rebuild equivalence.
- Later work streams can import a stable canon rather than inventing new event semantics.

Tradeoffs:

- CDM v0.1 must respect the existing `EventEnvelope` field names even if earlier drafts used `CommonEvent`, `event_id`, or `kind` at the top level.
- Some schemas will be split across repositories by design, which requires standards locks and compatibility records.
- Denylist enforcement must be scoped carefully to avoid breaking historical notes or external citations.

## Follow-up work

1. Add `docs/standards/100-commons-data-model-and-map-log.md` in this repository.
2. Add CDM JSON Schema profile artifacts and examples, either here as normative references or in `SourceOS-Linux/sourceos-spec` as canonical machine-readable contracts.
3. Add Ontogenesis CDM vocabulary, JSON-LD context, and SHACL shapes.
4. Add knowledge and agent profile documents.
5. Add platform enforcement templates and conformance gates.
6. Add `standards.lock.yaml` discipline for downstream consumers.
