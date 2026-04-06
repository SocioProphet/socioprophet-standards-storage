# KubeFed Multi-Cluster Federation Standards — SocioProphet Platform

- Last updated: 2026-01-27
- Status: Active governance document
- Owner: Platform Engineering / Platform Security
- Applies to: SocioProphet KubeFed control plane and all member clusters

---

## Table of Contents

1. [KubeFed Architecture for SocioProphet](#kubefed-architecture-for-socioprophet)
2. [mTLS Between Federation Control Plane and Member Clusters](#mtls-between-federation-control-plane-and-member-clusters)
3. [Secret Synchronization Across Clusters](#secret-synchronization-across-clusters)
4. [Federated RBAC Policies](#federated-rbac-policies)
5. [Cross-Cluster Audit Log Aggregation](#cross-cluster-audit-log-aggregation)
6. [Disaster Recovery and Multi-Cluster Failover](#disaster-recovery-and-multi-cluster-failover)
7. [Federated Network Policies](#federated-network-policies)
8. [Health Monitoring for Federation Endpoints](#health-monitoring-for-federation-endpoints)

---

## KubeFed Architecture for SocioProphet

The SocioProphet platform deploys workloads across multiple geographic regions to meet availability, data residency, and compliance requirements. KubeFed provides the control plane for coordinating workload distribution, configuration propagation, and federated resource management across member clusters.

### Cluster Topology

```
┌─────────────────────────────────────────────────────────────────┐
│              KubeFed Host Cluster (us-east-1)                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │  KubeFed Controller Manager                              │   │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐   │   │
│  │  │ FederatedType│  │ PropagationP │  │ ReplicaSched │   │   │
│  │  │ Controller   │  │ olicy Ctrl   │  │ uler         │   │   │
│  │  └──────────────┘  └──────────────┘  └──────────────┘   │   │
│  └──────────────────────────────────────────────────────────┘   │
└──────────────────┬──────────────────────┬───────────────────────┘
                   │ mTLS                 │ mTLS
       ┌───────────▼───────┐   ┌──────────▼──────────┐
       │  Member Cluster   │   │   Member Cluster    │
       │  (us-west-2)      │   │   (eu-central-1)    │
       │  FIPS kube build  │   │   FIPS kube build   │
       └───────────────────┘   └─────────────────────┘
```

### Cluster Registration

Member clusters are registered using `kubefedctl join`, which creates a `KubeFedCluster` resource in the host cluster. The registration process must:

1. Use a dedicated service account in the member cluster (`kubefed-member-sa`), not the `cluster-admin` account.
2. Bind the service account to the `kubefed:member-role` ClusterRole (read Namespaces, write federated resources).
3. Store the kubeconfig credential in Vault (`kv/v2/kubefed/member-<cluster-name>`) and inject it via External Secrets Operator.

```yaml
apiVersion: core.kubefed.io/v1beta1
kind: KubeFedCluster
metadata:
  name: member-us-west-2
  namespace: kube-federation-system
spec:
  apiEndpoint: https://kube.us-west-2.socioprophet.internal:6443
  caBundle: <base64-encoded-CA>
  secretRef:
    name: member-us-west-2-credentials
```

### Supported Federated Resource Types

| Resource | Federation Mode | Overrides Allowed |
|---|---|---|
| Deployment | Propagated | Replica count per cluster |
| Service | Propagated | None |
| ConfigMap | Propagated | Cluster-specific values |
| NetworkPolicy | Propagated | None — policy must be identical |
| Namespace | Propagated | Labels only |
| ServiceAccount | Propagated | None |
| ExternalSecret | Propagated | Vault path per cluster |

---

## mTLS Between Federation Control Plane and Member Clusters

All communication between the KubeFed host cluster controller manager and member cluster kube-apiservers is protected by mTLS. This is enforced at two layers:

1. **Kubeconfig-level TLS**: The kubeconfig stored in Vault for each member cluster uses a client certificate signed by the SocioProphet Internal CA (see [SECRETS-MANAGEMENT.md](./SECRETS-MANAGEMENT.md) for Vault PKI configuration).
2. **Network-level mTLS**: Istio PeerAuthentication STRICT mode is applied to the `kube-federation-system` namespace, ensuring all inter-cluster control traffic is encrypted and mutually authenticated.

### Certificate Requirements

| Certificate | Algorithm | Key Size | Validity | Rotation |
|---|---|---|---|---|
| KubeFed controller client cert | ECDSA | P-256 | 90 days | Automated via cert-manager |
| Member cluster CA | ECDSA | P-384 | 5 years | Manual with dual approval |
| Inter-cluster API client cert | ECDSA | P-256 | 30 days | Automated via Vault PKI |

### cert-manager Certificate for KubeFed Controller

```yaml
apiVersion: cert-manager.io/v1
kind: Certificate
metadata:
  name: kubefed-controller-client
  namespace: kube-federation-system
spec:
  secretName: kubefed-controller-tls
  duration: 2160h  # 90 days
  renewBefore: 720h  # 30 days before expiry
  subject:
    organizations: [SocioProphet Platform]
  commonName: kubefed-controller.kube-federation-system
  keyAlgorithm: ecdsa
  keySize: 256
  usages:
    - client auth
  issuerRef:
    name: vault-pki-issuer
    kind: ClusterIssuer
```

---

## Secret Synchronization Across Clusters

Secrets are never stored in etcd unencrypted and are never propagated via KubeFed's built-in secret propagation. Instead, the SocioProphet platform uses a federated External Secrets Operator approach:

### Architecture

Each member cluster runs its own ESO instance, and each ESO instance reads from the cluster-local Vault instance (or from the regional Vault cluster). Vault DR replication ensures that each regional Vault contains the same secrets as the primary.

```
Host Cluster            Member Cluster (us-west-2)
┌───────────┐           ┌─────────────────────────┐
│ FederatedE│           │ ExternalSecret          │
│ xternalSe │ propagate │ (generated by federation│
│ cret      │──────────►│  controller)            │
└───────────┘           └────────────┬────────────┘
                                     │ reads from
                              ┌──────▼──────┐
                              │ Vault       │
                              │ us-west-2   │
                              │ (DR replica)│
                              └─────────────┘
```

### FederatedExternalSecret Custom Resource

The platform uses a custom controller (`fed-secrets-controller`) that watches `FederatedExternalSecret` resources on the host cluster and creates corresponding `ExternalSecret` resources on each member cluster.

```yaml
apiVersion: socioprophet.io/v1alpha1
kind: FederatedExternalSecret
metadata:
  name: db-credentials
  namespace: socioprophet-prod
spec:
  template:
    spec:
      refreshInterval: 1h
      secretStoreRef:
        name: vault-backend
        kind: ClusterSecretStore
      target:
        name: db-credentials
        creationPolicy: Owner
      data:
        - secretKey: password
          remoteRef:
            key: socioprophet/database
            property: password
  placement:
    clusters:
      - name: member-us-west-2
      - name: member-eu-central-1
  overrides:
    - clusterName: member-us-west-2
      clusterOverrides:
        - path: /spec/data/0/remoteRef/key
          value: socioprophet-us-west/database
    - clusterName: member-eu-central-1
      clusterOverrides:
        - path: /spec/data/0/remoteRef/key
          value: socioprophet-eu/database
```

### Encrypted Transit Requirements

All Vault API communication for secret retrieval uses TLS 1.3 with ECDHE-ECDSA cipher suites. The Vault agent sidecar injects credentials directly into pod memory; secrets do not touch disk.

---

## Federated RBAC Policies

RBAC policies are federated from the host cluster to all member clusters. Local RBAC overrides on member clusters are forbidden; all access is governed by federated policies.

### FederatedClusterRole

```yaml
apiVersion: types.kubefed.io/v1beta1
kind: FederatedClusterRole
metadata:
  name: socioprophet-workload
  namespace: kube-federation-system
spec:
  template:
    rules:
      - apiGroups: [""]
        resources: [configmaps]
        verbs: [get, list, watch]
      - apiGroups: [""]
        resources: [serviceaccounts/token]
        verbs: [create]
  placement:
    clusterSelector:
      matchLabels:
        socioprophet.io/member: "true"
```

### Federated ClusterRoleBinding

```yaml
apiVersion: types.kubefed.io/v1beta1
kind: FederatedClusterRoleBinding
metadata:
  name: socioprophet-workload-binding
  namespace: kube-federation-system
spec:
  template:
    roleRef:
      apiGroup: rbac.authorization.k8s.io
      kind: ClusterRole
      name: socioprophet-workload
    subjects:
      - kind: Group
        name: "oidc:socioprophet-workloads"
        apiGroup: rbac.authorization.k8s.io
  placement:
    clusterSelector:
      matchLabels:
        socioprophet.io/member: "true"
```

### RBAC Drift Detection

A weekly CronJob runs `kubectl auth can-i --list` against each member cluster API server and diffs the results against the expected federated policy. Any deviation triggers an alert in Alertmanager (see [AUDIT-OBSERVABILITY.md](./AUDIT-OBSERVABILITY.md)).

---

## Cross-Cluster Audit Log Aggregation

Each member cluster ships its kube-apiserver audit logs to the central OpenSearch cluster via a Vector agent. The aggregation pipeline is described in detail in [AUDIT-OBSERVABILITY.md](./AUDIT-OBSERVABILITY.md); the KubeFed-specific configuration is:

### Log Enrichment

Each audit log event is enriched with the following fields before forwarding:

```json
{
  "cluster": "member-us-west-2",
  "region": "us-west-2",
  "federation_host": "host-us-east-1",
  "compliance_scope": "fips-140-2",
  "environment": "production"
}
```

### Cross-Cluster Correlation

Federated operations (e.g., propagation of a FederatedDeployment) generate audit events on both the host cluster and the member clusters. The `requestID` field is preserved across clusters by the federation controller to enable correlation.

A Jaeger trace is emitted for each federated operation, linking the host-cluster API call to the member-cluster API calls. This trace is stored in the SocioProphet Jaeger instance and retained for 90 days.

---

## Disaster Recovery and Multi-Cluster Failover

### Failover Tiers

| Scenario | Recovery Action | RTO | RPO |
|---|---|---|---|
| Member cluster unreachable (transient) | KubeFed retries for 5 minutes; alerts after 2 minutes | < 5 min | 0 (no data loss) |
| Member cluster permanently failed | Promote standby cluster; re-register with KubeFed | < 30 min | < 5 min |
| Host cluster failure | Promote DR host cluster; re-federate all members | < 2 hours | < 15 min |
| Multi-region split-brain | Activate break-glass; manual quorum decision | < 4 hours | Varies |

### Member Cluster Failover Procedure

1. **Declare incident**: Page Platform Engineering on-call. Open an incident ticket.
2. **Isolate failed cluster**: Remove the `KubeFedCluster` resource for the failed member (`kubectl delete kubefedcluster member-<name> -n kube-federation-system`).
3. **Provision standby**: If a warm standby is available, update DNS to point to the standby cluster.
4. **Re-register standby**: `kubefedctl join member-<standby-name> --host-cluster-context=<host> --cluster-context=<standby>`.
5. **Trigger reconciliation**: The KubeFed controller will propagate all FederatedResources to the new member within the next reconciliation cycle (default: 10 seconds).
6. **Validate**: Run the post-deployment checklist from [INTEGRATION-CHECKLIST.md](./INTEGRATION-CHECKLIST.md) against the new member cluster.
7. **Update audit records**: Document all manual actions in the incident ticket with timestamps.

### Host Cluster DR

The KubeFed host cluster's etcd is backed up every 4 hours to S3 (encrypted with AES-256-GCM using a Vault-managed key). A DR host cluster is maintained in a separate region in warm-standby mode.

---

## Federated Network Policies

Network policies are federated using the same `FederatedNetworkPolicy` pattern as other resource types. The same default-deny baseline defined in [KUBERNETES-SECURITY.md](./KUBERNETES-SECURITY.md) is propagated to all member clusters.

```yaml
apiVersion: types.kubefed.io/v1beta1
kind: FederatedNetworkPolicy
metadata:
  name: default-deny-all
  namespace: kube-federation-system
spec:
  template:
    spec:
      podSelector: {}
      policyTypes:
        - Ingress
        - Egress
  placement:
    clusters:
      - name: member-us-west-2
      - name: member-eu-central-1
```

### Regional Egress Overrides

Clusters in the EU region have additional egress restrictions to comply with GDPR data residency requirements. These are applied as overrides on the FederatedNetworkPolicy:

```yaml
  overrides:
    - clusterName: member-eu-central-1
      clusterOverrides:
        - path: /spec/egress
          value:
            - to:
                - ipBlock:
                    cidr: 10.200.0.0/16  # EU VPC CIDR only
              ports:
                - protocol: TCP
                  port: 443
```

---

## Health Monitoring for Federation Endpoints

### KubeFed Controller Health Metrics

The KubeFed controller exposes Prometheus metrics at `:8080/metrics`. The following metrics are scraped by the cluster-local Prometheus instance:

| Metric | Alert Condition |
|---|---|
| `kubefed_controller_reconcile_errors_total` | > 5 in 5 minutes → PagerDuty critical |
| `kubefed_cluster_healthy` (gauge) | = 0 → PagerDuty critical |
| `kubefed_resource_propagation_duration_seconds` | p99 > 30s → Slack warning |
| `kubefed_controller_queue_depth` | > 100 → Slack warning |

### Member Cluster Health Checks

A synthetic health check job runs every 60 seconds against each member cluster's `/healthz`, `/readyz`, and `/livez` endpoints. The job is run from the host cluster and from an external monitoring node (cross-cluster validation).

```yaml
apiVersion: monitoring.coreos.com/v1
kind: ProbeList
metadata:
  name: member-cluster-health
  namespace: monitoring
spec:
  prober:
    url: blackbox-exporter.monitoring.svc.cluster.local:9115
  targets:
    staticConfig:
      static:
        - https://kube.us-west-2.socioprophet.internal:6443/healthz
        - https://kube.eu-central-1.socioprophet.internal:6443/healthz
      labels:
        environment: production
        component: kubernetes-apiserver
```

### Alertmanager Rules

```yaml
groups:
  - name: kubefed
    rules:
      - alert: KubeFedMemberClusterUnhealthy
        expr: kubefed_cluster_healthy == 0
        for: 2m
        labels:
          severity: critical
          team: platform
        annotations:
          summary: "KubeFed member cluster {{ $labels.cluster_name }} is unhealthy"
          runbook: "https://docs.socioprophet.internal/runbooks/kubefed-unhealthy"
      - alert: KubeFedReconcileErrors
        expr: rate(kubefed_controller_reconcile_errors_total[5m]) > 1
        for: 5m
        labels:
          severity: warning
          team: platform
        annotations:
          summary: "KubeFed controller reconcile errors elevated"
```
