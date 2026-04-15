# Vendor Adapter Security Standard

## Purpose

This standard defines the mandatory security posture for vendor adapters and local model gateways in our stack. It is a normative control document. It is not an external remediation memo, a third-party maintenance guide, or a product endorsement.

## Scope

This standard applies to any service that exposes one or more of the following surfaces:

- model inference APIs
- tool-calling or function-calling APIs
- model metadata or capability advertisement APIs
- administrative, debug, or observability endpoints
- local or remote tool transport bridges, including MCP-style integrations

## Core Security Objective

The primary security objective is to prevent semantic trust collapse between model output, tool intent, and executable capability.

## Normative Controls

### 1. Network Binding and Authentication

Non-loopback binds must require explicit authentication by default. Browser-origin checks may be used as a secondary browser control, but they do not count as authentication and must never be treated as network access control.

### 2. Administrative and Debug Surface Isolation

Administrative, debug, and trace endpoints must be isolated from the main inference surface. They must be loopback-only by default or protected by a distinct authorization scope.

### 3. Explicit Capability Scope

Advertised capability is not executable capability. Server-discovered or ambiently available tools must not silently widen executable scope for a request. Effective tool scope must be explicit per request or per policy context.

### 4. Strict Tool Intent

Executable tool intent must arrive in a strict structured form. Tool execution must not be triggered by heuristically extracting JSON or JSON-like content from prose, markdown, quoted examples, mixed-content responses, or permissively normalized partial payloads.

### 5. Planning and Execution Separation

Planning and execution must be separate phases. Side-effectful execution should default to plan-only or approval-gated operation unless a stronger policy explicitly authorizes immediate execution.

### 6. Tool Identity and Routing Integrity

Tool identifiers must be unambiguous within the effective execution scope. Duplicate or colliding tool names must fail closed rather than resolve through silent overwrite, precedence rules, or ambiguous routing behavior.

### 7. Transport and Subprocess Hygiene

Sensitive credentials must not be sent over unsafe transport paths. Response sizes and subprocess output must be bounded. Event-stream parsing must preserve protocol meaning and reject ambiguous or lossy interpretation.

### 8. Protocol Honesty

Unsupported API features must be declared explicitly. A gateway or adapter must not imply broad compatibility it cannot faithfully implement.

### 9. Documentation and Runtime Consistency

Documentation, CLI help, startup warnings, and runtime behavior must remain aligned. Security-relevant naming or behavior drift is a defect and must be corrected before release.

## Acceptance Gates

A service conforms to this standard only if all of the following are true:

1. Non-loopback startup without authentication fails hard by default.
2. Requests without explicit executable tool scope cannot execute tools.
3. Model prose containing JSON-like content cannot trigger execution.
4. Duplicate tool identities fail closed.
5. Administrative and debug surfaces are not exposed on the main inference plane without distinct authorization.
6. Unsafe credential transport is blocked.
7. Unsupported API features return explicit errors rather than degraded silent behavior.
8. Security-relevant docs and runtime flags are consistent.

## Non-Goals

This standard does not prescribe any specific vendor runtime, model provider, or third-party adapter implementation. It defines the minimum security properties our implementation must preserve regardless of substrate.

## Relationship to Companion Artifacts

This standard is the policy layer. The companion artifact `vendor_adapter_security_hardening_spec.md` remains the implementation-oriented doctrine, and `local_model_gateway_security_baseline.md` remains the concise operational baseline.
