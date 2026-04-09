# IFC Conformance Fixtures

## Purpose
This directory holds fixture definitions used to validate backend, adapter, and reference-stack conformance with IFC.

## Minimum fixture families
Implementations SHOULD provide fixtures for at least:

1. **Projection downgrade**
   - incidence-preserving to star-expansion
   - incidence-preserving to dyadic projection
   - dyadic projection to embedding compression

2. **Identity operations**
   - merge
   - split
   - mistaken-identity rollback

3. **Claim lifecycle**
   - observation -> candidate -> validated
   - validated -> disputed
   - superseded / retracted / deprecated

4. **Contradiction handling**
   - visible contradictions
   - hidden-until-resolved contradictions
   - scenario-scoped contradictions

5. **Delegation and obligation propagation**
   - bounded delegation
   - obligation carry-through on derivation
   - review-required weakening

6. **Backend posture**
   - lossless claim verification
   - review-required projection downgrade
   - unsafe-task rejection

## Suggested fixture shape
A fixture SHOULD declare:
- fixture id
- target backend / adapter / stack
- input projection kind
- output projection kind
- expected recoverability class
- expected loss modes
- required review kind
- expected pass/fail result

## Status
Scaffold only. Concrete fixture files should be added in follow-on PRs.
