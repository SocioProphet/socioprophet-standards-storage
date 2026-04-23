# ADR-052: Storage-Fabric History Horizon Expansion

## Status
Accepted

## Context

Long-horizon threshold learning cannot activate without enough preserved benchmark history.

## Decision

Preserve benchmark-history baselines so methodology can inspect usable historical versions and decide whether long-horizon learning should activate.

## Consequences

- reports should expose the usable history window
- sparse preserved history is acceptable but must not be overstated
- executable harnesses may implement activation logic, but methodology owns the interpretation semantics
