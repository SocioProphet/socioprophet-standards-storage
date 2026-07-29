# 082 — Banking Contracts and Lineage Standard

## Purpose

Define the first contract and lineage requirements for banking twin artifacts.

## Required lineage fields

Every cross-repo banking twin artifact SHOULD carry:
- `tenant_id`
- `legal_entity_ref`
- `as_of_date`
- `source_refs`
- `schema_ref`
- `model_pack_refs` where applicable
- `policy_refs` where applicable
- `evidence_refs` where applicable
- `receipt_refs` where applicable

## Contract families

The first banking contract families are:
- twin state snapshot
- stress run
- capital state snapshot
- filing pack
- model evidence pack

## FIBO and BIAN guidance

Contract naming SHOULD prefer FIBO-compatible financial concepts for domain entities.
Service and API boundary naming SHOULD consider BIAN service-domain language.

## Compatibility

Breaking field changes MUST use a new versioned contract path.
Additive fields SHOULD be optional until two consumer repos have adopted them.
