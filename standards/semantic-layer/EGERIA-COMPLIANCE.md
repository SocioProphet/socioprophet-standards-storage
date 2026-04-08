# Compliance Concepts in Egeria

## Purpose

This document specifies how Egeria (Open Metadata and Governance) acts as the authoritative governance authority for FIPS compliance in the SocioProphet platform. Egeria is the single source of truth for asset metadata, compliance classifications, lineage, governance workflows, and audit trails.

---

## Egeria Asset Types

The following Egeria asset types are used to represent platform resources subject to FIPS governance.

| Asset Type | Description | Examples |
|---|---|---|
| `DataAsset` | Persistent data stores | PostgreSQL databases, data warehouses, object storage |
| `Process` (training) | ML training and data transformation pipelines | Feature pipelines, model training jobs |
| `Process` (CI/CD) | Continuous integration and deployment workflows | GitHub Actions workflows, deployment pipelines |
| `DeployedService` | Running service endpoints | REST APIs, gRPC services, prediction endpoints |
| `SoftwareComponent` | Reusable libraries and frameworks | Cryptographic libraries, authentication middleware |
| `CertificateAsset` | Cryptographic credentials | TLS certificates, signing keys, key pairs |
| `GovernancePolicy` | Access and usage policies | Data access policies, key rotation policies |

### Asset Registration Requirements

- Every asset that stores, processes, or transmits regulated data MUST be registered in Egeria before production deployment.
- `CertificateAsset` instances MUST include expiry date, issuing authority, and key algorithm as Egeria properties.
- `GovernancePolicy` instances MUST reference the NIST 800-53 control(s) they implement.

---

## Compliance Classification

Egeria classifications tag assets with their compliance posture and link governance artifacts to assets.

### Standard Classification Tags

| Tag | Meaning | Required Evidence |
|---|---|---|
| `FIPS-Compliant` | Asset satisfies all applicable FIPS controls | All required controls implemented; evidence attached |
| `NIST-800-53-Aligned` | Asset implements controls from the NIST 800-53 baseline | Control implementations linked and verified |
| `ZeroTrust` | Asset follows Zero Trust Architecture principles | NeverImplicitTrust, ContinuousVerification enforced |
| `AuditLogged` | Asset generates audit events for all regulated operations | Audit event stream active; AU-2 / AU-12 satisfied |

### Classification Requirements

- Governance classifications MUST be attached per asset, not per system — a single system may host multiple assets with different postures.
- Each classification MUST reference the `SecurityControl` instances it satisfies (linked via `implementation:evidence`).
- Evidence artifacts (log references, code paths, configuration keys) MUST be attached to the classification at the time of tagging.
- Classifications MUST be reviewed and re-attested on a schedule not exceeding 90 days.

---

## Lineage Tracking

Egeria records provenance and dependency chains for all registered assets.

### Data Lineage

- **Source → Transformation → Destination**: Every data flow between assets is recorded as a lineage edge.
- Transformation processes MUST carry references to the `SecurityControl` instances that govern the transformation (e.g., encryption controls for data in transit).
- Lineage records MUST be immutable once written; corrections are additive (new assertion supersedes old).

### Service Dependency

- **Service A calls Service B**: Dependency edges are registered so that compliance impact analysis can propagate.
- A `DeployedService` classified `FIPS-Compliant` MUST NOT depend on a `DeployedService` that is not classified `FIPS-Compliant` without an explicit exemption recorded in Egeria.

### Model Lineage

- **Training data → Model → Serving endpoint**: ML asset lineage tracks the data provenance of every deployed model.
- Lineage records MUST include the training dataset classification (e.g., `FIPS-Compliant`, `AuditLogged`) so that the model inherits or escalates data governance requirements.

### Impact Analysis

- Egeria MUST support impact analysis queries of the form: "if asset X changes or becomes non-compliant, which downstream assets are affected?"
- Impact analysis results MUST be surfaced in governance approval workflows before any change affecting a `FIPS-Compliant` asset is promoted to production.

---

## Governance Workflows in Egeria

Egeria orchestrates the following compliance-gated approval workflows.

### Data Governance

- **Question**: Who can access what data?
- **Gate**: Data access requests targeting `DataAsset` instances tagged `FIPS-Compliant` MUST be approved by the data owner and logged as a `GovernanceActionEvent`.
- **Enforcement**: Access denials and grants MUST be emitted as audit events consumable by the FIPS audit trail.

### Model Governance

- **Question**: Can this model be served?
- **Gate**: A model MUST not be deployed to serving unless its full lineage (training data → training process → model artifact) is recorded in Egeria and all upstream assets are `FIPS-Compliant`.
- **Enforcement**: CI/CD pipelines MUST query Egeria for lineage compliance status before creating a production `DeployedService` for a model.

### Deployment Approval

- **Question**: Can this system go to production?
- **Gate**: A `DeployedService` or `Process` MUST carry the `FIPS-Compliant` classification and all required `SecurityControl` evidence before a production deployment is approved.
- **Enforcement**: The deployment pipeline MUST block on a pending Egeria governance approval if the classification is absent or expired.

### Policy Review

- **Question**: Does this policy implement the required controls?
- **Gate**: `GovernancePolicy` assets MUST be reviewed whenever a referenced `SecurityControl` definition changes (e.g., a new NIST 800-53 control baseline is adopted).
- **Enforcement**: Egeria raises a governance action item for each policy that references the updated control; the item MUST be resolved before the new control version is considered active.

---

## Egeria Search and Discovery

Egeria MUST support the following compliance-oriented search queries.

| Query | Description |
|---|---|
| Find all assets tagged `FIPS-Compliant` | Enumerate the compliant asset population |
| Find all systems using `AES-256-GCM` | Verify approved algorithm adoption |
| Find assets without a recent audit log entry | Identify assets at risk of stale `AuditLogged` classification |
| Find systems violating data-retention policy | Surface assets whose lineage shows data held beyond policy limits |
| Find assets with expired `CertificateAsset` dependencies | Proactively detect certificate expiry risk |
| Find `DeployedService` assets with no evidence for a required control | Identify compliance gaps before they become findings |

All discovery queries MUST be expressible via Egeria's REST API and MUST be usable in CI/CD pipelines for automated compliance gates.

---

## Egeria Audit Trail

All metadata changes in Egeria are immutably logged to support audit and forensic investigation.

### What is Logged

- Every create, update, and delete of an asset, classification, or governance policy.
- Every governance workflow decision (approve, reject, defer, escalate).
- Every access-grant or access-denial event triggered by a `GovernancePolicy` evaluation.
- Every policy exception (exemption from a `FIPS-Compliant` requirement), including the approver and expiry date.

### Audit Record Fields

| Field | Description |
|---|---|
| `eventId` | Globally unique identifier for the audit event |
| `eventType` | One of: `MetadataChange`, `GovernanceDecision`, `AccessEvent`, `PolicyException` |
| `actor` | Identity (user or service account) that caused the event |
| `assetId` | Egeria identifier of the affected asset |
| `controlId` | NIST 800-53 control identifier (when applicable) |
| `timestamp` | ISO-8601 datetime (UTC) |
| `outcome` | `approved`, `rejected`, `deferred`, `exception-granted` |
| `rationale` | Free-text rationale (MUST be non-empty for exceptions) |
| `approvalChain` | Ordered list of approvers (identity + timestamp per approver) |

### Audit Trail Requirements

- Audit records MUST be written before the corresponding action takes effect (write-ahead).
- Audit records MUST be append-only; no record may be modified or deleted after creation.
- The audit trail MUST be queryable by asset, control, actor, time range, and outcome.
- Audit records MUST be retained for a minimum of three years to support FISMA audit cycles.

---

## Normative References

- NIST SP 800-53 Rev 5 — Security and Privacy Controls for Information Systems and Organizations
- FISMA 2014 — Federal Information Security Modernization Act
- Egeria Project — https://egeria-project.org/
- standards/semantic-layer/ARCHITECTURE.md — Ontology and reasoning rules
- docs/standards/050-security-oidc-policy.md — Platform security standard
