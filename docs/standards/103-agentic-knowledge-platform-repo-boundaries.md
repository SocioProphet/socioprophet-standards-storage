# Agentic Knowledge Platform Repository Boundaries

This document uses RFC 2119 language: **MUST**, **SHOULD**, **MAY**.

## 1. Scope

This standard defines repository placement rules for agentic knowledge platform artifacts across the
SocioProphet ecosystem.

Its purpose is to prevent canonical doctrine, public documentation, and runtime implementation details
from drifting into the wrong repositories.

## 2. Canonical repository roles

### 2.1 Standards authority repository

The standards authority repository is the canonical home for:
- normalized architectural doctrine
- standards and MUST/SHOULD/MAY requirements
- cross-repo inventory models
- architectural placement rules
- ADRs documenting repo-boundary and canonical-source decisions

For the current ecosystem, this role is performed by:
- `SocioProphet/socioprophet-standards-storage`

### 2.2 Public surface repository

The public surface repository is the canonical home for:
- public-safe summaries
- public docs pages
- web/docs presentation structure
- public navigation and reading paths
- mirrors of canonical standards where a public summary is appropriate

It is NOT automatically the canonical home for shared standards or subsystem doctrine.

For the current ecosystem, this role is performed by:
- `SocioProphet/socioprophet`

### 2.3 Runtime and deployment repository

The runtime/deployment repository is the canonical home for:
- concrete service topology
- runtime bindings
- deployable service contracts
- infra wiring and deployment manifests
- implementation-specific docs derived from upstream standards

It is NOT the canonical home for cross-repo doctrine unless explicitly designated.

For the current ecosystem, this role is performed by:
- `SocioProphet/prophet-platform`

### 2.4 Knowledge-context repository

A knowledge-context repository MAY carry:
- capability ontologies
- semantic crosswalks
- knowledge context schemas
- specialized knowledge-layer standards derived from upstream platform invariants

It is not the first landing zone for broad platform layer doctrine.

For the current ecosystem, this role is performed by:
- `SocioProphet/socioprophet-standards-knowledge`

## 3. Placement rules

### 3.1 Standards-first rule

When a new artifact defines shared doctrine for multiple repositories, it MUST land first in the standards
authority repository.

### 3.2 Public-mirror rule

When an artifact has public explanatory value, a public-safe summary MAY be mirrored in the public surface
repository after the canonical standards source exists.

### 3.3 Runtime-derivation rule

When a runtime repository needs implementation-facing guidance, that guidance SHOULD be derived from the
canonical standards artifact and MUST identify itself as an implementation mapping, binding, or deployment profile.

### 3.4 No public-first canonization

A new cross-repo architectural doctrine MUST NOT be canonized first in the public surface repository.
Doing so creates ambiguity and ownership drift.

## 4. Application to the agentic knowledge platform package

The following artifacts MUST live first in the standards authority repository:
- normalized layer model
- tooling inventory
- integration patterns
- repository boundary doctrine
- ADRs for package placement and canonical ownership

The following artifacts MAY mirror into the public surface repository:
- public-safe architecture summary pages
- product and enterprise pattern narratives derived from the canonical package

The following artifacts SHOULD land in the runtime repository after the standards package exists:
- runtime topology mappings
- concrete event and contract stubs
- deployment-specific architecture notes

The following artifacts MAY later land in the knowledge-context repository:
- capability ontology crosswalks
- semantic model mappings for layer/function vocabulary

## 5. Required cross-references

Any public or runtime derivative of the canonical package SHOULD link back to the relevant standard documents.
Any standard that defines a repo boundary SHOULD identify the intended downstream mirrors and derivatives.

## 6. Failure modes this standard prevents

This standard exists to prevent the following failure modes:
- the website repo becoming the accidental canonical home for platform doctrine
- runtime repos carrying shared doctrine without upstream reference
- knowledge-context repos absorbing general platform architecture prematurely
- generated inventory pages being mistaken for the canonical standards source

## 7. Related standards

- `000-platform-standards.md`
- `006-ecosystem-repos-docs-milestones.md`
- `080-knowledge-context.md`
- `100-agentic-knowledge-platform-layer-model.md`
- `101-agentic-knowledge-platform-tooling-inventory.md`
- `102-agentic-knowledge-platform-integration-patterns.md`

## 8. Implementation evidence

Derivative repositories SHOULD identify the exact upstream standards file they are implementing or summarizing.
Canonical standards SHOULD list the downstream repositories that consume them.