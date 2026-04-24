# Knowledge Context (Normative Pointer)

This repository defines platform contexts (event stream, artifacts, search, vectors, graphs, metrics) and the governing rules for interoperability.

The detailed Knowledge Context standards (micro-publications, meriotopographic relations, masking/tokenization/IR/vector flows, office/editor integration, agent-first + human validation gates) live in the sibling standards repository:

- `SocioProphet/socioprophet-standards-knowledge` (active; public; executable standards package with schemas, RPC metadata, fixtures, and verification tooling)

Related repositories:
- `SocioProphet/ontogenesis` — ontology modules, SHACL validation, mappings, and signed semantic supply-chain assets
- `SocioProphet/sociosphere` — workspace governance, manifest/lock coordination, and policy propagation

## Requirements
- Knowledge Context MUST comply with:
  - docs/standards/020-data-formats.md (Avro, Arrow, Parquet, JSON-LD overlays)
  - docs/standards/030-service-interfaces-tritrpc.md (typed RPC + required metadata headers)
  - docs/standards/070-graph-rdf-hypergraph.md (RDF/property/hypergraph mappings + workload-driven choices)

## Integration contract
- Storage standards repo remains the platform index + reading order; Knowledge Context repo is the detailed spec package.
- Docs automation vendors both repos at pinned commits and generates reference pages from rpc/*.yaml, schemas/*, and benchmarks/workloads/*.yaml.
