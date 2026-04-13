# ML Execution Adapters v1

## Purpose
Define how governed workflow steps are projected to Beam, Ray, CK, and optional quantum runtimes without creating a second orchestration system.

## Authority split
- Workflow objects: `SocioProphet/sociosphere`
- Placement/execution/replay: `SocioProphet/agentplane`
- Semantic lane definitions: `SocioProphet/ontogenesis`
- Runtime adapters: `SocioProphet/prophet-platform`
- Standards and schema authority: `SocioProphet/socioprophet-standards-storage`

## Executor URI grammar
- `exec://beam/local`
- `exec://beam/dataflow/<region>`
- `exec://ray/local/<node-or-profile>`
- `exec://ray/gcp/train-<region>`
- `exec://ray/gcp/serve-<region>`
- `exec://ck/<env>`
- `exec://quantum/provider/<provider>/backend/<backend>`

## Adapter interface
Each adapter MUST implement:
- `validate_inputs()`
- `resolve_artifacts()`
- `compile_execution_payload()`
- `dispatch()`
- `collect_outputs()`
- `emit_execution_record()`
- `emit_artifact_refs()`

## Beam adapter requirements
- Treat Beam as the transform plane only.
- Emit lineage manifests plus dataset / feature-set artifacts.
- Do not perform model registration directly.
- Record source/output URIs and row-count transitions for each stage.

## Ray train adapter requirements
- Use version-pinned code, image, and config.
- Emit checkpoint, metrics, train manifest, and model artifact candidate outputs.
- Do not allow downstream production use before CK registration succeeds.

## Ray serve adapter requirements
- Fetch only from CK.
- Pin an exact semantic model version.
- Verify the artifact hash after fetch and before load.
- Support canary rollout and rollback.
- Emit a serve-deployment record artifact.

## CK adapter requirements
- Registration MUST be atomic.
- Artifact identity MUST be content-addressable.
- Semantic version tagging MUST be supported.
- Promotion, demotion, retirement, and deletion MUST be immutable audit events.

## Quantum adapter requirements
- Simulator path projects to `compute`.
- Hardware path projects to `egress` and explicit approval.
- Provider / backend / qubit-budget / mitigation MUST be carried in constraints snapshot and artifacts.

## Mapping to workflow kernel
- `capabilityRef` selects the adapter family.
- `placement` selects executor URI and locality.
- `ArtifactRef` carries ML- and quantum-specific `schemaRef`s.
- `ExecutionEnvelope` carries subject, trust refs, input refs, and constraints only.
