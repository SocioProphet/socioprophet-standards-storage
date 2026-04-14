# Agent-plane repo index

## Purpose

This index provides a concise map of the repos, PRs, and file families involved in the agent-plane integration work.

For a fuller narrative, see:
- `docs/standards/agent-plane-repo-integration-status.md`
- `docs/standards/agent-plane-comprehensive-dossier.md`

## Merged implementation lanes

### `SourceOS-Linux/sourceos-spec` — PR #1
Role:
- canonical schema lane

Key file families:
- core runtime schemas
- second-wave runtime-law schemas
- additive OpenAPI / AsyncAPI patch files

### `SociOS-Linux/imagelab` — PR #1
Role:
- validator / admission lane

Key file families:
- capability-descriptor patch
- validator package scaffolding
- validator stubs

### `SocioProphet/agentplane` — PR #7
Role:
- control-plane artifact lane

Key file families:
- session artifact scaffold
- promotion artifact scaffold
- reversal artifact scaffold
- additive bundle patch fragment

### `SociOS-Linux/agentos-starter` — PR #1
Role:
- interface convergence lane

Key file families:
- baseline `interfaces/*.md` now carrying promoted runtime-law semantics
- transitional `interfaces/vNext/*` still present for cleanup/archive decision

### `SocioProphet/socioprophet-standards-storage` — PR #6
Role:
- workload and fixture evidence lane

Key file families:
- `benchmarks/workloads/agent-plane-runtime-law.yaml`
- `benchmarks/fixtures/agent-plane/**`

### `SourceOS-Linux/openclaw` — PR #1
Role:
- runtime proving-ground lane

Key file families:
- `examples/skill-manifests/**`
- `examples/execution-surfaces/**`
- proving-ground README / alignment notes

## Documentation lanes

### `SocioProphet/socioprophet-standards-storage` — PR #40
Role:
- repo-native cross-repo status note

### `SocioProphet/socioprophet-standards-storage` — this PR
Role:
- concise navigation index

## Remaining decisions

1. retire or archive `interfaces/vNext/` in `agentos-starter`
2. decide whether OpenClaw examples remain examples or become generated / validator-backed artifacts
3. keep fixture growth harness-driven rather than speculative

## Practical reading order

1. `sourceos-spec`
2. `imagelab`
3. `agentplane`
4. `agentos-starter`
5. `standards-storage`
6. `openclaw`
