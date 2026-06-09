# Personhood-bound identity mesh standard v0.1

## Status

Normative doctrine companion to `adr/ADR-042-personhood-bound-identity-mesh.md`.

This standard defines how SocioProphet binds identity to a person rather than to a thing.

## Core thesis

A person is not a wallet, account, portrait, biometric, device, credential, graph edge, agent, reputation score, sigil, proof artifact, or digital twin.

A personhood-bound identity mesh is a governed continuity system that connects a living human subject to controlled identifiers, credentials, signing authorities, delegations, reputation contexts, projections, recovery paths, and receipts without collapsing the person into any of those objects.

## Object family

### PersonhoodBindingRecord

A governed continuity claim that a living human subject controls or authorizes an identity mesh.

Required concepts:

- subject reference;
- twin or mesh subject reference;
- binding scope;
- assurance level;
- binding ceremony;
- independent evidence classes;
- proof policy;
- recovery path;
- revocation/correction path;
- transition receipts;
- non-claims.

### IdentitySigilSeal

A human-facing presentation and authority surface downstream of personhood binding.

Required concepts:

- personhood binding reference;
- subject reference;
- twin or mesh reference;
- sigil artifact and hash;
- optional portrait policy;
- scoped signing authorities;
- consent policy refs;
- delegation refs;
- reputation refs;
- transition receipts;
- non-claims.

### IdentityPersonhoodSigilGraphRecord

A graph materialization of personhood, sigil, authority, recovery, revocation, reputation, consent, and receipt relations.

Required concepts:

- `PERSONHOOD_BINDING` node;
- `IDENTITY_MESH_SUBJECT` node;
- `IDENTITY_SIGIL_SEAL` node;
- `PERSON_BOUND_TO_SUBJECT` edge originating from the personhood binding node;
- `SUBJECT_HAS_SIGIL_SEAL` edge supported by personhood binding evidence;
- recovery and revocation nodes/edges;
- non-claims and epistemic edge posture.

### PersonhoodBindingProofProfile

A proof-artifact profile for Identity Is Prime.

Required concepts:

- personhood binding ceremony as Event-IR trace;
- evidence-class checks;
- veto diagnostics;
- non-collapse policy constraints;
- proof artifact inputs, witnesses, and signatures.

### PersonhoodBoundExportReadiness

A Human Digital Twin export/readiness profile.

Required concepts:

- scoped assurance claim;
- Ω readiness state;
- purpose and recipient;
- evidence class summary rather than raw evidence;
- policy decision ref;
- validity/revalidation;
- revocation status;
- transition receipt;
- non-claims.

## Assurance levels

Canonical levels:

- `P0_unbound_pseudonym`
- `P1_self_attested`
- `P2_liveness_key_continuity`
- `P3_guardian_or_witness_supported`
- `P4_institutional_credential_supported`
- `P5_regulated_high_assurance`

P0/P1 may be valid for pseudonymous or low-risk contexts.

P3+ requires at least three active independent evidence classes.

P4+ requires institutional credential support.

## Evidence class vocabulary

Canonical evidence classes:

- `self_attestation`
- `liveness_or_presence`
- `credential_attestation`
- `guardian_or_witness_attestation`
- `device_key_continuity`
- `account_continuity`
- `recovery_policy`
- `revocation_policy`

Evidence classes are support for the binding. They are not the person.

## Minimum P3 policy

A P3+ personhood binding SHOULD include:

```text
self_attestation
liveness_or_presence
guardian_or_witness_attestation
recovery_policy
revocation_policy
```

It MUST reject single object-class personhood.

## Mandatory vetoes

A conforming implementation MUST veto:

- wallet-only personhood;
- account-only personhood;
- device-only personhood;
- portrait-only personhood;
- biometric-only personhood;
- credential-only personhood;
- agent-action-only personhood;
- reputation-only personhood;
- graph-inference-only personhood;
- personhood binding without subject consent;
- personhood binding without recovery;
- personhood binding without revocation/correction;
- public projection of all identity contexts by default;
- sigil seal treated as personhood without personhood binding reference;
- export of raw ceremony evidence by default.

## Mandatory non-claims

All conforming records SHOULD include equivalent non-claims:

- wallet is not the person;
- account is not the person;
- portrait is not biometric proof by default;
- device is not the person;
- credential is not the person;
- agent action is not direct human action unless explicitly delegated and receipted;
- reputation is contextual evidence, not global human worth;
- sigil is presentation, not the person;
- digital twin is governed representation, not the person;
- graph edge is evidence relation, not the person;
- proof artifact is proof, not the person;
- public projection does not authorize global identity correlation.

## Export rule

Exporters MUST export minimized assurance claims by default:

```text
subject_ref is person-bound at assurance_level for allowed_purpose under policy_decision_ref
```

Exporters MUST NOT export raw ceremony evidence, guardian refs, wallet refs, portrait refs, credential refs, account graph, recovery graph, or all identity contexts unless there is explicit consent and policy approval.

## Repository conformance map

Current first implementation lanes:

| Repo | Conformance role |
| --- | --- |
| `HolographMe` | Executable schemas, fixtures, and validators for personhood binding and sigil seal. |
| `regis-entity-graph` | Graph contract, schema, fixtures, and validator for personhood/sigil materialization. |
| `identity-is-prime-reference` | Proof-artifact profile and non-collapse policy interpretation. |
| `human-digital-twin` | Ω/export readiness doctrine, fixtures, and validator for minimized person-bound claims. |
| `socioprophet-standards-storage` | Canonical ADR and standard. |

## Migration posture

Existing identifiers should be connected as scoped bindings and evidence, not elevated into personhood.

Examples:

- Apple ID: account continuity and device/app ecosystem binding.
- Google/Microsoft account: account continuity and service access binding.
- GitHub: developer reputation and repo authority binding.
- Email/domain: communication and namespace binding.
- Wallet: signing/payment authority binding.
- Government or institutional credential: credential attestation.
- Passkey/hardware key: control continuity.

Migration target:

```text
existing ID -> contextual binding -> personhood ceremony evidence -> mesh-controlled authority -> sigil seal -> scoped projection/export -> old ID downgraded to alias or authority
```

## Safety note

Any implementation that says or implies “connect wallet to become you,” “face equals person,” “account equals person,” or “global reputation equals human value” is non-conforming.

The metaphysical clown car is not part of the standard.
