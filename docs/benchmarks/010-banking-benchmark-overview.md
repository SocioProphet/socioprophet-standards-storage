# Banking Benchmark Overview

## Purpose

Define the first benchmark lens for banking twin storage, contract, and replay workloads.

## Initial workload families

The first banking workload families are:
- twin state ingest
- scenario run materialization
- capital state roll-forward
- filing pack assembly
- evidence replay
- lineage traversal

## Metrics

Banking benchmark reports SHOULD include:
- p50 / p95 / p99 latency
- throughput
- error rate
- resource usage
- index build time where applicable
- recovery time under injected failure
- replay fidelity

## Evidence requirement

Any decision to specialize storage or introduce a new serving backend for banking workloads MUST cite benchmark evidence.

## Status

This is a first benchmark note. Workload YAML additions and certification result fixtures should follow once the first runtime slices are executable.
