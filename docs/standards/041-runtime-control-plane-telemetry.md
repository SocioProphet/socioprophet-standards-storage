# 041 Runtime Control Plane Telemetry

## Status
Proposed v2.

## Rationale
Interactive agentic platforms require more than generic observability. Runtime control planes must expose bootstrap evaluation, feature and dynamic configuration state, retry and stream policy, connector action boundaries, client memory surfaces, and recovery behavior as typed telemetry.

## Required object model
Implementations MUST model the following objects:

- `BootstrapEnvelope` — server-delivered startup state for identity, configuration, experiment evaluation, and runtime policy.
- `EvaluationSet` — evaluated gates, experiments, dynamic configs, layers, and secondary exposures.
- `RuntimePolicy` — cache, retry, stream, polling, concurrency, and timeout policy.
- `ConnectorRoutingProfile` — connector enablement, lexical routing, soft mentions, and action permissions.
- `ClientMemorySurface` — device, session, draft, onboarding, survey, recency, and maintenance checkpoint state.
- `TelemetryEnvelope` — emitted signal envelope with event, source, correlation, and recovery fields.
- `SensitiveBootstrapMaterial` — raw bootstrap data that requires redaction before storage or publication.

## Required signal fields
Telemetry signals MUST include:
- `event_name`
- `signal_class`
- `source`
- `ts_ms`
- `build_id`
- `environment`

Where available, signals SHOULD include:
- `trace_id`
- `span_id`
- `request_id`
- `session_id`
- `workspace_id`
- `user_id_hash`
- `query_key`
- `query_hash`
- `cache_key`
- `cache_version`
- `policy_decision_id`
- `artifact_digest`
- `recovery_policy`

## Transport coverage
Instrumentation MUST account for `fetch`, `XMLHttpRequest`, and beacon-style unload delivery.
A telemetry implementation MUST NOT assume that all browser telemetry uses `fetch`.

## Runtime policy requirements
Implementations MUST expose:
- retry count and backoff policy,
- stream idle and between-byte timeout policy,
- cache TTL and garbage-collection policy,
- polling interval and polling deadline policy,
- connector action enablement and deny rules,
- session recording and privacy posture where applicable.

## Client persistence requirements
Small UX memory MAY use local durable storage.
Large query results, paginated histories, evidence artifacts, and runtime records MUST use bounded structured stores or server-side persistence.
Write-on-read cache mutation is prohibited.

## Recovery requirements
Recovery MUST be scoped by feature surface, namespace, cache key, or artifact class whenever possible.
Global destructive purge is a last resort and MUST emit a high-severity recovery event.

## Redaction requirements
Raw bootstrap captures MUST be treated as sensitive. Implementations MUST redact tokens, account identifiers, precise user context, and signed URLs before committing examples, fixtures, issue comments, or evidence bundles.

## Related standards
- `030-service-interfaces-tritrpc.md`
- `040-observability-otel.md`
- `050-security-oidc-policy.md`

## Implementation evidence
Downstream consumers include `prophet-platform`, `global-devsecops-intelligence`, `agentplane`, and `policy-fabric` runtime/policy surfaces.
