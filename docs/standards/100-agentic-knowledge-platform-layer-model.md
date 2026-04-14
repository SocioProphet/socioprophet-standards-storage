# Agentic Knowledge Platform Layer Model

This document uses RFC 2119 language: **MUST**, **SHOULD**, **MAY**.

## 1. Scope

This standard defines the normalized layer model for the SocioProphet agentic knowledge platform.
It exists because the common "agentic RAG stack" representation is too narrow for a governed,
operator-grade, local-first, multimodal, and institutionally deployable system.

This standard applies to:
- architecture documents
- platform inventory packages
- public docs that summarize the stack
- runtime repos that implement parts of the stack
- evaluation, observability, and governance packages that describe stack boundaries

## 2. Why a normalized model is required

A simple pyramid of evaluation, LLMs, frameworks, vector databases, embeddings, extraction,
memory, and alignment is useful as an introduction, but it is insufficient as a canonical system model.

It typically omits or compresses:
- connectors and permission-preserving sync
- hybrid retrieval and reranking
- metadata and provenance stores
- application modules and workflow engines
- multimodal runtime planes
- sovereign local state and perspective graphs
- support operations, academy, discovery, and case-routing surfaces
- evaluation, synthetic feedback, and model/prompt lifecycle operations
- governance and safety controls distinct from observability

Canonical platform work MUST use the normalized model in this document rather than an informal logo collage.

## 3. Canonical layer model

The canonical platform model consists of the following layers.

### 3.1 Surface and channel layer

This layer includes the human- and system-facing entry points:
- web portals
- operator consoles
- terminal / shell-equivalent control surfaces
- chat surfaces
- API clients
- IDE and workflow integrations
- academy and discovery surfaces
- support and caseflow surfaces

### 3.2 Application and orchestration layer

This layer includes:
- API routes and gateways
- agent orchestration graphs
- workflow engines and SDKs
- state transition controllers
- approval, escalation, and review flows
- task routing and assignment logic

### 3.3 Tooling and integration layer

This layer includes:
- first-party and third-party tools
- connector registries
- MCP- or capability-style tool declarations
- side-effect boundaries
- sandboxed execution adapters
- notification, file, and event infrastructure modules

### 3.4 Retrieval and reasoning layer

This layer includes:
- query rewriting
- source routing
- hybrid retrieval
- metadata filtering
- reranking
- context compression
- citation assembly
- multi-hop retrieval and structured evidence joins

### 3.5 Knowledge and state layer

This layer includes:
- object stores for raw artifacts
- metadata and provenance stores
- vector indexes
- lexical / BM25 indexes
- graph and ontology stores
- user, tenant, and organization state
- memory and perspective stores

### 3.6 Ingestion and enrichment layer

This layer includes:
- connectors and sync jobs
- extraction and parsing
- OCR and layout handling
- deduplication and normalization
- tagging, entity extraction, and enrichment
- permission and ACL propagation
- multimodal conversion and indexing

### 3.7 Model and runtime layer

This layer includes:
- foundation models
- embedding models
- rerankers
- classifiers
- safety models
- multimodal models
- inference runtimes and serving planes

### 3.8 Evaluation and lifecycle layer

This layer includes:
- offline evaluation suites
- online monitoring and sampling
- synthetic and human feedback loops
- prompt, model, and retrieval regression gates
- training, tuning, approval, and deployment lifecycle controls
- drift, bias, and freshness monitoring

### 3.9 Governance, safety, and evidence layer

This layer includes:
- policy-as-code
- capability eligibility rules
- tool and source allowlists
- identity and authorization controls
- audit trails
- provenance receipts
- redaction and sensitive-data controls
- reversibility and promotion controls

## 4. Cross-cutting concerns

The following concerns apply across all layers and MUST NOT be modeled as belonging to only one layer:
- identity and tenant isolation
- observability and tracing
- cost and latency measurement
- evidence and provenance
- policy enforcement
- replay and reversibility
- accessibility and operator usability
- local-first and degraded/offline modes where applicable

## 5. Required distinctions

### 5.1 Observability is not alignment

Observability, trace analytics, and token/cost logging MUST be modeled separately from governance,
safety, and policy controls.

### 5.2 Embeddings are not retrieval quality by themselves

Canonical retrieval quality work MUST distinguish:
- candidate generation
- reranking
- citation construction
- answer generation

### 5.3 Memory is not only chat history

Memory MUST be modeled as a broader state system that may include:
- session state
- preference state
- episodic history
- procedural reuse
- sovereign perspectives
- signed local knowledge graphs

### 5.4 Extraction is not only text parsing

Extraction MUST include text, layout, image, screen, document, and video pathways when multimodal
sources are in scope.

## 6. Mandatory minimum architecture for canonical designs

A canonical SocioProphet design MUST specify, at minimum:
1. ingress surfaces
2. orchestration and workflow control
3. tool / connector boundaries
4. retrieval architecture including reranking
5. system-of-record and provenance storage
6. ingestion and enrichment pathways
7. model/runtime strategy
8. evaluation and lifecycle controls
9. governance and evidence boundaries

Architectures that omit any of the above MUST explicitly state that they are partial or pedagogical.

## 7. Relationship to public documentation

Public-facing docs MAY use simplified diagrams for readability, but the underlying narrative SHOULD
map back to this normalized model.

Public docs MUST NOT imply that the full system reduces to only:
- a model choice
- a framework choice
- a vector database choice
- an embedding choice

## 8. Relationship to implementation repositories

Implementation repositories SHOULD map their contents to this layer model.
Runtime repos MAY implement only a subset of layers, but they MUST identify which layers they own
and which layers are upstream dependencies.

## 9. Related standards

- `000-platform-standards.md`
- `005-design-philosophy.md`
- `030-service-interfaces-tritrpc.md`
- `040-observability-otel.md`
- `050-security-oidc-policy.md`
- `080-knowledge-context.md`

## 10. Implementation evidence

Implementation repositories that adopt this standard SHOULD include a short mapping table in their README
or architecture docs that shows which normalized layers they implement.