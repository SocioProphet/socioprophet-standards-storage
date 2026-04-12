# 041 — Transparent Telemetry Standard

## Status
Draft v0.1

## Rationale
The platform requires explicit runtime measurement for reliability, abuse defense, experimentation, ingestion, and product understanding. Opaque collection weakens trust, complicates governance, and makes deletion/retention claims difficult to verify. This standard defines a transparent telemetry model that preserves operational strength while enforcing purpose separation, minimization, user legibility, and evidence-bearing lifecycle semantics.

## Standard

### 1. Plane separation
Implementations MUST classify every telemetry family into exactly one primary plane:
- reliability
- security_abuse
- product_analytics
- experimentation
- developer_diagnostics
- content_receipts

Implementations MUST NOT emit generic unlabeled telemetry.

### 2. Contract-first manifests
Every telemetry family MUST resolve to a versioned manifest before network send.
Each manifest MUST define:
- event name
- plane
- purpose
- trigger
- essential status
- user-disable policy
- field catalog
- forbidden fields
- transform rules
- sampling policy
- retention period
- destination sinks
- owners
- review date

### 3. Semantic minimization
Implementations SHOULD prefer bounded summaries, turn/session aggregates, and meaningful state transitions over impression-heavy or per-frame event streams.
Implementations MUST NOT place raw prompt text, raw assistant text, file names, connector object identifiers, or content snippets into the product analytics plane unless explicitly justified and reviewed.

### 4. Policy on the path
A policy engine MUST evaluate every event prior to send.
The policy engine MUST support these actions:
- BLOCK
- TRANSFORM
- AGGREGATE
- SAMPLE
- DELAY
- ALLOW

Policy decisions MUST be versioned and replayable.

### 5. User transparency
Implementations MUST provide a user-visible telemetry inspector or equivalent surface that shows recent telemetry decisions.
The inspector MUST show:
- event name
- plane
- purpose
- mandatory or optional status
- policy action taken
- destination sinks
- retention deadline
- receipt hash or equivalent integrity identifier

Implementations SHOULD provide a searchable manifest viewer and a personal telemetry export.

### 6. Receipts and lifecycle evidence
Each event decision MUST produce a receipt or explicit block record.
Receipts MUST include:
- event name
- manifest version
- policy version
- action taken
- timestamp
- destinations
- retention deadline
- integrity hash

Implementations MUST support explicit expiry and deletion state transitions for telemetry objects.

### 7. Retention
Reliability and security_abuse planes SHOULD use shorter retention windows than product_analytics unless a stronger governance requirement exists.
Product analytics and experimentation telemetry MUST be disableable when not essential to correctness or safety.
Developer diagnostics MUST be time-boxed and off by default.

### 8. Content-handling receipts
Implementations MUST represent file/content handling as auditable receipts rather than burying sensitive lifecycle events inside generic analytics.
Content-handling receipts SHOULD include create, upload, process, retrieval, citation-resolution, expiry, and deletion boundaries where applicable.

## Reference slice
A conforming minimal slice SHOULD support:
- conversation prepare lifecycle
- streamed response lifecycle
- completion or incomplete state
- timeout and resume events
- citation render summary
- citation panel opened state
- citation resolution receipt

## Related Standards
- 030-service-interfaces-tritrpc.md
- 040-observability-otel.md
- 050-security-oidc-policy.md
- 093-forensic-audit-nist-800-88.md

## Implementation Evidence
Initial companion materials should live under:
- `docs/standards/042-live-telemetry-inspector.md`
- `schemas/telemetry/`
