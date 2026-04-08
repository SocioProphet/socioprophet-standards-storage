# Kubernetes Federation Standards (kubefed)

## Rationale

kubefed enables multi-cluster Kubernetes federation, allowing workloads, policies, and configurations to be propagated across multiple clusters. Federation extends the attack surface beyond a single cluster boundary. This standard defines security requirements for all federated control planes and workloads managed within the SocioProphet governance framework.

---

## Federation Control Plane Setup

### OIDC Authentication Across Clusters

- Each federated cluster MUST be individually configured with OIDC authentication as specified in [KUBERNETES-SECURITY.md](KUBERNETES-SECURITY.md).
- The federation control plane MUST authenticate to member clusters using service account tokens bound to OIDC-issued identities, not static kubeconfig credentials.
- A common OIDC issuer SHOULD be used across all federated clusters to enable consistent identity resolution.

### mTLS Communication Between Clusters

- All federation control-plane-to-member-cluster communication MUST use mTLS.
- Certificates MUST use ECDSA-P256 or RSA-4096 minimum.
- Certificates MUST be issued by a shared CA trusted by all member clusters.
- Certificate rotation MUST be automated (cert-manager or equivalent) with a maximum 30-day lifetime.

### Secret Synchronisation

- Raw Kubernetes `Secret` objects MUST NOT be synchronised between clusters by kubefed.
- Secrets MUST be synchronised via Vault: each cluster retrieves its secrets independently from the central Vault cluster.
- Sealed Secrets MAY be used as an interim measure with explicit documentation of the deviation and a remediation timeline.

### Audit Trail Federation

- Audit logs from all member clusters MUST be forwarded to a central, immutable log store.
- The central log store MUST retain logs for 90 days hot and 7 years archived.
- Each audit event MUST include the originating cluster identifier.

---

## Workload Federation

### Federated Resource Types

- Federated `Deployment`, `StatefulSet`, and `DaemonSet` resources MUST use the `FederatedDeployment`, `FederatedStatefulSet`, and `FederatedDaemonSet` APIs respectively.
- Federated resources MUST specify `placement` policies that explicitly list allowed member clusters; wildcard placement MUST NOT be used.

### Cross-Cluster Health Checks

- Each federated workload MUST define liveness and readiness probes.
- The federation control plane MUST monitor health status of each placement independently.
- Unhealthy placements MUST trigger an alert within 5 minutes.

### Failover Policies

- Federated workloads that are business-critical MUST define a `ReplicaSchedulingPreference` with failover targets.
- Failover MUST be automatic for production workloads and MUST not require manual intervention for the first failover event.
- Failover events MUST be logged as immutable audit entries.

### Traffic Policy

- Service discovery across clusters MUST use Istio or Linkerd service mesh with federated service entries; see [SERVICE-MESH-STANDARDS.md](SERVICE-MESH-STANDARDS.md).
- DNS federation MUST be implemented via ExternalDNS or equivalent, with DNSSEC enabled where the DNS provider supports it.

---

## Multi-Cluster Networking

### Service Mesh for Inter-Cluster Communication

- Istio multi-cluster mesh or Linkerd multi-cluster MUST be deployed for all inter-cluster communication.
- mTLS MUST be enforced for all cross-cluster traffic; plain-text inter-cluster communication is prohibited.
- Certificate issuers across clusters MUST share a common root CA or an intermediate CA hierarchy so that mTLS handshakes succeed without trust exceptions.

### CNI Consistency

- The same CNI plugin MUST be deployed on all member clusters or CNI plugins that support the same `NetworkPolicy` API semantics MUST be used.
- CNI plugin versions SHOULD be kept within one minor version across clusters to prevent policy interpretation drift.

### IP Address Management

- IP address ranges MUST NOT overlap between clusters.
- IP address management (IPAM) MUST be documented for each cluster and reviewed when a new cluster is added.

### DNS Federation

- Each cluster MUST have a distinct DNS zone.
- Cross-cluster service resolution MUST use fully qualified domain names (FQDNs).
- DNS over TLS or DNS over HTTPS MUST be used for any external DNS queries.

---

## Secrets Federation

### Centralised Secrets Provider

- HashiCorp Vault MUST be deployed in high-availability mode (3+ nodes) as the authoritative secrets provider; see [SECRETS-MANAGEMENT.md](SECRETS-MANAGEMENT.md).
- Each member cluster MUST authenticate to Vault using the Kubernetes JWT auth method scoped to that cluster.

### Per-Cluster Secret Projection

- Vault policies MUST be scoped per cluster; a compromised cluster MUST NOT allow access to another cluster's secrets.
- Secrets MUST be projected into pods via the Vault Agent Injector or External Secrets Operator on each member cluster independently.
- Raw secrets MUST NOT reside in etcd on any member cluster without envelope encryption.

### Audit Logging of Secret Access

- All Vault secret-read events MUST be forwarded to the central audit log store.
- Vault audit log events MUST include: cluster identifier, service account name, namespace, secret path, timestamp, and result.

### Rotation Policies

- Secret rotation policies MUST be synchronised across clusters; all clusters MUST rotate secrets within the same 30-day window.
- Rotation MUST be zero-downtime across all affected clusters simultaneously.

---

## RBAC Across Clusters

### Federated RBAC Policies

- `FederatedClusterRole` and `FederatedClusterRoleBinding` resources MUST be used to propagate RBAC policies uniformly to all member clusters.
- Per-cluster RBAC overrides MUST be documented and approved by the security team.

### Consistent Role Definitions

- Role names and permission sets MUST be consistent across all member clusters.
- Any divergence between a cluster's actual role and the federated role definition MUST trigger an automated alert.

### Cross-Cluster Service Accounts

- Cross-cluster service accounts MUST NOT share tokens; each cluster MUST issue its own bound token for the service account identity.
- Impersonation across clusters MUST be logged as an audit event in both the source and target cluster.

### Audit of Federated Access Decisions

- All federated RBAC decision events MUST be captured in the central audit log.
- Rejected cross-cluster access MUST generate a high-priority alert within 5 minutes.

---

## Disaster Recovery

### Failover Procedures

- Failover procedures MUST be documented in the operations runbook and reviewed quarterly.
- The runbook MUST include: detection trigger, cluster isolation steps, workload promotion steps, DNS cutover steps, and validation tests.

### Recovery Time Objective

- Recovery Time Objective (RTO) for federated workloads MUST be less than 1 hour from incident declaration.

### Recovery Point Objective

- Recovery Point Objective (RPO) for federated persistent state MUST be less than 5 minutes, enforced by continuous backup or synchronous replication.

### Quarterly DR Testing

- Disaster recovery scenarios MUST be tested quarterly in a non-production federation.
- Test results MUST be documented and retained for 3 years.
- Failures in quarterly DR tests MUST generate a remediation ticket with a 30-day resolution deadline.

---

## References

- kubefed Documentation: https://github.com/kubernetes-sigs/kubefed
- NIST SP 800-53 Rev. 5: https://csrc.nist.gov/publications/detail/sp/800-53/rev-5
- Istio Multi-Cluster: https://istio.io/latest/docs/setup/install/multicluster/
- Linkerd Multi-Cluster: https://linkerd.io/2.13/features/multicluster/
- ExternalDNS: https://github.com/kubernetes-sigs/external-dns
