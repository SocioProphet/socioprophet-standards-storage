# Conversational Mesh Canonical Plane (Normative)

This document uses RFC 2119 language: **MUST**, **SHOULD**, **MAY**.

## 1. Purpose
This standard defines the canonical sovereign conversation plane for SocioProphet.

It exists to prevent four recurring failures:
1. allowing a bridged external network to become the system of record,
2. conflating endpoint handles with canonical identity,
3. routing operator work directly in public or tenant-bound channels,
4. treating voice telephony as if it were operationally identical to chat.

## 2. Canonical plane
### 2.1 Native sovereign substrate
- Matrix **MUST** be the canonical sovereign messaging substrate.
- Internal operator coordination and durable high-context collaboration **MUST** converge on Matrix-native rooms or a compatible sovereign surface derived from the same canonical plane.
- External networks **MUST NOT** be treated as the canonical archive.

### 2.2 External adapter posture
- SMS/RCS, Telegram, Signal, Messenger, Instagram, iMessage, and Slack **MUST** be treated as ingress/egress adapters.
- Every adapter **MUST** be classified by trust tier and fragility tier.
- Adapter-local storage **MUST NOT** be the sole authority for message history, profile state, or routing decisions.

### 2.3 Local-first authority
- A canonical local ledger **MUST** store normalized conversation and call events before or at the same logical step as downstream automation, policy, or reply generation.
- The canonical local ledger **MUST** remain authoritative even when an external bridge is unavailable.

## 3. Canonical object families
The following object families are normative:
- `ConversationEnvelope`
- `ContactProfile`
- `CallEventEnvelope`
- `ProfileResolutionEvent`

Each family **MUST** publish:
- a versioned schema,
- at least one positive example fixture,
- at least one negative validation fixture for breaking cases.

## 4. Trust and fragility tiers
### 4.1 Trust tiers
- `T0` sovereign: native identities and rooms under direct SocioProphet control
- `T1` stable external: security- or continuity-oriented external channels
- `T2` growth/public external: consumer discovery channels
- `T3` device-bound external: channels whose continuity depends on a dedicated device or linked client
- `T4` tenant-bound external: workspace-scoped installs or shared enterprise tenants

### 4.2 Fragility tiers
- `F0` native protocol
- `F1` managed adapter
- `F2` device-coupled adapter
- `F3` tenant/policy-coupled adapter

Every inbound endpoint **MUST** carry both a trust-tier and fragility-tier classification.

## 5. Internal vs external room separation
- External-channel conversations **MUST NOT** be treated as the operator room of record.
- Internal operator rooms **MUST** be distinct from public or tenant-facing rooms.
- Escalations **MUST** be representable as canonical events even if the originating conversation remains on an external channel.

## 6. Publication and versioning
- Breaking schema changes **MUST** increment a major version and publish migration notes.
- The standards repo **MUST** remain the publication home for normative documents and schemas in this family.

## Related Standards
- `030-service-interfaces-tritrpc.md`
- `040-observability-otel.md`
- `050-security-oidc-policy.md`
- `092-zero-trust-nist-800-207.md`
