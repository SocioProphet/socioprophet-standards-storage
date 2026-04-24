# Vendor Adapter Security Verification Matrix

This document maps the vendor-adapter security controls to concrete verification paths, expected evidence, and downstream runtime consumers.

## Verification posture

The package defines normative controls in:
- `standard.md`
- `vendor-adapter-security-controls-checklist.yaml`

This matrix translates those controls into executable or reviewable verification work.

## Control mapping

| Control ID | Control Summary | Verification Type | Evidence | Automation Target | Priority |
| --- | --- | --- | --- | --- | --- |
| VAS-001 | Non-loopback binds require authentication | startup integration test | startup failure on remote bind without token | CI + runtime smoke test | P0 |
| VAS-002 | Origin checks are secondary browser controls only | design + middleware review | code path and docs alignment | static policy review | P1 |
| VAS-003 | Debug and admin surfaces are isolated | route exposure test | debug routes inaccessible without separate scope | integration test | P0 |
| VAS-004 | Advertised tools do not widen executable scope | handler behavior test | omitted tool declarations produce empty execution scope | unit + integration test | P0 |
| VAS-005 | Executable tool intent must be structured | negative parser test | prose and markdown JSON cannot execute | parser negative tests | P0 |
| VAS-006 | No permissive argument coercion | negative parser test | empty or plain-string arguments fail closed | parser negative tests | P0 |
| VAS-007 | Planning and execution are separate phases | execution-flow policy test | side-effectful execution requires explicit mode or approval | integration + policy test | P0 |
| VAS-008 | Tool identifiers are unambiguous | startup registry test | duplicate tool names fail closed | startup test | P0 |
| VAS-009 | Sensitive credentials never traverse unsafe transport | transport negative test | remote plaintext bearer-token path refused | transport test | P0 |
| VAS-010 | Response and subprocess outputs are bounded | resource-policy test | response size caps and bounded stderr observability | integration + resource test | P1 |
| VAS-011 | Unsupported features are declared explicitly | API contract test | unsupported endpoints return explicit errors | API compatibility suite | P1 |
| VAS-012 | Docs and runtime behavior stay aligned | documentation consistency review | CLI help, docs, and startup warnings match | release checklist + docs lint | P1 |

## Acceptance gate mapping

| Acceptance Gate | Controls | Suggested Evidence |
| --- | --- | --- |
| AG-001 | VAS-001 | startup log + failing remote-bind test |
| AG-002 | VAS-004, VAS-007 | request-handler trace + integration result |
| AG-003 | VAS-005, VAS-006 | negative parser tests |
| AG-004 | VAS-008 | startup failure with duplicate tool registry |
| AG-005 | VAS-003 | route-exposure test and auth policy evidence |
| AG-006 | VAS-009 | transport refusal test |
| AG-007 | VAS-011 | explicit error responses for unsupported features |

## Downstream consumers

Expected downstream runtime or policy consumers include:
- `agentplane`
- `sociosphere`
- `prophet-platform`
- any local model gateway or adapter runtime that exposes tool-calling, bridge, or administrative control surfaces

## Recommended follow-on

1. Bind each verification row to a concrete CI job in the corresponding runtime repository.
2. Add a schema validator step for `vendor-adapter-security-controls-checklist.yaml`.
3. Add a release checklist step that verifies security-doc and runtime-flag consistency.
