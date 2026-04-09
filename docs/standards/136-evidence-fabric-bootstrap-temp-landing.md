# 136. Evidence Fabric Bootstrap Temporary Landing (v0.1)

## Status

Temporary staging note.

## Purpose

This document explains how evidence-fabric work is being staged while the dedicated repo family does not yet exist.

The intended long-term repo family is:

- `evidence-contracts`
- `evidence-broker`
- `evidence-connectors-gdrive`
- `evidence-connectors-icloud`
- `evidence-validator`
- `evidence-storage-infra`

Because repository creation is not yet available in the current connector path, initial bootstrap assets MAY be staged temporarily in `socioprophet-standards-storage`.

## Temporary landing rules

### What MAY land here temporarily

- evidence contract seed schemas
- object-model notes
- bootstrap examples and fixtures
- broker manifest and validation notes
- storage-infra topology notes

### What SHOULD NOT become permanent here

- long-lived runtime broker code
- full connector implementations
- production storage deployment code
- large generated parser outputs

## Split-out rule

Any temporary evidence-fabric landing in this repository SHOULD be designed so it can be moved into a dedicated repo later with minimal path and semantic change.

That means temporary assets SHOULD:

- use stable object names,
- avoid repository-local assumptions,
- avoid coupling schema IDs to this repo path,
- remain valid when copied into the future dedicated repo family.

## Immediate bootstrap sequence

1. land architecture note
2. land seed evidence schemas
3. land local-file broker manifest contract
4. land validation and fixture notes
5. split into dedicated repos when repo-creation path is available

## Summary

This repository is a temporary standards-side landing zone for the evidence fabric bootstrap only. It is not the intended permanent home of the operational evidence-plane implementation.
