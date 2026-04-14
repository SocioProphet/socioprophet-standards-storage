# Workbench Run Bundle Receipt Binding v0.1

Status: Draft

Canonical standards authority: `SocioProphet/socioprophet-standards-storage`

Primary workbench producer: `SocioProphet/sociosphere`

Primary transport binding authority: `SocioProphet/TriTRPC`

Primary runtime consumer and receipt service surface: `SocioProphet/prophet-platform`

Knowledge classification and lifecycle authority: `SocioProphet/socioprophet-standards-knowledge`

## 1. Purpose

This document defines the normative binding between the current **agentic workbench execution objects** and the existing **run bundle and evidence receipt canon**.

Its purpose is to prevent semantic fork across the following active upstream surfaces:

- `WorkflowSpec`
- `WorkflowRun`
- `ExecutionEnvelope`
- `ExecutionRecord`
- `RunBundle`
- `maipj-run-receipt`
- evidence receipt schemas such as validation, observation, and publication receipts
- TriTRPC transport receipt binding

This document does **not** create a second workflow system and does **not** replace the existing standards authority for receipt, transport, or knowledge-state semantics.

## 2. Non-negotiable authority rules

### 2.1 Workbench object authority

`SocioProphet/sociosphere` remains the canonical authority for:

- workbench protocol indices
- workflow specification objects
- workflow run objects
- execution envelope objects
- execution record objects
- workbench UI and operator-facing workflow surfaces

### 2.2 Receipt authority

`SocioProphet/socioprophet-standards-storage` remains the canonical authority for:

- run bundle structure
- MAIPJ run receipt structure
- evidence receipt families
- conformance fixtures
- hash domain and crypto profile rules

### 2.3 Transport authority

`SocioProphet/TriTRPC` remains the canonical authority for:

- transport receipt binding
- route / peer / retry / timeout / latency transport evidence
- envelope transport semantics

### 2.4 Runtime service authority

`SocioProphet/prophet-platform` remains the canonical authority for:

- runtime-side execution services
- evidence receipt service exposure
- catalog publication and catalog-serving APIs

### 2.5 Knowledge-state authority

`SocioProphet/socioprophet-standards-knowledge` remains the canonical authority for:

- object class taxonomy
- lifecycle semantics for knowledge-bearing runtime artifacts
- receipt verification semantics when those artifacts become knowledge-state objects

## 3. Binding summary

The binding is defined as follows:

- `WorkflowSpec` declares the static workflow law.
- `WorkflowRun` is the canonical operator-facing **run request / run identity object**.
- `ExecutionEnvelope` carries execution-time context needed to dispatch work under policy.
- `ExecutionRecord` captures phase-by-phase execution evidence.
- `RunBundle` is the control-plane bundle projection for a completed or in-flight run.
- `maipj-run-receipt` is the normalized runtime receipt for placement, runtime, evidence, replay, and outcome posture.
- evidence receipts such as validation, observation, and publication receipts represent specialized downstream receipt views.
- TriTRPC receipt binding contributes transport evidence into normalized run/evidence receipts.

## 4. Canonical object crosswalk

| Upstream workbench object | Canonical meaning | Required downstream projection | Notes |
| --- | --- | --- | --- |
| `WorkflowSpec` | Static workflow declaration, defaults, trust/policy refs, graph, step set | Referenced by `WorkflowRun`; may be cited by `RunBundle` metadata | Declares what *should* run, not what *did* run |
| `WorkflowRun` | Canonical run identity and operator-facing invocation object | `RunBundle.run`, `maipj-run-receipt.context/run identity` | This is the preferred upstream surface for what operators informally call a work order |
| `ExecutionEnvelope` | Execution-time context bound to a run: subject, inputs, policy refs, attestation refs, transport context | `RunBundle.execution`, `maipj-run-receipt.context`, transport-linked evidence | Must preserve digest linkage to the originating `WorkflowRun` |
| `ExecutionRecord` | Ordered execution evidence across phases such as validation, placement, grant, dispatch, result, replay | `RunBundle.records[]`, `maipj-run-receipt.evidence`, specialized evidence receipt projections | This is the primary source of execution truth |
| `RunBundle` | Control-plane bundle view of run + execution state + receipt lineage | Aggregate of workbench objects plus normalized receipts | Must not redefine fields already governed by upstream workbench objects |
| `maipj-run-receipt` | Normalized runtime receipt for placement, runtime posture, outcome, replay, evidence | Produced from bound `WorkflowRun` + `ExecutionEnvelope` + `ExecutionRecord` + transport evidence | Operator-facing alias `UsageReceipt` MAY be provided only as a derived view |
| `validation-receipt` / `observation-receipt` / `publication-receipt` | Specialized downstream evidence receipt views | Derived from run bundle / MAIPJ run receipt / execution record subsets | These are receipt families, not substitutes for run identity |

## 5. Alias and naming rules

### 5.1 `WorkOrder`

The system MAY expose `WorkOrder` as an operator-friendly alias, but it MUST be a constrained projection of `WorkflowRun` and MUST NOT become an independent schema family with competing authority.

Any `WorkOrder` alias MUST preserve at minimum:

- run identity
- workflow spec reference and digest
- caller / requesting principal
- input digest set
- policy pack reference
- trust profile reference when applicable
- ledger head or evidence chain reference when applicable

### 5.2 `UsageReceipt`

The system MAY expose `UsageReceipt` as an operator-friendly or UI-friendly projection, but it MUST be derived from the existing receipt canon and MUST NOT replace:

- `maipj-run-receipt`
- evidence receipt families
- TriTRPC transport receipt binding

A `UsageReceipt` alias MUST clearly declare the normalized source documents from which it is projected.

### 5.3 `LaunchConfig`

`LaunchConfig` MAY be introduced as a workbench-side execution request refinement object, because there is currently no explicit canonical launch object in the active upstream surface.

However, `LaunchConfig` MUST:

- reference exactly one `WorkflowRun`
- bind to one `ExecutionEnvelope`
- declare runtime profile and placement hints without mutating canonical run identity
- avoid duplicating receipt fields that belong in `ExecutionRecord` or `maipj-run-receipt`

### 5.4 `ProfileArtifact`

`ProfileArtifact` MAY be introduced as a first-class profiling output object, because a first-class profiling artifact schema is not yet established in the active upstream execution surface.

`ProfileArtifact` MUST:

- reference exactly one `WorkflowRun`
- declare profiling toolchain and version
- declare sample mode / collection posture
- link to execution phase and artifact hashes
- be admissible into `ExecutionRecord` evidence sets and receipt bundles

## 6. Required normalized flow

Any conforming implementation MUST be able to perform the following flow without semantic loss:

1. accept a `WorkflowRun`
2. bind it to an `ExecutionEnvelope`
3. execute work and emit one or more `ExecutionRecord` entries
4. merge transport evidence from TriTRPC receipt binding when transport is involved
5. project the execution truth into a `RunBundle`
6. normalize runtime evidence into `maipj-run-receipt`
7. produce specialized receipt projections when needed
8. expose receipt and catalog surfaces through runtime services

## 7. Required field preservation

The following field classes MUST survive the binding and projection process:

- run identity and workflow digest linkage
- caller / principal identity
- input digests and artifact digests
- policy pack references
- trust profile references
- attestation references
- placement / runtime environment posture
- transport evidence when transport is involved
- execution phase ordering
- outcome / replay linkage
- evidence signature and hash-domain posture

No projection layer may silently discard these classes.

## 8. Minimal reference implementation requirement

The first conforming reference implementation SHOULD provide a boring local execution path:

- consume `WorkflowRun`
- construct or resolve `ExecutionEnvelope`
- execute locally
- emit `ExecutionRecord`
- produce `RunBundle`
- normalize to `maipj-run-receipt`
- expose the resulting receipt bundle through the runtime receipt service
- append catalog delta for the resulting artifacts

This local path is the precondition for later scheduler adapters such as Slurm.

## 9. Conformance requirements

A repo claiming conformance to this binding MUST be able to show:

1. the exact mapping from `WorkflowRun` to `RunBundle`
2. the exact mapping from `ExecutionRecord` to receipt evidence sections
3. the exact source of transport evidence when TriTRPC is involved
4. the exact derivation path for any `WorkOrder` or `UsageReceipt` alias
5. evidence that no duplicate schema family has been introduced for the same semantic role

## 10. Repo implementation split

### 10.1 `sociosphere`

`sociosphere` SHOULD:

- retain the canonical workbench object family
- add any needed aliases such as `WorkOrder` only as projections over `WorkflowRun`
- add `LaunchConfig` and `ProfileArtifact` if required
- keep UI and operator-facing workflow tooling aligned to this binding

### 10.2 `socioprophet-standards-storage`

`standards-storage` SHOULD:

- remain the canonical home for receipt canon
- publish conformance fixtures for this binding
- define normalized projection expectations for `RunBundle` and MAIPJ/evidence receipts

### 10.3 `TriTRPC`

`TriTRPC` SHOULD:

- remain the authority for transport evidence binding
- avoid redefining workbench execution semantics

### 10.4 `prophet-platform`

`prophet-platform` SHOULD:

- implement the local reference runner first
- expose normalized receipt bundles and specialized receipt views
- auto-publish catalog deltas from completed runs

### 10.5 `socioprophet-standards-knowledge`

`standards-knowledge` SHOULD:

- classify receipt-bearing runtime artifacts in object taxonomy terms
- define how these artifacts enter knowledge-state lifecycle stages

## 11. Explicit non-goals

This binding does not:

- replace Common Workflow Language
- redefine platform runtime profiles
- define Slurm or other scheduler adapters in full
- define a profiling toolchain selection policy
- standardize a global filesystem contract

Those may be layered on top, but they are not the purpose of this document.
