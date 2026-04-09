# AgentPlane Governance Note for the Incidence Fabric Contract

## Purpose
This note defines how AgentPlane workflows SHOULD enforce the Incidence Fabric Contract (IFC) in repository-governed delivery.

It is not the canonical semantic specification. It is the repo-native governance and control-plane note that makes the IFC enforceable in day-to-day work.

## Workflow modes
### Direct mode
`direct` mode SHOULD be restricted to changes that do not widen semantic authority and do not alter recoverability or governance semantics.

Examples:
- local documentation edits,
- non-semantic packaging updates,
- low-risk benchmark harness fixes,
- additive backend notes that do not change lowering behavior.

### Branch / PR mode
`branch_pr` mode MUST be used for any change that affects:

- projection kind,
- recoverability class,
- loss modes,
- identity merge or split,
- contradiction visibility,
- lifecycle semantics,
- delegation scope,
- obligation propagation,
- policy or provenance interpretation,
- backend capability profile meaning,
- conformance rules.

## Verify gates
AgentPlane verify SHOULD fail when:

1. a change downgrades from incidence-preserving or star-expansion semantics to dyadic or embedding semantics without a loss certificate;
2. a change broadens delegation scope without bounded expiry, review class, and max depth;
3. a change weakens propagated obligations without explicit review;
4. a change modifies contradiction handling or claim visibility without scenario-aware tests;
5. a backend adapter claims losslessness without a certified capability profile;
6. identity merge / split actions lack explicit governance artifacts.

## Required governance artifacts
For IFC-sensitive changes, the PR or task package SHOULD include:

- projection declaration,
- loss certificate when applicable,
- intended-use scope,
- forbidden-use scope,
- backend capability profile delta,
- contradiction / lifecycle impact note,
- delegation / obligation impact note,
- reference conformance scenarios touched.

## Minimum repo layout recommendation
Projects adopting IFC via AgentPlane SHOULD maintain repo-local control files under a path such as:

```text
.agentplane/ifc/
  profiles/
  loss-certificates/
  query-profiles/
  policy/
  contradictions/
  identity/
  conformance/
```

## Decision posture
AgentPlane MUST be used here as a governance shell around the semantic contract, not as a substitute for the contract.

The semantic model remains IFC. AgentPlane enforces:

- who may change it,
- how changes are reviewed,
- what evidence must accompany change,
- what tasks are blocked when semantic downgrades occur.

## Recommended initial policy
- Treat all projection downgrades as review-required.
- Treat all identity reconciliation actions as review-required.
- Treat all contradiction visibility changes as review-required.
- Treat all obligation weakening as review-required.
- Treat all backend profile changes affecting losslessness claims as review-required.

## Follow-on repo work
The next recommended repo-native additions are:

1. backend profile documents for target engines,
2. repo-local loss-certificate examples,
3. query-profile examples,
4. identity reconciliation playbooks,
5. contradiction test fixtures,
6. reference-stack certification notes.
