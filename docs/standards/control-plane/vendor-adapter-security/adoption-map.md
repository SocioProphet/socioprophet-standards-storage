# Vendor Adapter Security Adoption Map

## Purpose

This adoption map turns the vendor-adapter security package from a standards artifact into a cross-repository implementation plan.

The package is already normative and verification-oriented. The remaining work is consumption by runtime, policy, and workspace-control repositories.

## Current standards package state

Canonical package path:

```text
docs/standards/control-plane/vendor-adapter-security/
```

Core artifacts:

- `README.md` — package entry point
- `standard.md` — normative policy standard
- `hardening-spec.md` — implementation-oriented hardening doctrine
- `local-model-gateway-security-baseline.md` — short operator baseline
- `vendor-adapter-security-controls-checklist.yaml` — machine-checkable control manifest
- `vendor-adapter-security-controls.schema.json` — checklist schema
- `verification-matrix.md` — control-to-evidence verification map

## Adoption lanes

| Lane | Repository | Required work | Status |
| --- | --- | --- | --- |
| Standards authority | `SocioProphet/socioprophet-standards-storage` | Package, checklist, schema, verification matrix | Landed |
| Platform runtime | `SocioProphet/prophet-platform` | Pin the standard in `standards.lock.yaml`; bind controls to gateway, identity, office-adapter, and local-model runtime contracts | Not started |
| Execution plane | `SocioProphet/agentplane` | Consume controls in agentic execution admission, work-order validation, and tool-scope policy | Partial: control-plane contract merged; validator still closing |
| Policy plane | `SocioProphet/policy-fabric` | Consume VAS controls in Diff Hygiene / execution-admission verdict reports | Partial: policy contract merged; validator still closing |
| Workspace registry | `SocioProphet/sociosphere` | Track per-repo VAS adoption status and standards-consumption references | Not started |
| SourceOS operator tooling | `SourceOS-Linux/sourceos-devtools` | Bind local-model, native-assistant, network, and portable-AI commands to the local gateway baseline | Partial: devtools repo exists; Portable AI Kit scaffold in progress |
| SourceOS normative spec | `SourceOS-Linux/sourceos-spec` | Reference the standard from local model / native assistant / developer-toolchain topology descriptors | Partial: devtools topology role merged |
| AgentOS assembly | `SociOS-Linux/agentos-spine` | Reference the standard from fog runtime assembly and future manifests | Partial: assembly role note merged |

## Control-to-consumer map

| Control | Primary consumer | Secondary consumers |
| --- | --- | --- |
| `VAS-001` non-loopback auth | `prophet-platform`, `sourceos-devtools` | `agentos-spine` |
| `VAS-002` origin is secondary | `prophet-platform` | `sourceos-devtools` |
| `VAS-003` debug/admin isolation | `prophet-platform`, `sourceos-devtools` | `sociosphere` |
| `VAS-004` no ambient executable scope | `agentplane`, `prophet-platform` | `policy-fabric` |
| `VAS-005` structured tool intent | `agentplane`, `prophet-platform` | `sourceos-devtools` |
| `VAS-006` no permissive argument coercion | `agentplane`, `prophet-platform` | `sourceos-devtools` |
| `VAS-007` planning/execution split | `agentplane`, `policy-fabric` | `prophet-platform` |
| `VAS-008` unique tool IDs | `agentplane`, `prophet-platform` | `sourceos-devtools` |
| `VAS-009` no unsafe credential transport | `prophet-platform`, `sourceos-devtools` | `agentos-spine` |
| `VAS-010` bounded response/subprocess output | `sourceos-devtools`, `prophet-platform` | `agentplane` |
| `VAS-011` protocol honesty | `prophet-platform` | all adapters |
| `VAS-012` docs/runtime consistency | all consuming repos | `sociosphere` registry |

## Required implementation sequence

### 1. Standards discovery closure

Update root and control-plane indexes so the package is visible from repository entry points.

Target files:

- `README.md`
- `docs/standards/control-plane/README.md`

This step is intentionally separated because safe in-place README updates require an update-capable write path.

### 2. Checklist validation closure

Validate `vendor-adapter-security-controls-checklist.yaml` against `vendor-adapter-security-controls.schema.json` in CI.

Expected evidence:

- GitHub Actions workflow result
- local validation command or equivalent inline CI command

### 3. Platform consumption

Add the vendor-adapter standard to `prophet-platform/standards.lock.yaml` as a controlled normative standard import.

Runtime targets should include:

- `apps/gateway`
- `apps/identity-prime`
- office adapter profiles
- local model routing
- network/native-assistant bridge planning surfaces

### 4. Policy and execution-plane enforcement

Close the current Policy Fabric validator lane, then consume it from AgentPlane work-order validation.

Expected closure:

- Policy Fabric diff hygiene validator merged
- AgentPlane work-order validator merged
- AgentPlane schema index cleanup merged
- work-order examples include policy-verdict evidence refs

### 5. SourceOS devtools/local gateway binding

Bind `sourceosctl` local-model, portable-AI, native-assistant, and network command groups to the local-model-gateway baseline.

Required checks:

- no prompt egress by default
- dry-run by default
- no ambient tool execution
- explicit `--execute --policy-ok` for materialization
- secret-free evidence records
- strict remote-bind refusal or explicit unsafe override

### 6. Estate registry tracking

Add VAS adoption status to Sociosphere registry snapshots.

Suggested status values:

- `not_started`
- `referenced`
- `schema_pinned`
- `validator_present`
- `runtime_enforced`
- `ci_enforced`
- `blocked`

## Near-term backlog

1. Add CI validation for the checklist/schema pair in this repository.
2. Patch repository indexes for package discovery.
3. Pin the package into `prophet-platform/standards.lock.yaml`.
4. Land Policy Fabric validator closure.
5. Land AgentPlane validator/index cleanup closure.
6. Add VAS adoption registry tracking in Sociosphere.
7. Bind SourceOS devtools local-model/portable-AI surfaces to the baseline.

## Non-goals

This adoption map does not prescribe any external vendor adapter, closed provider runtime, or third-party implementation. It exists only to coordinate internal standards consumption and enforcement.
