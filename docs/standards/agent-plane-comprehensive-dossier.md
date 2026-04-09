# Agent-plane comprehensive integration dossier

## Purpose

This dossier preserves the broader integration details developed across the agent-plane work so they live in GitHub, not only in PR threads or external notes.

It complements the shorter cross-repo status note already present in this repository.

## Scope

GitHub orgs involved:
- `SourceOS-Linux`
- `SociOS-Linux`
- `SocioProphet`

Core repos involved:
- `SourceOS-Linux/sourceos-spec`
- `SociOS-Linux/imagelab`
- `SocioProphet/agentplane`
- `SociOS-Linux/agentos-starter`
- `SocioProphet/socioprophet-standards-storage`
- `SourceOS-Linux/openclaw`

Clean-room posture:
- the work encodes schema, interface, artifact, validation, benchmark, and runtime-example doctrine
- no proprietary implementation details were copied

## Cross-repo dependency order

1. `sourceos-spec` defines the canonical object family.
2. `imagelab` provides validator/admission scaffolding.
3. `agentplane` expresses control-plane artifact semantics.
4. `agentos-starter` aligns provider interfaces with the merged object family.
5. `standards-storage` defines workload methodology and golden fixture evidence.
6. `openclaw` serves as the runtime proving-ground mapping layer.

## Repo-by-repo status

### 1) `SourceOS-Linux/sourceos-spec`
Role:
- canonical schema lane

Merged outputs include the core runtime-law object family:
- `ExecutionDecision`
- `AgentSession`
- `ExecutionSurface`
- `SkillManifest`
- `MemoryEntry`
- `SessionReceipt`

Merged second-wave objects include:
- `SessionReview`
- `ExperimentFlag`
- `RolloutPolicy`
- `TelemetryEvent`
- `FrustrationSignal`
- `ReleaseReceipt`

The repo also carries additive OpenAPI / AsyncAPI patch files for the runtime-law surface.

Interpretation:
- this lane is the upstream schema source of truth
- follow-up work should be bugfix / canonicalization oriented, not parallel redesign

### 2) `SociOS-Linux/imagelab`
Role:
- validator and admission lane

Merged outputs include:
- capability-descriptor patching
- validator package scaffolding
- validator stubs for `ExecutionDecision`, `SkillManifest`, and `SessionReceipt`

Interpretation:
- validator entrypoints exist
- deeper schema-aware validation remains a future hardening step

### 3) `SocioProphet/agentplane`
Role:
- control-plane artifact lane

Merged outputs include:
- session artifact scaffold
- promotion artifact scaffold
- reversal artifact scaffold
- additive bundle patch fragment

Interpretation:
- control-plane receipt families are represented
- canonical bundle-schema folding can be treated as a later cleanup step if needed

### 4) `SociOS-Linux/agentos-starter`
Role:
- interface convergence lane

The key transition that occurred during this work:
- the baseline interface files were promoted to carry the runtime-law semantics

Baseline files now carrying promoted semantics:
- `interfaces/MemoryAPI.md`
- `interfaces/Orchestrator.md`
- `interfaces/Executor.md`

These baseline files now cover:
- session-oriented orchestration
- defer / resume decision flow
- authored vs learned memory separation
- execution-surface awareness
- receipt-compatible reporting language

Transitional files remain in `interfaces/vNext/`.
A checklist file exists to guide retirement or archival of that transitional surface.

Interpretation:
- the repo should now converge on the baseline interface files as canonical
- `interfaces/vNext/` should not become a permanent second interface surface

### 5) `SocioProphet/socioprophet-standards-storage`
Role:
- workload and fixture evidence lane

Merged outputs include:
- runtime-law workload catalog
- fixture README
- starter golden fixtures for:
  - deferred execution decision
  - deferred session receipt
  - rule memory entry
  - learned memory entry
  - session review
  - review-only execution surface
  - promotion artifact
  - reversal artifact(s)
  - verified release receipt

Interpretation:
- this lane now contains a real starter golden set
- fixture expansion should remain harness-driven rather than speculative

### 6) `SourceOS-Linux/openclaw`
Role:
- runtime proving-ground lane

Merged outputs include:
- `SkillManifest` example files for `coding-agent` and `review-pr`
- `ExecutionSurface` example files for `coding-agent` and `review-pr`
- README / alignment notes documenting why these are examples-first proving-ground artifacts

Interpretation:
- this lane maps live runtime behavior onto the merged contract family
- one policy decision remains: whether examples remain examples or become generated / validator-backed artifacts

## Design interpretation

The architecture work is no longer speculative.
Across the repos above, the following layers now exist in GitHub:
- canonical runtime-law schema family
- validator/admission scaffolding
- control-plane artifact scaffolding
- promoted provider interfaces
- workload and fixture evidence lane
- runtime example / proving-ground lane

The remaining work is cleanup, hardening, and policy decisions—not fundamental redesign.

## Main remaining decisions

### AgentOS Starter
Decision:
- remove or archive `interfaces/vNext/`

Desired outcome:
- one canonical interface surface in the repo

### Standards Storage
Decision:
- keep fixture growth harness-driven

Desired outcome:
- a compact but sufficient golden fixture set for runtime-law validation

### OpenClaw
Decision:
- keep examples as examples, or
- promote them to generated / validator-backed artifacts

Desired outcome:
- explicit policy rather than indefinite ambiguity

## Risks

### Transitional drift
If `interfaces/vNext/` remains indefinitely beside the promoted baseline files, the repo carries two interface surfaces.

### Fixture sprawl
If the fixture set grows without harness demand, it becomes maintenance noise instead of measurement value.

### Example stagnation
If OpenClaw’s example artifacts remain forever without a policy decision, the proving-ground lane stays ambiguous.

## Recommended next order of work

1. Finish AgentOS Starter canonicalization by retiring or archiving `interfaces/vNext/`.
2. Keep Standards Storage fixture growth tied to concrete harness needs.
3. Resolve the OpenClaw example-vs-generated decision.
4. Treat the merged schema, validator, and artifact lanes as upstream truth unless a precise follow-up change is required.

## Practical summary

This work has already moved out of chat and into GitHub.
What remains is no longer “how should the architecture work?”
What remains is:
- cleanup
- hardening
- fixture sufficiency
- runtime proving-ground policy
