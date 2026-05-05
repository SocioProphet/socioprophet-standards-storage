# Identity Control Plane Conformance Matrix

## Scope
This matrix describes the minimum conformance outputs expected from each public lane in the current SourceOS/SocioProphet identity-control-plane stack.

| Repo / Lane | Role | Must Publish / Implement | Evidence / Tests Required | Notes |
|---|---|---|---|---|
| trusted-service-identity | Workload identity | SPIFFE/SPIRE identity schema profile; federation guidance; credential rotation rules | Examples; config validation; attestation/federation tests | Owns workload identity, not human semantic identity |
| identity-is-prime-reference | Semantic identity | Event-IR schema; ProofArtifact schema; merge/disclosure admissibility rules; policy-veto examples | Example traces; proof fixtures; policy-veto tests; schema validation | Reference-grade but semantically central |
| human-digital-twin | Export/readiness | Ω state model; HDT decision summary; export/repair policy profile; TritRPC surface | Promotion tests; policy tests; schema validation | Must remain distinct from semantic identity |
| mcp-a2a-zero-trust | Governance schemas | Versioned Grant / AttestationBundle / PolicyDecision / QuorumProof / LedgerEvent schemas; semantic/export proof references | JSON Schema validation; round-trip examples; negative validation tests | Runtime authorization substrate |
| TriTRPC | Transport/receipt | AUX profile for policy/evidence refs; canonicalization rules; profile registry | Cross-language fixture parity; tamper tests; receipt verification tests | Transport carrier, not policy engine |
| agentplane | Execution/evidence | Bundle admission contract; evidence pack schema; replay contract | End-to-end run/validate/evidence/replay tests | Operational enforcement/control plane |
| A2A adapter lane | Agent-to-agent interoperability | Alias map from A2A identifiers to canonical principal tuple; grant and policy decision binding; artifact/evidence reference binding | Negative tests proving A2A agent card metadata cannot authorize execution by itself | A2A is discovery/task/collaboration surface, not canonical identity authority |
| MCP adapter lane | Tool/context/resource interoperability | Alias map for MCP server/tool/resource ids; tool provenance and sandbox posture binding; grant and policy decision binding | Negative tests proving MCP tool/server metadata cannot bypass canonical authorization | MCP exposes capabilities; execution still requires canonical grant/policy binding |
| ANP adapter lane | Network/linked-data agent discovery and negotiation | Alias map for linked-data/decentralized ids; canonical binding for any privileged action; asserted-claim treatment before trust elevation | Negative tests proving ANP/JSON-LD identifiers cannot replace workload identity or runtime grants | ANP-style ids are discovery/semantic refs unless bound by the identity control plane |
| AG-UI adapter lane | Human-agent UI interaction surface | Alias map for UI session/component/event ids; user-intent evidence capture; grant/policy binding before execution | Negative tests proving UI events cannot directly authorize privileged runtime action | AG-UI can provide intent/session evidence, not execution authority |
| socioprophet-standards-storage | Normative registry | ADRs; standards; schema index; conformance profiles | CI validation of schema links, hashes, and examples | Publication home |
| sourceos-a2a-mcp-bootstrap | Bootstrap/dev harness | Canonical verifier; hard CI failure on verification; alignment with published canonicalization rules | `make verify` must fail on drift/tamper | Current local harness needs tightening |

## Cross-repo required fixtures
1. Workload identity → grant issuance fixture
2. Event-IR → proof artifact fixture
3. Proof artifact + HDT decision summary → policy decision fixture
4. Policy decision + grant → TriTRPC AUX carriage fixture
5. Runtime decision → ledger event fixture
6. agentplane replay fixture from prior evidence pack
7. A2A adapter fixture: agent card/task metadata → canonical principal tuple + grant/policy decision refs
8. MCP adapter fixture: tool/resource invocation → canonical principal tuple + grant/policy decision refs + sandbox posture
9. ANP adapter fixture: linked-data/decentralized identifier → asserted alias → canonical principal binding
10. AG-UI adapter fixture: UI event/session intent → runtime grant request → evidence artifact

## Minimum CI gates
- Schema validation
- Cross-reference validation between standards and schema paths
- At least one positive and one negative fixture per artifact family
- Version bump enforcement for breaking changes
- Negative adapter tests proving protocol-local identifiers cannot bypass canonical principal binding, grant issuance, or policy decision checks
