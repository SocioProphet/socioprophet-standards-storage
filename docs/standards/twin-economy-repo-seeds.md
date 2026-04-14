# Twin economy repo seeds (v0.1)

This document seeds the two repositories proposed by ADR-040 that cannot be created directly from the current connector surface:

- `socioprophet-standards-agents`
- `prophet-domain-twin-economy`

These are **repo seed specifications**, not substitutes for the actual repositories.

---

## 1. `socioprophet-standards-agents`

### Purpose
Sibling standards package for:
- capability descriptors
- action manifests
- trust classes
- approval profiles
- policy bundles
- hard/soft lane commit semantics
- human/agent governance contracts

### Relationship to existing repos
- Inherits platform invariants from `socioprophet-standards-storage`
- Imports claim/evidence semantics from `socioprophet-standards-knowledge` where needed
- Feeds replayable approval/action semantics into `cairnpath-mesh`
- Feeds route / rpc mapping into `TriTRPC` and `prophet-platform`

### Proposed initial tree

```text
socioprophet-standards-agents/
├── README.md
├── LICENSE
├── SECURITY.md
├── Makefile
├── requirements-dev.txt
├── .github/
│   └── workflows/
│       └── ci.yml
├── adr/
│   ├── README.md
│   └── ADR-000-template.md
├── docs/
│   ├── README.md
│   ├── standards/
│   │   ├── capability-descriptor-overview.md
│   │   ├── action-manifest-overview.md
│   │   ├── trust-tier-model.md
│   │   ├── approval-profile-model.md
│   │   └── hard-soft-lane-commit-rules.md
│   └── crosswalks/
│       ├── storage-dependencies.md
│       ├── knowledge-dependencies.md
│       └── cairnpath-replay-dependencies.md
├── schemas/
│   ├── action/
│   │   └── action-manifest.schema.json
│   ├── agents/
│   │   ├── capability-descriptor.schema.json
│   │   ├── policy-bundle.schema.json
│   │   ├── approval-profile.schema.json
│   │   └── trust-tier.schema.json
│   └── examples/
│       ├── capability-descriptor.example.json
│       ├── approval-profile.example.json
│       └── action-manifest.example.json
└── tools/
    └── validate.py
```

### Proposed first files

#### `README.md`
Should state that this repo defines the normative governance contracts for agent capability, action rights, approvals, and trust boundaries, and that platform invariants remain upstream in `socioprophet-standards-storage`.

#### First ADR
`ADR-010-agent-governance-repo-split.md`
Decision: this repo exists because storage, knowledge, replay, and transport layers are insufficient homes for capability/policy/action-governance semantics.

#### First schema priorities
1. `capability-descriptor.schema.json`
2. `approval-profile.schema.json`
3. `policy-bundle.schema.json`
4. `action-manifest.schema.json`

### Acceptance criteria
- validation gate runs cleanly
- schemas can reference storage/knowledge IDs without redefining them
- one worked approval flow exists for a contested-logistics action commit

---

## 2. `prophet-domain-twin-economy`

### Purpose
Domain and semantic-composition repo for:
- contested logistics
- food resilience
- field operations
- cross-domain twin economy semantics
- worked examples that bind state + knowledge + agent governance + replay + transport

### Relationship to existing repos
- Imports canonical twin-state contracts from `socioprophet-standards-storage`
- Imports knowledge/evidence semantics from `socioprophet-standards-knowledge`
- Imports capability/action governance from `socioprophet-standards-agents`
- Imports replay semantics from `cairnpath-mesh`
- Imports transport mapping conventions from `TriTRPC`
- References GAIA only where domain packs consume GAIA ontologies or source curation
- Feeds deployable service requirements into `prophet-platform`

### Proposed initial tree

```text
prophet-domain-twin-economy/
├── README.md
├── LICENSE
├── SECURITY.md
├── Makefile
├── requirements-dev.txt
├── .github/
│   └── workflows/
│       └── ci.yml
├── docs/
│   ├── README.md
│   ├── architecture/
│   │   ├── twin-economy-overview.md
│   │   ├── domain-composition-model.md
│   │   └── dependency-graph.md
│   ├── worked-examples/
│   │   └── contested-logistics-decision-cycle.md
│   └── gaia-bridges/
│       └── gaia-overlay-policy.md
├── specs/
│   └── domain-packs/
│       ├── contested-logistics-v0.1.md
│       ├── food-resilience-v0.1.md
│       └── field-operations-v0.1.md
├── examples/
│   ├── twins/
│   │   └── contested-logistics-twin.example.json
│   ├── actions/
│   │   └── route-reallocation-action.example.json
│   └── replay/
│       └── contested-logistics-cairn.example.json
└── bindings/
    ├── storage/
    ├── knowledge/
    ├── agents/
    ├── cairn/
    └── transport/
```

### Proposed first files

#### `README.md`
Should describe this repo as the semantic composition and domain-pack layer for the SocioProphet twin economy. It is not the authoritative home for storage contracts, transport, or replay semantics; it composes those layers into domain slices.

#### Initial architecture docs
1. `twin-economy-overview.md`
2. `domain-composition-model.md`
3. `dependency-graph.md`

#### First domain pack priorities
1. contested logistics
2. food resilience
3. field operations

### Acceptance criteria
- each domain pack references upstream standards rather than redefining them
- one worked example spans twin state, action governance, replay, and transport references
- at least one GAIA bridge doc exists for GAIA-dependent overlays without making GAIA mandatory for every domain pack

---

## Recommended creation order

1. Create `socioprophet-standards-agents` from the existing sibling-standards pattern.
2. Create `prophet-domain-twin-economy` with a minimal docs-first skeleton.
3. Move the previously drafted `action-manifest.schema.json` into the new standards-agents repo.
4. Move the previously drafted contested-logistics pack into the new domain repo.
5. Add one worked example that binds both repos to `cairnpath-mesh` and `TriTRPC`.

## What not to do

- Do not seed either repo by copying runtime code from `prophet-platform`.
- Do not let the domain repo redefine storage, replay, or transport semantics.
- Do not let the standards-agents repo become a vague “all agents” dumping ground; it is for normative contracts and governance only.
