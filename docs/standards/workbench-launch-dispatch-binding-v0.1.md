# Workbench Launch Dispatch Binding v0.1

Status: Draft

Canonical standards authority: `SocioProphet/socioprophet-standards-storage`

Primary workbench producer: `SocioProphet/sociosphere`

Primary runtime consumer: `SocioProphet/prophet-platform`

Runtime-profile overlay authority: `SocioProphet/prophet-platform-standards`

## 1. Purpose

This document defines the binding between the workbench-side `LaunchConfig` projection and the scheduler-facing dispatch posture required to launch work under the current workbench/run/receipt spine.

It introduces the concept of a `LaunchDispatchRecord` as a scheduler-facing projection that captures dispatch state and identifiers without replacing:

- `ExecutionRecord`
- `RunBundle`
- `maipj-run-receipt`
- evidence receipt families

## 2. Non-negotiable authority rules

### 2.1 Workbench launch authority

`SocioProphet/sociosphere` remains the canonical authority for:

- `LaunchConfig`
- workbench-side launch refinements
- `LaunchDispatchRecord` projection schema

### 2.2 Receipt and evidence authority

`SocioProphet/socioprophet-standards-storage` remains the canonical authority for:

- run bundle canon
- MAIPJ receipt canon
- evidence receipt families
- binding rules that map launch and dispatch posture into receipt and execution evidence

### 2.3 Runtime-profile authority

`SocioProphet/prophet-platform-standards` remains the authority for:

- runtime profile overlays
- scheduler observability posture
- resource-limit and immutable-node policies
- storage-fabric constraints

### 2.4 Runtime adapter authority

`SocioProphet/prophet-platform` remains the authority for concrete runtime adapter implementations, such as local and Slurm dispatch helpers.

## 3. Binding summary

The launch/dispatch binding is defined as follows:

- `LaunchConfig` is the workbench-side request refinement object.
- `LaunchDispatchRecord` is the scheduler-facing projection that captures dispatch identifiers and posture.
- `ExecutionRecord` remains the canonical execution-phase evidence surface.
- `LaunchDispatchRecord` may be cited by `ExecutionRecord` and receipt evidence, but it MUST NOT become a competing execution truth surface.

## 4. Canonical object crosswalk

| Workbench / runtime object | Canonical meaning | Required downstream use | Notes |
| --- | --- | --- | --- |
| `LaunchConfig` | Launch request refinement over one `WorkflowRun` and one `ExecutionEnvelope` | Consumed by runtime adapter | Workbench-side declaration only |
| `LaunchDispatchRecord` | Scheduler-facing dispatch posture and identifiers | Referenced by `ExecutionRecord` evidence and receipt bundles | Projection, not receipt canon |
| `ExecutionRecord` | Execution-phase evidence including dispatch/result posture | Canonical execution truth | Remains above dispatch record in authority |
| `maipj-run-receipt` | Normalized runtime receipt | MAY include dispatch posture derived from `LaunchDispatchRecord` | Receipt canon stays authoritative |

## 5. Dispatch posture rules

### 5.1 Local dispatch

For `schedulerKind=local`, a `LaunchDispatchRecord` SHOULD capture:

- `dispatchStatus`
- `resourceSnapshot`
- optional local queue or worker label
- placement posture when known

A local dispatch MAY omit `schedulerJobId` when no external scheduler allocates one.

### 5.2 Slurm dispatch

For `schedulerKind=slurm`, a `LaunchDispatchRecord` SHOULD capture:

- `schedulerJobId`
- `queueRef` or partition reference
- placement details such as cluster and partition
- dispatch status transitions from `submitted` to `accepted` and beyond

### 5.3 Non-goal: scheduler semantics replacement

`LaunchDispatchRecord` MUST NOT attempt to replace native scheduler truth or emulate the full native scheduler object model. It only captures the normalized dispatch facts needed by the workbench/run/receipt spine.

## 6. Required field preservation

The following fields MUST survive dispatch normalization:

- `launchId`
- `runId`
- `schedulerKind`
- dispatch status
- queue or partition references when applicable
- scheduler job identifier when applicable
- resource snapshot when known
- evidence references tying dispatch posture back to execution truth

## 7. Minimal reference implementation requirement

The first conforming reference implementation SHOULD provide:

- a local adapter that projects `LaunchConfig` into `LaunchDispatchRecord`
- a Slurm stub adapter that returns a normalized `LaunchDispatchRecord` shape without requiring a live cluster
- tests proving that the dispatch record can be linked to the current local-runner execution flow

## 8. Follow-on integration

Once the dispatch layer is stable, the next binding tasks are:

1. wire `LaunchDispatchRecord` into `ExecutionRecord` evidence references
2. surface dispatch posture in normalized MAIPJ receipts where appropriate
3. fold scheduler adapter execution into the canonical unified runtime shell
