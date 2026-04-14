# Agentic Local-First Fog Mesh — Standards Package

This directory contains the preserved and integrated standards package for the canonical v1 agentic local-first fog mesh baseline.

## Contents

- `canonical-v1-rfc.md` — normative RFC-style baseline
- `registry/` — decisions, KRs, NFRs, owners, and control-plane gates
- `schemas/` — JSON Schemas for the registry surface
- `validate_mesh_spec.py` — repo-runnable validator for the integrated layout
- `control-plane-mapping.md` — mapping from baseline commitments to control-plane enforcement surfaces
- `preservation-manifest.json` — checksum and byte-count ledger for preserved artifacts

## Intent

This package exists to keep the baseline, registries, and enforcement surfaces together so the work is not stranded in local artifacts or parallel drafts. It is intended as the canonical review and integration point inside the standards repository.
