# Orchestration Layer Standards Index

## Overview

This index governs FIPS-compliant deployment of workloads across Kubernetes, container runtimes, federation tooling, local development clusters, service meshes, and secrets management systems within the SocioProphet governance framework.

Orchestration components sit between cryptographic primitives and application-layer logic. All systems catalogued here MUST enforce FIPS-approved algorithms, immutable audit trails, and zero-trust access control as defined in the cross-referenced cryptographic standards.

---

## System Categorisation

| Category | Systems | Standard |
|---|---|---|
| Cluster Management | Kubernetes | [KUBERNETES-SECURITY.md](KUBERNETES-SECURITY.md) |
| Federation | kubefed | [KUBEFED-STANDARDS.md](KUBEFED-STANDARDS.md) |
| Local Development | KinD, minikube | [KIND-STANDARDS.md](KIND-STANDARDS.md), [MINIKUBE-STANDARDS.md](MINIKUBE-STANDARDS.md) |
| Container Runtime | Docker, containerd | [CONTAINER-RUNTIME-SECURITY.md](CONTAINER-RUNTIME-SECURITY.md) |
| Service Mesh | Istio, Linkerd | [SERVICE-MESH-STANDARDS.md](SERVICE-MESH-STANDARDS.md) |
| Secrets Management | HashiCorp Vault | [SECRETS-MANAGEMENT.md](SECRETS-MANAGEMENT.md) |
| Audit & Observability | Prometheus, Loki, Jaeger | [AUDIT-OBSERVABILITY.md](AUDIT-OBSERVABILITY.md) |

---

## Network Security Requirements

| Component | Transport | Encryption | Certificate Authority |
|---|---|---|---|
| Kubernetes API server | TLS 1.3 minimum | AES-256-GCM | Internal PKI or external CA |
| etcd | TLS 1.3 minimum | AES-256-GCM at rest | Internal PKI |
| kubefed control plane | mTLS | ECDSA-P256 or RSA-4096 | Shared CA across clusters |
| Service mesh (Istio/Linkerd) | mTLS mandatory | ECDSA-P256 minimum | cert-manager automated rotation |
| Vault agents | mTLS | AES-256-GCM | Vault PKI secrets engine |
| Container registry | TLS 1.3 minimum | AES-256-GCM | Public or internal CA |
| KinD/minikube (local) | TLS recommended | N/A (test only) | Self-signed acceptable |

All production network paths MUST use TLS 1.3 or later. TLS 1.2 is permitted only when a legacy peer requires it and MUST be documented as a known deviation with a remediation timeline.

---

## RBAC and Access Control Frameworks

### Kubernetes RBAC
- All workloads MUST have a dedicated `ServiceAccount`; the `default` service account MUST NOT be used.
- `ClusterAdmin` binding MUST NOT be granted to application workloads.
- Role definitions MUST follow the principle of least privilege.
- RBAC policies MUST be reviewed quarterly.

### Federation RBAC (kubefed)
- Federated `ClusterRole` and `ClusterRoleBinding` resources MUST mirror per-cluster RBAC policies.
- Cross-cluster service accounts MUST have scoped permissions per federated namespace.

### Vault RBAC
- Vault policies MUST scope secret read/write to the consuming workload's path only.
- Human-operator policies MUST be separate from machine/service-account policies.
- Vault policy review MUST occur quarterly and after any personnel change.

---

## Secrets Management Integration

All systems MUST integrate with HashiCorp Vault as the authoritative secrets provider. Specific requirements:

- Secrets MUST NOT be stored in Kubernetes `Secret` objects backed only by etcd without envelope encryption.
- Vault JWT/OIDC auth MUST be used for workload identity.
- Secret rotation period MUST NOT exceed 30 days for long-lived credentials.
- Emergency rotation procedures MUST be documented and tested annually.

See [SECRETS-MANAGEMENT.md](SECRETS-MANAGEMENT.md) for full specification.

---

## Audit Logging and Observability

- Kubernetes API audit logging MUST be enabled and directed to external, immutable storage.
- Audit events MUST capture: principal identity, source IP, resource kind/name/namespace, verb, HTTP status, timestamp.
- Retention MUST be: 90 days hot storage, 7 years archived.
- Audit logs MUST be cryptographically signed (ECDSA-P256) with RFC 3161 timestamps.
- Observability stack (Prometheus, Loki, Jaeger, Grafana, AlertManager) MUST be deployed for all production clusters.

See [AUDIT-OBSERVABILITY.md](AUDIT-OBSERVABILITY.md) for full specification.

---

## Integration Checklist

A per-system compliance checklist is provided in [INTEGRATION-CHECKLIST.md](INTEGRATION-CHECKLIST.md). Each checklist item maps to one or more NIST 800-53 controls listed below.

---

## NIST 800-53 Control Alignment

| Control | Title | Applicable Systems |
|---|---|---|
| AC-2 | Account Management | Kubernetes SA lifecycle, Vault identity |
| AC-3 | Access Enforcement | RBAC, network policies, pod security |
| AC-5 | Separation of Duties | Role segregation, no cluster-admin for apps |
| AC-17 | Remote Access | mTLS, TLS 1.3 encrypted communications |
| AU-2 | Audit Events | Kubernetes API audit, container events |
| AU-12 | Audit Generation | Immutable external audit logs |
| CA-7 | Continuous Monitoring | Observability, anomaly detection |
| IA-2 | Identification and Authentication | OIDC, mTLS, certificates |
| IA-4 | Identifier Management | Service account lifecycle |
| SC-7 | Boundary Protection | Network policies, micro-segmentation |
| SC-8 | Transmission Confidentiality | mTLS, TLS 1.3 |
| SC-12 | Cryptographic Key Management | Certificate automation, secret rotation |
| SI-4 | Information System Monitoring | Anomaly detection, forensic readiness |
| SI-7 | Software and Information Integrity | Image signing, SBOM |

---

## Orchestration System Integration Status

| System | OIDC | mTLS | Secrets | Audit | RBAC | Target |
|---|---|---|---|---|---|---|
| Kubernetes | ✅ Required | ✅ Required | ✅ Vault | ✅ External | ✅ Required | Q3 2026 |
| kubefed | ✅ Required | ✅ Required | ✅ Vault | ✅ Centralized | ✅ Federated | Q3 2026 |
| KinD | ⚠️ Optional | ⚠️ Optional | ❌ Test only | ✅ Local | ✅ Required | Q3 2026 |
| minikube | ⚠️ Optional | ⚠️ Optional | ❌ Test only | ⚠️ Optional | ✅ Required | Q3 2026 |
| containerd | ✅ Via K8s | ✅ Via K8s | ✅ Via K8s | ✅ K8s audit | N/A | Q3 2026 |
| Istio | N/A | ✅ Required | ✅ Via K8s | ✅ Via mesh | N/A | Q3 2026 |
| Linkerd | N/A | ✅ Required | ✅ Via K8s | ✅ Via mesh | N/A | Q3 2026 |
| Vault | ✅ Required | ✅ Required | N/A | ✅ Required | ✅ Required | Q3 2026 |

---

## Cross-References to Cryptographic Standards

- FIPS 140-2/140-3 Module Validation: https://csrc.nist.gov/projects/cryptographic-module-validation-program/
- NIST SP 800-53 Rev. 5: https://csrc.nist.gov/publications/detail/sp/800-53/rev-5
- NIST SP 800-207 (Zero Trust): https://csrc.nist.gov/publications/detail/sp/800-207
- NIST SP 800-88 (Audit/Forensics): https://csrc.nist.gov/publications/detail/sp/800-88
- RFC 3161 (Time-Stamp Protocol): https://tools.ietf.org/html/rfc3161
- Kubernetes Security: https://kubernetes.io/docs/concepts/security/
- HashiCorp Vault: https://www.vaultproject.io/docs
