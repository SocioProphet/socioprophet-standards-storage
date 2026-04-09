# GitHub Organization Capture Plan — Polycentric Observer-Control Model

## Why this exists

We need a single placement plan so the polycentric observer-control model lands in the correct repositories without duplicating canonical ownership.

## Canonical split

### 1. Normative doctrine (this repository)

**Repository:** `SocioProphet/socioprophet-standards-storage`

Own here:

- reference model and terminology
- invariants and non-negotiables
- state lattice
- entity / interaction / view doctrine
- trust / flow doctrine
- retention / revocation doctrine
- consistency rules by object class
- ADRs and governance guidance

### 2. Machine-readable contract layer

**Repository:** `SourceOS-Linux/sourceos-spec`

Own there:

- JSON Schemas for entity / interaction / state / view / observation / claim / evidence / inference / action / effect / artifact / policy decision / resource account / trust label / flow rule / retention policy
- conforming example payloads
- JSON-LD / Hydra semantic overlays
- eventual OpenAPI / AsyncAPI bindings where appropriate

### 3. Knowledge-context / ontology companion

**Repository:** `SocioProphet/socioprophet-standards-knowledge`

Own there:

- observer ontology
- knowledge-context conventions
- claim/evidence/inference semantics
- graph / hypergraph / search / browser / IDE projection notes

### 4. Operational profiles

**Repository:** `SocioProphet/prophet-platform-standards`

Own there:

- machine-readable surface profiles
- DevSecOps / CI/CD / observability / RBAC / audit bindings
- compile-target operational guidance
- dashboard / telemetry / audit-log mappings

### 5. Transport binding

**Repository:** `SocioProphet/TriTRPC`

Own there:

- transport mapping for canonical interaction envelopes
- deterministic fixture implications for canonical objects

Do **not** duplicate the normative semantics here.

### 6. Execution binding

**Repository:** `SocioProphet/agentplane`

Own there:

- mapping from canonical interaction / effect / policy decision / artifact objects into execution-evidence artifacts
- execution-surface profile bindings
- replay / evidence / placement integration notes

Do **not** make this the canonical spec home.

### 7. Runtime adoption and lock coordination

**Repository:** `SocioProphet/prophet-platform`

Own there:

- rollout / adoption tracker
- standards lock references
- concrete service and deployment consumption of upstream standards

## Delivery order

1. Land doctrine and ADRs here.
2. Land schemas and examples in `sourceos-spec`.
3. Land ontology and knowledge-context companion notes.
4. Land operational profiles and bindings.
5. Land transport and execution bindings.
6. Update runtime repos to consume the canon by reference, not by copy.

## Anti-patterns

Do not:

- place the entire package only in `agentplane`
- place the entire package only in `TriTRPC`
- bury the canonical doctrine only inside `prophet-platform`
- duplicate schema truth across multiple repos

## Immediate next action

Open a matching schema-capture PR in `SourceOS-Linux/sourceos-spec` that reserves the machine-readable lane for this model.
