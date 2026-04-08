# Agentic Control Matrix v3 example package

This directory seeds the released-package shape for the Agentic Control Matrix.

## Included in this seed

- `manifest.json` — package identity and row-count summary
- `matrix_compiler_v3.py` — compact reference compiler that turns summary/detail/test/monitor CSV inputs into policy/monitor/test bundles

## Intentionally omitted from this first landing

The full workbook and compiled bundles remain generated artifacts outside the repository until the release/import flow is locked. This seed PR establishes:

- canonical home
- schema surface
- package identity
- compiler contract
- repository topology

The next landing can add versioned release assets or vendored bundles once the runtime import lane is pinned.
