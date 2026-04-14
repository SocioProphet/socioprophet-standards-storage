# 142. Action Ontology Edge and Bridge Cases (v0.1)

## Purpose

This note defines the first negative-case and cross-pattern interaction surface for the bootstrap Action Ontology package.

## Negative cases in scope

The bootstrap suite now includes bundles that MUST fail validation:

- missing-state bundle
- Contract Net bundle with missing `done.refAction`
- Pub/Sub bundle with missing `ack`
- ContractNet↔PubSub bridge bundle with missing publish bridge

These negative bundles exist to prove the validators reject obvious protocol and reference drift rather than only accept happy-path examples.

## Cross-pattern bridge in scope

The first bridge profile is:

- Contract Net `cfp` trace with `taskId`
- matching Pub/Sub `publish` trace carrying the same `taskId`

This is a lightweight bootstrap bridge, not yet a full cross-pattern semantics framework.

## Validation tools

- `tools/action_ontology_bundle_check.py`
- `tools/action_ontology_pattern_check.py`
- `tools/action_ontology_negative_check.py`
- `tools/action_ontology_validate_all.sh`

## Summary

The bootstrap Action Ontology package now validates both positive examples and deliberate failure cases, and includes a first cross-pattern bridge profile for ContractNet↔PubSub interaction.
