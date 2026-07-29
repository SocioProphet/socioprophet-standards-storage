# Scoped Disclosure and Room Contract Standard v0

Status: Draft v0  
Authority: Governance-oriented standard for citizen-first and institution-safe disclosure surfaces  
Canonical repo role: This document is the normative doctrine layer for scoped disclosure, bounded pseudonymity, masked participation, relay control, reveal governance, and replayable moderation.

## 1. Purpose

This standard defines how SocioProphet systems MAY support candid human disclosure without collapsing into either:

1. fully attributable public speech for every context, or
2. ungoverned anonymous speech with no meaningful accountability path.

The goal is a governed middle layer: **scoped disclosure**.

Scoped disclosure treats identity as persistent at the root and selectively projected at the surface. It assumes that a human actor remains real and governable, while what other parties can know about that actor varies by room contract, discourse class, relay rights, and adjudication policy.

This standard exists because ordinary identity-forward social systems suppress candid speech, while naive anonymous systems often drift into gossip, harassment, rumor, extortion, or unverifiable accusation. The system requirement is therefore not “anonymity” in the abstract. The requirement is **context-bounded candor with explicit governance**.

## 2. Scope

This standard governs:

- room contracts for bounded disclosure contexts
- actor projection modes
- discourse classes and their default policy posture
- relay and re-share rules
- reveal and adjudication rules
- minimum anti-inference controls
- retention and export posture
- evidence and replay obligations

This standard does **not** define:

- the deterministic wire format
- the executor implementation
- the local storage engine
- the user-interface presentation layer

Those concerns are owned by sibling repositories.

## 3. Cross-repository ownership

This document is the doctrine and governance source of truth. Downstream repositories consume it as follows:

- `SocioProphet/identity-is-prime-reference` — root actor and projection semantics, fog-first scoping, worked examples
- `SocioProphet/TriTRPC` — typed method catalog, fixture pack, transport-facing request/response shapes
- `SocioProphet/sociosphere` — local-first room materialization, manifest handling, local relay/storage precedence
- `SocioProphet/agentplane` — tenant-side adjudication, reveal execution, evidence-bearing moderation tasks
- `SocioProphet/cairnpath-mesh` — replayable disclosure, moderation, reveal, and divergence artifacts
- `SocioProphet/socioprophet` — public explanation, docs surfacing, non-canonical product narrative

## 4. Normative language

The key words **MUST**, **MUST NOT**, **SHOULD**, **SHOULD NOT**, and **MAY** are to be interpreted as normative requirements.

## 5. Core model

### 5.1 Root actor

A **Root Actor** is the persistent human or institutional actor at the base of the identity model.

Requirements:

- A system implementing scoped disclosure **MUST NOT** treat masking as destruction of the root actor.
- A disclosure event **MUST** be attributable to a root actor within the governed trust boundary, even when the audience cannot resolve that actor.
- The root actor record **MUST** remain distinct from any surface alias, room pseudonym, or masked token.

### 5.2 Projection

A **Projection** is a context-specific presentation of a root actor.

Supported projection modes:

1. **Attributable** — audience can resolve the author identity.
2. **Scoped pseudonymous** — audience sees a stable alias only within a room or bounded context.
3. **Masked** — audience sees no stable author identity, while governed reveal may still be possible.

Requirements:

- Projection mode **MUST** be declared per room and/or per event class.
- Projection mode **MUST NOT** silently widen from masked or scoped pseudonymous to attributable.
- Any reveal from a non-attributable mode **MUST** produce an evidence artifact.

### 5.3 Room contract

A **Room Contract** is the policy object that defines the governance boundary for a disclosure context.

A conforming room contract **MUST** specify at least:

- `room_id`
- `purpose`
- `membership_rule`
- `projection_policy`
- `minimum_anonymity_set`
- `allowed_discourse_classes`
- `relay_policy`
- `moderation_policy`
- `reveal_policy`
- `retention_policy`
- `evidence_policy`

A conforming implementation **SHOULD** also specify:

- timing-obfuscation policy
- alias-rotation policy
- external-export policy
- challenge and appeal path

### 5.4 Discourse class

A **Discourse Class** is a policy-bearing type assigned to a disclosure event.

Minimum baseline classes:

- `confessional`
- `support_request`
- `general_discussion`
- `humor_or_low_stakes_banter`
- `allegation_or_accusation`
- `operational_incident`
- `civic_report`
- `moderator_only_signal`

Requirements:

- Every disclosure event **MUST** carry exactly one primary discourse class.
- Each class **MUST** have explicit defaults for relay, retention, moderation visibility, and evidence burden.
- `allegation_or_accusation` **MUST NOT** inherit the same defaults as `confessional`.
- `operational_incident` and `civic_report` **SHOULD** support optional evidentiary attachments or linked evidence references.

### 5.5 Relay grant

A **Relay Grant** is the bounded permission that determines how a disclosure may move beyond its initial room or audience.

Minimum relay modes:

- `none`
- `room_only`
- `bounded_secondary_room`
- `moderator_only`
- `policy_authorized_external`

Requirements:

- Relay rights **MUST** be explicit.
- Relay rights **MUST NOT** default to open-ended viral fan-out.
- Relay decisions outside the room default **MUST** emit a relay evidence artifact.

### 5.6 Reveal authority

A **Reveal Authority** is the policy-recognized actor or quorum authorized to request or approve identity reveal for a non-attributable disclosure.

Requirements:

- Reveal authority **MUST** be declared in the room contract.
- Reveal authority **MUST NOT** be implicit operator omniscience.
- Reveal **MUST** require a reason code and an evidence trail.
- Reveal authority for severe classes such as `allegation_or_accusation` or `credible_harm_signal` **SHOULD** be quorum-based rather than unilateral.

## 6. Baseline room contract requirements

A conforming implementation **MUST** enforce the following baseline rules.

### 6.1 Audience and membership

- Membership **MUST** be explicit, provable, or derivable from a governed trust edge.
- Contact-list upload alone **MUST NOT** be treated as sufficient governance.
- Room membership changes **MUST** be recorded as evidence-bearing governance events.

### 6.2 Minimum anonymity set

- Masked posting **MUST** define a minimum effective anonymity set.
- If the current audience size falls below that minimum, the system **MUST** either block masked posting, degrade to a safer projection mode, or delay delivery until the minimum set is satisfied.
- Small-room masked posting **SHOULD** apply stronger anti-inference measures.

### 6.3 Retention

- Retention policy **MUST** be explicit per room.
- Rooms involving sensitive disclosure **SHOULD** support shorter retention and limited export.
- Governance, moderation, and reveal artifacts **MUST** be retained long enough to support audit, challenge, and replay.

### 6.4 Export

- Raw participant export **MUST** respect room contract and discourse class.
- External export of masked or scoped pseudonymous content **MUST NOT** widen author identity by default.
- Institution-facing export **SHOULD** support redacted and fully governed forms.

## 7. Discourse policy defaults

The following baseline defaults apply unless a stricter room contract overrides them.

### 7.1 Confessional

- default projection: masked or scoped pseudonymous
- default relay: room_only
- default moderation visibility: limited
- default evidence burden: low
- default export: redacted only

### 7.2 Support request

- default projection: masked or scoped pseudonymous
- default relay: room_only or moderator_only
- default moderation visibility: limited with escalation path
- default evidence burden: low

### 7.3 Allegation or accusation

- default projection: masked or scoped pseudonymous
- default relay: moderator_only until review
- default moderation visibility: elevated
- default evidence burden: medium or high depending on claimed harm
- default reveal posture: policy-controlled and auditable

### 7.4 Operational incident

- default projection: attributable or scoped pseudonymous depending lane
- default relay: policy_authorized_external
- default moderation visibility: elevated
- default evidence burden: medium or high
- default replay obligation: required

### 7.5 Civic report

- default projection: masked, scoped pseudonymous, or attributable depending threat model
- default relay: bounded_secondary_room or policy_authorized_external
- default moderation visibility: elevated
- default evidence burden: medium or high

## 8. Anti-inference controls

A conforming implementation **MUST** address the fact that nominal masking is often defeated by timing, phrasing, topic selection, or small audience size.

Minimum controls:

- audience-size checks for masked posting
- metadata minimization
- no unnecessary author-side device leakage to participants
- no automatic display of proximity hints that shrink the anonymity set

Recommended controls:

- timed batching or delivery jitter for small rooms
- scoped alias rotation under contract rules
- reply-thread guardrails that avoid accidental deanonymization
- moderation tooling that surfaces inference risk before publish

## 9. Reveal and adjudication

### 9.1 Reveal request

A reveal request **MUST** include:

- target event or actor projection reference
- requester identity or authority role
- reason code
- policy basis
- requested reveal scope

### 9.2 Reveal decision

A reveal decision **MUST** include:

- decision outcome
- deciding authority or quorum record
- rationale
- scope of identity disclosure
- timestamp
- replay reference

### 9.3 Reveal constraints

- Reveal **MUST** be least-privilege and scope-bounded.
- Reveal **MUST NOT** automatically imply public attribution.
- Reveal for moderation **SHOULD** remain hidden from ordinary room participants unless policy requires otherwise.
- All reveal flows **MUST** emit evidence artifacts.

## 10. Evidence and replay

A scoped disclosure system **MUST** emit replayable, auditable artifacts for the core governance path.

Minimum artifact families:

- `DisclosureEvent`
- `RelayReceipt`
- `ModerationDecision`
- `RevealRequest`
- `RevealDecision`
- `WithdrawalEvent`
- `ChallengeEvent`
- `RoomMembershipChange`
- `RoomContractRevision`

Requirements:

- Every artifact **MUST** be linked to a replayable event lineage.
- Contract revisions **MUST** be versioned.
- A room state materialization **SHOULD** be reconstructable from disclosure, moderation, membership, and reveal artifacts.

## 11. Separation of concerns

This standard intentionally separates:

- **identity root** from **identity projection**
- **room contract** from **transport method**
- **moderation decision** from **reveal action**
- **public explanation** from **canonical doctrine**

That separation is necessary to prevent consumer-social ambiguity from contaminating institutional governance surfaces.

## 12. Initial acceptance criteria

A v0 implementation is conformant only if it can demonstrate all of the following:

1. A masked post remains linked to a governed root actor without exposing that actor to the ordinary audience.
2. Room contracts explicitly define relay, reveal, retention, and discourse class posture.
3. Allegations are not treated with the same defaults as confessional speech.
4. Reveal requires explicit authority, rationale, and artifact emission.
5. A room history can be replayed as an evidence-bearing sequence rather than a mutable opaque feed.

## 13. Immediate downstream work items

The first downstream deliverables aligned to this standard are:

- Identity projection worked example and synthetic trace in `identity-is-prime-reference`
- A transport-facing scoped disclosure slice pack in `TriTRPC`
- Local-first room materialization note in `sociosphere`
- Reveal and moderation artifact hooks in `agentplane`
- Disclosure/reveal/moderation cairn schemas in `cairnpath-mesh`

## 14. Design posture

This standard does not treat secrecy as a product novelty. It treats bounded disclosure as a governed systems problem. The objective is not maximal concealment. The objective is to make candid human communication possible without surrendering the ability to audit, challenge, replay, and govern harmful conduct.
