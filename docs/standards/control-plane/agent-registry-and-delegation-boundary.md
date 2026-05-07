# Agent Registry and Delegation Boundary for Control-Plane Contracts

This note corrects the first control-plane contract tranche by making the authority split explicit.

## Authority split

Control-plane contracts must distinguish these domains:

- `agent-registry` owns agent specs, identities, sessions, tool grants, revocation, and runtime authority records.
- `HolographMe` owns human delegation, consent, and acting-for-human authority semantics.
- `agentplane` owns execution admission and run/replay evidence for admitted work.
- `mcp-a2a-zero-trust` owns broker enforcement, policy checks, attestation, and zero-trust boundary behavior.
- `policy-fabric` owns policy approval and compiled policy evidence.

## Contract implications

Capability leases should be able to reference:

- `grant_ref` from Agent Registry,
- `delegation_ref` from HolographMe when acting-for-human authority is involved,
- `admission_ref` from AgentPlane when an event proposes executable work,
- `policy_ref` from Policy Fabric where approval or policy evidence is required,
- `broker_ref` from the enforcing broker where a capability is actually consumed.

## Non-goals

This note does not redefine the full lease schema in this tranche.

It records the authority boundary so the next schema revision can add these references without collapsing distinct ownership domains.
