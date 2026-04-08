# ADR-040: Twin economy repo boundaries and split plan

- Date: 2026-03-28
- Status: Proposed
- Decision owner: SocioProphet
- Contexts affected: twin state, agent governance, evidence/replay, transport, domain packs, platform runtime

## Context
We have a growing body of twin-economy work spanning:
- typed twin state and objectives
- action manifests and approval semantics
- evidence / replay / checkpoint artifacts
- domain packs such as contested logistics and food resilience
- transport mappings for typed service calls
- runtime services and deployment wiring

The current repo surface already has clear role boundaries:
- `socioprophet-standards-storage` is the platform-wide standards and decision layer for storage contexts, data contracts, interfaces, and benchmarks.
- `socioprophet-standards-knowledge` is the sibling standards package for knowledge-context semantics.
- `TriTRPC` is the deterministic transport + fixture + protocol repository.
- `cairnpath-mesh` owns CairnPath schemas, policy bounds, fixtures, and validator logic.
- `prophet-platform` is the thin shipping platform monorepo for apps, infra, rpc, and runtime schemas.
- `prophet-domain-gaia-world-model` is the GAIA / Earth-domain world-model + ontology + action framework.

The mistake to avoid is creating a free-floating twin-economy repo or dropping cross-cutting artifacts into GAIA, TriTRPC, or prophet-platform without first defining their canonical homes.

A second issue is that we do not currently have a dedicated sibling standards repo for agent capability, action rights, trust classes, approval policies, and governance contracts.

A third issue is that the repository currently named `agent-world-model` is not our semantic home for this work; it is an imported synthetic RL environment project and should not be treated as the canonical twin-economy domain repository.

## Decision
Adopt a split architecture for twin-economy material.

1. Keep `socioprophet-standards-storage` as the **index + governance + platform invariants** repo.
2. Keep `socioprophet-standards-knowledge` as the **claim / evidence / provenance / knowledge validation** repo.
3. Create a new sibling repo named `socioprophet-standards-agents` for **capability descriptors, policy bundles, action manifests, trust tiers, human-gate semantics, and agent governance contracts**.
4. Keep `cairnpath-mesh` as the canonical home for **Cairn / replay / materialize / step-result / frontier-bound / validator** semantics.
5. Keep `TriTRPC` as the canonical home for **transport framing, deterministic fixtures, AUX/control mapping, and transport-level verification**.
6. Keep `prophet-platform` as the canonical home for **shipping services, runtime rpc contracts, deployable schemas, and infra wiring**.
7. Keep `prophet-domain-gaia-world-model` as the canonical home only for **GAIA-linked ontologies, Earth-domain source integration, provenance discipline, and domain overlays that truly depend on GAIA resources**.
8. Create a new domain repo named `prophet-domain-twin-economy` for **cross-domain twin-economy composition, semantic models, and domain packs** that are broader than GAIA and not merely runtime implementation details.

## Options considered
1. Create a standalone `twin-economy-spec` repo and place all schemas + plans there.
2. Put the twin-economy work directly into `prophet-domain-gaia-world-model`.
3. Put the work into `prophet-platform` because runtime services will eventually ship there.
4. Split the work across existing standards / replay / transport / platform repos and add the missing sibling standards + domain repos.

## Tradeoffs
- **Modularity / clarity:** Option 4 preserves clean ownership boundaries and avoids turning any one repo into an incoherent monolith.
- **Cross-repo overhead:** Option 4 adds dependency pinning, vendoring, and documentation sync work.
- **Correctness / reproducibility:** Option 4 aligns replay semantics with `cairnpath-mesh` and transport semantics with `TriTRPC` instead of re-inventing them in-place.
- **Domain scope control:** Option 4 prevents GAIA from becoming a generic catch-all while still allowing GAIA-linked overlays.
- **Runtime velocity:** Option 3 would be simpler short-term, but it would blur standards and shipping code and make later refactoring more painful.

## Measurement plan
This decision is successful when:
1. The twin-economy bundle is decomposed into canonical destinations with no orphan schemas.
2. `socioprophet-standards-agents` and `prophet-domain-twin-economy` exist (or are explicitly accepted as deferred with named interim homes).
3. A cross-repo dependency graph is published and pinned.
4. At least one worked slice (contested logistics) is split cleanly across standards, domain, replay, transport, and platform layers.
5. Validation gates exist for schemas, replay fixtures, and transport mappings.

## Consequences
What becomes easier:
- reasoning about ownership and review paths
- introducing new domain packs without polluting GAIA or runtime repos
- keeping transport, replay, governance, and storage concerns independent but composable
- publishing a clearer public architecture story

What becomes harder:
- more repos to create and maintain
- stricter cross-repo pinning and vendoring discipline
- more explicit versioning and promotion rules

What must be built next:
1. A check-in split map for the current twin-economy bundle.
2. The new sibling repo `socioprophet-standards-agents`.
3. The new domain repo `prophet-domain-twin-economy`.
4. A cross-repo import / dependency manifest.
5. The first worked contested-logistics slice using the new boundaries.
