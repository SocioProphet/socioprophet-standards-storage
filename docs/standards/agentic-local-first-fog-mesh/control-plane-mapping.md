# Control Plane Mapping v1

This document maps the canonical baseline into enforceable control-plane surfaces. It is subordinate to `canonical-v1-rfc.md` and uses the registry IDs as the authoritative linkage surface.

## 1. Enforcement model

The baseline is enforced through five gate classes:

1. **GDP release gates** for signing, trust-chain validation, quarantine, and rollback
2. **Edge consent gates** for local sovereignty and release authorization
3. **Fog topology admission gates** for RTT and logical-group authorization
4. **Cloud synthesis gates** for privacy and utility validation
5. **Governance gates** for FCR routing, review, and archival

Each gate is declaratively represented in `registry/control_plane_gates.yaml`.

## 2. Mapping table

| Gate | Component | Stage | Enforces | Evidence emitted | Fail behavior |
|---|---|---|---|---|---|
| GATE-GDP-001 | GDP release pipeline | Pre-publish | KR-UPD-01, NFR-SEC-02 | Signed manifest, certificate-chain validation log, artifact digest | Quarantine artifact, stop rollout, page Security Architecture |
| GATE-GDP-002 | Edge agent installer | Pre-install | KR-UPD-01, NFR-SEC-02 | Local verification log, installed version record, rollback decision | Abort install, retain last known good |
| GATE-CNS-001 | Consent policy engine | Pre-release of derived artifact | NFR-SEC-01, NFR-GOV-01, KR-LOC-01 | Policy decision record, data classification, purpose binding, audit log | Deny release, emit policy-conflict event |
| GATE-FOG-001 | Fog topology admission controller | Peer admission | KR-FOG-01, KR-FOG-02, KR-FOG-03, NFR-PER-01 | RTT measurement, mTLS auth record, logical-group membership | Reject peer, trigger rediscovery, topology re-evaluation |
| GATE-SYN-001 | Cloud synthesis pipeline | Pre-publish synthetic output | KR-SYN-01, KR-SYN-02, NFR-PRI-01, NFR-PRI-02 | Privacy run metadata, utility validation report, drift monitor output | Pause synthesis, revert last approved config |
| GATE-FCR-001 | Governance workflow | Baseline change request | KR-GOV-01, NFR-MAI-01, NFR-GOV-01 | FCR record, approval chain, ADR reference, archival receipt | Reject change, restore previous baseline |

## 3. Event surfaces

The control plane should emit the following minimum event classes:

- `gdp.artifact.publish.requested`
- `gdp.artifact.publish.blocked`
- `edge.policy.release.denied`
- `edge.policy.conflict.detected`
- `fog.peer.admission.accepted`
- `fog.peer.admission.rejected`
- `cloud.synthesis.paused`
- `governance.fcr.opened`
- `governance.fcr.approved`
- `governance.fcr.rejected`

## 4. Minimum implementation order

1. GDP signing and installer rejection path
2. Edge consent decision logging
3. Fog admission checks for RTT and mTLS trust
4. Cloud synthesis drift blocking
5. FCR archival and approval-chain enforcement

## 5. Known gap

This mapping defines *what* the control plane must enforce, but not yet the exact transport or event envelope used to carry these decisions. That should be the next integration step against the wire/control-plane design.
