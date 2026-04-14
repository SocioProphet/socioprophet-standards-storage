# Agentic Knowledge Platform Tooling Inventory

This document uses RFC 2119 language: **MUST**, **SHOULD**, **MAY**.

## 1. Scope

This standard defines the canonical tooling inventory categories for the SocioProphet agentic knowledge platform.
It is intentionally broader than a conventional "agentic RAG" inventory because the platform includes
workflow, multimodal reasoning, support operations, academy/discovery, and sovereign local state.

The purpose of this document is not to endorse specific vendors. The purpose is to define the classes of
technology that MUST be considered whenever the platform stack is analyzed, compared, or proposed.

## 2. Inventory method

Inventory work MUST distinguish between:
- **function** — what the system must do
- **tool class** — the type of component that can satisfy the function
- **candidate implementation** — a specific project or product
- **canonical role** — whether a component is system-of-record, derived index, control plane, runtime, or operator surface

Inventories MUST NOT present candidate implementations without also identifying the function they serve.

## 3. Canonical inventory by layer

### 3.1 Surface and channel layer

Required inventory categories:
- public site and docs surfaces
- operator console and shell-equivalent surfaces
- support/caseflow surfaces
- academy and people-development surfaces
- APIs and integration surfaces
- chat and messaging surfaces
- builder and developer surfaces

Representative patterns observed in the input corpus:
- terminal-first agent surfaces
- public-safe architecture/docs surfaces
- support portal and case-routing surfaces
- people/coaches/teams/communities/discovery surfaces

### 3.2 Application and orchestration layer

Required inventory categories:
- HTTP/API backends
- workflow engines and workflow SDKs
- orchestration graphs and runtime controllers
- state propagation and controller/event patterns
- approval and escalation machinery
- modular business/infrastructure backends

Representative patterns observed in the input corpus:
- modular backend compositions with infrastructure modules for caching, events, files, notifications, and locking
- controller-driven UI state propagation rather than ad hoc prompt-only interfaces

### 3.3 Tooling and integration layer

Required inventory categories:
- connectors to enterprise systems and knowledge sources
- function/tool registries
- sandboxed code/tool execution adapters
- file, notification, and event integration services
- collaboration and communication adapters
- external business system adapters

Representative patterns observed in the input corpus:
- Slack, Teams, email, file systems, HRIS, admin/storefront, and support-system integration
- workflow SDK and modular infrastructure integration surfaces

### 3.4 Retrieval and reasoning layer

Required inventory categories:
- lexical search
- vector search
- hybrid retrieval orchestration
- rerankers
- citation/provenance assemblers
- query rewrite and source-routing logic
- graph-aware retrieval when relations matter

Mandatory note:
A canonical inventory MUST treat reranking as a first-class category. It MUST NOT collapse reranking
into embeddings or vector storage.

### 3.5 Knowledge and state layer

Required inventory categories:
- raw artifact/object storage
- metadata and provenance store
- vector index
- lexical index
- graph / ontology / knowledge context store
- memory stores and perspective stores
- asset reuse graphs and typed knowledge assets

Representative patterns observed in the input corpus:
- signed local knowledge graphs
- user-owned perspective stores
- asset reuse managers and recommendation feedback loops

### 3.6 Ingestion and enrichment layer

Required inventory categories:
- crawling and web extraction
- document parsing and layout extraction
- OCR and image/document handling
- video/screen/image enrichment
- deduplication and normalization
- semantic tagging and entity extraction
- permission sync and ACL propagation

Mandatory note:
Inventories MUST distinguish extraction from enrichment. Parsing a document and constructing a multimodal,
permission-aware, citation-ready knowledge artifact are not the same operation.

### 3.7 Model and runtime layer

Required inventory categories:
- foundation models
- embedding models
- rerankers and cross-encoders
- classifiers and policy/safety models
- multimodal models
- local and remote inference runtimes
- model gateways and routers

Mandatory note:
A model runtime such as a local-serving layer MAY host an embedding model but MUST NOT be treated as the
embedding model itself.

### 3.8 Evaluation and lifecycle layer

Required inventory categories:
- offline evaluation harnesses
- online monitoring and trace review
- synthetic feedback systems
- automatic baseline comparison systems
- human review queues
- model/prompt/retrieval regression suites
- training/tuning/deployment pipelines
- drift, bias, freshness, and approval controls

Representative patterns observed in the input corpus:
- synthetic preference-learning loops
- automatic win-rate comparison against baselines
- development → pre-production → production evaluation pipelines

### 3.9 Governance, safety, and evidence layer

Required inventory categories:
- identity and authorization controls
- policy-as-code
- prompt injection and source-trust defenses
- audit and evidence capture
- sensitive data controls and redaction
- promotion, rollback, and reversibility controls
- provenance and receipt systems

Mandatory note:
Observability products MUST be inventoried separately from safety/governance controls even when a single
product supports both reporting and policy workflows.

## 4. Specific omissions the canonical inventory must correct

Any canonical inventory derived from a simple agentic stack pyramid MUST explicitly add the following
missing categories:
- application modules and workflow engines
- gateways, caches, and event buses
- metadata/provenance stores
- lexical search and hybrid retrieval
- rerankers
- multimodal runtime plane
- sovereign local state / perspective graph plane
- support operations and case-routing plane
- academy, discovery, and matching plane
- evaluation/feedback/training lifecycle plane

## 5. Open-source-first posture

Canonical inventories SHOULD prefer open-source or self-hostable candidate implementations when feasible.
When a managed or proprietary candidate is listed for comparison, the inventory SHOULD also list:
- the corresponding open class of alternative
- the reason the managed candidate was considered
- the lock-in, trust, or portability tradeoffs

## 6. Repository placement for inventory artifacts

The canonical inventory belongs in the standards authority repository.
Public summaries MAY mirror the inventory in public docs.
Runtime repos SHOULD only carry the subset of inventory relevant to their owned implementation surface.

## 7. Related standards

- `100-agentic-knowledge-platform-layer-model.md`
- `030-service-interfaces-tritrpc.md`
- `040-observability-otel.md`
- `050-security-oidc-policy.md`
- `080-knowledge-context.md`

## 8. Implementation evidence

Future repo mappings SHOULD show, per repository:
- owned inventory categories
- external dependencies
- controlled interfaces between categories
- explicitly out-of-scope categories