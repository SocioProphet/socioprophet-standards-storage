# NIST 800-53 Control Mappings

This document maps the 28 critical NIST SP 800-53 Rev. 5 controls to their implementation locations across the SocioProphet platform. Use this as the authoritative cross-reference between governance standards and code implementations.

## Control Mapping Format

Each entry follows the format:

```
Control ID: <NIST 800-53 control identifier>
Title: <control name>
Status: Implemented | Partial | Planned
Standard: <link to governing standards document>
Implementation: <repo/path where control is implemented>
Evidence: <artifact or test that demonstrates compliance>
```

---

## AC (Access Control)

### AC-2 — Account Management
**Status**: Implemented  
**Standard**: `docs/standards/050-security-oidc-policy.md`, `docs/standards/090-fips-nist-compliance.md`  
**Implementation**: `SocioProphet/sociosphere/auth/oidc.py`  
**Evidence**: OIDC provider integration test; service account lifecycle automation  
**Notes**: Accounts provisioned/deprovisioned via OIDC; quarterly access reviews required.

### AC-3 — Access Enforcement
**Status**: Implemented  
**Standard**: `docs/standards/050-security-oidc-policy.md`, `docs/standards/090-fips-nist-compliance.md`  
**Implementation**: `SocioProphet/sociosphere/auth/rbac-policy.yaml`  
**Evidence**: OPA/Kyverno policy evaluation logs; deny-by-default rule verification  
**Notes**: RBAC enforced via Kubernetes RBAC + Open Policy Agent; least-privilege per workload.

### AC-17 — Remote Access
**Status**: Implemented  
**Standard**: `docs/standards/090-fips-nist-compliance.md`, `docs/standards/095-orchestration-fips-compliance.md`  
**Implementation**: `SocioProphet/sociosphere/k8s/network-policies/`  
**Evidence**: Network policy audit; VPN/zero-trust gateway configuration  
**Notes**: All remote access must use zero-trust gateway with MFA + mTLS.

---

## AU (Audit and Accountability)

### AU-2 — Event Logging
**Status**: Implemented  
**Standard**: `docs/standards/090-fips-nist-compliance.md`, `docs/standards/093-forensic-audit-nist-800-88.md`  
**Implementation**: `SocioProphet/sociosphere/observability/audit-pipeline.yaml`  
**Evidence**: Audit event schema validation; log pipeline integration test  
**Notes**: All authentication, authorization, and data access events logged.

### AU-3 — Content of Audit Records
**Status**: Implemented  
**Standard**: `docs/standards/093-forensic-audit-nist-800-88.md`  
**Implementation**: `SocioProphet/sociosphere/observability/audit-schema.json`  
**Evidence**: Audit event schema includes timestamp, actor, action, resource, result, IP  
**Notes**: RFC 3161 timestamps; ECDSA-P256 signatures per log entry.

### AU-9 — Protection of Audit Information
**Status**: Implemented  
**Standard**: `docs/standards/090-fips-nist-compliance.md`, `docs/standards/093-forensic-audit-nist-800-88.md`  
**Implementation**: `SocioProphet/sociosphere/observability/log-immutability.yaml`  
**Evidence**: WORM storage configuration; log integrity verification job  
**Notes**: Audit logs are append-only; signed and stored in tamper-evident store.

### AU-12 — Audit Record Generation
**Status**: Implemented  
**Standard**: `docs/standards/090-fips-nist-compliance.md`, `docs/standards/094-data-layer-fips-compliance.md`  
**Implementation**: `SocioProphet/sociosphere/observability/audit-pipeline.yaml`  
**Evidence**: Per-system audit log verification; centralized log store check  
**Notes**: All 6 data stores and Kubernetes API server emit audit records.

---

## CA (Assessment, Authorization, and Monitoring)

### CA-7 — Continuous Monitoring
**Status**: Planned  
**Standard**: `docs/standards/090-fips-nist-compliance.md`  
**Implementation**: `SocioProphet/sociosphere/monitoring/compliance-dashboard.yaml`  
**Evidence**: Prometheus alert rules; daily compliance scan job  
**Notes**: Daily automated scans; weekly trend analysis; quarterly full audit.

### CA-9 — Internal System Connections
**Status**: Partial  
**Standard**: `docs/standards/092-zero-trust-nist-800-207.md`, `docs/standards/095-orchestration-fips-compliance.md`  
**Implementation**: `SocioProphet/sociosphere/mesh/authorization-policies.yaml`  
**Evidence**: Service mesh topology map; default-deny AuthorizationPolicy verification  
**Notes**: All inter-service connections documented and authorized via service mesh.

---

## CM (Configuration Management)

### CM-2 — Baseline Configuration
**Status**: Implemented  
**Standard**: `docs/standards/095-orchestration-fips-compliance.md`  
**Implementation**: `SocioProphet/sociosphere/k8s/baseline/`  
**Evidence**: GitOps baseline repository; configuration drift detection alerts  
**Notes**: Infrastructure as code; all configuration managed via GitOps (Flux/ArgoCD).

### CM-6 — Configuration Settings
**Status**: Implemented  
**Standard**: `docs/standards/090-fips-nist-compliance.md`  
**Implementation**: `SocioProphet/sociosphere/k8s/pod-security/pss-policy.yaml`  
**Evidence**: Pod Security Standards enforcement policy; Kyverno admission controller  
**Notes**: CIS Kubernetes Benchmark Level 2 applied.

---

## IA (Identification and Authentication)

### IA-2 — Identification and Authentication (Organizational Users)
**Status**: Implemented  
**Standard**: `docs/standards/050-security-oidc-policy.md`, `docs/standards/090-fips-nist-compliance.md`  
**Implementation**: `SocioProphet/sociosphere/auth/oidc.py`  
**Evidence**: OIDC token validation test; MFA enforcement policy  
**Notes**: All users authenticate via OIDC with MFA. Service accounts use mTLS.

### IA-5 — Authenticator Management
**Status**: Implemented  
**Standard**: `docs/standards/090-fips-nist-compliance.md`  
**Implementation**: `SocioProphet/sociosphere/vault/vault-config.hcl`  
**Evidence**: Secret rotation job; Vault audit log showing rotation events  
**Notes**: Automated 90-day rotation for symmetric keys; 1-year for asymmetric.

### IA-8 — Identification and Authentication (Non-Organizational Users)
**Status**: Partial  
**Standard**: `docs/standards/050-security-oidc-policy.md`  
**Implementation**: `SocioProphet/sociosphere/auth/external-idp.yaml`  
**Evidence**: External OIDC provider configuration; JWT validation middleware  
**Notes**: External users authenticated via federated OIDC with role mapping.

---

## IR (Incident Response)

### IR-4 — Incident Handling
**Status**: Planned  
**Standard**: `docs/standards/090-fips-nist-compliance.md`  
**Implementation**: `SocioProphet/sociosphere/runbooks/incident-response.md`  
**Evidence**: Incident response drill results; runbook execution tests  
**Notes**: Runbook includes automated workload isolation for compliance violations.

### IR-6 — Incident Reporting
**Status**: Planned  
**Standard**: `SECURITY.md`  
**Implementation**: `SocioProphet/sociosphere/runbooks/incident-reporting.md`  
**Evidence**: Incident report template; escalation path documentation  
**Notes**: Integrates with PagerDuty/OpsGenie for on-call escalation.

---

## SC (System and Communications Protection)

### SC-7 — Boundary Protection
**Status**: Implemented  
**Standard**: `docs/standards/092-zero-trust-nist-800-207.md`, `docs/standards/095-orchestration-fips-compliance.md`  
**Implementation**: `SocioProphet/sociosphere/k8s/network-policies/default-deny.yaml`  
**Evidence**: Network policy audit; ingress controller configuration  
**Notes**: Default-deny network policies at namespace level; explicit allow per workload pair.

### SC-8 — Transmission Confidentiality and Integrity
**Status**: Implemented  
**Standard**: `docs/standards/090-fips-nist-compliance.md`, `docs/standards/094-data-layer-fips-compliance.md`  
**Implementation**: `SocioProphet/sociosphere/mesh/mtls-policy.yaml`  
**Evidence**: TLS 1.3 enforced; cipher suite audit results  
**Notes**: All data in transit protected by TLS 1.3 minimum; mTLS for inter-service.

### SC-12 — Cryptographic Key Establishment and Management
**Status**: Implemented  
**Standard**: `docs/standards/090-fips-nist-compliance.md`  
**Implementation**: `SocioProphet/sociosphere/vault/vault-config.hcl`  
**Evidence**: Vault key lifecycle audit log; rotation automation test  
**Notes**: Vault HA cluster manages all keys; 90-day rotation enforced.

### SC-13 — Cryptographic Protection
**Status**: Implemented  
**Standard**: `docs/standards/090-fips-nist-compliance.md`  
**Implementation**: `SocioProphet/sociosphere/crypto/`  
**Evidence**: FIPS algorithm whitelist enforcement; CI check for non-FIPS imports  
**Notes**: Only AES-256-GCM, ECDSA-P256, SHA-256+ permitted in production.

### SC-28 — Protection of Information at Rest
**Status**: Implemented  
**Standard**: `docs/standards/090-fips-nist-compliance.md`, `docs/standards/094-data-layer-fips-compliance.md`  
**Implementation**: See `094-data-layer-fips-compliance.md` for per-store configuration  
**Evidence**: Encryption configuration audit; test decryption verification  
**Notes**: AES-256-GCM at rest for all 6 data stores.

---

## SI (System and Information Integrity)

### SI-2 — Flaw Remediation
**Status**: Implemented  
**Standard**: `docs/standards/090-fips-nist-compliance.md`  
**Implementation**: `SocioProphet/sociosphere/.github/workflows/vuln-scan.yaml`  
**Evidence**: Trivy/Grype scan reports; remediation SLA tracker  
**Notes**: Critical: 30 days; High: 90 days; automated scanning in CI/CD.

### SI-3 — Malicious Code Protection
**Status**: Partial  
**Standard**: `docs/standards/090-fips-nist-compliance.md`  
**Implementation**: `SocioProphet/sociosphere/.github/workflows/sbom.yaml`  
**Evidence**: SBOM generation reports; dependency scanning results  
**Notes**: SBOM generated for all components; dependency scanning on each merge.

### SI-4 — System Monitoring
**Status**: Implemented  
**Standard**: `docs/standards/090-fips-nist-compliance.md`  
**Implementation**: `SocioProphet/sociosphere/monitoring/prometheus-rules.yaml`  
**Evidence**: Prometheus alert rules; anomaly detection baseline  
**Notes**: Prometheus + Grafana for metrics; Loki for logs; Jaeger for traces.

### SI-7 — Software, Firmware, and Information Integrity
**Status**: Implemented  
**Standard**: `docs/standards/090-fips-nist-compliance.md`, `docs/standards/095-orchestration-fips-compliance.md`  
**Implementation**: `SocioProphet/sociosphere/k8s/admission/image-signing.yaml`  
**Evidence**: Cosign/Sigstore container signing; admission webhook verification  
**Notes**: All container images must be signed; unsigned images blocked at admission.

### SI-10 — Information Input Validation
**Status**: Partial  
**Standard**: `docs/standards/030-service-interfaces-tritrpc.md`  
**Implementation**: `SocioProphet/sociosphere/api/input-validation.py`  
**Evidence**: Input validation middleware tests; fuzz testing results  
**Notes**: All API endpoints validate input against schemas (Avro/JSON-LD).

---

## Control Implementation Status Summary

| Family | Implemented | Partial | Planned | Total |
|--------|-------------|---------|---------|-------|
| AC     | 2           | 0       | 1       | 3     |
| AU     | 3           | 0       | 1       | 4     |
| CA     | 0           | 1       | 1       | 2     |
| CM     | 2           | 0       | 0       | 2     |
| IA     | 2           | 1       | 0       | 3     |
| IR     | 0           | 0       | 2       | 2     |
| SC     | 4           | 0       | 0       | 4     |
| SI     | 2           | 2       | 0       | 4     |
| **Total** | **15**   | **4**   | **5**   | **28** |

## Related Standards

- `090-fips-nist-compliance.md` — Cryptographic requirements (FIPS 140-2/140-3)
- `050-security-oidc-policy.md` — Identity and authorization
- `092-zero-trust-nist-800-207.md` — Zero-trust architecture
- `093-forensic-audit-nist-800-88.md` — Forensic audit trails
- `094-data-layer-fips-compliance.md` — Data layer controls
- `095-orchestration-fips-compliance.md` — Orchestration layer controls
