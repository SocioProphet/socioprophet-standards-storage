# Source Alignment v0

Status: Draft-for-execution
Decision record: EDR-GWOP-2026-06-05-001
Owning issue: #92

This file maps uploaded design sources into the Google Workspace Operations Prototype standard.

## 1. CSKG into TriTRPC VNext alignment blueprint

Imported rule: cadence separation.

- Hot-path surfaces carry compact routing and control metadata.
- Rich semantic truth belongs in payloads, manifests, ledgers, and canonical registries.
- Calendar events should carry compact structured metadata only; meeting notes, decision records, and artifacts carry richer semantic truth.
- Dashboard panels should read from ledgers, not from raw calendar prose.

Workspace consequence:

- Calendar description metadata is a cadence-scoped control header.
- Drive notes and Sheets rows are the semantic payload layer.
- Later SocioProphet migration should preserve this split as `CadenceEvent` plus `GovernanceSession` plus `ArtifactRef`.

## 2. Bluesky Adapter Realization Plan

Imported rule: external adapters are not semantic truth.

- External network source state, execution truth, canonical knowledge objects, scope/governance plane, distribution plane, and synchronous control plane must remain separate.
- Workspace prototype adopts the same separation: Google Calendar is not the decision truth, Groups are not identity truth, Drive is not necessarily standards truth, dashboards are not source data.

Workspace consequence:

- `source_ref`, `artifact_ref`, `event_ref`, `calendar_event_id`, and `dashboard_key` remain separate identifiers.
- Automation must record source and target object references separately.
- Any derived routing, ranking, or extraction step must emit a receipt-like automation record.

## 3. Bluesky Adapter PR Map

Imported rule: split work by repository and responsibility.

- Slash topics, knowledge standards, New Hope carrier logic, implementation module, and hardening work are separate PR lanes.
- Workspace prototype should likewise split normative standard, implementation scripts, dashboards, and runtime migration issues.

Workspace consequence:

- This standards repo owns schemas and operating contracts.
- Apps Script prototypes and runtime services belong in implementation repositories later.
- Dashboard configurations should be treated as derived implementation artifacts.

## 4. SocioProphet Labor Network Charter

Imported rule: request-centric operations.

- The management layer should model work as structured request + response + evidence + fulfillment + trust.
- We should not manage work as ambient feed, chat scroll, or generic calendar churn.

Workspace consequence:

- Add `Requests` and `Responses` tabs to the operational ledger.
- Governance meetings should produce typed requests, action items, decisions, risks, or trust events.
- Labor/work management dashboards prioritize requests, matches, work in progress, evidence, and trust events over generic activity.

## 5. Identity Is Prime landing-zone section

Imported rule: projection surfaces must be policy-gated.

- The landing zone is a convergence layer for semantics, policy, proofs, storage, sync, projection, and control.
- Sensitive semantics remain close to the core; outward surfaces are deliberately coarsened.
- Policy must be executable, inspectable, replayable, and operational.

Workspace consequence:

- Groups and calendars are projection/control surfaces, not identity truth.
- Automation runs must preserve policy and replay references.
- Dashboards surface coarsened operational state and must not leak private identity or proof detail.
- Migration readiness should test semantic, policy, proof, projection, storage/sync, and control-plane coverage.

## 6. Context Management Patterns

Imported rule: persistent artifact state beats ephemeral conversation state.

- Conversation context can be summarized or lost; artifacts, commits, and persistent state survive.
- Workspace prototype must write durable decisions, actions, risks, and schemas into Sheets, Drive, and GitHub.

Workspace consequence:

- No governance decision is considered captured until it exists as a ledger row or committed artifact.
- Meeting summaries are not enough; structured rows and artifact refs are required.
- The `MigrationReadiness` tab tracks whether prototype state is durable enough to move into SocioProphet.

## 7. Sherlock Shell Matrix Room Administration Runbook

Imported rule: human control rooms project state and collect approvals; they are not systems of record.

- Rooms can act as human control planes, queue spaces, case rooms, admin rooms, and bridge rooms.
- Rooms project canonical state and collect approvals; authoritative case/search state lives elsewhere.
- Bridge rooms are lower trust and require explicit policy.

Workspace consequence:

- Calendars and Chat/Matrix rooms are approval and coordination projections.
- The ledger stores canonical prototype state.
- Dedicated bridge/control surfaces should be represented explicitly in `Calendars`, `Groups`, and `Artifacts` ledgers.
- Bot or bridge automations must be isolated from admin groups and must emit replay-protected run records.

## Consolidated design law

Google Workspace is a projection and rehearsal surface. SocioProphet owns the future native model. The prototype is successful when every useful Workspace behavior has a typed ledger representation, a dashboard projection, an automation-run trace, and a migration target.
