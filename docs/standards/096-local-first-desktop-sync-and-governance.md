# 096 — Local-First Desktop, Sync, and Governance Standard

Status: Draft v0.1  
Scope: SourceOS, SociOS, SocioProphet runtime surfaces  
Normative language: MUST / SHOULD / MAY

## 1. Purpose

This standard defines the canonical platform posture for:

1. Linux desktop application distribution and containment
2. local-first state ownership and synchronization
3. capability-mediated desktop access
4. governance and trust scoring for packages, remotes, sessions, agents, and sync peers
5. cross-repository alignment between transport, policy, runtime, semantic, and contract layers

This standard exists because the platform cannot claim user sovereignty, offline resilience, auditability, or governed agent execution unless those properties are enforced across the desktop, sync, policy, and contract layers at the same time.

## 2. Design goals

The platform MUST satisfy all of the following:

- local state is authoritative by default
- user actions commit locally before network synchronization
- desktop applications run with containment by default
- desktop capabilities are granted through explicit mediation, not ambient host access
- collaboration works under partition and resume conditions
- remotes, mirrors, and cloud coordination points are replaceable
- reputation and visibility systems MUST NOT collapse into winner-take-all concentration dynamics
- every material decision can emit evidence and replayable receipts

## 3. Canonical stack choices

### 3.1 Desktop distribution and execution

The default Linux distribution posture SHOULD be:

- Flatpak-compatible packaging for desktop applications
- OSTree-style content-addressed delivery and delta updates
- bubblewrap-class process containment for host boundary enforcement
- XDG desktop portal mediation for file access, URI opening, screen access, device selection, and other high-risk host interactions

Implementations MAY support additional packaging or runtime systems, but those systems MUST provide equivalent or stronger guarantees for:

- reproducible delivery
- inspectable permission surfaces
- host capability minimization
- rollback / provenance / integrity evidence

### 3.2 Local-first data ownership

The local device copy MUST be treated as the user-authoritative working state for interactive operations.

Interactive writes MUST:

1. commit to local durable state first
2. generate a local receipt or mutation record
3. synchronize asynchronously to one or more replicas
4. preserve reconciliation metadata sufficient for replay and conflict analysis

### 3.3 Synchronization model

The platform defines two first-class sync patterns:

#### Pattern A — CRDT-first collaborative artifacts

This pattern SHOULD be used for:

- shared documents
- collaborative graphs
- multi-actor editing surfaces
- notebooks, boards, canvases, notes, and live semantic workspaces

Required properties:

- commutative merge semantics for concurrent edits
- resumable sync under partitions
- snapshot and compaction discipline
- actor / device attribution for mutation provenance

#### Pattern B — replicated-document / record-first state

This pattern SHOULD be used for:

- metadata records
- cached entity state
- manifests
- receipts
- durable structured application records that do not require fine-grained collaborative merge behavior

Required properties:

- deterministic document identity
- replication filters and policy gates
- explicit conflict detection and repair semantics
- recoverable history for audit and replay

#### Pattern C — hybrid deployment

The preferred system architecture MAY combine Pattern A and Pattern B, where:

- collaborative state is CRDT-backed
- metadata, indexing, manifests, and receipts are record-backed
- CRDT snapshot references and record identities are mutually linked

## 4. Capability and permission model

Applications and agents MUST NOT receive unrestricted host access by default.

All host capability access MUST be modeled as explicit grants, including but not limited to:

- file and folder access
- camera and microphone use
- screen capture / screen share
- notifications
- URI handlers
- device and network adjacency
- credential or secret access
- clipboard flows

The grant model MUST support:

- least privilege
- time-bounded grants where possible
- auditable user-visible reasoning for the grant
- revocation
- replayable evidence of grant issuance and use

## 5. Governance and trust requirements

### 5.1 Anti-concentration rule

Reputation, ranking, visibility, or reward systems MUST NOT be designed as simple winner-take-all escalators.

Any governance subsystem that influences package visibility, agent preference, mirror selection, or task allocation MUST measure at least:

- concentration / inequity
- utility / service quality
- abuse / scam loss proxy
- newcomer viability or onboarding survivability

### 5.2 Trust tuple

Every governed subject SHOULD be representable as a trust tuple:

- identity
- provenance
- policy posture
- observed behavior
- evidence freshness
- concentration / inequity contribution
- utility contribution
- operator override state

Governed subjects include:

- packages
- remotes / mirrors
- sessions
- agents
- users
- ontologies / mappings
- synchronization peers
- runtime nodes

### 5.3 Remote independence

A default catalog or remote MAY exist, but implementations MUST support:

- multiple remotes
- mirror preference or fallback policy
- trust-root pinning
- local caching
- degraded-mode operation when central services are unreachable

## 6. Evidence and receipts

Material state transitions MUST be able to emit receipts for:

- local mutation
- sync enqueue and sync acknowledgement
- policy decision
- capability grant or denial
- placement decision
- remote / mirror selection
- reputation score change
- package install / update / rollback

Receipts MUST be linkable to higher-order evidence graphs.

## 7. Cross-repository contract allocation

This standard allocates binding responsibility as follows:

### 7.1 `SocioProphet/TriTRPC`

TriTRPC is the normative transport surface for:

- sync control messages
- evidence envelopes
- placement receipts
- trust-context propagation
- compact authenticated transport of local-first mutation and repair flows

### 7.2 `SocioProphet/policy-fabric`

Policy Fabric is the normative governance surface for:

- capability policy
- remote trust policy
- reputation weighting
- concentration guards
- operator override policy
- validation and release gating of the above

### 7.3 `SocioProphet/prophet-platform`

Prophet Platform is the runtime binding surface for:

- deployable services implementing the sync and evidence model
- session and placement execution
- platform receipts and health flows
- integration of transport and policy into running systems

### 7.4 `SocioProphet/synapseiq`

SynapseIQ is the semantic enrichment and intelligence surface for:

- local-first semantic work products
- sync-aware enrichment pipelines
- semantic provenance binding
- quality and reasoning passes over synchronized records and collaborative artifacts

### 7.5 `SocioProphet/ontogenesis`

Ontogenesis is the semantic graph and ontology binding surface for:

- provenance-aware graph formation
- layered ontology linking across local, middle, and upper models
- mapping synchronized local artifacts into governed semantic structures

### 7.6 `SourceOS-Linux/sourceos-spec`

SourceOS typed contracts are the canonical machine-readable schema authority for:

- capability grant objects
- package / remote / mirror receipts
- sync session contracts
- evidence and telemetry objects
- local-first desktop and collaboration contracts

## 8. Minimum implementation obligations

A conforming implementation MUST provide:

1. a local-first write path
2. at least one explicit capability mediation surface
3. at least one governed sync path
4. evidence emission for material actions
5. a non-winner-take-all trust or visibility model when ranking affects user outcomes
6. contract or schema alignment back to the typed contract layer

## 9. Recommended next standards work

Follow-on standards SHOULD define:

- package receipt schema
- remote and mirror trust schema
- capability grant schema
- sync mutation envelope schema
- collaborative artifact schema family
- reputation and concentration telemetry schema
- rollback and replay semantics for desktop-installed agentic applications

## 10. Adoption note

This document is intentionally cross-cutting. No single repository should absorb the entire design. Instead, each repository MUST bind the portion of this standard that belongs to its layer while preserving common vocabulary and evidence continuity across the stack.
