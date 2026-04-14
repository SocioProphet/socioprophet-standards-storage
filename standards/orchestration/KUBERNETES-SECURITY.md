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
### External Secrets Operator

The SocioProphet platform uses the [External Secrets Operator (ESO)](https://external-secrets.io/) to synchronize secrets from Vault into Kubernetes Secrets. No secret value is stored in Git or etcd unencrypted.

```yaml
apiVersion: external-secrets.io/v1beta1
kind: ClusterSecretStore
metadata:
  name: vault-backend
spec:
  provider:
    vault:
      server: https://vault.socioprophet.internal:8200
      path: socioprophet
      version: v2
      auth:
        kubernetes:
          mountPath: kubernetes
          role: socioprophet-prod
          serviceAccountRef:
            name: external-secrets-sa
            namespace: external-secrets
---
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: db-credentials
  namespace: socioprophet-prod
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
```

### Sealed Secrets (CI Environments)

For CI/CD environments where Vault is not directly accessible, [Sealed Secrets](https://github.com/bitnami-labs/sealed-secrets) is used to encrypt Kubernetes Secrets with the cluster's public key so they can be stored in Git.

- Sealed Secrets keys are rotated every 30 days.
- Sealing keys are backed up to Vault.
- Sealed Secrets are used exclusively for non-sensitive CI credentials (image pull tokens, test API keys). Production secrets never use Sealed Secrets.

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
All SocioProphet production namespaces enforce the **Restricted** Pod Security Standard. This is enforced via the Kubernetes built-in Pod Security Admission controller.

### Namespace Labels

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: socioprophet-prod
  labels:
    pod-security.kubernetes.io/enforce: restricted
    pod-security.kubernetes.io/enforce-version: latest
    pod-security.kubernetes.io/audit: restricted
    pod-security.kubernetes.io/warn: restricted
```

### Restricted Profile Requirements

Under the Restricted profile, the following are enforced:

| Requirement | Configuration |
|---|---|
| `hostProcess` | Must be false or unset |
| `hostNetwork` | Must be false |
| `hostPID` | Must be false |
| `hostIPC` | Must be false |
| `privileged` | Must be false |
| `allowPrivilegeEscalation` | Must be false |
| `runAsNonRoot` | Must be true |
| `runAsUser` | Must be ≥ 1000 |
| `readOnlyRootFilesystem` | Must be true |
| `seccompProfile.type` | Must be RuntimeDefault or Localhost |
| `capabilities.drop` | Must include ALL |
| `capabilities.add` | Only NET_BIND_SERVICE permitted |
| `volumes` | Only configMap, downwardAPI, emptyDir, persistentVolumeClaim, projected, secret permitted |

---

## Audit Logging

### kube-apiserver Audit Policy

The following audit policy captures all security-relevant events at `RequestResponse` level for sensitive resources, with reduced verbosity for high-volume low-risk resources.

```yaml
apiVersion: audit.k8s.io/v1
kind: Policy
omitStages:
  - RequestReceived
rules:
  # Log all requests to secrets, configmaps, tokens at RequestResponse level
  - level: RequestResponse
    resources:
      - group: ""
        resources: [secrets, configmaps, serviceaccounts/token]
    omitManagedFields: false
  # Log all RBAC changes
  - level: RequestResponse
    resources:
      - group: rbac.authorization.k8s.io
        resources: [clusterroles, clusterrolebindings, roles, rolebindings]
  # Log all auth-related events
  - level: Request
    users: [system:anonymous]
    verbs: [get, list, watch]
  # Log pod creation and deletion
  - level: Request
    resources:
      - group: ""
        resources: [pods]
    verbs: [create, delete, patch, update]
  # Log namespace operations
  - level: Request
    resources:
      - group: ""
        resources: [namespaces]
  # Log admission webhook changes
  - level: RequestResponse
    resources:
      - group: admissionregistration.k8s.io
        resources: [mutatingwebhookconfigurations, validatingwebhookconfigurations]
  # Reduce verbosity for read-heavy system components
  - level: None
    users:
      - system:kube-proxy
      - system:kube-scheduler
      - system:node-problem-detector
    verbs: [get, watch, list]
  # Default: log metadata only for everything else
  - level: Metadata
    omitManagedFields: true
```

Audit logs are forwarded to the centralized OpenSearch pipeline described in [AUDIT-OBSERVABILITY.md](./AUDIT-OBSERVABILITY.md).

---

## Image Security and Admission Control

### Cosign Signature Verification

All container images deployed to SocioProphet production clusters must be signed with Cosign using an ECDSA-P256 key. The signing key is stored in Vault's Transit engine.

The `ImagePolicyWebhook` admission plugin calls the SocioProphet image verification service, which:

1. Retrieves the image digest from the registry.
2. Fetches the Cosign signature from the OCI registry.
3. Verifies the signature against the SocioProphet platform signing key.
4. Checks the image against the Trivy vulnerability database; blocks if critical CVEs are present.
5. Returns allow/deny to the API server.

```yaml
# Kyverno policy for image signature enforcement (used alongside the webhook)
apiVersion: kyverno.io/v1
kind: ClusterPolicy
metadata:
  name: require-signed-images
spec:
  validationFailureAction: Enforce
  background: false
  rules:
    - name: check-image-signature
      match:
        any:
          - resources:
              kinds: [Pod]
              namespaces: [socioprophet-prod, socioprophet-staging]
      verifyImages:
        - imageReferences:
            - "registry.socioprophet.internal/*"
          attestors:
            - count: 1
              entries:
                - keyless:
                    rekor:
                      url: https://rekor.socioprophet.internal
                    issuer: https://auth.socioprophet.internal/oidc
                    subject: "*.socioprophet.internal"
```

### AlwaysPullImages Admission Plugin

The `AlwaysPullImages` plugin is enabled on all production clusters. This ensures that:

- The registry authorization is checked on every pod start (not just first pull).
- A node compromise cannot serve cached images to bypass image signing checks.

---

## etcd Encryption at Rest

etcd must encrypt all Secrets (and optionally ConfigMaps) at rest using AES-256-GCM. The `aescbc` provider is legacy and must not be used for new clusters.

```yaml
# /etc/kubernetes/encryption-config.yaml
apiVersion: apiserver.config.k8s.io/v1
kind: EncryptionConfiguration
resources:
  - resources:
      - secrets
      - configmaps
    providers:
      # Primary: AES-GCM (FIPS-approved)
      - aesgcm:
          keys:
            - name: key-2026-01
              secret: <base64-encoded-256-bit-key-from-vault>
      # Fallback identity for migration reads only — remove after migration
      - identity: {}
```

Key rotation procedure:
1. Generate a new 256-bit key in Vault Transit engine (`vault write transit/keys/etcd-encryption type=aes256-gcm96`).
2. Export the derived key material and update the encryption config with the new key as the first entry.
3. Restart all kube-apiserver pods (rolling restart).
4. Run `kubectl get secrets --all-namespaces -o json | kubectl replace -f -` to re-encrypt all secrets with the new key.
5. Remove the old key from the encryption config.
6. Rotate the key in Vault.

---

## CIS Kubernetes Benchmark Compliance

The SocioProphet platform targets CIS Kubernetes Benchmark v1.9 Level 2. Automated scanning is performed by `kube-bench` on every cluster on a weekly schedule.

| Section | Control | Status | Notes |
|---|---|---|---|
| 1.1 | Master Node Config Files permissions | ✅ | Enforced by bootstrap |
| 1.2.1 | anonymous-auth=false | ✅ | kube-apiserver flag |
| 1.2.2 | BasicAuth disabled | ✅ | Not enabled |
| 1.2.6 | AlwaysAdmit plugin not set | ✅ | |
| 1.2.10 | admission plugins set | ✅ | See §OIDC config |
| 1.2.19 | audit-log-path set | ✅ | |
| 1.2.20 | audit-log-maxage ≥ 30 | ✅ | Set to 30 |
| 1.2.29 | TLS cipher suites FIPS | ✅ | See §TLS config |
| 1.3.1 | terminated-pod-gc-threshold set | ✅ | 12500 |
| 2.1 | etcd cert-file and key-file | ✅ | |
| 2.2 | etcd peer-client-cert-auth=true | ✅ | |
| 3.1.1 | Client cert auth not used for users | ✅ | OIDC only |
| 4.2.1 | anonymous-auth=false on kubelet | ✅ | |
| 5.1.1 | cluster-admin not used broadly | ✅ | Break-glass only |
| 5.2 | Pod Security Standards enforced | ✅ | Restricted profile |
| 5.4 | Secrets not in env vars | ✅ | ESO / Vault injection |
| 5.7.1 | Namespaces used for isolation | ✅ | Per-service namespaces |

---

## Kubernetes Hardening Checklist

Use this checklist during cluster provisioning and during quarterly security reviews.

### Control Plane

- [ ] kube-apiserver started with all required security flags (see §OIDC section)
- [ ] anonymous-auth=false
- [ ] OIDC issuer and CA configured
- [ ] Audit policy file deployed and audit logging enabled
- [ ] etcd encryption at rest configured (AES-GCM-256)
- [ ] etcd peer-to-peer TLS enforced
- [ ] Service account token automounting disabled globally (overridden per pod where needed)
- [ ] `cluster-admin` binding count = 1 (break-glass account only)

### Worker Nodes

- [ ] kubelet anonymous auth disabled
- [ ] kubelet authorization mode = Webhook
- [ ] kubelet read-only port = 0
- [ ] Rotate kubelet server certificates enabled
- [ ] Kernel default protections enabled (`protectKernelDefaults: true`)

### Workloads

- [ ] All production namespaces labeled with `pod-security.kubernetes.io/enforce: restricted`
- [ ] Default-deny NetworkPolicy applied to all namespaces
- [ ] No Pods run as root (UID 0)
- [ ] No Pods with privileged=true or allowPrivilegeEscalation=true
- [ ] All capabilities dropped; NET_BIND_SERVICE only if needed
- [ ] readOnlyRootFilesystem=true on all containers
- [ ] No hostPath volumes in production namespaces

### Images

- [ ] All images signed with Cosign; signature verified at admission
- [ ] AlwaysPullImages admission plugin enabled
- [ ] Image vulnerability scanning passed (no critical CVEs)
- [ ] Images sourced only from `registry.socioprophet.internal`
- [ ] Base images are distroless or UBI minimal

### Secrets

- [ ] No secrets in environment variables
- [ ] No secrets in ConfigMaps
- [ ] All secrets sourced from Vault via External Secrets Operator or Vault Agent
- [ ] Secret rotation verified (≤ 90 days)
