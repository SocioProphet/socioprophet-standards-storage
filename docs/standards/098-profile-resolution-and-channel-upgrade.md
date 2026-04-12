# Profile Resolution and Channel Upgrade (Normative)

This document uses RFC 2119 language: **MUST**, **SHOULD**, **MAY**.

## 1. Purpose
This standard defines how external endpoints bind to canonical profiles and how conversations may upgrade from first-contact channels to more durable channels.

## 2. Endpoint claims are not identities
- An external handle **MUST** be treated as a claim attached to evidence, not as a canonical identity by itself.
- A canonical `ContactProfile` **MUST** remain authoritative over any single external identity.
- A system **MUST NOT** auto-merge profiles based only on display name, avatar, or linguistic similarity.

## 3. Resolution state machine
The minimum resolution states are:
- `observed_singleton`
- `candidate_link`
- `verified_link`
- `contested_link`
- `split_required`

A system **MUST** preserve provenance for every transition between these states.

## 4. Confidence classes
The minimum confidence classes are:
- `C0` observed only
- `C1` soft heuristic
- `C2` user asserted
- `C3` operator verified
- `C4` cryptographically or operationally proven

Default policy:
- `C0` and `C1` **MUST NOT** trigger automatic merge.
- `C2` **MAY** trigger automatic merge when policy permits and the workflow is not high-risk.
- `C3` and `C4` **SHOULD** be sufficient for merge unless contrary evidence exists.

## 5. Merge and split rules
- A system **MUST** support reversible merges.
- A system **MUST** preserve the audit trail for both merge and split actions.
- A system **MUST** support reassigning message/call ownership after a mistaken merge without losing provenance.

## 6. Channel upgrade policy
- First contact **MUST** default to reply-on-origin unless policy forbids it.
- A system **SHOULD** propose migration to Matrix when the interaction becomes durable, high-context, document-heavy, or operationally important.
- A system **SHOULD** propose migration to Signal when privacy needs increase but Matrix migration is not yet accepted.
- A system **MUST NOT** force channel migration merely to acknowledge a first contact.
- A system **MUST** persist the user’s preferred reply channel and any refusal to upgrade.

## 7. Upgrade triggers
Recommended upgrade triggers include:
- durable multi-turn collaboration,
- exchange of structured artifacts or documents,
- security-sensitive or privacy-sensitive discussion,
- incident or operator workflow involvement,
- channel continuity risk caused by device-bound or tenant-bound transports.

## Related Standards
- `096-conversational-mesh-canonical-plane.md`
- `097-channel-ranking-and-routing.md`
- `099-telephony-ingress-and-handoff.md`
