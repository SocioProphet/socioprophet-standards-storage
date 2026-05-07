# Channel Ranking and Routing (Normative)

This document uses RFC 2119 language: **MUST**, **SHOULD**, **MAY**.

## 1. Purpose
This standard defines channel ranking, reply routing, and escalation posture for the conversational mesh.

## 2. Ranked channel relevance
The default ranked order is:
1. Matrix
2. SMS/RCS
3. Telegram
4. Signal
5. Messenger / Instagram
6. iMessage
7. Slack

Interpretation:
- Higher rank means greater architectural relevance to the canonical conversational mesh.
- Rank is based on a weighted combination of discoverability, sovereignty, continuity, identity quality, and adapter maturity.
- Rank **MUST NOT** be interpreted as a universal claim about user preference in every market.

## 3. Channel classes
### 3.1 Acquisition channels
- SMS/RCS
- Messenger / Instagram
- public Telegram entrypoints

Acquisition channels **SHOULD** optimize for first contact and low-friction discovery.

### 3.2 Continuity channels
- Telegram
- Signal

Continuity channels **SHOULD** support ongoing user communication without yet becoming canonical authority surfaces.

### 3.3 Sovereign channels
- Matrix

Sovereign channels **MUST** be the preferred durable target for long-lived, document-heavy, operationally important, or high-context collaboration.

### 3.4 Tenant channels
- Slack workspace installs

Tenant channels **MUST** be treated as tenant-scoped integrations, not universal public identities.

### 3.5 Escalation channels
- PSTN / SIP voice
- internal operator Matrix rooms

Escalation channels **MUST** support human handoff and incident/urgent handling.

## 4. Reply routing defaults
- A system **MUST** reply on the channel of origin for first contact unless policy forbids it.
- A system **MUST** persist the routing decision in canonical form.
- A system **SHOULD** offer migration toward Matrix when the relationship becomes durable, sensitive, or operationally important.
- A system **SHOULD** offer migration toward Signal when the user needs a stronger privacy-oriented external channel but is not ready to move to Matrix.
- A system **MUST NOT** require immediate migration merely to acknowledge first contact.

## 5. Channel capability vectors
Every enabled channel **SHOULD** publish a capability vector containing at least:
- `discoverability`
- `sovereignty_control`
- `bridge_maturity`
- `device_coupling`
- `identity_quality`
- `privacy_posture`
- `media_richness`
- `operational_continuity`
- `tenant_dependence`

The vector **MAY** be scored numerically or ordinally, but the scoring rule **MUST** be explicit.

## 6. Operator escalation
- External conversations **MAY** remain on their origin channel while the internal handling and escalation path occurs in operator rooms.
- Operator escalation **MUST** preserve a canonical link to the originating conversation and contact profile.

## Related Standards
- `096-conversational-mesh-canonical-plane.md`
- `098-profile-resolution-and-channel-upgrade.md`
- `099-telephony-ingress-and-handoff.md`
