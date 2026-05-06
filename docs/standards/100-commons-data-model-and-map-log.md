# 100 — Commons Data Model and Map Log Standard

## Status

Normative v0.1 bootstrap standard.

## Purpose

This standard defines the **Commons Data Model (CDM)**, **Commons Data Map**, and **Map Log** as the vendor-neutral, non-enterprise semantic spine for shared data, evidence, provenance, knowledge, agent observations, and derived projections.

The purpose is to make every participating work stream speak the same minimal language for objects, facets, relationships, observations, transitions, projections, provenance, and policy hooks while allowing each domain to extend the model through registered profiles.

## Non-goals

This standard does not pick a single database, graph engine, search engine, vector store, ontology editor, catalog tool, or workflow engine. Contracts are the product. Engines are implementations.

This standard does not replace the base machine-readable schema layer in `SourceOS-Linux/sourceos-spec`. CDM v0.1 profiles the existing SourceOS `EventEnvelope` family rather than forking it.

This standard does not redefine knowledge atoms owned by `SocioProphet/socioprophet-standards-knowledge`; it provides the lower semantic spine those atoms can profile.

## Normative vocabulary

### Commons Data Model

The **Commons Data Model** is the structural and semantic model for:

- Data Objects,
- Facets,
- Relationships,
- Evidence References,
- Provenance Records,
- Policy Hooks,
- Identity Links,
- Temporal Assertions,
- Observation Payloads,
- Transition Payloads,
- Projection Payloads.

### Commons Data Map

The **Commons Data Map** is the current assembled state derived from accepted map transitions. It MAY be materialized in relational stores, document stores, RDF stores, property graphs, hypergraphs, search indexes, vector indexes, or columnar analytic views, but it MUST remain rebuildable from the Map Log and associated snapshots.

### Map Log

The **Map Log** is the append-only ordered transition stream from which the Commons Data Map and projections can be reconstructed.

The Map Log is the replay spine. It is not an implementation detail.

### Data Object

A **Data Object** is any addressable thing represented in the map. Examples include files, datasets, records, messages, people, agents, devices, concepts, policies, claims, annotations, evidence artifacts, runs, services, projections, and external resources.

### Facet

A **Facet** is a typed attribute bundle attached to a Data Object. Facets MUST declare a `facetType`. Important facet types SHOULD have registered schemas. Unregistered free-form facets are allowed only in experimental or local scopes and MUST NOT be promoted to canonical work streams without registration.

### Relationship

A **Relationship** is a typed link between Data Objects. Relationships MUST declare a `relationshipType`, a source object, a target object, and optional attributes. Important relationship types SHOULD have semantic IRIs in Ontogenesis.

### CDM Event

A **CDM Event** is an `EventEnvelope`-compatible event whose payload conforms to one of the CDM payload profiles:

- `OBSERVATION`,
- `TRANSITION`,
- `PROJECTION`,
- `AUDIT`,
- `DEADLETTER`.

Earlier drafts used the documentation term `CommonEvent`. For v0.1, the canonical machine alignment term is **CDM Event profile over SourceOS EventEnvelope**.

## Banned and deprecated vocabulary

The following terms MUST NOT define new canonical schema names, API names, normative labels, diagrams, or repository surfaces:

- `EDM`,
- `EDF`,
- `Enterprise Data Map`,
- `Enterprise Data Model`,
- `Enterprise Data Frame`,
- `WKC`,
- `WKS`,
- `WDS`,
- `Watson`.

The word `enterprise` MAY appear in historical migration notes, external citations, compatibility notes, or market-context prose, but MUST NOT define core CDM semantics.

## SourceOS EventEnvelope profile

`SourceOS-Linux/sourceos-spec` already defines `EventEnvelope` as the universal wrapper for AsyncAPI channel messages. CDM events MUST profile that envelope.

Required SourceOS envelope fields are:

- `eventId`,
- `eventType`,
- `specVersion`,
- `occurredAt`,
- `actor`,
- `objectId`,
- `payload`.

CDM profile rules:

1. `eventId` MUST use `urn:srcos:event:<local-id>` until a later cross-repo ADR introduces a CDM-specific event URN.
2. `eventType` MUST use a lowercase dotted CDM event type.
3. `specVersion` MUST identify the CDM profile version.
4. `occurredAt` MUST be an ISO 8601 date-time.
5. `actor.subjectId` MUST identify the subject, agent, service, or system that emitted or caused the event.
6. `objectId` MUST identify the primary Data Object, map partition, projection target, or stable aggregate object affected by the event.
7. `payload.kind` MUST be one of `OBSERVATION`, `TRANSITION`, `PROJECTION`, `AUDIT`, or `DEADLETTER`.
8. `payload` MUST satisfy the CDM payload schema for that kind.
9. `integrity.eventHash` SHOULD be populated with a canonical digest over the normalized payload and provenance anchors.
10. `integrity.signature` SHOULD be populated for cross-boundary, evidence-grade, release, governance, or audit flows.

Recommended `eventType` values include:

- `cdm.observation.recorded`,
- `cdm.transition.object_upserted`,
- `cdm.transition.facet_added`,
- `cdm.transition.relationship_added`,
- `cdm.transition.retracted`,
- `cdm.transition.objects_merged`,
- `cdm.transition.object_split`,
- `cdm.transition.snapshot_recorded`,
- `cdm.projection.upserted`,
- `cdm.projection.rebuilt`,
- `cdm.audit.policy_evaluated`,
- `cdm.deadletter.recorded`.

## Payload kinds

### Observation payload

An observation payload is an idempotent assertion of observed objects, facets, relationships, evidence references, and provenance.

Observation payloads SHOULD be deterministic. Re-emitting the same observation from the same evidence anchors SHOULD produce the same idempotency key or equivalent duplicate-detection result.

Observation payloads MUST NOT directly mutate the Commons Data Map. They are claims to be verified, normalized, rejected, merged, or transformed into ordered transitions.

### Transition payload

A transition payload is an ordered mutation applied to the Map Log.

Supported transition operators are:

- `UPSERT_OBJECT`,
- `ADD_FACET`,
- `ADD_RELATIONSHIP`,
- `RETRACT`,
- `MERGE`,
- `SPLIT`,
- `SNAPSHOT`.

Transition payloads MUST include references to the observation, command, policy decision, or prior transition that justified them.

Transition payloads MUST define ordering and conflict semantics through partition keys, sequence numbers, map versions, or equivalent implementation-specific controls.

### Projection payload

A projection payload records a derived read model update or rebuild.

Projection targets include, but are not limited to:

- search indexes,
- graph stores,
- RDF datasets,
- property graph views,
- hypergraph views,
- vector indexes,
- catalog services,
- materialized analytic tables,
- evidence bundles.

Projection events MUST retain source transition IDs and projection build metadata.

## Identity rules

### Data Object identifiers

CDM Data Object identifiers SHOULD be URI-shaped and stable.

Recommended patterns:

- `urn:srcos:<type>:<slug>` for SourceOS-native object families,
- `obj://org.socioprophet/<type>/<stable-key>` for CDM-specific bootstrap objects,
- content-addressed identifiers for immutable artifacts,
- minted time-sortable identifiers for mutable or conceptual objects.

A later cross-repo ADR SHOULD converge these into a single canonical identity profile.

### Identity relations

CDM implementations SHOULD support the following identity and derivation relations:

- `same_as`,
- `derived_from`,
- `version_of`,
- `representation_of`,
- `supersedes`,
- `retracted_by`.

These relations SHOULD be registered in Ontogenesis with stable IRIs and SHACL constraints.

## Ordering, partitioning, and replay

A CDM implementation MUST specify:

- observation idempotency key rules,
- transition partition key rules,
- per-partition ordering semantics,
- map version or sequence semantics,
- duplicate detection,
- conflict handling,
- retry behavior,
- dead-letter behavior,
- snapshot boundaries,
- replay determinism checks.

The same Map Log, snapshots, schemas, and profile versions MUST rebuild the same Commons Data Map, modulo explicitly declared nondeterministic or eventually consistent projection surfaces.

## Projection conformance

A projection is conformant only if it can prove rebuild equivalence.

For a given map version and projection profile version:

1. incremental projection updates MUST equal rebuild-from-log output,
2. projection outputs MUST record source transition IDs,
3. projection outputs SHOULD record schema/profile versions,
4. projection outputs SHOULD record engine/index/build metadata,
5. projection query responses SHOULD support explainability back to source transitions and evidence anchors.

## Physical event channels

Non-segmented messaging means one semantic event profile, not one mandatory physical topic.

Implementations MAY separate physical channels for throughput, retention, locality, security, replay, or governance.

Recommended logical channels:

- `cdm.observations`,
- `cdm.transitions`,
- `cdm.projections`,
- `cdm.audit`,
- `cdm.deadletter`.

## Governance and policy hooks

CDM events and objects SHOULD support policy metadata from v0.1. At minimum, implementations SHOULD allow profile-specific fields or facets for:

- classification,
- retention,
- redaction/masking obligations,
- provenance visibility,
- tenant or context boundary,
- purpose binding,
- policy decision references,
- deletion/retraction semantics.

These hooks are required because CDM is intended to carry personal, organizational, operational, evidence, research, and agentic data across mixed-trust contexts.

## Ontology and schema synchronization

The structural and semantic layers MUST remain aligned:

- JSON Schema validates structure.
- Ontogenesis owns semantic IRIs, RDF/OWL vocabulary, JSON-LD contexts, and SHACL gates.
- Avro MAY be used for wire-efficient payloads and executable fixtures where required.
- JSON-LD contexts SHOULD map CDM fields and registered facet/relationship types to stable semantic IRIs.
- Every promoted CDM semantic term SHOULD have a registry entry.

## Standards locks

Downstream consumers SHOULD pin CDM imports through `standards.lock.yaml` or an equivalent compatibility record.

A lock record SHOULD include:

- source repository,
- version,
- commit SHA,
- schema IDs,
- imported files,
- conformance level,
- validation command,
- last validated date.

Consumers MUST NOT silently import `main` as a hidden dependency for release-grade work.

## Migration appendix

Old terminology maps to CDM terminology as follows:

| Deprecated term | Replacement |
| --- | --- |
| `Enterprise Data Map` | `Commons Data Map` |
| `Enterprise Data Model` | `Commons Data Model` |
| `EDM Events` | `Map Transition Events` |
| `EDM Topic` | `Map Log Stream` or `cdm.transitions` |
| `EDF` | `Data Object` |
| `WKC Updater` | `Catalog Projection Builder` |
| `WKC` | `Open Catalog Service` |
| `ES Index` | `Search Index` |
| `Neo4J Builder` | `Graph Projection Builder` |
| `ElasticSearch Builder` | `Search Projection Builder` |
| `GraphX / Spark` | `Batch / Graph Compute Builder` |

## Cross-repo ownership

| Layer | Owning repository |
| --- | --- |
| Normative CDM doctrine, map log, storage/projection conformance | `SocioProphet/socioprophet-standards-storage` |
| Machine-readable JSON Schema, OpenAPI/AsyncAPI, examples | `SourceOS-Linux/sourceos-spec` |
| RDF/OWL/JSON-LD/SHACL vocabulary and semantic registry | `SocioProphet/ontogenesis` |
| Knowledge atom profile | `SocioProphet/socioprophet-standards-knowledge` |
| Agent-facing emission/evidence/replay profile | `SocioProphet/socioprophet-agent-standards` |
| CI/CD, RBAC/audit, OTEL, GitOps enforcement | `SocioProphet/prophet-platform-standards` |
| Workspace orchestration and drift validation | `SocioProphet/sociosphere` |

## Versioning policy

CDM follows semantic versioning:

- `MAJOR`: breaking field, ordering, identity, or semantic changes,
- `MINOR`: additive optional fields, new registered facets, new registered relationships, new transition operators,
- `PATCH`: clarifications, examples, documentation fixes, non-semantic test corrections.

Frozen schema IDs MUST NOT mutate. New incompatible semantics require new schema IDs, migration notes, and compatibility records.

## Minimum v0.1 conformance

A v0.1 conformant implementation MUST:

1. produce SourceOS `EventEnvelope`-compatible CDM events,
2. distinguish observation, transition, and projection payloads,
3. preserve provenance and source event references,
4. define transition ordering semantics,
5. support replay from the Map Log,
6. define projection rebuild equivalence tests,
7. avoid banned enterprise/Watson terminology in canonical surfaces,
8. document standards imports and compatibility pins.
