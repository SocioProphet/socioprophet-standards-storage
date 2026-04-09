# Agentic Knowledge Platform Integration Patterns

This document uses RFC 2119 language: **MUST**, **SHOULD**, **MAY**.

## 1. Scope

This standard defines the canonical integration patterns for the SocioProphet agentic knowledge platform.
It describes how the normalized layers interact, which boundaries are mandatory, and which event flows
must be explicit for the platform to remain governed, inspectable, and replayable.

## 2. Architectural principle

The platform MUST be described as interacting planes rather than a single linear request path.
At minimum, canonical designs MUST identify:
- an ingestion and enrichment plane
- an online query and action plane
- an evaluation and feedback plane
- a governance and evidence plane

Designs MAY add specialized planes such as multimodal runtime, support operations, academy/discovery,
or sovereign local-state synchronization, but they MUST still map to the canonical model.

## 3. Ingestion and enrichment plane

### 3.1 Required steps

A canonical ingestion flow MUST specify:
1. source discovery or change detection
2. permission and ownership resolution
3. extraction and parsing
4. normalization and deduplication
5. enrichment and tagging
6. chunking / segmentation
7. embedding and lexical indexing as needed
8. provenance and version recording
9. index publication / readiness event

### 3.2 Required outputs

The ingestion plane MUST produce, at minimum:
- a raw artifact reference
- normalized extracted content
- permission / ACL association
- chunk or segment identifiers
- provenance metadata sufficient for citation and replay
- one or more search/index representations

### 3.3 Mandatory control note

The system-of-record MUST remain separate from derived indexes. A vector index or lexical index MUST NOT
be treated as the authoritative record for the artifact itself.

## 4. Online query and action plane

### 4.1 Required steps

A canonical online flow MUST specify:
1. ingress surface and authenticated caller identity
2. policy and capability eligibility checks
3. query rewrite and routing logic where applicable
4. retrieval and filtering strategy
5. reranking and context assembly
6. agent/tool invocation if needed
7. output safety/policy check
8. evidence and trace capture
9. response emission

### 4.2 Mandatory retrieval distinction

Canonical online designs MUST distinguish:
- lexical retrieval
- vector retrieval
- metadata filtering
- reranking
- citation assembly

It is non-compliant with this standard to collapse all of the above into a single opaque "RAG" step.

### 4.3 Tool invocation boundary

Tool calls MUST cross an explicit boundary that records:
- the invoked capability
- the resolved arguments
- the policy decision permitting the call
- the resulting side effects or returned evidence

## 5. Multimodal runtime plane

When image, document layout, screen, or video sources are in scope, the architecture MUST define a
multimodal runtime plane that handles:
- modality-specific extraction
- normalized intermediate representations
- tagging/captioning/search/extraction/action outputs
- provenance links back to the source media

Text-only retrieval pipelines MUST NOT pretend to be sufficient for multimodal workloads.

## 6. Sovereign memory and perspective plane

When local-first, user-owned, or perspective-scoped state is in scope, the architecture SHOULD define a
sovereign memory plane that includes:
- user or tenant-owned perspective objects
- signed local knowledge graphs or equivalent state representations
- synchronization or share boundaries
- explicit retention and forgetting rules
- trust boundaries between local and shared state

Memory writes MUST be governed by policy and purpose. They MUST NOT default to storing every interaction.

## 7. Support operations and academy/discovery overlays

Canonical platform designs MAY layer specialized product surfaces on top of the same core architecture.
Examples include:
- support portal and case-routing flows
- asset reuse and recommendation systems
- academy, matching, coaching, or discovery surfaces

When these overlays are present, the design MUST still identify:
- the shared core services they depend on
- the additional routing, recommendation, or feedback loops they require
- the ownership boundary between shared platform and product-specific logic

## 8. Evaluation and feedback plane

### 8.1 Required flows

Canonical evaluation design MUST specify:
- offline regression input sets
- online trace sampling
- synthetic feedback loops where used
- human review queues where required
- approval gates before promotion
- drift/bias/freshness monitoring after promotion

### 8.2 Feedback separation

The platform MUST distinguish between:
- user-facing task success or failure
- retrieval quality signals
- model output quality signals
- support/academy/business outcome signals
- safety or policy violations

## 9. Governance and evidence plane

The architecture MUST define how the platform records:
- policy decisions
- source eligibility and permission checks
- tool eligibility and capability routing
- provenance receipts
- promotion and rollback evidence
- reversible state transitions where supported

Where possible, these records SHOULD be emitted as structured events rather than only implicit logs.

## 10. Recommended event surfaces

Canonical designs SHOULD define explicit contracts for events such as:
- `doc_changed`
- `artifact_normalized`
- `index_updated`
- `retrieval_result`
- `tool_call`
- `evaluation_result`
- `safety_action`
- `promotion_decision`
- `rollback_decision`

## 11. Repository split implication

Shared integration doctrine belongs in the standards authority repository.
Public docs MAY carry simplified mirrors.
Runtime repos SHOULD carry concrete bindings, contracts, and service topology derived from these patterns.

## 12. Related standards

- `100-agentic-knowledge-platform-layer-model.md`
- `101-agentic-knowledge-platform-tooling-inventory.md`
- `030-service-interfaces-tritrpc.md`
- `040-observability-otel.md`
- `050-security-oidc-policy.md`

## 13. Implementation evidence

Implementation repos adopting this standard SHOULD document which of the canonical planes they implement,
which event contracts they emit, and where replay/provenance evidence is stored.