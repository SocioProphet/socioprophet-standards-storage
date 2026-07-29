# Entity Registri / Proof Fabric (Normative Pointer)

This repository defines **platform contexts** and the governing rules for interoperability.

The detailed **Entity Registri / Proof Fabric** standards package lives in the sibling detailed standards repository:

- `SocioProphet/socioprophet-standards-knowledge`

## Purpose

Entity Registri / Proof Fabric defines the canonical package for:

- entity registry objects
- artifact manifests and custody pointers
- higher-order relation records / hyperedge-capable proof objects
- projection metadata across RDF / property graph / hypergraph views
- checkpoint / replay manifests that bind proof objects back to deterministic evidence and replay surfaces

This pointer exists so the platform index remains authoritative about **where** the detailed package lives and **which upstream standards** govern it.

## Requirements

Entity Registri / Proof Fabric MUST comply with:

- `docs/standards/020-data-formats.md` — Avro canonical event contracts and durable records; JSON-LD semantic overlay; SchemaSalad-or-equivalent package validation.
- `docs/standards/030-service-interfaces-tritrpc.md` — typed RPC + required metadata headers and transport discipline.
- `docs/standards/070-graph-rdf-hypergraph.md` — RDF / property graph / hypergraph mappings and engine-neutral graph contracts.

## Integration contract

- Storage standards repo remains the **platform index + reading order**.
- Detailed Registri / Proof Fabric schemas, manifests, fixtures, and binding docs live in the sibling detailed standards repo.
- Runtime consumers SHOULD import generated contracts through their standards lock / generated-contract pipeline rather than re-stating the package locally.
- Graph interrogation remains behind `graph.store.v0`; Registri owns canonical object lifecycle, not a rival graph-query universe.

## Relationship to adjacent packages

- `Knowledge Context` remains the existing detailed standards package for `Note`, `Claim`, `Annotation`, and `MeriotopographicEdge`.
- `Entity Registri / Proof Fabric` extends that lane with canonical entity, artifact, and higher-order relation packages while preserving down-projection to existing meriotopographic structures when relations collapse cleanly to subject–predicate–object.
- Replay / evidence integration must remain compatible with `agentplane` and transport/runtime imports pinned through downstream platform standards locks.
