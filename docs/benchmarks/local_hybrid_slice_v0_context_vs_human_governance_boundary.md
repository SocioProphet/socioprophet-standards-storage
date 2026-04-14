# Local-Hybrid Benchmark Boundary: Context vs Human Governance

This note clarifies a standards-lane separation that should remain explicit as benchmark and schema work evolves.

## Separation rule

The local-hybrid slice benchmark depends on both governed context and human-governance state, but these are separate architectural planes.

### Governed context plane
**Repository:** `slash-topics`

Benchmark-relevant concerns:
- pack identity and digest integrity
- locality class
- provenance and freshness
- cache-hit behavior
- remote fetch and movement costs

### Human-governance plane
**Repository:** `human-digital-twin`

Benchmark-relevant concerns:
- policy bundle identity
- consent state
- approval requirement/outcome
- attestation references
- replay implications for human-governed decisions

## Why this matters in the standards lane

If benchmark notes or schemas compress these two planes into a single generic metadata concept, the resulting contracts become harder to govern, harder to replay, and easier to misuse.

The benchmark lane should therefore preserve the split:
- context metrics stay tied to governed context surfaces
- approval/consent/policy metrics stay tied to the human-governance surface
- receipts may reference both, but the standards model should not erase the ownership boundary

## Related docs

- `docs/benchmarks/local_hybrid_slice_v0.md`
- `docs/standards/control-plane/repository-topology.md`
