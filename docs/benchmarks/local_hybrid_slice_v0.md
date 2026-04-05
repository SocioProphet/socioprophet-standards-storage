# Local-Hybrid Slice v0 Benchmark Note

## Purpose

This note defines the first benchmark-oriented workload set for the local-hybrid slice.

The goal is not to benchmark every possible capability. The goal is to measure whether the first local-first plus tenant-hybrid control path behaves correctly and predictably.

## Workload set

### 1. Local-only denied remote

Policy denies egress and the task completes locally.

Measure:
- local completion latency
- evidence append latency
- replay materialization success rate
- zero remote dispatch confirmation

### 2. Remote allowed redacted

Policy allows tenant execution only after transformations.

Measure:
- policy decision latency
- transformation overhead
- capability resolution latency
- worker execution latency
- evidence append latency
- end-to-end latency

### 3. Tenant unreachable fallback

Policy allows remote execution but the tenant lane is unavailable.

Measure:
- fallback detection latency
- degraded local completion time or deferred-state issuance time
- rate of ambiguous partial completion

### 4. Evidence append failure quarantine

Execution completes but evidence append fails.

Measure:
- quarantine response time
- rate of incorrect promotion despite missing evidence
- recovery or retry path correctness

### 5. Cairn replay roundtrip

A completed execution boundary is replayed from the recorded cairn.

Measure:
- replay handle resolution time
- digest consistency
- lineage stability
- replay success rate

## Minimum metrics for the slice

- p50 and p95 latency per step
- success and failure counts per method
- rate of policy denial by label combination
- rate of fallback activation
- evidence append success rate
- replay roundtrip success rate

## Cross-repo relationship

- `TriTRPC` provides the method and fixture surface for this slice
- `agentplane` provides the tenant-side execution path
- `sociosphere` provides the local supervisor and local-first behavior
- this repository provides the shared schemas and benchmark framing
