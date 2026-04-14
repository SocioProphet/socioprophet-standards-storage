# Local Model Gateway Security Baseline

## Purpose

This baseline defines the minimum security posture for any local model gateway or vendor-adapter service that exposes inference, tool calling, model metadata, or administrative observability surfaces.

The purpose is not to mirror any external implementation. The purpose is to prevent known classes of trust collapse that commonly emerge when convenience-oriented adapters bridge model output to executable tools.

## Baseline Controls

### 1. Binding and Authentication

A non-loopback bind must require explicit authentication by default. Browser-origin checks may be used as a secondary browser control, but they do not count as authentication and must not be treated as network access control.

### 2. Capability Scope

Advertised capability is not executable capability. Tool execution scope must be explicit per request or policy context. Ambient server-side tool availability must not silently widen what a request is allowed to execute.

### 3. Tool Intent

Executable tool intent must be structurally explicit and schema-valid. Tool calls must not be inferred from prose, markdown, quoted examples, or permissively normalized partial payloads.

### 4. Planning Versus Execution

Planning and execution must be separate phases. Side-effectful tools should default to plan-only or approval-gated execution unless a stronger policy explicitly authorizes immediate execution.

### 5. Tool Identity and Routing

Tool identifiers must be unambiguous. Duplicate names or ambiguous routing targets must fail closed rather than resolve by overwrite or precedence rules hidden from the caller.

### 6. Administrative and Debug Surfaces

Debug logs, request traces, and operational introspection endpoints must be isolated from the main inference surface. They should be loopback-only by default or protected by a distinct authorization scope.

### 7. Transport Hygiene

Sensitive credentials must not be sent over unsafe transport paths. Response sizes and subprocess output must be bounded. Event-stream parsing should be strict enough to preserve protocol meaning and resist ambiguity.

### 8. Protocol Honesty

Unsupported features must be declared explicitly. A gateway must not pretend to support API surfaces it cannot faithfully implement.

## Acceptance Gates

A gateway meets this baseline only if all of the following are true:

1. Non-loopback startup without auth fails hard by default.
2. Requests without explicit tool scope cannot execute tools.
3. Model prose containing JSON-like content cannot trigger execution.
4. Duplicate tool names fail closed.
5. Debug and admin surfaces are not exposed on the main inference plane without distinct authorization.
6. Unsafe credential transport is blocked.
7. Unsupported API features return explicit errors rather than degraded silent behavior.

## Implementation Note

This baseline is designed to pair with the companion artifact `vendor_adapter_security_hardening_spec.md`, which contains the more detailed doctrinal and implementation-oriented treatment of these controls.
