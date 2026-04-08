# Orchestration Layer FIPS Compliance Integration Checklist

| Metadata | Details |
| --- | --- |
| Version | 1.0 |
| Status | Active |
| Authority | SocioProphet Governance Committee |
| Last Reviewed | 2026-04-05 |
| NIST References | NIST 800-53 Rev 5, NIST 800-190, NIST 800-207 |

## Overview

This checklist provides per-system compliance procedures for the SocioProphet orchestration layer. Each system must pass all applicable checks before promotion to production. Checks are organized by compliance domain and linked to NIST 800-53 controls.

**Legend**: ✅ Implemented | ⚠️ In Progress | ❌ Not Started | N/A Not Applicable

---

## Kubernetes Cluster Compliance

### Authentication & Authorization (IA-2, AC-3)

| # | Check Item | Control | Priority | Status |
|---|---|---|---|---|
| K-001 | kube-apiserver `--oidc-issuer-url` configured | IA-2 | P0 | ⚠️ |
| K-002 | kube-apiserver `--oidc-client-id` set | IA-2 | P0 | ⚠️ |
| K-003 | kube-apiserver `--oidc-username-claim` set to email or sub | IA-2 | P0 | ⚠️ |
| K-004 | kube-apiserver `--oidc-groups-claim` configured | AC-3 | P0 | ⚠️ |
| K-005 | No anonymous authentication (`--anonymous-auth=false`) | IA-2 | P0 | ❌ |
| K-006 | RBAC enabled (`--authorization-mode=RBAC`) | AC-3 | P0 | ✅ |
| K-007 | No ClusterRoleBinding to system:masters beyond break-glass | AC-5 | P0 | ⚠️ |
| K-008 | All service accounts use projected tokens (not legacy) | IA-5 | P1 | ❌ |
| K-009 | Automount service account token disabled where not needed | AC-3 | P1 | ❌ |

### Encryption & Secrets (SC-12, SC-13)

| # | Check Item | Control | Priority | Status |
|---|---|---|---|---|
| K-010 | etcd encryption-at-rest enabled (aesgcm or secretbox provider) | SC-28 | P0 | ❌ |
| K-011 | etcd TLS mutual authentication configured | SC-8 | P0 | ⚠️ |
| K-012 | kube-apiserver to etcd TLS certificates valid and rotated | SC-12 | P0 | ⚠️ |
| K-013 | Secrets not stored in plaintext ConfigMaps | SC-28 | P0 | ❌ |
| K-014 | External Secrets Operator or Vault Agent Injector deployed | SC-12 | P1 | ❌ |
| K-015 | No hardcoded secrets in container images | SC-28 | P0 | ✅ |

### Pod Security (SI-7, CM-6)

| # | Check Item | Control | Priority | Status |
|---|---|---|---|---|
| K-016 | Pod Security Standards enforced: Restricted profile on prod namespaces | SI-7 | P0 | ❌ |
| K-017 | No privileged containers in production | SI-7 | P0 | ✅ |
| K-018 | No hostPID / hostNetwork / hostIPC in production pods | SC-39 | P0 | ✅ |
| K-019 | Containers run as non-root user | CM-6 | P1 | ⚠️ |
| K-020 | Read-only root filesystem enforced where possible | CM-6 | P1 | ❌ |
| K-021 | Seccomp profile: RuntimeDefault or custom | SI-7 | P1 | ❌ |
| K-022 | AppArmor/SELinux profiles applied | SI-7 | P2 | ❌ |

### Network Security (SC-7, AC-4)

| # | Check Item | Control | Priority | Status |
|---|---|---|---|---|
| K-023 | Default-deny NetworkPolicy applied in all namespaces | SC-7 | P0 | ❌ |
| K-024 | Ingress rules limited to required source namespaces/CIDRs | AC-4 | P0 | ❌ |
| K-025 | Egress rules restrict outbound to known endpoints | SC-7 | P1 | ❌ |
| K-026 | Node-level firewall rules configured | SC-7 | P1 | ❌ |

### Audit Logging (AU-2, AU-12)

| # | Check Item | Control | Priority | Status |
|---|---|---|---|---|
| K-027 | kube-apiserver audit policy configured (RequestResponse for secrets/pods) | AU-12 | P0 | ❌ |
| K-028 | Audit logs forwarded to centralized system (Fluentd/OpenSearch) | AU-2 | P0 | ❌ |
| K-029 | Audit log retention: 7 years minimum | AU-11 | P0 | ❌ |
| K-030 | Audit log integrity protection (WORM or signed) | AU-9 | P1 | ❌ |

### Image Security (SI-3, CM-7)

| # | Check Item | Control | Priority | Status |
|---|---|---|---|---|
| K-031 | Image signing enforced (Cosign/Sigstore) | SI-7 | P0 | ❌ |
| K-032 | Admission webhook validates image signatures | CM-7 | P0 | ❌ |
| K-033 | Container image vulnerability scanning in CI pipeline | SI-3 | P0 | ⚠️ |
| K-034 | No critical/high CVEs in production images | SI-3 | P0 | ⚠️ |
| K-035 | Base images from approved registry only | CM-7 | P1 | ❌ |

---

## KubeFed (Multi-Cluster Federation) Compliance

### Federation Security (SC-8, IA-3)

| # | Check Item | Control | Priority | Status |
|---|---|---|---|---|
| F-001 | KubeFed control plane using TLS 1.3+ for API | SC-8 | P0 | ❌ |
| F-002 | mTLS enabled between federation host and member clusters | SC-8 | P0 | ❌ |
| F-003 | Member cluster identities validated via certificates | IA-3 | P0 | ❌ |
| F-004 | Federation RBAC policies aligned with per-cluster RBAC | AC-3 | P1 | ❌ |
| F-005 | Secret synchronization uses encrypted channels only | SC-8 | P0 | ❌ |
| F-006 | Cross-cluster audit events centrally aggregated | AU-2 | P1 | ❌ |
| F-007 | Disaster recovery failover tested quarterly | CP-4 | P1 | ❌ |

---

## KinD (CI/CD Environment) Compliance

### CI Security (SI-2, AU-2)

| # | Check Item | Control | Priority | Status |
|---|---|---|---|---|
| KI-001 | KinD uses FIPS-compatible base images | SC-13 | P0 | ❌ |
| KI-002 | Ephemeral clusters destroyed after CI job | CM-7 | P0 | ❌ |
| KI-003 | No production secrets injected into KinD clusters | SC-28 | P0 | ✅ |
| KI-004 | CI audit logs captured per run | AU-12 | P1 | ❌ |
| KI-005 | RBAC applied to KinD test namespaces | AC-3 | P2 | ❌ |
| KI-006 | Audit policy configured (minimal profile) in KinD | AU-2 | P2 | ❌ |
| KI-007 | GitHub Actions workflow uses pinned action versions | SI-7 | P0 | ⚠️ |

---

## minikube (Developer Laptops) Compliance

### Developer Environment Security (AT-2, CM-6)

| # | Check Item | Control | Priority | Status |
|---|---|---|---|---|
| M-001 | minikube profile isolated from production namespaces | SC-7 | P0 | ✅ |
| M-002 | No production secrets on developer machines | SC-28 | P0 | ✅ |
| M-003 | Developer machines covered by MDM/endpoint management | CM-6 | P1 | ❌ |
| M-004 | Local OIDC provider (Dex or similar) for dev auth | IA-2 | P2 | ❌ |
| M-005 | Security policy documentation provided to developers | AT-2 | P0 | ⚠️ |
| M-006 | Dev environment scanning runs before commit | SI-3 | P1 | ❌ |

---

## Istio / Linkerd Service Mesh Compliance

### mTLS & Authentication (SC-8, IA-3)

| # | Check Item | Control | Priority | Status |
|---|---|---|---|---|
| SM-001 | PeerAuthentication STRICT mode applied cluster-wide (Istio) | SC-8 | P0 | ❌ |
| SM-002 | Automatic mTLS enabled for all services (Linkerd) | SC-8 | P0 | ❌ |
| SM-003 | SPIFFE/SPIRE identity provisioning configured | IA-3 | P0 | ❌ |
| SM-004 | Certificate rotation period ≤ 24 hours for workload certs | SC-12 | P0 | ❌ |
| SM-005 | Root CA stored in Vault (not in cluster) | SC-12 | P0 | ❌ |

### Authorization (AC-3, AC-4)

| # | Check Item | Control | Priority | Status |
|---|---|---|---|---|
| SM-006 | AuthorizationPolicy resources defined per service (Istio) | AC-3 | P0 | ❌ |
| SM-007 | Default-deny authorization policy applied | AC-3 | P0 | ❌ |
| SM-008 | Egress restricted via ServiceEntry/egress gateway | SC-7 | P1 | ❌ |
| SM-009 | Rate limiting policies deployed for sensitive endpoints | SC-5 | P1 | ❌ |

### Observability (AU-2, SI-4)

| # | Check Item | Control | Priority | Status |
|---|---|---|---|---|
| SM-010 | Access logs enabled and forwarded to SIEM | AU-2 | P0 | ❌ |
| SM-011 | Distributed tracing (Jaeger/Zipkin) configured | SI-4 | P1 | ❌ |
| SM-012 | Prometheus metrics exported for mesh health | SI-4 | P1 | ❌ |

---

## Docker / containerd Runtime Compliance

### Image Supply Chain (SI-7, CM-7)

| # | Check Item | Control | Priority | Status |
|---|---|---|---|---|
| CR-001 | All production images signed with Cosign (ECDSA-P256) | SI-7 | P0 | ❌ |
| CR-002 | SBOM generated for every image (Syft, CycloneDX format) | SA-12 | P0 | ❌ |
| CR-003 | Images scanned for CVEs before registry push (Trivy/Grype) | SI-3 | P0 | ⚠️ |
| CR-004 | No images with CRITICAL severity CVEs in production | SI-3 | P0 | ⚠️ |
| CR-005 | Approved base images list maintained and enforced | CM-7 | P1 | ❌ |
| CR-006 | Multi-stage builds to minimize attack surface | CM-7 | P1 | ✅ |
| CR-007 | Registry requires authentication (no anonymous pull in prod) | IA-2 | P0 | ❌ |

### Runtime Security (SI-7, CM-6)

| # | Check Item | Control | Priority | Status |
|---|---|---|---|---|
| CR-008 | containerd configured with restricted snapshotter | CM-6 | P1 | ❌ |
| CR-009 | Runtime syscall filtering (seccomp) applied | SI-7 | P1 | ❌ |
| CR-010 | Rootless container mode where possible | CM-6 | P1 | ❌ |

---

## HashiCorp Vault Compliance

### Core Security (SC-12, IA-2)

| # | Check Item | Control | Priority | Status |
|---|---|---|---|---|
| V-001 | Vault HA with Raft integrated storage (3+ nodes) | CP-9 | P0 | ❌ |
| V-002 | Vault auto-unseal using cloud KMS (FIPS-compliant) | SC-12 | P0 | ❌ |
| V-003 | OIDC auth method configured with approved provider | IA-2 | P0 | ❌ |
| V-004 | Kubernetes auth method configured per namespace | IA-3 | P0 | ❌ |
| V-005 | Root token revoked after initial setup | IA-2 | P0 | ❌ |
| V-006 | Break-glass emergency tokens stored offline (offline root keys) | CP-2 | P0 | ❌ |
| V-007 | TLS 1.3 on Vault listener | SC-8 | P0 | ❌ |

### Secret Engines & Policies (SC-12, AC-3)

| # | Check Item | Control | Priority | Status |
|---|---|---|---|---|
| V-008 | KV v2 secret engine used for static secrets | SC-28 | P0 | ❌ |
| V-009 | PKI engine configured for internal CA | SC-12 | P0 | ❌ |
| V-010 | Transit engine used for application-level encryption | SC-13 | P1 | ❌ |
| V-011 | Database secret engine generating dynamic credentials | AC-3 | P0 | ❌ |
| V-012 | Lease TTL ≤ 90 days for all secrets | IA-5 | P0 | ❌ |
| V-013 | Vault policies follow least privilege | AC-3 | P0 | ❌ |
| V-014 | Sentinel EGP/RGP policies for enhanced controls | AC-3 | P2 | ❌ |

### Audit & Monitoring (AU-2, SI-4)

| # | Check Item | Control | Priority | Status |
|---|---|---|---|---|
| V-015 | Vault audit device: file + syslog enabled | AU-2 | P0 | ❌ |
| V-016 | Vault audit logs forwarded to SIEM (OpenSearch) | AU-2 | P0 | ❌ |
| V-017 | Alerting for failed Vault operations | SI-4 | P1 | ❌ |
| V-018 | Vault performance metrics exported to Prometheus | SI-4 | P1 | ❌ |

### Disaster Recovery (CP-9, CP-10)

| # | Check Item | Control | Priority | Status |
|---|---|---|---|---|
| V-019 | Vault DR replication configured (multi-region) | CP-9 | P1 | ❌ |
| V-020 | Vault snapshots taken and encrypted daily | CP-9 | P0 | ❌ |
| V-021 | Snapshot restoration tested quarterly | CP-4 | P0 | ❌ |
| V-022 | DR runbook documented and reviewed annually | CP-2 | P0 | ❌ |

---

## Pre-Deployment Gate: Production Promotion Criteria

Before any orchestration system is promoted to production, the following gate criteria must be met:

### P0 Gate (Blocking)

All P0 checks for the target system must be ✅ Implemented. No exceptions without documented risk acceptance from the CISO.

```
Required P0 checks passing:
  Kubernetes:  K-001..K-035 (P0 items)
  KubeFed:     F-001..F-006 (P0 items)
  ServiceMesh: SM-001..SM-005 (P0 items)
  ContainerRT: CR-001..CR-007 (P0 items)
  Vault:       V-001..V-022 (P0 items)
```

### P1 Gate (Non-Blocking for Initial Release, Required by Q3 2026)

P1 checks must be completed within 90 days of initial production deployment. A remediation plan must be submitted to the Governance Committee.

### P2 Gate (Roadmap)

P2 checks are planned improvements tracked on the governance roadmap.

---

## NIST 800-53 Control Coverage Matrix

| Control | Description | Kubernetes | KubeFed | ServiceMesh | Vault | Status |
|---|---|---|---|---|---|---|
| AC-2 | Account Management | K-001..009 | F-004 | — | V-003..006 | ⚠️ |
| AC-3 | Access Enforcement | K-006..009 | F-004 | SM-006..009 | V-013 | ⚠️ |
| AC-4 | Info Flow Enforcement | K-023..026 | — | SM-008 | — | ❌ |
| AC-5 | Separation of Duties | K-007 | — | — | V-005 | ⚠️ |
| AU-2 | Event Logging | K-027..030 | F-006 | SM-010 | V-015..016 | ❌ |
| AU-9 | Audit Integrity | K-030 | — | — | V-015 | ❌ |
| AU-11 | Audit Retention | K-029 | — | — | — | ❌ |
| AU-12 | Audit Generation | K-027..028 | F-006 | SM-010 | V-015 | ❌ |
| CM-6 | Configuration Settings | K-016..022 | — | — | — | ❌ |
| CM-7 | Least Functionality | K-031..035 | — | — | — | ❌ |
| CP-2 | Contingency Plan | — | F-007 | — | V-022 | ❌ |
| CP-4 | Contingency Testing | — | F-007 | — | V-021 | ❌ |
| CP-9 | Backup | — | F-007 | — | V-019..021 | ❌ |
| IA-2 | Identification/Auth | K-001..005 | — | — | V-001..006 | ⚠️ |
| IA-3 | Device Identification | — | F-003 | SM-003 | V-004 | ❌ |
| IA-5 | Authenticator Mgmt | K-008 | — | SM-004 | V-012 | ❌ |
| SA-12 | Supply Chain | — | — | CR-002 | — | ❌ |
| SC-5 | DoS Protection | — | — | SM-009 | — | ❌ |
| SC-7 | Boundary Protection | K-023..026 | — | SM-008 | — | ❌ |
| SC-8 | Transmission Confid. | K-011..012 | F-001..002 | SM-001..002 | V-007 | ❌ |
| SC-12 | Key Establishment | K-010..012 | — | SM-004..005 | V-001..002 | ❌ |
| SC-13 | Crypto Protection | K-010 | — | — | V-010 | ❌ |
| SC-28 | Protection at Rest | K-010..013 | — | — | V-008 | ❌ |
| SC-39 | Process Isolation | K-018 | — | — | — | ✅ |
| SI-3 | Malicious Code Prot. | K-033..034 | — | CR-003..004 | — | ⚠️ |
| SI-4 | System Monitoring | — | — | SM-011..012 | V-017..018 | ❌ |
| SI-7 | Software Integrity | K-016..022 | — | — | CR-001..010 | ❌ |

---

## Validation Procedures

### Automated Validation

Run the compliance check script against each target:

```bash
# Kubernetes cluster compliance check
python3 tools/validate.py --module orchestration --target kubernetes --kubeconfig ~/.kube/config

# Vault compliance check
python3 tools/validate.py --module orchestration --target vault --vault-addr https://vault.internal:8200

# Service mesh compliance check
python3 tools/validate.py --module orchestration --target service-mesh --namespace istio-system
```

### Manual Review Schedule

| Review Type | Frequency | Owner |
|---|---|---|
| P0 check audit | Monthly | Platform Security Lead |
| Full compliance review | Quarterly | Governance Committee |
| Penetration test | Annually | External Auditor |
| DR failover test | Quarterly | Platform Engineering |
| Certificate expiry audit | Monthly | Automated + Manual |

---

## Remediation Process

When a check is found non-compliant:

1. **Severity P0**: Open P0 ticket immediately. Patch/remediate within 7 days. Notify CISO.
2. **Severity P1**: Open P1 ticket. Remediate within 30 days. Include in sprint backlog.
3. **Severity P2**: Roadmap item. Schedule within next quarterly planning cycle.

All remediation evidence (screenshots, configs, audit logs) must be stored in:
```
standards/evidence/orchestration/<system>/<control-id>/<date>/
```

---

## Related Documents

- [Orchestration INDEX](./INDEX.md)
- [Kubernetes Security](./KUBERNETES-SECURITY.md)
- [KubeFed Standards](./KUBEFED-STANDARDS.md)
- [KinD Standards](./KIND-STANDARDS.md)
- [minikube Standards](./MINIKUBE-STANDARDS.md)
- [Container Runtime Security](./CONTAINER-RUNTIME-SECURITY.md)
- [Service Mesh Standards](./SERVICE-MESH-STANDARDS.md)
- [Secrets Management](./SECRETS-MANAGEMENT.md)
- [Audit Observability](./AUDIT-OBSERVABILITY.md)
- [NIST 800-53 Control Mappings](../nist-800-53/CONTROL-MAPPINGS.md)
- [Integration Map](../INTEGRATION-MAP.md)
