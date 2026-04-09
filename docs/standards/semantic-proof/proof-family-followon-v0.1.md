# Semantic-proof proof-family follow-on v0.1

This follow-on widens the merged semantic-proof core with the remaining first-pass proof family:

- `exclusion`
- `consistency`
- `snapshot_diff`

It also seeds compact pass/fail fixture examples for each proof family so the verifier surface is no longer inclusion-only.

## Why this is a follow-on PR

The original seed PR intentionally stayed narrow enough to establish repo fit, naming, and the first proof-bearing artifacts.
This PR widens the family now that the seed has landed on `main`.

## Intentional scope

Included:
- remaining first-pass proof schemas
- compact pass fixtures
- compact invalid fixtures mapped to explicit verifier failure modes

Excluded:
- policy/rule lowering
- transport-facing method bindings
- runtime receipt ownership
- replay/materialize validator ownership
