# 042 — Live Telemetry Inspector Standard

## Status
Draft v0.1

## Rationale
A telemetry system is not transparent merely because a privacy policy exists. Transparency requires a first-class product surface that lets a user inspect what fired, why it fired, whether it was mandatory, where it went, and how long it will be kept. This standard defines the minimum inspector behavior for systems adopting the Transparent Telemetry Standard.

## Standard

### 1. Inspector requirement
Implementations conforming to the transparent telemetry model MUST provide a live telemetry inspector or an equivalent first-class inspection surface.

### 2. Minimum event row fields
The inspector MUST render, for each recent telemetry decision:
- event name
- plane
- purpose
- mandatory or optional status
- action taken by policy engine
- transformed field list or summary
- destination sink set
- timestamp
- retention deadline
- receipt hash or integrity identifier

### 3. State model
The inspector MUST visually distinguish at least these states:
- allowed
- blocked
- transformed
- aggregated
- sampled
- delayed
- expired
- deleted

Implementations MAY render composite states such as `aggregate_allow` or `transform_allow`.

### 4. User controls
The inspector MUST link to or embed plane-level controls for:
- service integrity telemetry
- abuse-defense telemetry
- experimentation telemetry
- product analytics telemetry
- optional diagnostics

If a plane is essential and cannot be disabled, the inspector MUST say so explicitly.

### 5. Explanations
For blocked or transformed events, the inspector MUST display the reason.
Examples:
- disabled by user
- forbidden field present
- excessive frequency
- diagnostics expired
- jurisdiction denied

### 6. Export
Implementations SHOULD provide export of recent receipts in JSONL or equivalent open format.
The export SHOULD preserve:
- event name
- plane
- policy action
- timestamp
- retention deadline
- integrity hash

### 7. Filtering and search
The inspector SHOULD support filtering by:
- plane
- action state
- time window
- mandatory or optional
- destination sink

The inspector SHOULD support text search over event name and purpose.

### 8. Privacy constraints
The inspector MUST NOT reveal forbidden fields merely because the inspector itself is visible.
If an event was transformed or redacted, the inspector SHOULD show field names or field classes, not the removed values.

### 9. Reference slice behavior
For the conversation-streaming plus citation slice, the inspector MUST show at least:
- conversation.prepare.started
- conversation.prepare.succeeded
- conversation.stream.started
- conversation.stream.completed or conversation.stream.incomplete
- conversation.timeout_reached when applicable
- conversation.resume.attempted and outcome when applicable
- analytics.turn.rendered.summary
- analytics.citations.rendered.summary
- analytics.citation_panel.opened when applicable
- receipts.citation_resolution.summary

### 10. Acceptance criteria
A conforming inspector MUST satisfy:
1. blocked events remain visible as blocked decisions
2. transformed events show transformed field summaries
3. retention deadlines are visible for allowed events
4. users can distinguish essential from optional telemetry
5. users can navigate from inspector entries to manifest definitions
6. receipt hashes remain stable across export and local display

## Related Standards
- 041-transparent-telemetry.md
- 040-observability-otel.md
- 093-forensic-audit-nist-800-88.md

## Implementation Evidence
Initial package evidence should live under:
- `schemas/telemetry/`
- implementation repo inspector UI paths once available
