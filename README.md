# SocioProphet Platform Standards — Storage, Contracts, and Measurement

| Metadata | Details |
| --- | --- |
| Description | Standards and measurement guidance for interoperable storage, data contracts, and benchmarking in an incident intelligence / ChatOps platform. |
| Website | https://github.com/SocioProphet |
| Topics | incident-intelligence, chatops, standards, data-contracts, avro, arrow, parquet, json-ld, rdf, sparql, property-graph, hypergraph, tritrpc, event-streams, benchmarks, storage, opensearch, postgres, vector-search, graph-database, observability, governance, interoperability |

**Description:** Standards and measurement guidance for interoperable storage, data contracts, and benchmarking in an incident intelligence / ChatOps platform.

## Repository description
This repository is a **standards and decision** package for an open, vendor-neutral incident intelligence / ChatOps platform. It defines storage contexts, data contracts, service interfaces, and benchmark methodology for evaluating portability, performance, and governance across the stack.

## Metadata summary
| Key | Summary |
| --- | --- |
| Repository role | Canonical standards source for storage, contracts, and benchmark methodology in SocioProphet platform workstreams. |
| Primary outputs | Normative standards (`docs/standards`), benchmark guidance (`docs/benchmarks`), workload definitions (`benchmarks/workloads`), and ADRs (`adr`). |
| Contract formats | Avro (events), Arrow/Parquet (analytics), JSON-LD (semantic/provenance overlays). |
| Interface standards | TritRPC service interfaces and event bus topic conventions. |
| Decision posture | Vendor-neutral defaults with workload-driven adoption gates for vector and graph systems. |
| Governance intent | Reproducible measurement, portability, and security-first interoperability across contexts. |

We treat the platform as a set of **contexts** (event stream, incident state, artifacts, search, vectors, graphs, metrics) and we standardize:
- **Data contracts:** Avro for event contracts; Arrow + Parquet for analytic payloads; JSON-LD for semantic/provenance overlays.
- **Interfaces:** TritRPC (typed RPC) for service calls; event bus topics for asynchronous flows.
- **Execution:** Beam for batch/stream transforms; Ray for training/serving/task placement.
- **Storage portfolio:** Postgres as system-of-record; OpenSearch for text; optional vector/graph stores based on measured workload triggers.
- **Measurement:** a benchmark harness with 30 defined workloads (latency/throughput/cost/recovery).

## Repository map
- `docs/standards/` — normative standards (MUST/SHOULD/MAY language)
- `docs/benchmarks/` — benchmark methodology and reporting format
- `benchmarks/workloads/` — workload definitions (YAML)
- `benchmarks/harness/` — harness scaffold (drivers to implement)
- `adr/` — Architecture Decision Records (templates + initial decisions)
- `schemas/` — schema placeholders for Avro/Arrow/JSON-LD contexts
- `ops/` — deployment conventions (placeholders)
- `SECURITY.md` — security policy and reporting guidance
- `LICENSE` — Apache-2.0 license

## Status
- Initial scaffold created: 2026-01-08
- Next: implement benchmark harness code + populate schema directories with v1 contracts.



## Graph Layer

This repo now includes the Graph Store Abstraction standard (RDF/SPARQL, property graph, and AtomSpace-style hypergraph) plus a dedicated graph benchmark workload suite.

## Security policy
Please review `SECURITY.md` for supported versions, vulnerability disclosure, and response expectations.

## License
Licensed under the Apache-2.0 license. See `LICENSE` for full text.

## Dev setup

python3 -m venv .venv
. .venv/bin/activate
python3 -m pip install -U pip
python3 -m pip install -r requirements-dev.txt
