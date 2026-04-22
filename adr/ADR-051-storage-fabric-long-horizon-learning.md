# ADR-051: Storage-Fabric Long-Horizon Threshold Learning

## Status
Accepted

## Context

Fixed threshold policy is useful at bootstrap, but longer benchmark history should improve threshold estimates.

## Decision

When enough usable historical benchmark windows are present, storage-fabric methodology should allow learned thresholds to augment or replace policy fallback thresholds.

## Consequences

- reports should state whether thresholds are learned or fallback
- learned thresholds depend on preserved usable benchmark history
- short history horizons should be reported honestly as immature evidence
