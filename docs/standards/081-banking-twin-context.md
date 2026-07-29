# 081 — Banking Twin Context Standard

## Purpose

Define the initial context boundary for SocioProphet banking-firm digital twin work.

## Scope

This standard applies to banking twin state, scenario, capital, filing, evidence, and benchmark artifacts that cross repository or runtime boundaries.

## Normative posture

Implementations MUST preserve:
- tenant identity,
- legal-entity identity,
- as-of date,
- source provenance,
- scenario identity where applicable,
- model-pack identity where applicable,
- evidence and receipt references where applicable.

Implementations SHOULD align financial and legal-entity concepts with FIBO where practical.
Implementations SHOULD align service-domain and runtime boundary names with BIAN where practical.

## Non-goals

This document does not claim full FIBO or BIAN conformance.
It defines the seed context needed for interoperable banking twin artifacts.
