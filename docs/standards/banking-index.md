# Banking Twin Standards Index

## Purpose

This index collects the first banking-twin standards, schemas, benchmark notes, and fixture placeholders.

The banking twin standardization lane is intentionally seed-grade. It provides contract and evidence discipline for downstream runtime work without claiming complete regulatory or FIBO/BIAN conformance.

## Standards

- `docs/standards/081-banking-twin-context.md`
- `docs/standards/082-banking-contracts-and-lineage.md`
- `docs/standards/083-banking-model-evidence-pack.md`
- `docs/standards/084-banking-filing-pack-and-correction-chain.md`

## Benchmarks

- `docs/benchmarks/010-banking-benchmark-overview.md`
- future workload entries for twin ingest, scenario run, capital roll-forward, filing assembly, and evidence replay

## Schemas and examples

Located under `schemas/banking/`.

Current placeholder families:
- twin state snapshot
- stress run
- capital state snapshot
- filing pack
- model evidence pack

## External reference anchors

- FIBO should inform financial concept, legal-entity, instrument, contract, and credit semantics.
- BIAN should inform service-domain and operational boundary alignment.

## Status

This index is a first navigation surface. Follow-on PRs should add concrete Avro / Arrow / JSON-LD contract families and benchmark result fixtures.
