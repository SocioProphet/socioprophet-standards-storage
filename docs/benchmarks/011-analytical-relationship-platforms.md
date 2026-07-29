# 011 — Analytical Relationship Platforms Benchmark Methodology

## Purpose

This document defines the benchmark methodology for analytical relationship platforms: systems intended to support deep, iterative, relationship-centric analysis over large, evolving, heterogeneous datasets.

The benchmark is designed to answer five questions:

1. Does the system improve end-to-end analyst throughput, not only raw query latency?
2. Does the system preserve correctness under many-to-many and event-centric relationship structures?
3. What performance and operational tradeoffs arise from its abstraction layer?
4. What portion of the claimed capability is native versus dependent on external systems?
5. Under what workload shape is the system genuinely superior?

## Architecture classes under comparison

Benchmark candidates SHOULD be labeled as one or more of the following:

- OLTP relational
- MPP / columnar analytical
- native graph database
- lakehouse / query engine
- hybrid analytical relationship platform

The report MUST identify the primary class and any important secondary characteristics.

## Workload suite

The canonical workload definitions live in `benchmarks/workloads/relationship-platforms.yaml`.

### Workload families

| Family | Goal | Typical failure mode |
| --- | --- | --- |
| Cold-cache iterative exploration | Measure first-pass analyst round trips | planner or compilation overhead dominates |
| Warm-cache iterative exploration | Measure repeated hypothesis refinement | demo-path cache illusion |
| Granular mutation under concurrent reads | Reveal write-path penalties | merge debt or read degradation |
| Schema evolution propagation | Measure real agility | hidden downstream reconfiguration cost |
| Aggregate correctness on connected data | Validate correctness under fanout | duplicate inflation or path overcounting |
| Dependency recomputation | Measure invalidation precision | recomputation storming |
| Relationship expressiveness | Measure model and query burden | bridge-node or join explosion |
| Layered freshness | Measure true freshness semantics | raw data visible but derived views stale |
| Unstructured pipeline integration | Separate platform value from extractor value | ontology debt and noisy linkage |
| Policy-filtered exploration | Measure governance overhead | correctness, latency, or admin entropy |

## Required datasets

Each benchmark campaign SHOULD include three dataset classes:

1. **Synthetic controlled corpus** for reproducibility and parameter sweeps.
2. **Open structured corpus** for realistic connected data workloads.
3. **Mixed structured + unstructured corpus** for entity extraction, resolution, and provenance testing.

Each corpus SHOULD include adverse conditions:

- duplicate entities;
- partial keys;
- conflicting timestamps;
- stale or contradictory facts;
- ambiguous roles;
- noisy text extraction artifacts;
- schema drift between source versions.

## Measurement rules

### Cold-cache versus warm-cache

1. Cold-cache and warm-cache runs MUST be reported separately.
2. Warm-cache runs MUST identify the source run or initialization protocol used to warm the system.
3. Results MUST NOT mix cold and warm samples in a single latency distribution.

### Percentiles and distributions

1. Percentile reporting MUST include p50, p95, and p99 when applicable.
2. Heavy-tailed workloads SHOULD include raw histograms or equivalent distribution artifacts.
3. Means MAY be reported, but MUST NOT replace percentile reporting.

### Correctness

Correctness-sensitive workloads MUST include a gold-standard reference computation and MUST report both the numerical result and the deviation from the reference.

### Concurrency

Workloads MUST declare their concurrency profile explicitly. "Supports N users" is not acceptable without the workload mix.

Recommended profiles:

- analyst_heavy_rw
- analyst_heavy_ro
- dashboard_light_ro
- mixed_ingest_and_explore
- policy_heavy_filtered_queries

### Freshness

Freshness MUST be reported in layers:

- source event -> raw ingest visible
- raw ingest visible -> queryable
- queryable -> derived relationship refresh
- derived refresh -> scored/alerted/searchable view refresh

## Canonical metrics and definitions

### Analyst workflow metrics

- `analyst_roundtrip_p50_ms`: median time from analyst action to visible response.
- `analyst_roundtrip_p95_ms`: p95 of the same path.
- `iterative_cycle_time_s`: time for a multi-step exploration cycle.
- `time_to_first_valid_hypothesis_s`: time until the first non-trivial, correct intermediate analytical hypothesis is produced.
- `time_to_corrected_hypothesis_s`: time until an incorrect early hypothesis is corrected with supporting evidence.

### Freshness metrics

- `raw_ingest_visibility_lag_ms`
- `queryable_visibility_lag_ms`
- `derived_relationship_refresh_lag_ms`
- `scored_view_refresh_lag_ms`
- `replay_reproducibility_rate`

### Correctness metrics

- `aggregate_correctness_rate`
- `duplicate_count_error_rate`
- `entity_resolution_precision`
- `entity_resolution_recall`
- `entity_resolution_f1`
- `relation_extraction_f1`

### Operational metrics

- `internal_artifact_count`
- `recomputation_duration_s`
- `recomputation_blast_radius_ratio`
- `storage_amplification_ratio`
- `operator_hours_per_new_source`
- `schema_change_propagation_count`

### Human-effort metrics

- `analyst_steps_per_investigation`
- `query_reformulations_per_investigation`
- `manual_context_preservation_events`
- `operator_touchpoints_per_model_change`

## Instrumentation and evidence

Every serious run SHOULD collect:

- execution traces;
- query plans or equivalent execution plans;
- cache hit/miss counters;
- temporary object counts;
- memory and CPU saturation metrics;
- compaction / merge / maintenance backlog where applicable;
- policy evaluation latency where applicable;
- provenance or replay identifiers where available.

When the surrounding platform supports typed RPC, event envelopes, checkpointing, or replay semantics, the benchmark SHOULD emit identifiers that allow the run to be reconstructed end-to-end.

## External capability matrix

The final report MUST include a matrix classifying each claimed advanced capability as one of:

- native
- embedded external
- tightly integrated external
- loosely integrated external
- unsupported

Minimum rows:

- entity extraction
- relation extraction
- entity resolution
- clustering
- scoring
- policy filtering
- graph traversal
- aggregate correctness safeguards
- vector similarity
- provenance traversal

## Reporting package

Each campaign MUST publish a report directory with:

- report summary;
- reproducibility manifest;
- workload definitions used;
- environment description;
- dataset version information;
- raw result files or machine-readable summaries;
- scorecard with category-level results;
- gating results;
- limitations and unsupported features.

Recommended location:

`benchmarks/reports/<date>-<candidate>/relationship-platforms/`

## Interpretation guidance

A candidate may lose on isolated microbenchmarks and still win on end-to-end analyst productivity. Reports MUST discuss this explicitly. Conversely, a candidate may demo well under warm-cache traversal while failing freshness, correctness, or operational burden requirements. Reports MUST identify those tradeoffs plainly.

## Profile reference

- standard: `docs/standards/050-analytical-relationship-benchmark-profile.md`
- workload catalog: `benchmarks/workloads/relationship-platforms.yaml`
- run schema: `schemas/benchmarks/benchmark-run-envelope.schema.json`
- report schema: `schemas/benchmarks/benchmark-report.schema.json`
