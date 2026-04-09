# 132 — Incidence Fabric Contract (IFC) v0.2

## Status
Draft standard.

## Purpose
Define a canonical graph/fabric contract for SocioProphet systems where higher-order relations, provenance, policy, contradiction, and multi-view compilation must remain explicit.

This standard sits above any one storage model. It treats the canonical semantic layer as incidence-first and allows compiled views into property-graph, semantic-statement, relational, analytical, and embedding-oriented substrates.

## Why this standard exists
Traditional graph implementations blur together four different operations:

1. **Incidence-preserving lowering** — relation and participation identity remain recoverable.
2. **Star expansion** — higher-order membership is represented through an explicit relation vertex or bipartite encoding.
3. **Dyadic projection** — higher-order structure is collapsed into pairwise links and is usually lossy.
4. **Embedding compression** — graph or hypergraph structure is compressed into vectors for downstream ML tasks.

These are not equivalent. Any compliant implementation MUST declare which of these transformations is in use and what loss or recoverability class applies.

## Normative core
An IFC-conformant system MUST provide:

- **Entity identity** as a first-class concern.
- **Relation-instance identity** as a first-class concern.
- **Incidence / participation identity** as a first-class concern whenever role, order, multiplicity, provenance scope, or policy scope matter.
- Distinct property scopes for:
  - entities,
  - relation instances,
  - incidences / participations.
- Explicit support for:
  - provenance,
  - policy decisions,
  - claim lifecycle,
  - contradiction and competing-claim handling,
  - delegation and obligation propagation,
  - view-aware query semantics,
  - loss certificates for projection downgrades.

## Projection taxonomy
Every backend adapter, compiler step, or export MUST declare:

- `projection_kind`
  - `incidence_preserving`
  - `star_expansion`
  - `dyadic_projection`
  - `embedding_compression`
- `recoverability_class`
  - `lossless_structural`
  - `lossless_with_incidence_payload`
  - `lossy_but_task_acceptable`
  - `non_recoverable`
- `loss_modes` from at least:
  - `non_recoverability`
  - `tie_weakening`
  - `multi_cloning`
  - `role_loss`
  - `order_loss`
  - `multiplicity_loss`
  - `incidence_property_loss`
  - `temporal_scope_loss`
  - `policy_scope_loss`
  - `provenance_scope_loss`

## Truth and contradiction semantics
An IFC-conformant system MUST NOT flatten all assertions into a single truth surface.

At minimum, claim and evidence handling MUST distinguish:

- observations,
- candidate claims,
- validated claims,
- disputed claims,
- superseded claims,
- retracted claims,
- deprecated claims.

Implementations MUST support contradiction-aware relationships such as:

- `supports`
- `contradicts`
- `duplicates`
- `refines`
- `supersedes`
- `depends_on`

## Query obligations
A compliant query surface MUST require explicit declaration of:

- `view_family`
- `belief_mode`
- `contradiction_mode`
- `scenario_scope`

Queries MUST NOT silently change semantics by switching from incidence-preserving views to dyadic or embedding views.

## Governance requirements
Any change affecting the following MUST be governance-gated:

- projection downgrade,
- identity merge or split,
- contradiction visibility,
- delegation scope,
- obligation weakening,
- policy interpretation,
- provenance interpretation.

## Recommended compiled views
Recommended compiled views are:

- **reified LPG** for operational serving,
- **semantic-statement / RDF-star-like** publication views for standards-facing metadata exchange,
- **relational audit ledger** for canonical persistence and replay,
- **analytical reductions** only when loss certificates and allowed-use scopes are explicit,
- **embedding views** only as derived artifacts and never as the normative truth layer.

## AgentPlane implications
AgentPlane-governed implementations SHOULD:

- allow `direct` mode only for bounded, non-semantic-safe changes,
- require `branch_pr` mode for projection downgrades, identity actions, contradiction-visibility changes, and obligation/delegation changes,
- fail verify when a downgrade lacks a valid loss certificate,
- record lifecycle and governance decisions under repo-local control files.

## Backend posture
No currently targeted mainstream backend is treated as the canonical truth model.

Implementations SHOULD use IFC as the semantic contract above:

- LPG operational stores,
- semantic / RDF stores,
- embedded analytical graph engines,
- higher-order reasoning substrates,
- graph-over-relational overlays,
- version-aware knowledge stores.

## Initial reference-stack posture
The current recommended reference posture is:

- canonical relational IFC ledger as truth layer,
- reified-LPG operational serving layer,
- semantic publication / governance layer,
- explicit loss-certified analytical and embedding projections.

## Related materials
The following companion artifacts were prepared during this design tranche and should be imported or linked into repo-native standards workflows as follow-on work:

- IFC RFC v0.2
- IFC white paper v0.2
- executable companion and conformance suites
- backend selection and landscape review
- AgentPlane IFC governance overlays

## Follow-on required work
This standard is not complete until the repository also includes:

1. backend capability profiles,
2. loss certificate schemas and examples,
3. query IR schemas and examples,
4. authorization grammar,
5. merge / conflict semantics,
6. contradiction and obligation examples,
7. reference-stack conformance tests.
