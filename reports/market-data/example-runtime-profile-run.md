# Example Market-Data Runtime Profile Run

This report records the first provisional benchmark/certification artifact for the
market-data runtime profile.

## Scope
- authority split validation
- append-only raw-event posture
- replay/evidence readiness categories
- entitlement propagation as a required future check

## Current posture
The runtime profile is accepted provisionally as a runtime-scoped conformance layer.
Executable fixture evidence is still required for:
- deterministic replay over a pinned input window
- gap handling and late/out-of-order visibility
- entitlement propagation through replay/export surfaces
- bar source-window hashing or Merkle-root evidence

## Related artifacts
- `benchmarks/workloads/market-data/market-data-runtime-certification-stub.yaml`
- `benchmarks/workloads/market-data/results/market-data-runtime-profile-v0-provisional.result.yaml`
