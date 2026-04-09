# Agent-plane cross-repo integration status

## Purpose

This note captures the current cross-repo state of the agent-plane integration work so the outcome is preserved in GitHub rather than remaining only in chat transcripts or local artifacts.

## Scope

Repos involved:
- `SourceOS-Linux/sourceos-spec`
- `SociOS-Linux/imagelab`
- `SocioProphet/agentplane`
- `SociOS-Linux/agentos-starter`
- `SocioProphet/socioprophet-standards-storage`
- `SourceOS-Linux/openclaw`

Clean-room posture:
- The work encodes schema, interface, artifact, validation, benchmark, and runtime-example doctrine.
- No proprietary implementation details were copied.

## Merged lanes

### `SourceOS-Linux/sourceos-spec`
Merged work established the agent-plane object family, including:
- `ExecutionDecision`
- `AgentSession`
- `ExecutionSurface`
- `SkillManifest`
- `MemoryEntry`
- `SessionReceipt`
- `SessionReview`
- `ExperimentFlag`
- `RolloutPolicy`
- `TelemetryEvent`
- `FrustrationSignal`
- `ReleaseReceipt`

The repo also carries additive OpenAPI/AsyncAPI patch files for the agent-plane API/event surface.

### `SociOS-Linux/imagelab`
Merged work established the validator/admission lane, including:
- capability-descriptor patching
- validator package scaffolding
- validator stubs for `ExecutionDecision`, `SkillManifest`, and `SessionReceipt`

### `SocioProphet/agentplane`
Merged work established the control-plane artifact lane, including:
- session artifact schema scaffold
- promotion artifact schema scaffold
- reversal artifact schema scaffold
- additive bundle patch fragment

## Still-open or still-relevant lanes

### `SociOS-Linux/agentos-starter`
The baseline interface files have been promoted to carry the agent-plane runtime semantics:
- `interfaces/MemoryAPI.md`
- `interfaces/Orchestrator.md`
- `interfaces/Executor.md`

A transitional `interfaces/vNext/` surface still exists and should be removed or archived after reviewers confirm the baseline files are canonical.

### `SocioProphet/socioprophet-standards-storage`
This repo now carries the runtime-law measurement/evidence lane:
- workload catalog for agent-plane runtime law
- fixture README
- starter golden fixtures for:
  - deferred execution decision
  - deferred session receipt
  - rule memory entry
  - learned memory entry
  - session review
  - review-only execution surface
  - promotion artifact
  - reversal artifact
  - verified release receipt

### `SourceOS-Linux/openclaw`
This repo now carries the runtime proving-ground mapping layer:
- `SkillManifest` examples for `coding-agent` and `review-pr`
- `ExecutionSurface` examples for `coding-agent` and `review-pr`
- README / alignment notes explaining that these are examples-first proving-ground artifacts

## Recommended next decisions

### 1. AgentOS Starter
Retire or archive `interfaces/vNext/` so the repo has one canonical interface surface.

### 2. OpenClaw
Decide whether the example files remain stable examples or become generated / validator-backed artifacts.

### 3. Standards Storage
Keep fixture growth harness-driven. Avoid expanding the fixture set unless the harness requires more cases.

## Cross-repo dependency order

1. `sourceos-spec` defines the object family.
2. `imagelab` validates/admits the object family.
3. `agentplane` expresses control-plane artifact semantics.
4. `agentos-starter` aligns provider interfaces to the object family.
5. `standards-storage` defines the workload and fixture evidence lane.
6. `openclaw` maps a live runtime onto the object family.

## Practical interpretation

The architecture work is no longer speculative. The schema, validator, artifact, interface, benchmark, and proving-ground lanes now exist in GitHub. The remaining work is cleanup, promotion, and policy decisions, not fundamental design.
