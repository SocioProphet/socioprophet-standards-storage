# Storage Fabric Harness Scaffold

This directory contains the executable benchmark/conformance scaffold for the storage-fabric methodology.

It consumes the standards and schemas in this repository:
- `docs/benchmarks/storage-fabric/`
- `schemas/benchmarks/storage-fabric/`

## Initial scope

The first scaffold is intentionally narrow:
- validate generated report JSON against the report-family expectations
- preserve PASS / FAIL / SKIP semantics
- keep storage-fabric evidence in the storage standards repo rather than in product or contract-domain repos

## Non-goals

This scaffold does not own platform-wide storage doctrine. That doctrine is upstream in `SocioProphet/prophet-platform-standards`.

This scaffold does not own semantic catalog objects. Those belong in `SocioProphet/socioprophet-standards-knowledge`.
