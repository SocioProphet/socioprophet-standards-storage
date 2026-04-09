# Support Cognition Fabric Standards

This directory stages the support cognition fabric baseline inside the standards repository.

## Phase 1 contents
- ADR for the support cognition fabric baseline
- graph family notes
- graph query exemplars
- clean landing rules
- build and validation lane notes

## Purpose
This phase is intentionally documentation-first. It establishes the live repository anchor for the support cognition fabric before landing the larger generated schema, fixture, and codegen surfaces.

## Follow-on lanes
- canonical source YAML packs under `schemas/support/v0/source/`
- support event canon under `events/support/v0/`
- support fixtures under `fixtures/support/v0/`
- generated schemas and CI regeneration hooks once the path shape is accepted
