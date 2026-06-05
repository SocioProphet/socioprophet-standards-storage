# Google Workspace Operations Prototype v0

Status: Draft-for-execution
Decision record: EDR-GWOP-2026-06-05-001
Owning issue: #92
Companion workstream: cloud-vendor-strategy issue #91

## Thesis

Google Workspace is the disposable prototype control plane for SocioProphet operations. Calendars, groups, Drive folders, Sheets ledgers, Gmail/Chat notifications, and dashboard surfaces are used to prototype management cadence, approvals, routing, and observability. They are not the final system of record.

The migration target is SocioProphet-native control, where cadence, role binding, artifact registry, decision records, work requests, automations, dashboards, and policy gates are first-class objects.

## Non-negotiable invariants

1. Calendars project cadence and collect participation; they do not own operational truth.
2. Groups project roles and access boundaries; durable group IDs must be recorded separately from mutable email labels.
3. Drive stores prototype artifacts; GitHub standards and SocioProphet registries remain canonical for normative standards.
4. Sheets acts as the temporary operational ledger; every row must be migratable into a typed SocioProphet object.
5. Dashboards are management projections over ledgers; dashboards are not source data.
6. Automations must emit run records; no silent automation is allowed.
7. External networks and rooms are lower-trust ingress/approval surfaces unless promoted by explicit policy.
8. Canonical truth, execution truth, transport truth, source truth, and projection truth remain separate.
9. Request-centric operations are preferred over feed-centric operations.
10. Context is preserved in artifacts and ledgers, not only in chat or calendar prose.

## Prototype layers

| Layer | Google Workspace surface | SocioProphet native target |
|---|---|---|
| Cadence | Google Calendar events and recurring meetings | `CadenceEvent`, `GovernanceSession` |
| Role graph | Google Groups / Cloud Identity groups | `RoleBinding`, `CapabilityGrant` |
| Artifact graph | Drive folders, Docs, Sheets, GitHub links | `ArtifactRef`, `EvidenceObject`, `DecisionRecord` |
| Work graph | Sheets rows for requests, actions, risks, decisions | `Request`, `Response`, `ActionItem`, `Risk`, `TrustEvent` |
| Automation graph | Apps Script triggers and run logs | `AutomationRun`, `WorkflowExecution` |
| Dashboard graph | Sheets + Looker Studio | `DashboardPanel`, `MetricDefinition` |
| Approval/control rooms | Calendar/Chat/Matrix rooms | `ApprovalSurface`, `ControlRoomProjection` |

## First managed workstream

The first workstream is `cloud-vendor-strategy`, anchored by GitHub issue #91.

Required prototype surfaces:

- Calendar: `SP - Cloud Vendor Strategy`
- Calendar: `SP - Launch Council`
- Groups: `sp-launch-council`, `sp-product`, `sp-engineering`, `sp-partner-gtm`, `sp-legal-finance`, `sp-support-ops`, `sp-auditors`
- Drive folder: `/Prophet Operations/03-Cloud-Vendor-Strategy/`
- Sheet: `SocioProphet Operations Control Plane - Prototype`
- Dashboards: Executive Control Plane, Cloud Vendor Strategy, Automation Health, Migration Readiness

## Required ledger tabs

- `Workstreams`
- `Calendars`
- `Groups`
- `Meetings`
- `Decisions`
- `Requests`
- `Responses`
- `ActionItems`
- `Risks`
- `Artifacts`
- `Automations`
- `Dashboards`
- `CloudVendorReadiness`
- `MigrationReadiness`

## Migration rule

A Google Workspace prototype object is ready for SocioProphet migration when:

1. its ledger row schema has stabilized across at least two review cycles,
2. its source and target object identifiers are explicit,
3. its role and permission dependencies are recorded,
4. its automation behavior emits an `AutomationRun`, and
5. its dashboard representation can be regenerated from ledger data.

## Artifact map

- `schemas/ops-ledger.v0.yaml` defines sheet tabs and canonical column contracts.
- `schemas/calendar-event-metadata.v0.yaml` defines structured metadata embedded in calendar descriptions.
- `schemas/group-binding.v0.yaml` defines group-to-role bindings.
- `schemas/automation-run.v0.yaml` defines automation execution logging.
- `dashboards/panels.v0.md` defines the prototype dashboard panels.
- `alignment/source-alignment.v0.md` maps uploaded design sources into this standard.
