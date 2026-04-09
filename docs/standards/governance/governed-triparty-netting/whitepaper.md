# Governed Triparty Netting Fabric
## A Technical Architecture for Multi-Ledger Settlement, Proof-Carrying Coordination, and Controlled Export

### Publication Draft v1.1

## Abstract

The correct interoperability primitive is not a bridge, not a registry, and not a messaging standard in isolation. It is a **governed triparty netting fabric**: a three-party coordination cell that can cancel circulatory gross flow, preserve proof and provenance, separate evidence from permission, and support release, refund, suppression, or export according to policy rather than mere confidence.

The architecture is motivated by a recurring systems failure that appears across crypto-native settlement, institutional ledgers, identity systems, and disclosure systems: local records may be accurate while global truth remains delayed, hidden, partitioned, policy-constrained, or only partially reconstructable. Existing ecosystems already expose fragments of the required model. Intent systems provide structured orders and fills. Multi-party coordination systems provide proposal and acceptance states. Payment-channel systems provide escrow and delayed claims. Proof systems provide timeout and acknowledgement discipline. Credential systems provide selective disclosure and status. Capability systems provide bounded rights over data, models, and compute. What is missing is the **release constitution** that makes these fragments cohere.

This paper proposes that constitution. It introduces the governed triparty simplex as the minimal cell that supports genuine internal cancellation of cyclic demand, then extends it into a governed prism with typed events, scope boundaries, truth classes, policy bundles, action rights, and proof artifacts. The architecture distinguishes what evidence supports, what policy admits, what proof can release, and what may be exported into a wider downstream scope. This yields the governing rule: **Evidence proposes. Policy disposes. Proof preserves the result. Export is stricter than local validity.**

The paper is designed as a portable systems architecture. It is not tied to one chain, one registry, or one identity system. It can sit on existing rails and make them safer, clearer, and more composable.

## 1. Problem

Across public blockchains, rollups, bank ledgers, custodial systems, identity systems, and disclosure surfaces, the same failure appears repeatedly. A local system may be internally correct while the larger truth remains unresolved. In finance, this looks like gross bilateral settlement where multilateral netting should have been possible. In beneficial ownership and governed identity, it appears as locally truthful documents or role credentials that still fail to reveal globally operative control or authorize safe export into a wider scope. In artificial intelligence and service marketplaces, it appears as a valid payment or invocation that still lacks a rigorous release, contradiction, or export discipline.

This matters because modern interoperability is no longer only about moving value. It is about coordinating **value, authority, capability, and disclosure** under heterogeneous trust assumptions and heterogeneous finality models. A system that only moves tokens but cannot reason about admissibility, release rights, reversal, contradiction, and export is incomplete.

## 2. Core Thesis

The minimal useful clearing object is a triparty simplex:

\[
\Delta^2 = [A, B, C]
\]

A pair of systems supports bilateral transfer. A filled triangle is the smallest object that supports genuine internal cancellation of cyclic demand. If directed obligations exist along A to B, B to C, and C to A, then the common cyclic component can be extinguished internally before any residual imbalance is pushed to the edges.

But the real production object is not only a triangle. It is a **governed prism** built from:
- typed events and claims,
- scope and trust-domain boundaries,
- truth classes,
- policy bundles,
- action rights,
- proof artifacts,
- replay and timeout discipline,
- contradiction and reversal paths.

The production system therefore has four progressively stronger sets:
- what evidence supports,
- what policy admits,
- what proof can release,
- what may be exported into a wider scope.

That is the central constitutional move of the paper.

## 3. Typed Record Model

Every local object in the fabric is modeled as a typed record

\[
z = (y, q, s, \chi, v, \mu, \alpha, \pi)
\]

where:
- y is the typed event, claim, leg, packet, credential, or ledger action,
- q is the context or prime vector,
- s is the scope or trust domain,
- chi is the truth class,
- v is the validity or finality interval,
- mu is the policy bundle,
- alpha is the action-rights bundle,
- pi is the proof artifact or proof pointer.

This record shape is deliberately general. It allows the same architecture to model settlement intents, capability grants, credentials, witness attestations, fill receipts, export decisions, and reversal records using one governance grammar.

## 4. Truth Classes

The paper uses four operational truth classes:
- **PROVEN**
- **ATTESTED**
- **INFERRED**
- **REPUTED**

These are not descriptive labels. They are action-governance classes.

**PROVEN** includes settled ledger entries, verified packet proofs, valid acknowledgements, and similarly hard state. PROVEN may support release once freshness, replay, and scope conditions pass.

**ATTESTED** includes authenticated participant acceptances, institutional assertions, role credentials, and scoped witness claims. ATTESTED may support readiness or bounded admission, but not arbitrary irreversible release without the rest of the release conditions.

**INFERRED** includes model outputs, route quality estimates, hidden-state reconstruction, forecasted capacities, and similar machine-generated or analytic judgments. INFERRED may affect pricing, routing, reserve margins, and review priority. It must not masquerade as proof.

**REPUTED** includes intelligence feeds, risk context, and external soft signals. REPUTED may shape haircuts or manual review, but not settlement authority.

This partition matters because modern systems routinely confuse confidence with permission. The architecture rejects that confusion.

## 5. Release Calculus

Let the directed gross obligations in a triparty cell be

\[
f = (f_{AB}, f_{BC}, f_{CA}), \qquad f_{ij} \ge 0.
\]

Let observed and attested capacities be c_obs and c_att, and let risk, governance, and drift/finality haircuts be r, g, and d. Trusted executable capacity is determined by the minimum of observed and attested capacity, multiplied by the remaining capacity after those haircuts.

The evidentially nettable cycle is the minimum directed obligation and trusted capacity around the cycle.

Policy then admits only some fraction of that evidence.

Proof, freshness, replay, contradiction, and finality discipline then determine what is releasable.

Only then can the admitted and proved amount be released. The remainder becomes residual edge settlement, refund, review, suppression, or deferred export.

The elegance here is practical, not aesthetic. Evidence is not yet release. Policy is not yet proof. Export is stricter than local release.

## 6. Lifecycle

The governed lifecycle is:

Observed -> Proposed -> Ready -> Escrowed -> Filled -> Verified -> Released

with side exits to:

Cancelled, Expired, Refunded, Revoked, Disputed, Unmerged.

The meaning of each state is:
- **Observed**: candidate claims, capacities, routes, credentials, or events are seen.
- **Proposed**: a structured coordination object is formed.
- **Ready**: all required acceptances and witness conditions are satisfied.
- **Escrowed**: money or rights are conditionally locked.
- **Filled**: one or more execution legs have been performed.
- **Verified**: proofs, acknowledgements, freshness, replay, contradiction, and timeout conditions are checked.
- **Released**: only the releasable amount finalizes.

This lifecycle is intentionally stricter than a simple executed or not executed state. It is designed for heterogeneous systems where asynchronous completion, delayed proof, stale witness state, or scope-sensitive export matter.

## 7. Trust Model

The system is trust-minimized, typed, and challengeable.

The architecture assumes different operations deserve different trust surfaces. A payer need not trust a filler with custody forever. A filler need not trust an attestor to be infallible. A downstream scope need not trust a locally admissible relation to be exportable. The protocol therefore does not attempt to remove trust. It attempts to force trust into explicit, bounded, slashable, and reversible channels.

The security objective is to guarantee:
1. no unauthorized release,
2. no proofless elevation,
3. no unbounded replay,
4. no silent export,
5. no irreversible corruption without challenge.

## 8. Adversaries and Challenge Windows

The architecture treats the following adversary classes as first-class:
- replay adversary,
- stale-attestation adversary,
- false-fulfillment adversary,
- scope-jump adversary,
- withholding adversary,
- collusive witness adversary,
- timing adversary,
- liquidity griefing adversary,
- policy-bypass adversary.

Challenge windows must therefore be typed rather than flat. Different objects require different windows. The paper treats this as a protocol responsibility, not an operational afterthought.

## 9. Interfaces and Bundles

The architecture is implemented through seven contract surfaces:
- **NettingCell**,
- **EscrowVault**,
- **BondVault**,
- **CapabilityRegistry**,
- **ProofRegistry**,
- **ReserveManager**,
- **FeeRouter**.

And through typed bundles:
- **IntentBundle**,
- **AcceptanceBundle**,
- **EscrowBundle**,
- **FillBundle**,
- **VerificationBundle**,
- **DisputeBundle**,
- **RevocationBundle**,
- **ExportBundle**.

This is where the abstract model becomes implementable. Replay, freshness, contradiction, witness state, export, and reversal are all represented as typed objects rather than invisible control flow.

## 10. Timestamped Worked Trace

The prior worked example showed the release calculus. This version adds the operational choreography.

Assume a triparty cell involving:
- **A**: payer or initiating domain,
- **B**: filler or intermediate execution domain,
- **C**: destination provider or target state domain.

Assume the following challenge windows are set by policy:
- acceptance freshness window: 15 minutes,
- optimistic fill challenge window: 2 hours,
- packet timeout window: 30 minutes,
- revocation lookback for stronger reversal: 7 days,
- export challenge window: 30 days.

### Time-indexed execution

**T0 - Observed**  
Directed obligations and capacities are observed. A route estimate and witness set are assembled. No value moves.

**T0 + 2 minutes - Proposed**  
An IntentBundle is formed with a unique proposal nonce, participants, leg descriptors, scope, release policy reference, and deadlines.

**T0 + 7 minutes - Ready**  
Required AcceptanceBundle objects are submitted by the admissible participants. Their timestamps are within the acceptance freshness window. The witness set passes policy.

**T0 + 10 minutes - Escrowed**  
An EscrowBundle is recorded. The payer locks value or rights in the escrow surface. This does not yet imply release.

**T0 + 18 minutes - Filled**  
A FillBundle is produced for the destination leg. The filler fronts liquidity or performs the required remote leg. The fill is provisionally accepted but not yet final.

**T0 + 23 minutes - Verified (provisional)**  
A VerificationBundle is assembled. Packet acknowledgement or local receipt is present. Replay checks pass. No contradiction evidence is yet known. The object is eligible to enter the challenge window.

**T0 + 2 hours 23 minutes - Released**  
The optimistic challenge window clears without successful dispute. Release conditions are satisfied. The releasable amount moves from admitted state into final released state. Fees and residual obligations are computed.

### Failure branch

If at T0 + 40 minutes a contradiction witness or timeout proof appears, the state does not progress to Released. Instead, the object moves to Disputed or Refunded depending on the failure class. This is the operational meaning of the paper's claim that evidence, admission, release, and export must remain distinct.

### Export branch

Even after Released, no wider-scope export occurs automatically. If the resulting relation, capability, or credential needs to cross into a broader disclosure scope, an ExportBundle must satisfy the stricter export gate and survive the export challenge window.

This example is still stylized, but it is materially stronger than a flat arithmetic example because it forces the lifecycle and challenge windows to do real work.

## 11. ASI / SingularityNET Integration Posture

The right posture is not replacement. It is layering.

The current SingularityNET ecosystem already provides useful rails: a native token and payment surface, Multi-Party Escrow, payment-channel style settlement, daemon-mediated service execution, and a broader path toward AI-native chain and capability-oriented primitives.

Our architecture adds the missing higher-order control layer:
- separation of evidence, admission, release, and export,
- contradiction-aware and witness-aware admission,
- replay and timeout discipline,
- reversibility and reversal lineage,
- distinct but coupled treatment of value, authority, capability, and disclosure.

So the correct external line is simple:

**We are not trying to replace your rails. We are supplying the missing governance and release discipline that makes those rails safer, clearer, and more composable.**

## 12. Product Boundary

The first bounded product is not all interoperability. It is a **Governed Coordination Kernel Toolkit** consisting of:
- canonical lifecycle,
- canonical bundles,
- proof and policy logic,
- replay and timeout rules,
- trace model,
- adapter interface contract,
- worked integrations.

That is the right first product because it is portable, demonstrable, and narrow enough to implement without collapsing into ecosystem-specific consultancy.

## 13. Why This Matters

The paper's importance is not that it proposes a better bridge. It proposes a better release constitution.

That matters because modern systems increasingly coordinate across heterogeneous ledgers, identity systems, service markets, capability surfaces, and disclosure regimes. In such systems, truth is often distributed, delayed, scoped, and only partially exportable. A modern interoperability architecture must therefore clear more than value. It must clear value, authority, claims, and disclosure rights together.

## Conclusion

The governed triparty netting fabric is the smallest architecture that can:
- cancel circulatory gross flow,
- preserve proof and provenance,
- separate evidence from permission,
- support policy-bounded release,
- and control export into wider scopes.

It is broader than a bridge, narrower than a fantasy global brain, and practical enough to sit on existing rails while improving them.

The near-term strategy is not to rebuild ecosystems from scratch. It is to layer a stronger governance and release discipline onto the rails that already exist, prove that discipline through bounded integrations, and only then widen the scope.

That is the central claim of this paper.

---

# Appendix A - Formal Bundle Field Sketch

This appendix makes the typed bundles more explicit without pretending to lock a final implementation application binary interface.

## IntentBundle
- proposal identifier
- proposal nonce domain
- originating scope
- participant set
- leg descriptors
- gross directed obligations
- policy reference
- acceptance deadline
- export class if applicable
- trace identifier

## AcceptanceBundle
- proposal identifier
- acceptance nonce
- accepting party identifier
- asserted role
- scope of acceptance
- timestamp
- expiry
- signature or proof of assent

## EscrowBundle
- proposal identifier
- escrow identifier
- deposited asset or rights
- amount or bounded quantity
- lock time
- refund conditions
- trace identifier

## FillBundle
- proposal identifier
- fill identifier
- filler identifier
- destination action or remote execution proof
- packet identifier if relevant
- timestamp
- provisional outcome
- trace identifier

## VerificationBundle
- proposal identifier
- verification nonce
- proof references
- freshness check result
- replay check result
- contradiction check result
- timeout or acknowledgement result
- releasable amount
- timestamp
- trace identifier

## DisputeBundle
- proposal identifier
- dispute identifier
- challenger identifier
- challenged object reference
- reason code
- evidence pointer
- timestamp
- requested remedy

## RevocationBundle
- object identifier
- revoking authority
- revocation reason
- timestamp
- status handle or proof pointer

## ExportBundle
- source object identifier
- source scope
- target scope
- export nonce
- export policy reference
- witness bundle if required
- admissibility result
- timestamp
- trace identifier

The main design principle is that every stronger transition requires a stronger object class and a narrower proof path. Nothing becomes stronger merely because a previous object exists.
