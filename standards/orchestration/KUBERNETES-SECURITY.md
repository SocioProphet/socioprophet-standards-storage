# Kubernetes Security Standards — SocioProphet Platform

- Last updated: 2026-01-27
- Status: Active governance document
- Owner: Platform Engineering / Platform Security
- Applies to: All SocioProphet Kubernetes clusters (production, staging, CI)

---

## Table of Contents

1. [OIDC Authentication Configuration](#oidc-authentication-configuration)
2. [RBAC Policies](#rbac-policies)
3. [Network Policies](#network-policies)
4. [Secrets Management](#secrets-management)
5. [Pod Security Standards](#pod-security-standards)
6. [Audit Logging](#audit-logging)
7. [Image Security and Admission Control](#image-security-and-admission-control)
8. [etcd Encryption at Rest](#etcd-encryption-at-rest)
9. [CIS Kubernetes Benchmark Compliance](#cis-kubernetes-benchmark-compliance)
10. [Kubernetes Hardening Checklist](#kubernetes-hardening-checklist)

---

## OIDC Authentication Configuration

The SocioProphet platform uses OIDC as the primary human operator authentication mechanism for the Kubernetes API server. Service-to-service authentication uses SPIFFE/SPIRE SVIDs distributed through Istio or Linkerd.

### kube-apiserver OIDC Flags

All kube-apiserver deployments must be started with the following OIDC flags. These values are environment-specific; the placeholders below must be replaced with cluster-specific values stored in Vault.

```
--oidc-issuer-url=https://auth.socioprophet.internal/oidc
--oidc-client-id=kube-apiserver
--oidc-username-claim=email
--oidc-username-prefix=oidc:
--oidc-groups-claim=groups
--oidc-groups-prefix=oidc:
--oidc-ca-file=/etc/kubernetes/pki/oidc-ca.crt
--oidc-required-claim=aud=kube-apiserver
```

### Additional kube-apiserver Security Flags

```
--anonymous-auth=false
--authorization-mode=Node,RBAC
--enable-admission-plugins=NodeRestriction,PodSecurity,EventRateLimit,\
  AlwaysPullImages,ImagePolicyWebhook,LimitRanger,\
  ResourceQuota,ServiceAccount
--audit-log-path=/var/log/kubernetes/audit.log
--audit-policy-file=/etc/kubernetes/audit-policy.yaml
--audit-log-maxage=30
--audit-log-maxbackup=10
--audit-log-maxsize=100
--tls-min-version=VersionTLS12
--tls-cipher-suites=TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384,\
  TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384,\
  TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256,\
  TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256
--encryption-provider-config=/etc/kubernetes/encryption-config.yaml
--service-account-issuer=https://kubernetes.socioprophet.internal
--service-account-signing-key-file=/etc/kubernetes/pki/sa.key
--service-account-key-file=/etc/kubernetes/pki/sa.pub
--kubelet-certificate-authority=/etc/kubernetes/pki/ca.crt
--kubelet-client-certificate=/etc/kubernetes/pki/apiserver-kubelet-client.crt
--kubelet-client-key=/etc/kubernetes/pki/apiserver-kubelet-client.key
--profiling=false
--request-timeout=120s
--feature-gates=RotateKubeletServerCertificate=true
```

### kubelet Configuration

```yaml
authentication:
  anonymous:
    enabled: false
  webhook:
    enabled: true
  x509:
    clientCAFile: /etc/kubernetes/pki/ca.crt
authorization:
  mode: Webhook
tlsCipherSuites:
  - TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384
  - TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384
  - TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256
  - TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256
tlsMinVersion: VersionTLS12
rotateCertificates: true
serverTLSBootstrap: true
protectKernelDefaults: true
readOnlyPort: 0
eventRecordQPS: 5
```

---

## RBAC Policies

### ClusterRoles for SocioProphet Services

SocioProphet defines the following ClusterRoles. All are named with the `socioprophet:` prefix to avoid collisions with built-in roles.

```yaml
# Read-only access for observability services (Prometheus, Grafana, Jaeger)
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: socioprophet:observability-reader
rules:
  - apiGroups: [""]
    resources: [nodes, pods, services, endpoints, namespaces]
    verbs: [get, list, watch]
  - apiGroups: [apps]
    resources: [deployments, replicasets, statefulsets, daemonsets]
    verbs: [get, list, watch]
  - apiGroups: [batch]
    resources: [jobs, cronjobs]
    verbs: [get, list, watch]
  - nonResourceURLs: [/metrics, /healthz, /readyz]
    verbs: [get]
---
# Vault Agent Injector needs to patch pods
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: socioprophet:vault-agent-injector
rules:
  - apiGroups: [""]
    resources: [pods]
    verbs: [get, list, watch, patch]
  - apiGroups: [admissionregistration.k8s.io]
    resources: [mutatingwebhookconfigurations]
    verbs: [get, list, watch, create, update, patch]
---
# External Secrets Operator
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: socioprophet:external-secrets-operator
rules:
  - apiGroups: [external-secrets.io]
    resources: [externalsecrets, secretstores, clustersecretstores]
    verbs: [get, list, watch, create, update, patch, delete]
  - apiGroups: [""]
    resources: [secrets, serviceaccounts]
    verbs: [get, list, watch, create, update, patch, delete]
  - apiGroups: [""]
    resources: [events]
    verbs: [create, patch]
```

### Namespace-Scoped Roles

```yaml
# SocioProphet application workload — minimal permissions per namespace
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: socioprophet:workload
  namespace: socioprophet-prod
rules:
  - apiGroups: [""]
    resources: [configmaps]
    verbs: [get, list, watch]
  - apiGroups: [""]
    resources: [pods]
    verbs: [get]
  - apiGroups: [""]
    resources: [serviceaccounts/token]
    verbs: [create]
---
# CI/CD deploy role — scoped to apply manifests, not to read secrets
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: socioprophet:cicd-deploy
  namespace: socioprophet-prod
rules:
  - apiGroups: [apps]
    resources: [deployments, statefulsets]
    verbs: [get, list, watch, create, update, patch]
  - apiGroups: [""]
    resources: [services, configmaps]
    verbs: [get, list, watch, create, update, patch]
  - apiGroups: [networking.k8s.io]
    resources: [ingresses]
    verbs: [get, list, watch, create, update, patch]
```

### RoleBinding and ClusterRoleBinding Conventions

- All bindings use OIDC group subjects (`oidc:<group>`) rather than individual user subjects.
- Service accounts are bound to the minimum Role required. No service account is bound to `cluster-admin`.
- `cluster-admin` is reserved for break-glass emergency access only, governed by the break-glass procedure in [SECRETS-MANAGEMENT.md](./SECRETS-MANAGEMENT.md).
- All bindings are audited on a 30-day cycle; unused bindings are removed.

---

## Network Policies

### Default-Deny Baseline

Every SocioProphet namespace must have a default-deny policy applied before any workloads are scheduled. Namespace provisioning automation enforces this.

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-all
  namespace: socioprophet-prod
spec:
  podSelector: {}
  policyTypes:
    - Ingress
    - Egress
```

### Ingress Rules — Application Tier

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-ingress-from-mesh
  namespace: socioprophet-prod
spec:
  podSelector:
    matchLabels:
      app.kubernetes.io/part-of: socioprophet
  policyTypes:
    - Ingress
  ingress:
    - from:
        - namespaceSelector:
            matchLabels:
              kubernetes.io/metadata.name: istio-system
      ports:
        - protocol: TCP
          port: 8080
    - from:
        - namespaceSelector:
            matchLabels:
              kubernetes.io/metadata.name: socioprophet-prod
      ports:
        - protocol: TCP
          port: 8080
        - protocol: TCP
          port: 9090
```

### Egress Rules — Controlled Outbound

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-egress-controlled
  namespace: socioprophet-prod
spec:
  podSelector:
    matchLabels:
      app.kubernetes.io/part-of: socioprophet
  policyTypes:
    - Egress
  egress:
    # DNS resolution
    - to:
        - namespaceSelector:
            matchLabels:
              kubernetes.io/metadata.name: kube-system
      ports:
        - protocol: UDP
          port: 53
        - protocol: TCP
          port: 53
    # Vault for secrets
    - to:
        - namespaceSelector:
            matchLabels:
              kubernetes.io/metadata.name: vault
      ports:
        - protocol: TCP
          port: 8200
    # Intra-namespace traffic
    - to:
        - namespaceSelector:
            matchLabels:
              kubernetes.io/metadata.name: socioprophet-prod
```

---

## Secrets Management

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
