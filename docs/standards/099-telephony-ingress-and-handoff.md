# Telephony Ingress and Handoff (Normative)

This document uses RFC 2119 language: **MUST**, **SHOULD**, **MAY**.

## 1. Purpose
This standard defines how voice telephony enters the conversational mesh and how calls transition between automation, human handling, queues, and recorded follow-up.

## 2. Telephony is a distinct ingress class
- PSTN, SIP, WebRTC, and Matrix VoIP **MUST** be treated as telephony/media ingress classes, not generic text-message channels.
- Call events **MUST** be normalized into a `CallEventEnvelope` distinct from `ConversationEnvelope`.
- Telephony and messaging **MAY** converge at the canonical `ContactProfile` and `conversation_uuid` layers, but **MUST NOT** share the same event schema.

## 3. Minimum call state machine
The minimum call states are:
- `ringing`
- `answered`
- `active`
- `held`
- `transferred`
- `voicemail`
- `missed`
- `ended`

A compliant deployment **MUST** preserve state transitions as first-class events.

## 4. Routing outcomes
The minimum routing outcomes are:
- `bot`
- `human`
- `callback_queue`
- `voicemail`
- `transfer`

A system **MUST** persist the final routing outcome for every completed call attempt.

## 5. Handoff rules
- Voice interactions **SHOULD** escalate to a human more aggressively than text interactions.
- When automation cannot continue safely, the system **MUST** provide a deterministic fallback path.
- Deterministic fallback paths **MUST** include at least one of: operator queue, callback queue, or voicemail.
- A system **SHOULD** persist transcript and summary references into the same canonical relationship context when policy permits.

## 6. Operational separation
- Telephony infrastructure **SHOULD** be isolated operationally from bridge infrastructure even when both feed the same canonical ledger.
- Inbound endpoint matching and routing policies **MUST** be deterministic.

## 7. Voice escalation posture
Recommended default posture:
- informational: voicemail or callback queue permitted,
- routine service: automation first with human fallback,
- identity-sensitive or legal/financial: constrained automation or human-first,
- urgent operational: immediate operator escalation.

## Related Standards
- `096-conversational-mesh-canonical-plane.md`
- `097-channel-ranking-and-routing.md`
- `098-profile-resolution-and-channel-upgrade.md`
