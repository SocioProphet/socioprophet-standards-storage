# Orchestration Layer FIPS Compliance Standard

This document uses RFC 2119 language: **MUST**, **SHOULD**, **MAY**.

## 1. Overview

This standard defines FIPS 140-2/140-3 compliance requirements for the SocioProphet orchestration layer, covering:

- **Kubernetes** clusters (all environments)
- **kubefed** (federation control plane)
- **KinD** (CI testing)
- **minikube** (local development)
- **Istio/Linkerd** (service mesh)
- **HashiCorp Vault** (secrets management)

These requirements implement NIST 800-53 controls: **AC-2, AC-3, AC-17, IA-2, SC-7, SC-8, SC-12, AU-12, SI-7**.

---

## 2. Kubernetes Cluster Hardening

### 2.1 API Server Configuration

- The Kubernetes API server MUST be configured with:
  - `--tls-min-version=VersionTLS13` — enforce TLS 1.3 minimum
  - `--anonymous-auth=false` — no anonymous access
  - `--audit-log-path` — external audit log destination
  - `--audit-log-maxbackup=10` and `--audit-log-maxsize=100` — log rotation
  - `--audit-policy-file` — pointing to the audit policy document
  - `--oidc-issuer-url` — OIDC provider for user authentication
  - `--oidc-client-id` — OIDC client
  - `--oidc-username-claim=email` and `--oidc-groups-claim=groups`
  - `--authorization-mode=Node,RBAC` — RBAC authorization only
  - `--enable-admission-plugins=NodeRestriction,PodSecurity,ImagePolicyWebhook`
  - `--feature-gates=SeccompDefault=true`

- The etcd cluster MUST be configured with:
  - `--cipher-suites=TLS_AES_256_GCM_SHA384,TLS_CHACHA20_POLY1305_SHA256`
  - `--peer-auto-tls=false` — use manually provisioned certificates
  - `--client-cert-auth=true` — require client certificate authentication
  - etcd data directory MUST be on an encrypted volume (AES-256-GCM)

### 2.2 OIDC Integration (IA-2)

- All cluster users MUST authenticate via OIDC.
- Kubernetes service accounts MUST use projected service account tokens (not legacy tokens).
- `automountServiceAccountToken: false` MUST be the default; only set `true` where required.
- Service account token expiry MUST NOT exceed 24 hours (`--service-account-max-token-expiration=24h`).
- Cluster kubeconfig files MUST use OIDC credentials, not long-lived cluster admin certificates.

### 2.3 RBAC Hardening (AC-3)

- `cluster-admin` ClusterRoleBinding MUST be restricted to break-glass emergency accounts only.
- Every workload MUST use a dedicated ServiceAccount with minimal ClusterRole or Role.
- The `default` ServiceAccount in each namespace MUST have no permissions (`automountServiceAccountToken: false`).
- Namespace-scoped Roles MUST be preferred over ClusterRoles.
- RBAC audit MUST be conducted quarterly; unused roles and bindings MUST be removed.
- Kyverno or OPA/Gatekeeper MUST enforce that new ClusterRoleBindings require change control annotation.

---

## 3. Pod Security

### 3.1 Pod Security Standards (PSS)

- All production namespaces MUST enforce `pod-security.kubernetes.io/enforce: restricted`.
- CI/test namespaces MAY use `pod-security.kubernetes.io/enforce: baseline`.
- Development namespaces SHOULD use `pod-security.kubernetes.io/enforce: baseline`.
- Exception process MUST be documented and require security team approval.

### 3.2 Pod Security Requirements (Restricted Profile)

Every pod in production MUST comply with:
- `runAsNonRoot: true`
- `runAsUser: >= 1000`
- `readOnlyRootFilesystem: true`
- `allowPrivilegeEscalation: false`
- `capabilities: drop: [ALL]`; add only specific capabilities with documented justification
- `seccompProfile: RuntimeDefault` or `seccompProfile: Localhost`
- Resource limits (CPU and memory) MUST be defined for every container
- No `hostNetwork`, `hostPID`, or `hostIPC`

### 3.3 Container Image Security (SI-7)

- All container images MUST be signed using **Cosign/Sigstore**.
- An admission webhook (Kyverno `ImageVerification` policy) MUST reject unsigned images.
- Images MUST be pulled from a controlled, authenticated registry.
- Base images MUST use the minimal approved base (distroless or UBI-minimal).
- Images MUST be scanned for vulnerabilities before promotion to production (Trivy/Grype in CI).
- SBOM MUST be generated and attached to every image (Syft/Trivy SBOM output, CycloneDX or SPDX format).

---

## 4. Network Security

### 4.1 Network Policies (SC-7, AC-17)

- A **default-deny** NetworkPolicy MUST be deployed in every namespace:

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

- Explicit allow rules MUST be defined per source namespace, destination namespace, and port.
- Cross-namespace communication MUST be documented and approved.
- External egress MUST be restricted to approved endpoints (egress gateway or explicit allow rules).
- DNS egress MUST be allowed to kube-dns only (`port: 53`, `protocol: UDP/TCP`).

### 4.2 Ingress and Egress Control

- All external ingress MUST traverse an authenticated ingress controller (zero-trust gateway).
- Ingress MUST enforce TLS termination with certificates from the internal PKI.
- Direct pod-to-external-internet connections MUST be blocked.
- Egress to the internet MUST flow through a controlled egress gateway with allowlist policy.

---

## 5. Service Mesh (Istio/Linkerd)

### 5.1 mTLS Enforcement (SC-8)

- mTLS MUST be enforced across the entire mesh via a `PeerAuthentication` policy:

```yaml
apiVersion: security.istio.io/v1beta1
kind: PeerAuthentication
metadata:
  name: default
  namespace: istio-system
spec:
  mtls:
    mode: STRICT
```

- Permissive mode MUST NOT be used in production.
- Service mesh sidecar certificates MUST be issued by the internal PKI (Vault PKI engine via cert-manager).
- Certificate rotation MUST be automated (maximum 24-hour certificate lifetime for workloads).

### 5.2 Authorization Policies

- A default-deny `AuthorizationPolicy` MUST be applied at the mesh level:

```yaml
apiVersion: security.istio.io/v1beta1
kind: AuthorizationPolicy
metadata:
  name: deny-all
  namespace: istio-system
spec:
  {}
```

- Explicit allow policies MUST be defined per source principal (SPIFFE URI) and destination.
- JWT-based policies MUST validate OIDC tokens from the configured issuer.
- All policy evaluation results MUST be emitted as audit events.

### 5.3 Observability

- Service mesh MUST export metrics (Prometheus), distributed traces (Jaeger/Zipkin), and access logs (Envoy access log).
- Access logs MUST include: source IP, destination service, method, response code, latency, trace ID.
- Grafana dashboards MUST visualize mTLS coverage, error rates, and latency percentiles.
- Alert rules MUST fire on: mTLS failure spike, error rate >1%, P99 latency >500ms.

---

## 6. Secrets Management (HashiCorp Vault)

### 6.1 Vault Deployment

- Vault MUST be deployed in **High Availability (HA)** mode with a minimum of 3 nodes.
- Vault backend MUST use integrated storage (Raft) or a FIPS-compliant external backend.
- Vault MUST be configured with FIPS 140-2 mode enabled when using Vault Enterprise.
- Auto-unseal MUST use a cloud KMS (AWS KMS, GCP KMS) or HSM that is FIPS 140-2 Level 3 certified.

### 6.2 Vault Authentication (IA-2, IA-5)

- Kubernetes workloads MUST authenticate to Vault using the **Kubernetes auth method** (JWT-based with bound service account).
- Vault authentication MUST use short-lived tokens (TTL ≤ 1 hour).
- Vault root token MUST be revoked after initial setup; break-glass procedure MUST be documented.
- Vault admin access MUST use OIDC auth method with MFA.

### 6.3 Secrets Rotation (SC-12)

- All dynamic secrets (database passwords, API keys) MUST be rotated automatically via Vault dynamic secrets engines.
- Static secrets MUST be rotated at least every **90 days**; rotation MUST be automated.
- Vault lease duration for database credentials MUST NOT exceed 1 hour.
- Secret rotation events MUST be logged as audit events in Vault's audit device.

### 6.4 Vault Audit

- At least **two Vault audit devices** MUST be configured (e.g., file + syslog) for availability.
- Vault audit logs MUST be forwarded to the centralized log store.
- Vault audit logs MUST be retained for 7 years (see `093-forensic-audit-nist-800-88.md`).
- Vault audit log integrity MUST be verified daily (see `093-forensic-audit-nist-800-88.md`).

### 6.5 Secret Injection into Pods

- **Vault Secrets Operator** or **Vault Agent Injector** MUST be used to inject secrets into pods.
- Secrets MUST be projected into pods as files (not environment variables where possible).
- `envFrom.secretRef` MUST NOT be used for sensitive credentials (secrets mounted as files instead).
- `ExternalSecret` resources (External Secrets Operator) SHOULD be used to synchronize secrets into Kubernetes Secret objects where pod file injection is not feasible.

---

## 7. Kubernetes Federation (kubefed)

### 7.1 Federation Control Plane Security

- kubefed control plane MUST authenticate to member clusters using short-lived OIDC tokens.
- Federation control plane API MUST enforce TLS 1.3 with mutual client authentication.
- Cross-cluster communication MUST use mTLS (Istio multi-cluster or Submariner).
- Federation policies MUST be stored and audited in the central GitOps repository.

### 7.2 Multi-Cluster RBAC

- Each member cluster MUST have independent RBAC policies; federation MUST NOT grant cluster-admin globally.
- Cross-cluster service account tokens MUST use the **TokenRequestProjection** feature.
- Federation sync MUST log all cross-cluster resource creates/updates/deletes as audit events.

---

## 8. Kubernetes Audit Logging (AU-12)

### 8.1 Audit Policy

The Kubernetes API server audit policy MUST capture at `RequestResponse` level:
- All requests to `secrets`, `configmaps`, `serviceaccounts`, `roles`, `rolebindings`, `clusterroles`, `clusterrolebindings`
- All `exec`, `port-forward`, and `attach` operations
- All `create`, `update`, `patch`, `delete` operations on all resources

At `Metadata` level (log request/response metadata, not body):
- All other API requests

No audit events MUST be omitted (no `None` rules without explicit justification).

### 8.2 Audit Log Shipping

- API server audit logs MUST be shipped to the centralized log store within 60 seconds.
- Log shipping MUST use a dedicated, isolated log forwarder (Fluentbit/Fluentd in a privileged namespace).
- Audit log forwarder MUST authenticate to the log store with mTLS.
- In the event of log store unavailability, logs MUST be buffered locally (max 10 GB or 24 hours).

---

## 9. Local and CI Environments

### 9.1 KinD (CI)
- KinD clusters MUST use the same audit policy as production (reduced retention).
- Container images MUST be signed and verified in CI (same admission policy as production).
- CI secrets MUST be injected via CI secrets management (GitHub Actions Secrets / Vault CI integration).

### 9.2 minikube (Local Development)
- Local environments MAY use `pod-security.kubernetes.io/enforce: baseline`.
- Developers MUST NOT use production credentials in local environments.
- FIPS compliance checks MUST run in CI (not required for local developer machines).

---

## 10. Compliance Verification

- CI/CD pipelines MUST run a Kyverno policy audit on every deployment.
- A daily CIS Kubernetes Benchmark scan MUST run against all production clusters.
- Vault seal status and HA health MUST be monitored with alerts firing within 5 minutes of failure.
- All cluster certificates MUST be monitored for expiry (alert at 30 days before expiration).
- Pod security violations MUST generate alerts in the monitoring stack.

## Related Standards

- `050-security-oidc-policy.md` — Identity and authorization
- `090-fips-nist-compliance.md` — Cryptographic requirements
- `091-nist-800-53-control-mappings.md` — NIST 800-53 control mappings
- `092-zero-trust-nist-800-207.md` — Zero-trust architecture
- `093-forensic-audit-nist-800-88.md` — Forensic audit trails
- `094-data-layer-fips-compliance.md` — Data store compliance (Vault integration)

## Implementation Evidence

- API server configuration: `SocioProphet/sociosphere/k8s/apiserver/kube-apiserver.yaml`
- Pod Security Standards: `SocioProphet/sociosphere/k8s/pod-security/pss-policy.yaml`
- Default-deny network policies: `SocioProphet/sociosphere/k8s/network-policies/default-deny.yaml`
- Istio PeerAuthentication: `SocioProphet/sociosphere/mesh/mtls-policy.yaml`
- Istio AuthorizationPolicies: `SocioProphet/sociosphere/mesh/authorization-policies.yaml`
- Vault HA configuration: `SocioProphet/sociosphere/vault/vault-config.hcl`
- Vault auth method: `SocioProphet/sociosphere/vault/k8s-auth.hcl`
- Kyverno image signing policy: `SocioProphet/sociosphere/k8s/admission/image-signing.yaml`
- CI audit policy: `SocioProphet/sociosphere/k8s/audit/audit-policy.yaml`
- Log shipping: `SocioProphet/sociosphere/observability/fluentbit-audit.yaml`
