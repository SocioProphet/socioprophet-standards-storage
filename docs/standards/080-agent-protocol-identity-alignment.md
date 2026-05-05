# Agent Protocol Identity Alignment (Normative)

This document uses RFC 2119 language: **MUST**, **SHOULD**, **MAY**.

## 1. Purpose

This standard defines how external and adjacent agent protocols align with the SourceOS identity control plane.

The purpose is to prevent protocol adapters from inventing parallel identity semantics. A2A, MCP, ANP, AG-UI, and any future agent protocol MAY carry identity, capability, context, or UI interaction metadata, but they **MUST NOT** become independent sources of identity truth when the SourceOS identity control plane already defines canonical bindings.

## 2. Relationship to Standard 050

Standard 050 defines the canonical identity planes:

- workload identity plane,
- semantic human/event identity plane,
- human artifact readiness/export plane,
- runtime grant/policy plane,
- transport/receipt plane,
- execution/evidence plane.

This standard defines how protocol adapters bind into those planes.

## 3. Canonical identity tuple

Any privileged agent action crossing a trust boundary **MUST** bind to the canonical principal tuple:

- `spiffe_id`,
- `aum_digest`,
- optional `session_id`.

Protocol-local identifiers **MUST NOT** replace this tuple.

Examples of protocol-local identifiers include, but are not limited to:

- A2A agent card identifiers,
- MCP server/tool/resource identifiers,
- ANP linked-data identifiers,
- AG-UI conversation, component, or event identifiers.

These identifiers **MAY** be recorded as references or aliases, but they **MUST** resolve to or be bound by the canonical principal tuple before privileged runtime authorization.

## 4. Protocol role map

### 4.1 A2A

A2A is an agent-to-agent collaboration protocol. In this stack it **MAY** carry agent metadata, task metadata, messages, artifacts, and capability declarations.

A2A adapters **MUST** bind privileged task execution to:

- a `Grant`,
- a `PolicyDecision`,
- a canonical principal tuple,
- any applicable `RuntimeEvidenceRefs`.

A2A agent cards **MUST NOT** be treated as sufficient workload identity. They are discovery and capability descriptors, not proof of execution authority.

### 4.2 MCP

MCP is a context/tool/resource protocol. In this stack it **MAY** expose tools, resources, prompts, server capabilities, and contextual data.

MCP adapters **MUST** bind tool execution to:

- a canonical principal tuple,
- an authorization grant,
- policy decision evidence,
- tool provenance and sandbox posture.

MCP server identity **MUST NOT** be confused with human semantic identity or export readiness. Any MCP tool that reads, transforms, exports, or projects human-centric artifacts **MUST** consume the relevant semantic/export proof references before egress.

### 4.3 ANP

ANP-style agent network protocols are adjacent identity and negotiation surfaces. They may use linked-data identifiers, decentralized identifiers, service descriptors, or meta-protocol negotiation.

ANP-linked identifiers **MAY** be used as discovery, routing, or semantic references. They **MUST NOT** replace workload identity issuance, runtime grant identity, or evidence-bound authorization.

If ANP metadata includes JSON-LD or linked-data identity claims, those claims **MUST** be treated as asserted context until they are bound to:

- the canonical principal tuple,
- trusted-service identity evidence,
- policy decision evidence,
- and, when human-centric, Event-IR / ProofArtifact / HDT decision references.

### 4.4 AG-UI

AG-UI-style protocols are human-agent interaction and UI event surfaces. They may carry user actions, UI state, component events, or interaction transcripts.

AG-UI events **MAY** create session context and user-intent evidence. They **MUST NOT** independently authorize privileged runtime execution.

If AG-UI events initiate an agent action, the execution path **MUST** still pass through:

- runtime grant/policy evaluation,
- canonical principal binding,
- artifact readiness/export checks when human-centric content crosses a boundary,
- and replayable evidence capture in the execution/evidence plane.

## 5. Identity aliasing and resolution

Protocol adapters **MAY** record protocol-local aliases in evidence artifacts, but aliases **MUST** remain subordinate to canonical identity bindings.

The normative alias object for this standard is `schemas/identity/protocol_identity_aliases.schema.json`.

Recommended first-class alias fields are:

- `a2a_agent_card_ref`,
- `a2a_task_ref`,
- `mcp_server_ref`,
- `mcp_tool_ref`,
- `mcp_resource_ref`,
- `anp_agent_ref`,
- `anp_service_ref`,
- `agui_session_ref`,
- `agui_component_ref`,
- `agui_event_ref`.

Adapters **SHOULD** include protocol identity aliases in runtime evidence artifacts when they materially affect routing, discovery, authorization, or user intent.

Adapters **MUST NOT** treat the presence of a protocol alias as proof of authorization.

## 6. Evidence binding requirements

When an agent action crosses a trust boundary, protocol adapters **MUST** produce or preserve evidence sufficient to answer:

1. Which workload or service acted?
2. Which software/configuration bundle acted?
3. Which session or interaction scoped the action, if applicable?
4. Which policy authorized or denied the action?
5. Which semantic/export evidence influenced the decision, if applicable?
6. Which transport or UI protocol carried the request?
7. Which protocol-local aliases were involved?
8. Which replay/evidence artifact records the outcome?

## 7. Non-goals

This standard does not define the A2A, MCP, ANP, or AG-UI wire formats.

This standard does not make any adjacent protocol authoritative for SourceOS identity.

This standard does not prevent protocol-native identifiers from being used. It only requires them to be bound into the canonical identity, governance, and evidence planes before privileged action.

## 8. Conformance

A protocol adapter conforms to this standard when it provides:

- a protocol-local identity alias map conforming to `ProtocolIdentityAliases`,
- a canonical principal binding procedure,
- a grant/policy decision binding procedure,
- evidence references for semantic/export proof inputs when applicable,
- replayable evidence artifacts for privileged execution,
- negative tests proving protocol-local identifiers cannot bypass canonical authorization.
