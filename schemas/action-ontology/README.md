# Action Ontology bootstrap schemas

This directory contains the temporary bootstrap schema surface for Action Ontology examples and early integration work.

## Scope

The first bootstrap scope is intentionally small:

- `action-instance.schema.json` — portable shape for an Action-centered record bundle

## Rules

- keep IDs portable
- prefer strict schemas with `additionalProperties: false`
- avoid repository-local assumptions
- keep the schema surface compatible with a later split into a dedicated repo if needed

## Relationship to ontogenesis

Normative ontology terms and SHACL gates belong in `SocioProphet/ontogenesis`.
This directory exists for bootstrap JSON-level interoperability and example validation.