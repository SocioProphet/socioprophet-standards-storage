# AI+HW+State Doctrine v0.1
_A SocioProphet-oriented operational doctrine for energy-aware, state-aware, governed AI systems_

## 0. Why this exists

The recent AI+HW 2035 vision is directionally right: the field must optimize for **intelligence per joule**, and the dominant bottleneck is increasingly **data movement and memory hierarchy**, not raw arithmetic throughput. What it does not fully specify is the machinery required to make that vision operable in real systems.

This doctrine supplies the missing machinery.

### Core thesis

We should not optimize **AI + HW** in isolation.

We should optimize:

**AI + HW + State**

Where **state** includes:
- context and retrieval surfaces,
- manifests and lockfiles,
- policies and trust boundaries,
- receipts and replay evidence,
- caches and placement history,
- human approvals and consent traces,
- persistent artifacts that allow future work to be loaded safely and cheaply.

In other words:
- hardware determines what is physically efficient,
- models determine what is computationally useful,
- **state** determines what is actually reachable, reproducible, and governable.

---

## 1. Terms

### 1.1 State
Persistent, addressable, governed information required to execute, evaluate, reproduce, or audit a task.

### 1.2 Control plane
The machinery that decides **what runs where, under which constraints, using which resources, with which evidence**.

### 1.3 Data plane
The machinery that decides **what context and data move where, in what form, under what policy, and with what locality/provenance properties**.

### 1.4 Evidence plane
The receipts, hashes, attestations, policy decisions, replay logs, and benchmark outputs that make behavior inspectable and reproducible.

### 1.5 MAIPJ
**Mission-Adjusted Intelligence per Joule**. A task- and mission-weighted efficiency metric for socio-profit AI systems.

---

## 2. Design laws

1. **State is first-class.**  
   Context, policies, manifests, provenance, and receipts are part of the system, not documentation trivia.

2. **Data movement is an optimization target.**  
   Context movement, storage fetches, network hops, and cache misses are often more expensive than arithmetic.

3. **Every execution must be replayable or explicitly marked non-replayable.**  
   Silent irreproducibility is treated as a defect.

4. **Every context pack must be governed.**  
   No unscoped retrieval blob should enter a high-trust workflow without provenance, policy, and digest.

5. **Placement is policy-constrained optimization.**  
   The scheduler does not maximize throughput alone. It maximizes mission utility subject to energy, latency, privacy, locality, and trust constraints.

6. **Operator reality outranks benchmark theater.**  
   Observability, rollback, downgrade paths, and failure semantics are mandatory design inputs.

7. **Benchmark claims require energy boundaries.**  
   “Per joule” claims are invalid without explicit accounting boundaries and utilization assumptions.

8. **Human consent and governance are not app-layer garnish.**  
   They are core system state.

---

## 3. The six-layer stack

We number bottom-up because the machine is built from physical substrate upward.

## Layer 0 — Physical substrate
**Scope:** chips, memory, interconnect, power delivery, cooling, racks, edge devices, node pools, topology.  
**Primary question:** what is physically possible, and at what energy / latency / cost envelope?  
**Key invariants:**
- expose measurable energy boundaries,
- expose memory/locality topology,
- expose failure and thermal state to upper layers.

**Canonical artifacts:**
- node inventory,
- accelerator capabilities,
- topology maps,
- energy meters,
- thermal and power telemetry.

## Layer 1 — Model / runtime
**Scope:** models, compilers, runtimes, kernels, quantization, sparsity, model routing, token policies, adaptive inference.  
**Primary question:** what computation should happen, with what approximation and which execution strategy?  
**Key invariants:**
- model identity must be content-addressable,
- runtime settings must be logged,
- adaptive behavior must expose decision traces.

**Canonical artifacts:**
- model digests,
- quantization descriptors,
- compiler/runtime versions,
- inference plans,
- calibration/test artifacts.

## Layer 2 — Data plane
**Scope:** retrieval, context packaging, provenance, rights, locality, caches, vector/graph stores, artifact stores, sensor ingress, corpus slices.  
**Primary question:** what state is brought into the computation, from where, under what policy, and at what movement cost?  
**Key invariants:**
- every context pack has provenance, digest, policy, TTL, and locality metadata,
- context movement is metered,
- cacheability is explicit.

**Canonical artifacts:**
- topic packs,
- manifests,
- context receipts,
- corpus indexes,
- retrieval traces,
- provenance overlays.

## Layer 3 — Control plane
**Scope:** admission control, placement, scheduling, dependency resolution, retries, checkpointing, rollback, replay, quota, QoS, degradation policy.  
**Primary question:** how does the system choose and supervise execution?  
**Key invariants:**
- every run has a trace ID and receipt,
- placement decisions are explainable,
- rollback and replay paths are defined.

**Canonical artifacts:**
- execution bundles,
- run receipts,
- policy decisions,
- placement logs,
- failure taxonomies,
- replay manifests.

## Layer 4 — Identity / policy / evidence
**Scope:** attestation, trust boundaries, human consent, approvals, secret handling, authorization, evidence bundles, audit trails, compliance assertions.  
**Primary question:** who is allowed to do what, under what proof, and with what downstream accountability?  
**Key invariants:**
- sensitive actions require policy evaluation,
- human-centric data exports require consent state,
- evidence bundles must be tamper-evident.

**Canonical artifacts:**
- policy bundles,
- capability proofs,
- consent records,
- signatures / hashes,
- audit evidence,
- attestation records.

## Layer 5 — Mission / application
**Scope:** end-user workflows, socio-profit outcomes, safety constraints, latency SLOs, reliability expectations, human collaboration.  
**Primary question:** what mission-weighted value is the system delivering?  
**Key invariants:**
- every benchmark is tied to a task family,
- every task family has mission weight(s),
- utility is measured under explicit constraints, not vibes.

**Canonical artifacts:**
- benchmark families,
- mission-weight registry,
- workflow specs,
- human review protocols,
- service-level objectives,
- beneficiary impact logs.

---

## 4. Cross-layer contracts

The stack is only real if adjacent layers have explicit contracts.

### 4.1 Physical ↔ Runtime
- runtime must know locality, bandwidth classes, and energy envelopes;
- substrate must expose enough telemetry for per-run accounting.

### 4.2 Runtime ↔ Data plane
- model invocation declares required context shape, max context budget, and preferred locality;
- data plane returns context packs with provenance, TTL, policy labels, and size estimates.

### 4.3 Data plane ↔ Control plane
- control plane cannot place work without predicted movement cost;
- data plane must expose cache-hit potential and remote-fetch penalties.

### 4.4 Control plane ↔ Identity/policy/evidence
- high-risk actions require preflight policy checks;
- all decisions must emit receipts that can be replayed and audited.

### 4.5 Identity/policy/evidence ↔ Mission/application
- task families define the relevant safety, privacy, consent, and compliance obligations;
- utility claims are invalid without evidence coverage.

---

## 5. Metric constitution: MAIPJ

## 5.1 Primary metric

For task family k:

**MAIPJ = (sum over k of m_k * U_k) / (sum over k of E_k)**

Where:
- **m_k** = mission weight for task family k,
- **U_k** = realized utility under constraints,
- **E_k** = total end-to-end energy consumed.

This is a socio-profit metric.  
The numerator is **mission-weighted utility**, not revenue and not benchmark vanity.

## 5.2 Utility term

A practical decomposition is:

**U_k = B_k * C_k * R_k * P_k * H_k - N_k**

Where:
- **B_k** = base task success / quality score,
- **C_k** = calibration / confidence quality,
- **R_k** = robustness / retry-adjusted reliability,
- **P_k** = policy / privacy / compliance pass factor,
- **H_k** = human-approval / human-utility factor where applicable,
- **N_k** = penalties (unsafe behavior, irreproducibility, severe latency miss, harmful action, etc.).

This is intentionally multiplicative in the positive factors because a system that is “good” but unsafe or non-compliant should not be rewarded as if those were independent niceties.

## 5.3 Energy term

**E_k = E_train_amortized + E_infer + E_data_move + E_network + E_storage + E_control + E_idle + E_cooling_adjusted**

At minimum, reports MUST state:
- whether training energy is included,
- the amortization rule for training/fine-tuning,
- whether cooling is direct meter or PUE-adjusted,
- whether idle energy is charged for reserved-but-unused capacity,
- whether storage/network energy is measured or estimated,
- the physical/system boundary for the measurement.

## 5.4 Boundary rules

1. **No hidden denominator games.**  
   If energy terms are estimated, the estimation model must be named.

2. **Reserved capacity counts.**  
   If a workflow reserves a GPU/edge device and leaves it mostly idle, the idle tax is part of the system cost.

3. **Retrieval and orchestration count.**  
   If the agent spends more energy moving context, routing tools, or waiting on remote services than doing inference, that still counts.

4. **Replay is not free.**  
   Verification/replay costs must be tracked separately and optionally rolled into E_k.

5. **Human review time is not joules, but it is utility-relevant.**  
   Human burden should appear in side metrics even if not in the denominator.

---

## 6. Secondary metrics

### 6.1 Context Movement Fraction (CMF)
**CMF = (E_data_move + E_network + E_storage) / E_k**  
How much of the energy is spent moving or fetching state rather than computing.

### 6.2 Working-Set Hit Rate (WSHR)
Fraction of required context served from warm local state rather than remote or cold fetch.

### 6.3 Control-Plane Tax (CPT)
**CPT = E_control / E_k**  
The orchestration/governance overhead fraction.

### 6.4 Replay Tax (RT)
**RT = E_replay / E_original_execution**  
How expensive it is to verify or reproduce a run.

### 6.5 Misplacement Waste (MW)
Estimated excess energy from poor model/hardware/site selection relative to an oracle or best-known planner.

### 6.6 Evidence Coverage Ratio (ECR)
Fraction of critical execution steps accompanied by sufficient evidence for replay/audit.

### 6.7 Policy Friction Score (PFS)
Latency and workflow overhead induced by policy evaluation. This is not inherently bad; it should be visible so we can distinguish necessary governance from bureaucratic sludge.

---

## 7. Event model and receipt model

## 7.1 Event taxonomy

### Execution events
- run.started
- run.admitted
- run.placed
- run.completed
- run.failed
- run.replayed
- run.rolled_back

### Data/context events
- context.requested
- context.resolved
- context.cache_hit
- context.remote_fetch
- context.policy_denied
- context.expired

### Policy/evidence events
- policy.evaluated
- consent.checked
- attestation.verified
- evidence.emitted
- evidence.verified

### Benchmark/measurement events
- benchmark.case_started
- benchmark.case_completed
- benchmark.report_finalized

## 7.2 Minimal execution receipt

A receipt MUST include:
- stable run identifier,
- parent workflow / trace identifier,
- task family,
- model/runtime identity,
- context pack identifiers + digests,
- placement target,
- policy bundle identity,
- energy accounting vector,
- outcome vector,
- replayability flag,
- evidence references.

---

## 8. Benchmark families

Benchmarks should be organized by mission-relevant workflow families rather than raw model categories alone.

### Family A — Assistive knowledge work
Examples:
- retrieval + synthesis,
- structured drafting,
- policy-aware summarization,
- citation-grounded Q&A.

### Family B — Coordinated multi-agent work
Examples:
- planner + retriever + tool runner + verifier,
- delegation under bounded context and trust,
- fallback / degrade / replay workflows.

### Family C — Edge / local-first execution
Examples:
- intermittent connectivity,
- restricted power envelopes,
- limited-memory retrieval,
- privacy-constrained local execution.

### Family D — Human-governed sensitive workflows
Examples:
- consented exports,
- human approval chains,
- policy-gated decisions,
- regulated or high-stakes actions.

### Family E — Infrastructure and control-plane operations
Examples:
- placement quality,
- cache quality,
- scheduler efficiency,
- replay and rollback performance.

---

## 9. Mapping onto the public SocioProphet repo spine

This mapping uses public repo roles as the provisional ownership model.

### agentplane
**Role:** control plane core  
**Owns:**
- run bundle format,
- admission / placement receipts,
- replay and rollback semantics,
- execution evidence schema.

### sociosphere
**Role:** workspace / filesystem controller  
**Owns:**
- manifest and lock semantics,
- workspace composition,
- component fetch/build/test coordination,
- local override semantics.

### TriTRPC
**Role:** deterministic transport and protocol surface  
**Owns:**
- deterministic transport envelopes,
- request/response canonicalization,
- cross-language parity fixtures,
- authenticated hot-path framing.

### slash-topics
**Role:** governed context and retrieval plane  
**Owns:**
- signed topic packs,
- policy membranes,
- deterministic context receipts,
- scoped retrieval surfaces.

### human-digital-twin
**Role:** human policy / consent / evidence contract  
**Owns:**
- consent and export policy hooks,
- capability proofs,
- human-centric artifact evaluation,
- audit-grade evidence for human-facing state transitions.

### socioprophet-standards-storage
**Role:** standards, contracts, benchmark doctrine  
**Owns:**
- storage/data contracts,
- benchmark methodology,
- measurement guidance,
- portability and governance criteria.

### socioprophet
**Role:** mission/application umbrella  
**Owns:**
- benchmark task families,
- application-facing workflows,
- public mission surfaces,
- operator and beneficiary narratives.

---

## 10. Normative requirements for v0.1

1. Every benchmark report MUST include MAIPJ and the full energy vector.
2. Every execution on a governed path MUST emit a receipt.
3. Every context pack MUST be content-addressed and policy-labeled.
4. Every placement decision SHOULD expose predicted versus realized movement cost.
5. Every high-risk workflow MUST support replay or explain why replay is impossible.
6. Every task family MUST define mission weight(s), utility rubric, and failure penalties.
7. Every model or runtime update MUST be benchmarked against at least one hot-path family.
8. Every standards claim SHOULD ship with a minimal reference implementation or fixture pack.
9. Every human-facing export path MUST be policy-gated and evidence-bearing.
10. Every org-level dashboard SHOULD separate utility from vanity metrics.

---

## 11. 90-day build plan

### Phase 1 — Constitution
- ratify the six-layer model,
- freeze initial MAIPJ terms,
- define task-family registry,
- define energy boundary conventions.

### Phase 2 — Instrumentation
- implement event schema,
- emit run receipts from control-plane paths,
- log context-movement estimates,
- attach model/runtime digests to execution.

### Phase 3 — Benchmarking
- create 5–10 benchmark cases spanning cloud, edge, local-first, and human-governed flows,
- run baseline measurements,
- report MAIPJ + secondary metrics,
- identify dominant energy leaks.

### Phase 4 — Optimization
- improve working-set hit rate,
- reduce context movement,
- tighten placement quality,
- reduce control-plane tax,
- improve replayability coverage.

---

## 12. Open questions

1. How should mission weights be governed and revised?
2. Which energy terms can be directly metered today versus estimated?
3. What is the right replay policy for privacy-sensitive human workflows?
4. How should training amortization be reported for rapidly changing models?
5. Which task families become canonical hot-path benchmarks for SocioProphet first?

---

## 13. The short version

The paper says the future of AI is memory-centric and efficiency-centric.

We agree.

But the missing systems doctrine is:

- memory is not just HBM and SRAM,
- it is also manifests, context packs, policy state, receipts, and replay evidence;
- the missing stack layers are the **data plane** and the **control/governance plane**;
- the missing metric discipline is **Mission-Adjusted Intelligence per Joule** with explicit accounting boundaries;
- the missing implementation path is a governed, replayable control plane over deterministic transport and scoped context surfaces.

That is the operational bridge from manifesto to machine.