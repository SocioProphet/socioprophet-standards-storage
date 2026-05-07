# ADR-041 — Conversational Mesh Composition

## Status
Accepted (draft publication overlay)

## Context
SocioProphet needs a sovereign, local-first conversation fabric that can meet users where they already are without allowing any external platform to become the system of record.

The current platform direction requires:
- an open, self-hosted native channel for durable collaboration and operator routing,
- adapter lanes for public discovery and first-contact channels,
- a canonical local profile and message ledger independent of any bridge database,
- explicit separation between messaging ingress and telephony ingress,
- deterministic escalation paths into internal Matrix/ChatOps operator rooms.

Without a published composition contract, channel adapters can drift into becoming de facto authority surfaces, profile linkage can become unsafe, and telephony can be incorrectly treated as generic chat.

## Decision
We publish a canonical conversational mesh composition with the following split:

1. **Native sovereign lane**
   - canonical open substrate: Matrix
   - primary duties: durable conversation, internal routing, operator coordination, escalation

2. **Public ingress lane**
   - channel adapters: SMS/RCS, Telegram, Signal, Messenger/Instagram, iMessage, Slack tenant installs
   - primary duties: discovery, acquisition, first contact, continuity

3. **Canonical normalization lane**
   - canonical objects: `ConversationEnvelope`, `ContactProfile`, `CallEventEnvelope`, `ProfileResolutionEvent`
   - primary duties: local-first storage, evidence capture, policy inputs, replayability

4. **Routing and upgrade lane**
   - canonical decisions: reply-on-origin, channel upgrade, human handoff, operator escalation
   - primary duties: preserve user convenience while converging durable work toward sovereign channels

5. **Telephony lane**
   - canonical media classes: PSTN, SIP, WebRTC, Matrix VoIP
   - primary duties: inbound call handling, callback/voicemail routing, transcript/summary capture

## Consequences
- External handles are no longer treated as identities; they are attached claims bound to a canonical local profile.
- Matrix becomes the preferred durable and sovereign channel, but not the only ingress path.
- SMS/RCS and other public channels remain useful without being allowed to become archival authority.
- Voice and text are unified at the profile/conversation layer but remain distinct envelope families.
- Internal operator rooms and external channel rooms are explicitly separated.

## Follow-on work
- publish canonical conversation/profile/call/profile-resolution schemas
- publish conformance matrix and phase-1 deployment profile
- wire downstream implementations to bridge health monitoring and human handoff state
- publish device-bound channel failure runbooks
