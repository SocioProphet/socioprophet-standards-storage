# SocioProphet Platform Standards — Storage, Contracts, and Measurement

| Metadata | Details |
| --- | --- |
| Description | Standards and measurement guidance for interoperable storage, data contracts, and benchmarking in an incident intelligence / ChatOps platform. |
| Website | https://github.com/SocioProphet |
| Topics | incident-intelligence, chatops, standards, data-contracts, avro, arrow, parquet, json-ld, rdf, sparql, property-graph, hypergraph, tritrpc, event-streams, benchmarks, storage, opensearch, postgres, vector-search, graph-database, observability, governance, interoperability |

**Description:** Standards and measurement guidance for interoperable storage, data contracts, and benchmarking in an incident intelligence / ChatOps platform.

## Repository description
This repository is a **standards and decision** package for an open, vendor-neutral incident intelligence / ChatOps platform. It defines storage contexts, data contracts, service interfaces, and benchmark methodology for evaluating portability, performance, and governance across the stack.

We treat the platform as a set of **contexts** (event stream, incident state, artifacts, search, vectors, graphs, metrics) and we standardize:
- **Data contracts:** Avro for event contracts; Arrow + Parquet for analytic payloads; JSON-LD for semantic/provenance overlays.
- **Interfaces:** TritRPC (typed RPC) for service calls; event bus topics for asynchronous flows.
- **Execution:** Beam for batch/stream transforms; Ray for training/serving/task placement.
- **Storage portfolio:** Postgres as system-of-record; OpenSearch for text; optional vector/graph stores based on measured workload triggers.
- **Measurement:** a benchmark harness with 30 defined workloads (latency/throughput/cost/recovery).

## Repository map
- `docs/standards/` — normative standards (MUST/SHOULD/MAY language)
- `docs/benchmarks/` — benchmark methodology and reporting format
- `docs/fips/` — FIPS 140-2/140-3 governance framework (standards authority, activation plan, roadmap)
- `benchmarks/workloads/` — workload definitions (YAML)
- `benchmarks/harness/` — harness scaffold (drivers to implement)
- `adr/` — Architecture Decision Records (templates + initial decisions)
- `schemas/` — schema placeholders for Avro/Arrow/JSON-LD contexts
- `ops/` — deployment conventions (placeholders)
- `SECURITY.md` — security policy and reporting guidance
- `LICENSE` — Apache-2.0 license

## Status
- Initial scaffold created: 2026-01-08
- FIPS 140-2/140-3 governance framework added: 2026-Q2 (see `docs/fips/`)
- Next: implement benchmark harness code + populate schema directories with v1 contracts.



## Graph Layer

This repo now includes the Graph Store Abstraction standard (RDF/SPARQL, property graph, and AtomSpace-style hypergraph) plus a dedicated graph benchmark workload suite.

## FIPS 140-2/140-3 Governance

This repository hosts the FIPS governance framework for SocioProphet. See [`docs/fips/`](docs/fips/) for:

- [Standards authority](docs/fips/000-fips-standards-authority.md) — NIST/FIPS controls, approved algorithms, and 28 NIST 800-53 control mappings.
- [Week 1 activation plan](docs/fips/001-week1-activation-plan.md) — Day-by-day execution checklist for the governance committee.
- [10-step strategic roadmap](docs/fips/002-10-step-strategic-roadmap.md) — Q2–Q4 2026 path to FIPS 140-2 Level 2 certification.

## Security policy
Please review `SECURITY.md` for supported versions, vulnerability disclosure, and response expectations.

## License
Licensed under the Apache-2.0 license. See `LICENSE` for full text.

## Dev setup

python3 -m venv .venv
. .venv/bin/activate
python3 -m pip install -U pip
python3 -m pip install -r requirements-dev.txt
