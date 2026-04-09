# ADR-040: Canonical Placement for the Agentic Knowledge Platform Package

- Status: Accepted
- Date: 2026-04-09

## Context

SocioProphet work on the "agentic RAG" or broader agentic knowledge platform stack spans multiple repositories with
materially different roles:
- the standards authority repository
- the public docs / integration surface repository
- the runtime and deployment repository
- the knowledge-context repository

Recent architecture and inventory work showed that the platform is broader than a conventional agentic RAG pyramid.
It includes application modules, workflow engines, multimodal runtime, support operations, academy/discovery surfaces,
sovereign local state, and evaluation/feedback lifecycle machinery.

Without an explicit placement decision, these artifacts are likely to drift into whichever repository is currently most
visible, especially the public docs surface.

## Decision

The canonical package for this work SHALL live first in `SocioProphet/socioprophet-standards-storage`.

That canonical package includes:
- normalized layer model
- tooling inventory
- integration patterns
- repository boundary doctrine
- associated ADRs

Public-safe mirrors MAY later be created in `SocioProphet/socioprophet`.
Runtime-specific derivatives MAY later be created in `SocioProphet/prophet-platform`.
Knowledge-context semantic crosswalks MAY later be created in `SocioProphet/socioprophet-standards-knowledge`.

## Consequences

### Positive

- Canonical doctrine is kept in the repo already defined as the standards authority.
- Public docs can remain public-safe mirrors rather than accidental sources of truth.
- Runtime repos can carry derived bindings and contracts without owning the cross-repo doctrine.
- Knowledge-context repos can stay focused on ontology and semantic context rather than broad platform canon.

### Negative

- Some contributors may initially expect architecture pages to live in the public docs repo and may need redirection.
- The standards repo will carry a larger doctrinal footprint and will need disciplined cross-references.

### Neutral / operational

- Public docs should link back to the canonical standards files.
- Runtime docs should identify which upstream standard they implement or bind.
- Future repo-boundary disputes should cite this ADR and the companion repo-boundary standard.

## Rejected alternatives

### Alternative 1: Put the canonical package in the public docs repo first

Rejected because the public docs repo is intentionally not the automatic canonical home for every subsystem or doctrine artifact.
That would create ownership ambiguity and increase drift.

### Alternative 2: Put the canonical package directly in the runtime repo

Rejected because runtime repositories should carry implementation-specific topology, contracts, and bindings derived from standards,
not the cross-repo doctrine itself.

### Alternative 3: Put the canonical package in the knowledge-context repo

Rejected because knowledge-context repositories are appropriate for semantic/ontology-focused derivatives, not the first landing zone
for broad platform layer doctrine.

## Related standards

- `docs/standards/100-agentic-knowledge-platform-layer-model.md`
- `docs/standards/101-agentic-knowledge-platform-tooling-inventory.md`
- `docs/standards/102-agentic-knowledge-platform-integration-patterns.md`
- `docs/standards/103-agentic-knowledge-platform-repo-boundaries.md`
- `docs/standards/006-ecosystem-repos-docs-milestones.md`
- `docs/standards/080-knowledge-context.md`

## Implementation follow-on

The next follow-on work SHOULD be:
1. public-safe mirror pages in `SocioProphet/socioprophet`
2. runtime mapping docs and contract stubs in `SocioProphet/prophet-platform`
3. later semantic crosswalks in `SocioProphet/socioprophet-standards-knowledge`