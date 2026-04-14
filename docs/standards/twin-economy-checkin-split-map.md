# Twin economy check-in split map (v0.1)

This document translates the previously generated free-floating twin-economy bundle into canonical repository destinations.

It is intentionally a **split map**, not the final normative content. The goal is to prevent additional orphan artifacts.

## Principles

1. No new schema lands without a canonical repo owner.
2. Replay / checkpoint semantics are not redefined outside `cairnpath-mesh`.
3. Transport mappings are not treated as domain semantics.
4. GAIA only receives domain overlays that actually depend on GAIA sources / entrypoints.
5. Shipping contracts and deployable code land only after the standards layer is stable enough to reference.

## Canonical destinations

### A. `socioprophet-standards-storage`
Owns platform-wide typed state, storage-context contracts, service/data-interface contracts, and benchmark methodology.

Target material:
- `schemas/twin/twin.schema.json`
- `schemas/twin/twin-relationship.schema.json`
- `schemas/twin/objective-vector.schema.json`
- `docs/standards/twin-state-overview.md`
- benchmark workload definitions for twin-state persistence / query / synchronization

Notes:
- This is where the core twin-state shape belongs.
- This repo remains the index + governance layer for sibling standards repos.

### B. `socioprophet-standards-knowledge`
Owns claims, evidence overlays, provenance, validation semantics, and knowledge-context gates.

Target material:
- claim lifecycle semantics used by twins
- provenance / attribution overlays for twin observations and derived claims
- evidence bundle metadata that is not specific to CairnPath step materialization
- docs crosswalking twin claims to knowledge-context standards

Notes:
- Do not move generic storage or action-rights semantics here.
- This repo inherits platform invariants from `socioprophet-standards-storage`.

### C. `socioprophet-standards-agents` (new)
Owns capability descriptors, agent governance contracts, action manifests, trust classes, approval semantics, and policy bundles.

Target material:
- `schemas/action/action-manifest.schema.json`
- `schemas/agents/capability-descriptor.schema.json`
- `schemas/agents/policy-bundle.schema.json`
- `schemas/agents/approval-profile.schema.json`
- docs for hard/soft lane commit rules and human-gate semantics

Notes:
- This is the missing sibling standards repo.
- This repo should import platform invariants from `socioprophet-standards-storage` and knowledge semantics from `socioprophet-standards-knowledge` where needed.

### D. `cairnpath-mesh`
Owns replay, checkpoints, step/result/materialize semantics, frontier bounds, validator fixtures, and CairnPath policy structures.

Target material:
- rewrite the orphan `cairn.schema.json` into aligned CairnPath artifacts
- replay manifest for twin-economy decisions
- fixtures demonstrating twin decision cycle replay
- validator cases for bounded frontier and materialization semantics

Notes:
- Do not keep a standalone Cairn schema outside this repo.
- This repo is the evidence / replay / settlement spine.

### E. `TriTRPC`
Owns deterministic transport framing, fixtures, AUX/control structure, and transport-level verification.

Target material:
- mapping note from twin-economy contracts to TriTRPC routes / AUX bundles
- any generic route naming / envelope mapping needed for twin state, planning, evidence, and action flows
- fixtures only where transport interoperability is the purpose

Notes:
- Do not define the domain object model here.
- Do not place policy or replay semantics here unless they are truly envelope/AUX level.

### F. `prophet-domain-gaia-world-model`
Owns GAIA-linked ontologies, Earth-domain source integration, provenance discipline, canonical entrypoints, and GAIA-specific domain overlays.

Target material:
- bridge doc explaining how twin-economy domain packs consume GAIA resources
- food resilience / supply geography overlays that genuinely depend on GAIA sources
- ontology alignment notes from twin-economy semantics into GAIA canonical entrypoints

Notes:
- Do not place generic cross-domain twin-economy schemas here.
- Do not treat GAIA as the universal home for all domain packs.

### G. `prophet-domain-twin-economy` (new)
Owns cross-domain twin-economy semantic composition and domain packs.

Target material:
- contested logistics domain pack
- food resilience domain pack (platform semantics version)
- field operations domain pack
- semantic composition docs tying together storage, knowledge, agent governance, replay, and transport layers
- worked examples and sample instances

Notes:
- This repo exists because `agent-world-model` is not our semantic home and GAIA is domain-specific.
- This repo should reference GAIA where relevant but not depend on GAIA for all meaning.

### H. `prophet-platform`
Owns shipping services, runtime RPC contracts, deployment wiring, and operational docs.

Target material:
- `rpc/twin/*`
- `rpc/planning/*`
- `rpc/evidence/*`
- service scaffolds such as twin control plane, action gateway, evidence ledger, planner service
- `docs/` implementation plan and 90-day execution plan

Notes:
- Runtime work lands only after the standards and domain layers have canonical references.

## Mapping the previous free-floating bundle

### 1. `overview.md`
Status: **split / rewrite required**

Destination breakdown:
- repo-boundary decision -> `socioprophet-standards-storage/adr/`
- platform-invariant twin-state overview -> `socioprophet-standards-storage/docs/standards/`
- knowledge/evidence crosswalk -> `socioprophet-standards-knowledge/docs/`
- agent governance overview -> `socioprophet-standards-agents/docs/`
- domain composition overview -> `prophet-domain-twin-economy/docs/`
- runtime execution overview -> `prophet-platform/docs/`

### 2. `twin.schema.json`
Status: **keep, but move and expand**

Destination:
- `socioprophet-standards-storage/schemas/twin/twin.schema.json`

Required follow-ons:
- add relationship schema
- add objective vector schema
- add synchronization / merge notes

### 3. `action-manifest.schema.json`
Status: **move to new repo**

Destination:
- `socioprophet-standards-agents/schemas/action/action-manifest.schema.json`

Required follow-ons:
- tie to capability descriptor and approval profile
- define hard/soft lane commit rules

### 4. `cairn.schema.json`
Status: **discard as standalone; rewrite against CairnPath**

Destination:
- `cairnpath-mesh/` as aligned schema + fixtures + validator inputs

Required follow-ons:
- map checkpoint fields to Context / Step / Line / Result / Materialize
- add replay fixture for a twin decision cycle

### 5. `contested-logistics-v0.1.md`
Status: **keep, but move to new domain repo**

Destination:
- `prophet-domain-twin-economy/specs/domain-packs/contested-logistics-v0.1.md`

Required follow-ons:
- bind storage schemas
- bind agent governance contracts
- bind Cairn replay examples
- add TriTRPC route mapping note

### 6. `contested-logistics-90-day-plan.md`
Status: **keep, but move to platform execution layer**

Destination:
- `prophet-platform/docs/plans/contested-logistics-90-day-plan.md`

Required follow-ons:
- convert milestones into runtime service slices and validation gates

## Recommended creation order

1. Accept ADR-040 in `socioprophet-standards-storage`.
2. Create `socioprophet-standards-agents`.
3. Create `prophet-domain-twin-economy`.
4. Reconcile Cairn artifacts into `cairnpath-mesh`.
5. Move twin-state schemas into `socioprophet-standards-storage`.
6. Move action/governance schemas into `socioprophet-standards-agents`.
7. Move domain packs into `prophet-domain-twin-economy`.
8. Move runtime 90-day plan and rpc/service mapping into `prophet-platform`.

## Immediate do-not-do list

- Do not add generic twin-economy schemas directly to GAIA.
- Do not add action/governance contracts directly to `TriTRPC`.
- Do not add replay/checkpoint schemas outside `cairnpath-mesh`.
- Do not place domain-pack semantics directly into `prophet-platform` before standards exist.
- Do not reuse `agent-world-model` for this work.
