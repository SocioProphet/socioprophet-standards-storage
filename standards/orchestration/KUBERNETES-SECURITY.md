# Kubernetes Security Standards

## Rationale

Kubernetes clusters are the primary runtime for SocioProphet workloads. Misconfigured clusters represent the largest attack surface in the orchestration layer. This standard defines the minimum security posture that every Kubernetes cluster MUST maintain to be considered compliant with the SocioProphet governance framework and NIST 800-53 controls.

---

## Cluster API Authentication

### OIDC Integration

- Clusters MUST configure `--oidc-issuer-url`, `--oidc-client-id`, `--oidc-username-claim`, and `--oidc-groups-claim` on the API server.
- Accepted identity providers: GitHub (via GitHub Actions OIDC for CI), corporate identity providers (e.g., Okta, Azure AD, Keycloak).
- OIDC token validation MUST require audience restriction; tokens without an `aud` claim MUST be rejected.
- OIDC tokens MUST have a maximum lifetime of 1 hour for human users and 15 minutes for CI workloads.

### Webhook Token Authentication

- Webhook token authentication MAY be used as an alternative to OIDC where OIDC is unavailable.
- Webhook endpoints MUST use TLS 1.3 and authenticate with mutual TLS.
- Tokens passed to webhooks MUST be short-lived (maximum 1 hour).

### Service Account Management

- Every workload MUST use a dedicated `ServiceAccount`; the `default` service account in any namespace MUST have all tokens disabled (`automountServiceAccountToken: false`).
- Service account tokens MUST use the `BoundServiceAccountTokenVolume` feature (bound tokens with audience and expiry).
- Projected service account tokens MUST expire within 1 hour.
- Service accounts MUST NOT be granted `ClusterAdmin` or equivalent permissions.

### Client Certificate Authentication (mTLS)

- Client certificate authentication MUST only be used for break-glass emergency access.
- Certificates MUST use ECDSA-P256 or RSA-4096 minimum key size.
- Emergency certificates MUST be revoked within 24 hours of use via CRL or OCSP.
- Emergency certificate use MUST generate a high-priority audit alert.

---

## RBAC (Role-Based Access Control)

### Cluster Roles vs. Namespace Roles

- `ClusterRole` resources MUST only be used when cross-namespace or cluster-wide access is genuinely required.
- Namespace-scoped `Role` resources MUST be preferred for all application workloads.
- All `ClusterRoleBinding` resources MUST be reviewed and approved by the security team before deployment.

### Least Privilege Role Definitions

- Roles MUST enumerate only the specific `verbs`, `resources`, and `resourceNames` required.
- Wildcard (`*`) verbs or resources MUST NOT be used in production roles.
- Read-only access (`get`, `list`, `watch`) MUST be granted in preference to write access (`create`, `update`, `patch`, `delete`) unless the workload requires write.

### Service Account per Workload

- Each `Deployment`, `StatefulSet`, or `DaemonSet` MUST reference a unique `ServiceAccount`.
- Service accounts MUST be named to identify the owning workload (e.g., `<workload-name>-sa`).
- Service accounts MUST be annotated with the owning team and last-reviewed date.

### Separation of Duties

- Application workloads MUST NOT hold `cluster-admin` or any `ClusterRole` that grants write access to all resources.
- Platform operators (human) MUST use impersonation (`kubectl --as`) rather than holding persistent elevated permissions.
- `cluster-admin` binding MUST be restricted to a break-glass group with auditable access.

### Quarterly RBAC Review

- All `ClusterRoleBinding` and `RoleBinding` resources MUST be reviewed quarterly.
- Unused service accounts and roles MUST be removed within 30 days of identification.
- Review results MUST be recorded as an immutable audit event.

---

## Network Policies

### Default Deny

- Every namespace MUST contain a default-deny `NetworkPolicy` for both ingress and egress:

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-all
spec:
  podSelector: {}
  policyTypes:
    - Ingress
    - Egress
```

### Explicit Allow Rules

- Ingress and egress rules MUST be added as separate `NetworkPolicy` resources that explicitly enumerate allowed peer namespaces, pod selectors, ports, and protocols.
- DNS egress (UDP/TCP port 53 to `kube-dns`) MUST be explicitly permitted for all namespaces.
- Monitoring scrape paths (Prometheus) MUST be explicitly permitted.

### Pod-to-Pod Network Isolation

- Pods MUST NOT be reachable from outside their own namespace unless an explicit `NetworkPolicy` permits it.
- Cross-namespace communication MUST use `namespaceSelector` in the `NetworkPolicy` rule, not open CIDR ranges.

### Service Mesh Integration

- When Istio or Linkerd is deployed, `NetworkPolicy` MUST remain in place alongside service-mesh authorization policies; one MUST NOT substitute for the other.
- Service mesh mTLS MUST enforce per-service authorization; see [SERVICE-MESH-STANDARDS.md](SERVICE-MESH-STANDARDS.md).

---

## Secrets Management

### Encryption at Rest

- Kubernetes `Secret` objects MUST be encrypted at rest in etcd using `aescbc` with AES-256 or `aesgcm` with AES-256-GCM.
- The encryption configuration MUST be applied at API server startup via `--encryption-provider-config`.
- Encryption keys MUST be rotated annually or upon suspected compromise.

### External Secrets Provider (HashiCorp Vault)

- Application secrets MUST be sourced from HashiCorp Vault and injected into pods via the Vault Agent Injector or the External Secrets Operator.
- Kubernetes `Secret` objects created by the External Secrets Operator serve as a projection cache only; they MUST NOT be the authoritative secret store.
- See [SECRETS-MANAGEMENT.md](SECRETS-MANAGEMENT.md) for full Vault integration requirements.

### Secret Rotation

- Long-lived secrets MUST be rotated on a maximum 30-day cycle.
- Rotation MUST be zero-downtime (rolling update or dual-active).
- All rotation events MUST be logged as immutable audit entries.

### RBAC for Secret Access

- Only the `ServiceAccount` belonging to the consuming workload MAY have `get` access to its projected `Secret` object.
- No `list` or `watch` permission on `Secret` resources SHOULD be granted to application workloads.

---

## Pod Security Standards

### Enforced Restrictions

- All production namespaces MUST be labelled with `pod-security.kubernetes.io/enforce: restricted`.
- The `restricted` profile prohibits: privileged containers, host namespaces (PID, IPC, network), host path volumes (write), running as root, and privilege escalation.

### Security Contexts

Every pod MUST include:

```yaml
securityContext:
  runAsNonRoot: true
  runAsUser: 65534
  seccompProfile:
    type: RuntimeDefault
containers:
  - securityContext:
      allowPrivilegeEscalation: false
      readOnlyRootFilesystem: true
      capabilities:
        drop: ["ALL"]
```

### Image Pull Secrets

- Pods that pull from private registries MUST reference an `imagePullSecret` in their pod spec.
- Image pull credentials MUST be rotated on a 30-day cycle and sourced from Vault.

---

## Audit Logging

### API Audit Policy

- The Kubernetes API server MUST be started with `--audit-log-path`, `--audit-policy-file`, `--audit-log-maxage`, and `--audit-log-maxbackup` flags.
- The audit policy MUST log `RequestResponse` level for secrets, configmaps, and authentication-related resources.
- The audit policy MUST log at least `Metadata` level for all other resources.

### Immutable Audit Log Storage

- Audit logs MUST be forwarded to external, immutable storage (e.g., S3 with Object Lock, GCS with Bucket Lock) within 60 seconds.
- Logs MUST NOT be stored exclusively in cluster-local volumes.

### Retention

- Hot storage: 90 days.
- Archived storage: 7 years.

### Audit Events

Each audit event MUST include: `user.username`, `user.groups`, `sourceIPs`, `verb`, `objectRef.resource`, `objectRef.namespace`, `objectRef.name`, `responseStatus.code`, `requestReceivedTimestamp`, `stageTimestamp`.

---

## Image Security

### Vulnerability Scanning

- All container images MUST be scanned before admission using a tool such as Trivy, Grype, or equivalent.
- Images with Critical or High severity CVEs without a mitigating control MUST be blocked by admission policy.
- SBOM (Software Bill of Materials) MUST be generated and stored alongside each published image.

### Image Signing

- All images MUST be signed using `cosign` with ECDSA-P256 keys or `notary` with ECDSA-P256.
- Signing keys MUST be stored in Vault or a hardware-backed key store.

### Admission Control

- An `ImagePolicyWebhook` or equivalent admission controller MUST validate that all images are signed before a pod is admitted to any production namespace.
- Unsigned images MUST be blocked; admission MUST generate an audit event.

### Registry Authentication

- Image pulls MUST use TLS 1.3 to the registry.
- Unauthenticated pulls from public registries MUST be blocked in production namespaces.

---

## References

- NIST SP 800-53 Rev. 5: https://csrc.nist.gov/publications/detail/sp/800-53/rev-5
- Kubernetes Security Concepts: https://kubernetes.io/docs/concepts/security/
- Kubernetes Pod Security Standards: https://kubernetes.io/docs/concepts/security/pod-security-standards/
- cosign Image Signing: https://docs.sigstore.dev/cosign/overview/
- External Secrets Operator: https://external-secrets.io/
