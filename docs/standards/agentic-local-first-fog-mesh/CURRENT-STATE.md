# Current State — Agentic Local-First Fog Mesh Standards Package

This file supersedes earlier navigation notes where they conflict with the live branch contents.

## Canonical validation entrypoint

The canonical validator for branch and CI use is:

- `validate_mesh_spec_ci.py`

The earlier `validate_mesh_spec.py` is retained only as an earlier compatibility artifact and should not be treated as the primary enforcement path.

## CI status surface

The package now includes:

- `.github/workflows/validate-mesh-spec.yml`
- `schemas/control_plane_gates.schema.json`
- `validate_mesh_spec_ci.py`

These were added after the original preservation manifest and after the initial draft PR body was created.

## Preservation note

The branch should be treated as the primary preservation surface. Local downloadable bundles remain secondary recovery artifacts.

## Review note

PR comments document the post-PR enforcement additions so reviewers can reconcile the original PR body with the current branch state.
