# Conversational Mesh Conformance Matrix

## Scope
This matrix defines the minimum standards outputs and evidence expectations for the conversational mesh overlay.

| Lane / Artifact Family | Role | Must Publish / Implement | Evidence / Tests Required | Notes |
|---|---|---|---|---|
| `096-conversational-mesh-canonical-plane.md` | Sovereign conversation plane | Matrix-first canonical plane, trust/fragility tiering, internal/external room separation | Cross-reference validation, schema path validation | Canonical architectural boundary |
| `097-channel-ranking-and-routing.md` | Routing doctrine | ranked channel policy, reply-on-origin, escalation posture, capability-vector rule | Policy examples, routing test cases | Ranking is normative default, not universal market claim |
| `098-profile-resolution-and-channel-upgrade.md` | Identity and migration policy | merge/split state machine, confidence classes, upgrade rules | positive/negative merge fixtures, audit examples | Must support reversible merge/split |
| `099-telephony-ingress-and-handoff.md` | Voice ingress policy | call state machine, routing outcomes, fallback rules | call-state fixtures, handoff fixtures | Telephony remains distinct from chat schemas |
| `schemas/conversational/conversation_envelope.schema.json` | Canonical message event | normalized channel event schema | schema validation, positive/negative examples | core ingress record |
| `schemas/conversational/contact_profile.schema.json` | Canonical profile | local authority profile with handles and routing preference | schema validation, merge-split test linkage | endpoint claims are not identity |
| `schemas/conversational/call_event_envelope.schema.json` | Canonical call event | call-state transitions and routing outcome schema | schema validation, telephony fixtures | separate from message event family |
| `schemas/conversational/profile_resolution_event.schema.json` | Resolution audit artifact | merge/split and confidence transition event schema | positive/negative resolution fixtures | provenance-critical |

## Minimum CI gates
- Schema validation for all four schema families
- Cross-reference validation between standards and schema paths
- At least one positive and one negative fixture per schema family
- Version bump enforcement for breaking schema changes
- Conformance examples for reply-on-origin, channel upgrade, merge reversal, and telephony fallback
