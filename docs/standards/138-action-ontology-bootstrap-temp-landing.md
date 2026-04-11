# 138. Action Ontology Bootstrap Temporary Landing (v0.1)

## Status

Temporary staging note.

## Purpose

This document defines how the Action Ontology bootstrap package is staged while a dedicated runtime-facing repository does not yet exist.

The Action Ontology work is a cross-cutting standards surface for:

- agent/action/state/trace object contracts
- JSON-LD semantic overlays
- coordination pattern examples
- bootstrap validation rules
- future runtime consumers such as `agentplane`

## Split landing model

The package is intentionally split:

1. **Semantic core** lands in `SocioProphet/ontogenesis`.
2. **Bootstrap executable standards pack** lands here in `SocioProphet/socioprophet-standards-storage`.

This keeps ontology-source discipline separate from portable standards examples and validation helpers.

## What MAY land here temporarily

- normative standards prose
- JSON Schema contracts
- portable examples and fixtures
- lightweight verification helpers
- interoperability notes linking to ontology and transport layers

## What SHOULD NOT become permanent here

- long-lived runtime orchestrators
- provider-specific adapters
- production queue workers
- large generated outputs

## Cross-repository authority chain

- platform governance and bootstrap contracts: `SocioProphet/socioprophet-standards-storage`
- ontology source and semantic gates: `SocioProphet/ontogenesis`
- transport / framing / deterministic wire contract: `SocioProphet/TriTRPC`
- runtime consumer plane: `SocioProphet/agentplane`

## Summary

This repository is the correct temporary landing zone for the executable/bootstrap side of the Action Ontology package. It is not the permanent home of future runtime implementations.