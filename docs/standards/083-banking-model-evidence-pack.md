# 083 — Banking Model Evidence Pack Standard

## Purpose

Define the first evidence-pack expectations for banking model artifacts.

## Applies to

This standard applies to CCAR, regulatory capital, economic capital, PPNR, credit, market, operational risk, liquidity, and filing-support models.

## Required evidence sections

A banking model evidence pack SHOULD include:
- model identifier and semantic version
- model owner and reviewer
- intended use and prohibited use
- data lineage summary
- parameter snapshot or configuration ref
- scenario refs where applicable
- validation report refs
- challenger / benchmark refs where available
- policy decision refs
- promotion or release receipt refs

## Governance posture

Model evidence packs MUST NOT be treated as model approval by themselves.
Approval requires a policy or governance decision surface.

## RC and EC split

Evidence packs SHOULD clearly distinguish:
- regulatory capital / rule-based outputs,
- economic capital / internal risk-measure outputs,
- overlays and management judgment.
