# 148 Telemetry Control Plane and Recovery

## Status
Proposed v1.

## Rationale
`040-observability-otel.md` defines the OpenTelemetry baseline. This companion standard defines the portable control-plane, cache, error-tier, and recovery behavior required for interactive runtimes and platform UIs.

## Normative requirements

### 1. Telemetry control plane
Implementations MUST expose a telemetry control plane capable of:
- structured event logging,
- feature-gate and experiment exposure logging,
- dynamic configuration lookup,
- sender flush coordination,
- failure annotation.

The telemetry control plane MUST remain separable from the business-domain event plane.

### 2. Bootstrap-safe logger
Interactive runtimes MUST provide a buffered startup logger that can accept timings, first-occurrence timings, and structured errors before the final sink is ready.

The bootstrap logger MUST flush buffered signals once initialization completes.
If signals are coalesced or dropped, the behavior MUST be documented.

### 3. Signal envelope
Every telemetry signal MUST carry:
- `ts_ms`
- `signal_class`
- `event_name`
- `source`
- `session_id`
- `build_id`

Where relevant, implementations SHOULD also emit:
- `trace_id`
- `span_id`
- `request_id`
- `workspace_id`
- `conversation_id`
- `query_key`
- `query_hash`
- `cache_key`
- `cache_version`
- `error_boundary`
- `error_tier`
- `recovery_policy`

### 4. Error tiers
Errors MUST be classified into at least:
- `recoverable`
- `caught`
- `uncaught`

Boundary-contained failures SHOULD include a boundary identifier.
Recovery actions MUST be emitted as first-class telemetry events.

### 5. Query and cache observability
Cacheable data paths MUST expose stable query identity via `query_key` and/or `query_hash`.
Cache instrumentation MUST include hit/miss, presence, version, write failure, and eviction reason.

Persistent cache reads MUST NOT mutate storage solely to maintain read counters or touch markers.
Implementations SHOULD instrument storage pressure and quota headroom proactively.

### 6. Client-side persistence
Large query results, paginated histories, and evidence artifacts MUST NOT rely on unbounded localStorage persistence.
IndexedDB, SQLite-wasm, or another bounded structured store SHOULD be used for non-trivial client persistence.

Storage failures MUST fail safely and MUST emit structured telemetry.

### 7. Recovery semantics
UI or render exceptions MUST NOT trigger broad destructive cache purges by default.
Recovery SHOULD prefer scoped eviction by namespace, feature surface, or cache key.
Global purge MAY be used only as a last resort and MUST emit a high-severity recovery event.

### 8. Sender lifecycle
Telemetry senders MUST support batched delivery.
Senders SHOULD support compression, retry, pre-flush hooks, post-flush hooks, and beacon-like unload delivery where supported.

### 9. Signal planes
Implementations MUST distinguish at least these planes:
- product
- control
- data
- failure
- recovery
- security

### 10. Security and privacy
Telemetry MUST avoid raw secret material, bearer tokens, and full credential payloads.
Security-significant decisions such as policy denials, attestation failures, and evidence-chain breaks MUST retain durable correlation identifiers.

## Related standards
- `040-observability-otel.md`
- `050-security-oidc-policy.md`

## Implementation evidence
Initial downstream consumers:
- `SocioProphet/prophet-platform`
- `SocioProphet/global-devsecops-intelligence`
