# Deprecations

This file records compatibility artifacts that remain in the tree but are no longer canonical.

## Deprecated validator path

- `validate_mesh_spec.py`

Reason: retained as an earlier compatibility artifact only. The canonical validation entrypoint is:

- `validate_mesh_spec_ci.py`

## Deprecated manifest surface

- `preservation-manifest.json`

Reason: this file predates the CI validator, control-plane gate schema, workflow, and current-state notes. Reviewers and future maintainers should prefer:

- `CURRENT-STATE.md`
- `branch-state-v2.json`
- `canonical-manifest-v2.json`

## Policy

Deprecated artifacts SHOULD NOT be used as the primary review or enforcement surface.
