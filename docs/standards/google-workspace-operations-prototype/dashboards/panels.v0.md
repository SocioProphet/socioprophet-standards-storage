# Dashboard Panels v0

Status: Draft-for-execution
Decision record: EDR-GWOP-2026-06-05-001
Owning issue: #92

Dashboards are projections over ledger tabs. They do not own data and must be regenerable from Sheets or later SocioProphet-native stores.

## 1. Executive Control Plane

Source tabs: `Workstreams`, `Risks`, `Decisions`, `ActionItems`, `CloudVendorReadiness`

Panels:

- Active workstreams by status
- Open blockers by severity
- Open decisions by owner group
- Overdue action items
- SEV-1 risks
- Cloud vendor readiness by AWS / Azure / GCP
- Next governance meetings

## 2. Cloud Vendor Strategy

Source tabs: `CloudVendorReadiness`, `Artifacts`, `ActionItems`, `Decisions`

Panels:

- AWS readiness gates
- Azure readiness gates
- Google Cloud readiness gates
- Adapter mapping status
- Marketplace Readiness Kit completeness
- Private-offer / private-plan readiness
- Conformance fixture coverage
- Open partner / GTM actions

## 3. Operating Cadence

Source tabs: `Calendars`, `Meetings`, `Decisions`, `ActionItems`

Panels:

- Meetings scheduled vs held
- Meetings with no captured output
- Decisions per meeting type
- Action items created and closed by week
- Attendance by group
- Missed cadence by workstream
- Next review dates

## 4. Automation Health

Source tabs: `Automations`, `Meetings`, `Groups`, `Artifacts`

Panels:

- Automation runs by status
- Failed automation runs
- Quarantined automation runs
- Calendar sync drift
- Group membership drift
- Artifact ledger drift
- Last successful replay per automation

## 5. Request / Labor Operations

Source tabs: `Requests`, `Responses`, `ActionItems`, `Risks`, `Artifacts`

Panels:

- Requests by type and status
- Responses by request and owner group
- Compensation fields present / missing
- Evaluation criteria present / missing
- Fit packet readiness
- Open contextual conversations
- Trust-event capture status

## 6. Migration Readiness

Source tabs: `MigrationReadiness`, `Artifacts`, `Automations`, `Dashboards`

Panels:

- Prototype object types by schema stability
- Automation readiness by replay capability
- Dashboards with regenerable data
- Manual workflows remaining
- Native SocioProphet object targets
- Migration blockers

## Regeneration rule

Every dashboard panel must declare:

- source tab
- metric definition
- refresh cadence
- owner group
- migration target

A panel that cannot be regenerated from ledger data is considered a presentation artifact, not an operational dashboard.
