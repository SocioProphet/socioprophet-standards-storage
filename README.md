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

## FIPS 140-2/140-3 Compliance

This repository is the **standards authority** for FIPS 140-2/140-3 and NIST compliance across the SocioProphet platform. The FIPS/NIST standards are in `docs/standards/` (files 090–095).

### Cross-Repository Governance

Standards in this repository cross-reference implementations in the following repositories:

| Standard | Implementation Location |
|----------|------------------------|
| `090-fips-nist-compliance.md` | `SocioProphet/sociosphere/auth/oidc.py`, `SocioProphet/sociosphere/vault/vault-config.hcl` |
| `091-nist-800-53-control-mappings.md` | All 28 control implementations listed per-control with repo paths |
| `092-zero-trust-nist-800-207.md` | `SocioProphet/sociosphere/mesh/`, `SocioProphet/sociosphere/k8s/network-policies/` |
| `093-forensic-audit-nist-800-88.md` | `SocioProphet/sociosphere/observability/audit-pipeline.yaml` |
| `094-data-layer-fips-compliance.md` | `SocioProphet/postgres`, `SocioProphet/mongo`, `SocioProphet/elasticsearch`, `SocioProphet/redis`, `SocioProphet/minio`, `SocioProphet/rocksdb` |
| `095-orchestration-fips-compliance.md` | `SocioProphet/sociosphere/k8s/`, `SocioProphet/sociosphere/vault/`, `SocioProphet/sociosphere/mesh/` |

Implementation repositories that consume these standards MUST add a "Complies with Standards" section to their README, linking back to specific standard documents (bidirectional cross-reference requirement).

### Related Governance Repositories

- `SocioProphet/sociosphere` — workspace controller with FIPS validator tool and OIDC/mTLS enforcement
- `SocioProphet/socioprophet-standards-knowledge` — knowledge context ontologies and semantic governance

## Security policy
Please review `SECURITY.md` for supported versions, vulnerability disclosure, and response expectations.

## License
Licensed under the Apache-2.0 license. See `LICENSE` for full text.

## Dev setup

python3 -m venv .venv
. .venv/bin/activate
python3 -m pip install -U pip
python3 -m pip install -r requirements-dev.txt
