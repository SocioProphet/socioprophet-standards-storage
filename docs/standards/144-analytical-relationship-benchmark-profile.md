# 144 — Analytical Relationship Benchmark Profile

## Rationale

Analytical relationship platforms occupy an architectural middle ground between relational analytics, graph traversal systems, lakehouse execution layers, and investigation-facing analyst surfaces. Product claims in this class are frequently ambiguous. Terms such as "real-time," "graph analytics," "AI-ready," and "scalable" are often used without stable measurement semantics.

This standard defines a vendor-neutral benchmark profile for systems whose primary value proposition is deep exploration of large, evolving, relationship-rich data by analysts, investigators, or operators. The purpose is to make platform comparisons reproducible, defensible, and portable across candidate implementations.

## Scope

This profile applies to any system that presents one or more of the following characteristics:

- a graph-like or hypergraph-like logical model over relational or columnar storage;
- analyst-facing exploration workflows over connected entities, events, and artifacts;
- mixed structured and unstructured analytical inputs;
- derived links, scores, alerts, or dependency-driven recomputation;
- a claim of unified search, aggregation, relationship analysis, or investigative pivoting.

This profile does not replace workload-specific storage or service benchmarks elsewhere in this repository. It supplements them for the analytical relationship problem class.

## Candidate classification

Implementations evaluated under this profile MUST be classified into one or more of the following architecture classes before measurement begins:

1. OLTP relational
2. MPP / columnar analytical
3. native graph database
4. lakehouse / query engine
5. hybrid analytical relationship platform

Candidates MAY declare multiple classes, but the primary class MUST be identified.

## Normative requirements

### Measurement semantics

1. Benchmark reports MUST replace vague marketing terms with explicit measured quantities.
2. "Real-time" MUST be reported as one or more freshness metrics, including raw ingest visibility and derived-view freshness.
3. "Fast" MUST be reported as percentile distributions by workload class.
4. "Scalable" MUST be reported as degradation curves under defined concurrency and data growth conditions.
5. "Flexible" MUST be reported as schema evolution cost and propagation burden.

### Workload coverage

1. Candidates MUST be measured against the workload suite defined in `benchmarks/workloads/relationship-platforms.yaml`.
2. At minimum, each run MUST include:
   - one cold-cache exploration run;
   - one warm-cache exploration run;
   - one granular mutation run under concurrent reads;
   - one aggregate correctness run over many-to-many data;
   - one dependency recomputation run;
   - one policy-filtered exploration run.
3. Optional workloads MAY be skipped only when the report explicitly states why the feature is out of scope or unsupported.

### Baselines and comparators

1. Each serious comparison SHOULD include at least three baseline classes:
   - a hand-tuned relational or columnar baseline;
   - a native graph baseline;
   - a lakehouse or query-engine baseline.
2. When a baseline is omitted, the omission MUST be justified in the report.

### Correctness and semantics

1. Aggregate correctness MUST be validated against a gold-standard reference computation.
2. Reports MUST state whether the platform uses binary edges, event bridges, hyperedges, or equivalent abstractions.
3. Reports MUST describe how the model represents role-qualified relationships, temporal relationships, contradictory facts, and confidence-weighted links.
4. Reports MUST disclose whether unstructured extraction and entity resolution are native, embedded, tightly integrated, or external.

### Freshness disclosure

The following freshness layers MUST be measured separately when applicable:

- source event to raw ingest visibility;
- raw ingest visibility to queryability;
- queryability to derived relationship refresh;
- derived relationship refresh to scored/alerted view availability;
- end-to-end replay reproducibility for the same input window.

### Operational disclosure

Reports MUST disclose:

- internal artifact counts if the platform materializes temporary tables, views, caches, or indexes;
- recomputation blast radius for local, medium-scope, and global changes;
- concurrency profile by workload type, not only total user count;
- storage amplification under mutation-heavy workloads;
- operator burden for onboarding a new source and changing the logical model.

### External dependency disclosure

If a claimed capability depends on external systems, the report MUST identify:

- dependency name and role;
- whether the dependency is required or optional;
- the measured boundary between the candidate and the dependency;
- what evidence was collected inside the candidate versus outside it.

### Evidence and reproducibility

1. Every benchmark run MUST produce a reproducibility manifest.
2. Every benchmark run MUST record candidate version, configuration, dataset version, workload version, and environment details.
3. Where available, runs SHOULD emit trace identifiers and typed event identifiers for each workload execution.
4. Where available, runs SHOULD emit checkpoint identifiers for replay and divergence analysis.
5. Benchmark conclusions MUST be supported by artifacts in `benchmarks/reports/<date>-<candidate>/`.

## Canonical metrics

The following metrics are normative for this profile.

### Exploration metrics

- analyst_roundtrip_p50_ms
- analyst_roundtrip_p95_ms
- iterative_cycle_time_s
- time_to_first_valid_hypothesis_s
- time_to_corrected_hypothesis_s
- cache_reuse_ratio

### Freshness metrics

- raw_ingest_visibility_lag_ms
- queryable_visibility_lag_ms
- derived_relationship_refresh_lag_ms
- scored_view_refresh_lag_ms
- replay_reproducibility_rate

### Correctness metrics

- aggregate_correctness_rate
- duplicate_count_error_rate
- entity_resolution_precision
- entity_resolution_recall
- relation_extraction_f1

### Operational metrics

- internal_artifact_count
- recomputation_duration_s
- recomputation_blast_radius_ratio
- storage_amplification_ratio
- operator_hours_per_new_source
- schema_change_propagation_count

## Scoring and gates

The score for this profile MUST preserve category-level detail and MUST NOT collapse the benchmark into a single undifferentiated scalar without sub-scores.

Recommended scoring weights:

- interactive exploration: 18
- data model agility: 12
- aggregation correctness: 12
- freshness behavior: 10
- update behavior: 10
- recomputation control: 8
- security and governance: 10
- operational burden: 8
- concurrency and isolation: 6
- unstructured integration: 6

The following gates are mandatory:

- aggregate correctness below declared threshold fails the run;
- audit completeness failure fails the run;
- missing reproducibility manifest fails the run;
- missing workload disclosure fails the run;
- unsupported freshness disclosure fails the run when freshness is claimed.

## Versioning impact

This standard introduces a benchmark profile and associated report semantics. It does not change any on-wire contract directly, but downstream schemas, harnesses, and report templates SHOULD reference this profile identifier.

## Profile identifier

- profile_id: `benchmark.profile.analytical_relationship.v0`
- status: draft
- compatibility: additive
