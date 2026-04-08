# Orchestration Integration Checklist

This checklist MUST be completed for each system before it is considered compliant with the SocioProphet orchestration governance framework. Each item maps to one or more NIST 800-53 controls. Items marked with a control reference indicate the primary NIST control satisfied.

---

## Kubernetes Cluster

| # | Item | NIST Control | Status |
|---|---|---|---|
| K-01 | OIDC authentication enabled (`--oidc-issuer-url` set on API server) | IA-2 | [ ] |
| K-02 | RBAC enabled (not disabled via `--authorization-mode` override) | AC-3 | [ ] |
| K-03 | Pod security standards enforced (`pod-security.kubernetes.io/enforce: restricted` on all production namespaces) | AC-3 | [ ] |
| K-04 | Default-deny `NetworkPolicy` applied to every namespace | SC-7 | [ ] |
| K-05 | etcd encryption at rest configured (AES-256-GCM via `--encryption-provider-config`) | SC-28 | [ ] |
| K-06 | External secrets provider (Vault) integrated via JWT auth method | SC-12 | [ ] |
| K-07 | Kubernetes API audit logging enabled and forwarded to external immutable storage | AU-2, AU-12 | [ ] |
| K-08 | Image vulnerability scanning enabled at admission (ImagePolicyWebhook or equivalent) | SI-7 | [ ] |
| K-09 | Image signing enforced at admission (cosign or notary, ECDSA-P256) | SI-7 | [ ] |
| K-10 | Dedicated `ServiceAccount` per workload; `default` SA has `automountServiceAccountToken: false` | AC-2 | [ ] |
| K-11 | Resource limits (`cpu`, `memory`) declared for every container | SC-6 | [ ] |
| K-12 | Quarterly RBAC review scheduled and documented | AC-2 | [ ] |

---

## kubefed Federation

| # | Item | NIST Control | Status |
|---|---|---|---|
| F-01 | Control plane OIDC configured on all member clusters | IA-2 | [ ] |
| F-02 | mTLS enforced between federation control plane and member clusters | SC-8 | [ ] |
| F-03 | Secret synchronisation implemented via Vault (not raw kubefed secret propagation) | SC-12 | [ ] |
| F-04 | Centralised audit logging collecting events from all member clusters | AU-12 | [ ] |
| F-05 | Federated RBAC policies deployed (`FederatedClusterRole` / `FederatedClusterRoleBinding`) | AC-3 | [ ] |
| F-06 | Cross-cluster service discovery configured (service mesh or ExternalDNS) | SC-7 | [ ] |
| F-07 | Quarterly DR testing scheduled; test results documented | CP-4 | [ ] |
| F-08 | Failover procedures documented in operations runbook | CP-2 | [ ] |

---

## KinD Clusters (CI)

| # | Item | NIST Control | Status |
|---|---|---|---|
| C-01 | API audit logging enabled for CI clusters (log forwarded as CI artefact) | AU-2 | [ ] |
| C-02 | Pod security standards enforced (`restricted` profile on test namespaces) | AC-3 | [ ] |
| C-03 | Network policies enabled (CNI supporting `NetworkPolicy` deployed) | SC-7 | [ ] |
| C-04 | Test data isolation enforced (unique namespace per test suite, cross-suite `NetworkPolicy` deny) | SC-7 | [ ] |
| C-05 | Automatic cluster cleanup after each CI job (unconditional `kind delete cluster`) | CM-7 | [ ] |
| C-06 | No real/production secrets used in KinD clusters (synthetic test credentials only) | SC-12 | [ ] |

---

## minikube (Developer Laptops)

| # | Item | NIST Control | Status |
|---|---|---|---|
| M-01 | Reference minikube configuration provided and applied via setup script | CM-6 | [ ] |
| M-02 | RBAC enabled (not disabled via `--extra-config` override) | AC-3 | [ ] |
| M-03 | CNI with `NetworkPolicy` support deployed (`--cni=calico`) | SC-7 | [ ] |
| M-04 | Pod security admission enabled (`PodSecurity` admission plugin active) | AC-3 | [ ] |
| M-05 | Pre-commit hooks in place to detect hardcoded credentials | SC-12 | [ ] |
| M-06 | Local Vault dev server used for secrets (no hardcoded env vars) | SC-12 | [ ] |

---

## Container Runtime (Docker / containerd)

| # | Item | NIST Control | Status |
|---|---|---|---|
| R-01 | TLS 1.3 enabled for Docker daemon API; mTLS enforced for remote API access | SC-8 | [ ] |
| R-02 | Image signing enforcement enabled at runtime (`cosign`, ECDSA-P256) | SI-7 | [ ] |
| R-03 | `RuntimeDefault` seccomp profile applied to all containers | AC-3 | [ ] |
| R-04 | AppArmor or SELinux confinement applied to all containers | AC-3 | [ ] |
| R-05 | No privileged containers allowed (`securityContext.privileged: false` enforced by admission policy) | AC-3 | [ ] |
| R-06 | Resource limits (CPU, memory) enforced for all containers | SC-6 | [ ] |
| R-07 | Linux capabilities dropped by default (`capabilities.drop: ["ALL"]`) | AC-3 | [ ] |
| R-08 | Base images pinned to specific digest; automated update proposals enabled | SI-7 | [ ] |
| R-09 | SBOM generated and signed for every published image | SI-7 | [ ] |
| R-10 | Build provenance attestation (SLSA) generated for every image | SI-7 | [ ] |

---

## Service Mesh (Istio / Linkerd)

| # | Item | NIST Control | Status |
|---|---|---|---|
| S-01 | mTLS `STRICT` mode enabled cluster-wide (`PeerAuthentication` or equivalent) | SC-8 | [ ] |
| S-02 | Default-deny `AuthorizationPolicy` applied to all production namespaces | AC-3 | [ ] |
| S-03 | Certificate rotation automated (cert-manager, maximum 30-day lifetime) | SC-12 | [ ] |
| S-04 | Observability stack deployed (Prometheus, Loki, Jaeger, Grafana) | CA-7 | [ ] |
| S-05 | Distributed tracing enabled and forwarding to Jaeger | AU-2 | [ ] |
| S-06 | Anomaly detection alerts configured in AlertManager | CA-7, SI-4 | [ ] |
| S-07 | Service-to-service access matrix document maintained and reviewed | AC-3 | [ ] |
| S-08 | Sidecar resource limits defined in mesh control-plane configuration | SC-6 | [ ] |

---

## Vault Integration

| # | Item | NIST Control | Status |
|---|---|---|---|
| V-01 | HA Vault cluster deployed (minimum 3 nodes across 3 availability zones) | CP-9 | [ ] |
| V-02 | Kubernetes JWT/OIDC auth method configured (one mount per cluster) | IA-2 | [ ] |
| V-03 | Secret rotation automated (maximum 30-day cycle for long-lived secrets) | SC-12 | [ ] |
| V-04 | Vault audit logging enabled with `fail_on_error = true`; forwarded to external immutable store | AU-12 | [ ] |
| V-05 | Encrypted Vault Raft snapshots taken every 6 hours and stored off-site | CP-9 | [ ] |
| V-06 | Quarterly DR recovery testing scheduled and results documented | CP-4 | [ ] |
| V-07 | Vault policies reviewed quarterly; decommissioned workload policies revoked | AC-2 | [ ] |
| V-08 | Root token revoked after initial setup; break-glass procedures documented | AC-2 | [ ] |

---

## Compliance Sign-Off

Once all items for a system are checked, a compliance owner MUST record the following:

```
System: <system name and version>
Cluster / Environment: <cluster name, region, environment>
Review Date: <YYYY-MM-DD>
Reviewer: <name and role>
Outstanding Exceptions: <list any unchecked items with documented justification>
Next Review Due: <YYYY-MM-DD, maximum 90 days>
```

Sign-off records MUST be stored in the operations repository as immutable, version-controlled artefacts.

---

## References

- [INDEX.md](INDEX.md) — Orchestration Layer Standards Index
- [KUBERNETES-SECURITY.md](KUBERNETES-SECURITY.md) — Kubernetes Security Standards
- [KUBEFED-STANDARDS.md](KUBEFED-STANDARDS.md) — Kubernetes Federation Standards
- [KIND-STANDARDS.md](KIND-STANDARDS.md) — KinD Standards
- [MINIKUBE-STANDARDS.md](MINIKUBE-STANDARDS.md) — Minikube Standards
- [CONTAINER-RUNTIME-SECURITY.md](CONTAINER-RUNTIME-SECURITY.md) — Container Runtime Security Standards
- [SERVICE-MESH-STANDARDS.md](SERVICE-MESH-STANDARDS.md) — Service Mesh Standards
- [SECRETS-MANAGEMENT.md](SECRETS-MANAGEMENT.md) — Secrets Management Integration
- [AUDIT-OBSERVABILITY.md](AUDIT-OBSERVABILITY.md) — Orchestration Audit and Observability
- NIST SP 800-53 Rev. 5: https://csrc.nist.gov/publications/detail/sp/800-53/rev-5
