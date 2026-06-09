# ADR-042: Adopt personhood-bound identity mesh as the canonical human identity binding standard

- Date: 2026-06-09
- Status: Proposed
- Decision owner: SocioProphet
- Contexts affected: identity, personhood, sigils, human digital twin, graph, proof artifacts, export readiness, agents, reputation, recovery

## Context

ADR-040 adopted a multi-plane identity control plane: workload identity, semantic human/event identity, human artifact readiness/export, runtime grant/policy, transport/receipt, and execution/evidence.

The next missing boundary is sharper: existing identity systems bind users to things.

They bind to:

- wallets;
- accounts;
- devices;
- credentials;
- portraits;
- biometrics;
- social graphs;
- reputation scores;
- agent authorities.

That is insufficient. A living person is not any of those things. A wallet can sign. An account can authenticate. A portrait can present. A credential can attest. An agent can act. A graph edge can infer. None of these is the person.

The SocioProphet identity stack therefore needs a canonical standard for binding an identity mesh to a person while preserving context separation, consent, recovery, revocation, and non-collapse rules.

## Decision

Adopt **personhood-bound identity mesh** as the canonical human identity binding standard.

The standard consists of the following normative object family:

1. `PersonhoodBindingRecord`
   - Governs the claim that a living human subject controls or authorizes an identity mesh.
   - Requires ceremony, independent evidence classes, consent, recovery, revocation, receipts, and non-claims.

2. `IdentitySigilSeal`
   - Binds a human-recognizable sigil, optional portrait policy, scoped signing authorities, delegation refs, reputation refs, consent policy refs, and transition receipts to a personhood-bound subject.
   - Must reference a valid personhood binding before it may be treated as person-bound presentation.

3. `IdentityPersonhoodSigilGraphRecord`
   - Materializes personhood, sigil, authority, recovery, revocation, reputation, and receipt relations in Regis Entity Graph.
   - Must preserve epistemic edge posture and prevent object/person collapse.

4. `PersonhoodBindingProofProfile`
   - Extends Identity Is Prime proof artifact discipline to personhood binding ceremonies and independent evidence-class checks.

5. `PersonhoodBoundExportReadiness`
   - HDT export/readiness profile for exporting scoped person-bound assurance claims without raw personhood evidence leakage.

## Normative repository placement

- `HolographMe`
  - Owns first executable contracts for `PersonhoodBindingRecord` and `IdentitySigilSeal`.
  - Owns product-facing consent, projection, delegation, reputation, and transition receipt integration.

- `regis-entity-graph`
  - Owns graph materialization of personhood/sigil/authority/recovery/reputation/projection relations.
  - Owns epistemic edge posture for graph-derived or graph-promoted identity relations.

- `identity-is-prime-reference`
  - Owns the proof-artifact profile and formal non-collapse policy interpretation.

- `human-digital-twin`
  - Owns Ω/readiness/export gating for personhood-bound claims crossing a boundary.

- `socioprophet-standards-storage`
  - Owns the canonical standard, ADR, and conformance doctrine.

## Required evidence classes

The canonical evidence class vocabulary is:

- `self_attestation`
- `liveness_or_presence`
- `credential_attestation`
- `guardian_or_witness_attestation`
- `device_key_continuity`
- `account_continuity`
- `recovery_policy`
- `revocation_policy`

For P3+ personhood binding, at least three active independent evidence classes are required, and the recommended minimum is:

```text
self_attestation
liveness_or_presence
guardian_or_witness_attestation
recovery_policy
revocation_policy
```

For P4+ personhood binding, add `credential_attestation`.

## Non-collapse rules

The standard rejects the following as personhood binding:

- wallet-only binding;
- account-only binding;
- device-only binding;
- portrait-only or biometric-only binding;
- credential-only binding;
- reputation-only binding;
- agent-action-only binding;
- graph-inference-only binding;
- binding without recovery;
- binding without revocation/correction;
- binding that publicly correlates all identity contexts by default.

The core rule is:

```text
No personhood binding from a single object class.
```

## Export rule

Personhood-bound export must disclose the smallest sufficient claim:

```text
This subject is person-bound at assurance level Pn for purpose Y under policy Z.
```

It must not disclose raw ceremony evidence, guardians, credentials, wallet refs, portrait refs, linked account graph, or recovery graph unless separately consented and policy-approved.

## Consequences

What becomes easier:

- explaining how SocioProphet binds identity to a person rather than to an object;
- rejecting wallet/account/portrait/device identity collapse;
- carrying identity assertions across HolographMe, Regis, Identity Is Prime, and HDT;
- exporting person-bound assurance claims without leaking raw personhood evidence;
- aligning future agent delegation and reputation work to a single spine.

What becomes harder:

- implementers must distinguish personhood, presentation, authority, delegation, and reputation;
- raw account-linking shortcuts become invalid;
- public profile surfaces must avoid exposing high-assurance personhood evidence by default;
- conformance needs negative fixtures, not just happy-path schemas.

## Measurement plan

Success requires:

1. at least one valid and one rejected fixture in each executable lane;
2. validators for HolographMe personhood/sigil contracts;
3. Regis graph validator rejecting object-originated personhood edges;
4. Identity Is Prime proof profile for evidence-class and veto logic;
5. HDT export validator rejecting raw personhood evidence leakage;
6. this standards ADR and companion standards document as the canonical reference.

## Follow-on work

- Publish reusable JSON Schemas in `socioprophet-standards-storage` rather than only repo-local schemas.
- Add conformance tests that import the current fixtures from all four repos.
- Extend `agentplane` delegation receipts to reference personhood-bound identity and sigil seals.
- Extend `policy-fabric` with personhood-bound export and delegation policies.
- Add a migration standard for existing Apple/Google/GitHub/email/wallet identifiers.

## Non-claims

This ADR does not define legal identity proofing.

This ADR does not require biometrics.

This ADR does not require public real-name identity.

This ADR does not authorize global identity correlation.

This ADR does not make a wallet, account, portrait, device, credential, agent, graph edge, reputation score, proof artifact, sigil, or twin equivalent to the person.
