# Marketplace Readiness Kit Gates v1

Status: Draft-for-execution
Decision record: EDR-CVSP-2026-06-05-002
Owning issue: #91

These gates are blocking. A cloud marketplace listing or private offer is not ready until all applicable gates are satisfied.

## MRK-A — Legal and commercial

- Terms of service drafted and reviewed.
- Acceptable use policy drafted and reviewed.
- Privacy posture documented.
- Data processing posture documented.
- Support policy drafted.
- Cancellation and downgrade behavior documented.
- Private-offer / private-plan template drafted.
- SLA posture documented.

## MRK-B — Architecture and security

- Architecture overview completed.
- Data-flow narrative completed.
- Tenant-isolation model completed.
- Identity and access model completed.
- Audit logging posture completed.
- Vulnerability management narrative completed.
- Incident response and escalation path completed.
- Model-routing and data-boundary narrative completed.
- Entitlement reconciliation behavior documented.

## MRK-C — Marketplace listing

- AWS listing copy drafted.
- Azure listing copy drafted.
- Google Cloud listing copy drafted.
- Screenshots or diagrams prepared.
- Demo script prepared.
- Quickstart prepared.
- FAQ prepared.
- Onboarding URL behavior specified.
- Cloud-specific procurement narrative documented.

## MRK-D — Field and co-sell

- ICP defined.
- Personas defined.
- Discovery script drafted.
- Objection-handling guide drafted.
- Reference architecture drafted.
- Vertical one-pagers drafted.
- Procurement narrative drafted.
- Launch-council owner assigned.

## Blocking severity rules

- Paid-but-not-entitled is severity 1.
- Entitled-but-not-paid is severity 1 after grace policy expires.
- Unknown marketplace state must deny production access.
- Replay or idempotency failure blocks launch.
- Missing canonical mapping blocks launch.
- Missing reconciliation path blocks launch.
