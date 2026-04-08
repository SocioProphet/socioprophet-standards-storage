# Minikube Standards

## Rationale

minikube provides a single-node Kubernetes cluster for developer laptops. It is used for individual workload development and testing before code reaches CI pipelines. This standard defines the security baseline that minikube installations MUST maintain to prevent the developer environment from becoming a vector for credential leakage or security regression.

---

## Developer Onboarding

### Standardised minikube Configuration

- All developers MUST use a minikube configuration file (`~/.minikube/config/config.json` or equivalent) that enforces the baseline settings defined in this standard.
- The organisation MUST provide a reference configuration file in the repository at `ops/local-dev/minikube-config.yaml`.
- Developers MUST use the reference configuration as the starting point and MUST NOT disable security features without documented justification.

### Automated Setup Scripts

- An automated setup script MUST be provided at `ops/local-dev/setup-minikube.sh`.
- The script MUST:
  - Install minikube at a pinned version.
  - Apply the reference configuration.
  - Start minikube with required feature gates and addons.
  - Verify that RBAC, pod security admission, and network policy enforcement are active.
- The script MUST be tested in CI on every pull request that modifies it.

### Security Baseline Enforcement

- The setup script MUST fail with a clear error message if:
  - The host Docker daemon version is below the minimum supported version.
  - An insecure minikube driver (e.g., `none` driver without root) is detected.
  - RBAC is disabled in the minikube start flags.

---

## Local Development Best Practices

### No Hardcoded Credentials

- Source code, Helm values files, Kubernetes manifests, and configuration files committed to version control MUST NOT contain credentials of any kind.
- Pre-commit hooks MUST be configured to detect common credential patterns (API keys, passwords, tokens) and block commits that contain them.
- Detected violations MUST be treated as a security incident and rotated immediately.

### External Secrets Provider

- Developers MUST use a local Vault dev server (`vault server -dev`) rather than hardcoded environment variables or plain Kubernetes `Secret` objects.
- The Vault dev server MUST be started with a unique root token per session; the root token MUST NOT be persisted between sessions.
- Integration tests that require secrets MUST read them from the local Vault dev server using the same Vault Agent or External Secrets Operator path used in production.

### Network Policies for Testing

- minikube clusters MUST have a CNI addon that supports `NetworkPolicy` (e.g., Calico via `minikube start --cni=calico`).
- Developers MUST apply the same default-deny `NetworkPolicy` resources used in production namespaces to validate that their workloads declare correct ingress/egress rules.

### RBAC Testing

- Developers MUST test their workloads under the same `ServiceAccount` and `Role`/`RoleBinding` that will be used in production.
- Tests MUST NOT pass simply because the developer's `kubectl` context holds cluster-admin privileges.

---

## IDE and Tools Integration

### kubectl Context Switching

- Developers MUST use named contexts in their `kubeconfig` to distinguish between minikube, KinD, and production cluster connections.
- Context names MUST follow the pattern: `<environment>-<cluster-name>` (e.g., `local-minikube`, `ci-kind`, `prod-us-east-1`).
- A `kubectl` plugin or shell alias MUST be provided to warn the developer when switching to a production context.

### Helm Chart Testing

- Helm charts MUST be validated with `helm lint` and `helm template` before applying to minikube.
- `helm test` MUST be run against all charts on minikube before a pull request is opened.
- Charts that fail `helm lint` at the `error` severity MUST be fixed before merging.

### Debugging Workloads Securely

- Debugging sessions using `kubectl exec` or `kubectl port-forward` MUST NOT expose sensitive processes to the host network.
- `kubectl debug` ephemeral containers MUST NOT be granted capabilities beyond `CAP_NET_ADMIN` unless explicitly documented.
- Debugging sessions MUST be terminated once the debugging activity is complete; persistent debug containers MUST NOT be committed to workload manifests.

---

## Minikube Configuration Reference

The following `minikube start` flags MUST be set:

```bash
minikube start \
  --driver=docker \
  --kubernetes-version=<pinned-version> \
  --cni=calico \
  --extra-config=apiserver.enable-admission-plugins=NodeRestriction,PodSecurity \
  --extra-config=apiserver.audit-log-path=/var/log/kubernetes/audit.log \
  --extra-config=apiserver.audit-policy-file=/etc/kubernetes/audit-policy.yaml \
  --feature-gates=BoundServiceAccountTokenVolume=true
```

- `--kubernetes-version` MUST be pinned to a specific patch version and updated within 30 days of a security patch release.
- `--cni=calico` MUST be used to enable `NetworkPolicy` enforcement; the default Kindnet CNI does not enforce policies.
- Admission plugins MUST include `NodeRestriction` and `PodSecurity` at minimum.

---

## Differences from KinD

| Concern | KinD | minikube |
|---|---|---|
| Primary use | CI pipelines (ephemeral) | Developer laptops (persistent) |
| Cluster lifecycle | Created and destroyed per job | Persistent across sessions |
| OIDC | Optional | Optional |
| Audit logging | Required for CI artefacts | Recommended, stored locally |
| Secrets | Synthetic test data only | Local Vault dev server |
| Network policies | Required for test isolation | Required for policy testing |
| Cleanup | Automatic post-job | Manual (`minikube stop`) |

---

## References

- minikube Documentation: https://minikube.sigs.k8s.io/
- NIST SP 800-53 Rev. 5: https://csrc.nist.gov/publications/detail/sp/800-53/rev-5
- Kubernetes Pod Security Admission: https://kubernetes.io/docs/concepts/security/pod-security-admission/
- Calico CNI: https://docs.tigera.io/calico/latest/
- Vault Dev Server: https://developer.hashicorp.com/vault/docs/concepts/dev-server
# minikube Standards — SocioProphet Platform Developer Laptops

- Last updated: 2026-01-27
- Status: Active governance document
- Owner: DevSecOps / Platform Security
- Applies to: Developer laptops running minikube for local SocioProphet development

---

## Table of Contents

1. [minikube Configuration (FIPS-Compliant Profile)](#minikube-configuration-fips-compliant-profile)
2. [Developer Authentication Requirements](#developer-authentication-requirements)
3. [Local Secret Management](#local-secret-management)
4. [Network Isolation for minikube](#network-isolation-for-minikube)
5. [Allowed and Disallowed Operations](#allowed-and-disallowed-operations)
6. [Sync with Production Security Policies](#sync-with-production-security-policies)
7. [Security Scanning in Local Development Workflows](#security-scanning-in-local-development-workflows)

---

## minikube Configuration (FIPS-Compliant Profile)

Developers running minikube on SocioProphet projects must use the `socioprophet-fips` profile, which is pre-configured with FIPS-compatible settings. This profile is created and managed by the `prophet-cli` tool.

### Creating the Profile

```bash
# Using prophet-cli (preferred — handles all flag configuration)
prophet-cli dev cluster create --profile socioprophet-fips

# Manual equivalent (for reference):
minikube start \
  --profile socioprophet-fips \
  --kubernetes-version v1.29.2 \
  --iso-url https://artifactory.socioprophet.internal/minikube/minikube-fips-v1.32.0.iso \
  --driver docker \
  --nodes 1 \
  --cpus 4 \
  --memory 8192 \
  --disk-size 40g \
  --container-runtime containerd \
  --cni calico \
  --extra-config=apiserver.anonymous-auth=false \
  --extra-config=apiserver.authorization-mode=Node,RBAC \
  --extra-config=apiserver.tls-min-version=VersionTLS12 \
  --extra-config=apiserver.tls-cipher-suites=TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384,TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384,TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256,TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256 \
  --extra-config=apiserver.audit-log-path=/var/log/kubernetes/audit.log \
  --extra-config=apiserver.audit-policy-file=/etc/kubernetes/audit-policy.yaml \
  --extra-config=apiserver.profiling=false \
  --extra-config=kubelet.anonymous-auth=false \
  --extra-config=kubelet.authorization-mode=Webhook \
  --extra-config=kubelet.read-only-port=0
```

### FIPS ISO Image

The SocioProphet FIPS minikube ISO is built from the official minikube ISO with:

- Linux kernel compiled with `CONFIG_CRYPTO_FIPS=y`.
- OpenSSL 3.0 FIPS module installed and activated.
- The containerd runtime built with BoringCrypto.

The ISO is published to `artifactory.socioprophet.internal/minikube/minikube-fips-<version>.iso` and its SHA-256 digest is pinned in `prophet-cli`.

### Profile Persistence

The `socioprophet-fips` profile configuration is stored at `~/.minikube/profiles/socioprophet-fips/config.json`. Developers must not modify this file manually. Use `prophet-cli` to update profile settings.

### Required minikube Addons

| Addon | Purpose | Required |
|---|---|---|
| `metrics-server` | Local resource metrics | Yes |
| `ingress` | Local ingress for dev routing | Yes |
| `registry` | Local image registry (mirror) | Optional |
| `metallb` | LoadBalancer support | Optional |
| `calico` | Full NetworkPolicy support | Yes |

```bash
minikube addons enable metrics-server --profile socioprophet-fips
minikube addons enable ingress --profile socioprophet-fips
```

---

## Developer Authentication Requirements

### Local OIDC Stub (Dex)

The `socioprophet-fips` minikube profile includes a Dex OIDC provider deployed in the `auth` namespace. This provides local OIDC authentication for the minikube kube-apiserver, mirroring the production OIDC flow.

```yaml
# Dex configuration (deployed by prophet-cli dev cluster create)
issuer: https://dex.socioprophet.local
connectors:
  - type: local
    id: local
    name: Local
staticClients:
  - id: kube-apiserver
    redirectURIs:
      - http://localhost:8000
    name: Kubernetes API Server
    secret: dev-client-secret-not-for-production
staticPasswords:
  - email: "developer@socioprophet.local"
    hash: "$2a$10$..."  # bcrypt of dev password; not a production credential
    username: "developer"
    userID: "dev-user-001"
```

Developers authenticate to minikube using `kubectl oidc-login` (kubelogin plugin):

```bash
kubectl oidc-login setup \
  --oidc-issuer-url=https://dex.socioprophet.local \
  --oidc-client-id=kube-apiserver \
  --oidc-client-secret=dev-client-secret-not-for-production
```

### No Shared Credentials

Each developer uses their own OIDC identity. The Dex static password is per-developer and stored only in the local Dex ConfigMap. Team members should not share the same OIDC login.

---

## Local Secret Management

### Policy: No Production Secrets in minikube

This is an absolute policy. Violations are treated as security incidents.

**Production secrets include but are not limited to**:

- Any Vault tokens scoped to production or staging Vault namespaces.
- Production database credentials.
- Production API keys or OIDC client secrets.
- Production TLS private keys.
- Any credential with access to customer data.

### Developer Secret Patterns

All secrets in the `socioprophet-fips` minikube cluster are synthetic, scoped to local development only, and contain no sensitive data.

| Secret Type | Source | How to Create |
|---|---|---|
| Database credentials | Local Postgres in-cluster | Auto-seeded by `make dev-setup` |
| OIDC client secret | Dex static client (local only) | `dev-client-secret-not-for-production` |
| TLS certificates | Self-signed by minikube CA | Auto-generated at cluster start |
| Registry pull secret | Read-only token for `registry.socioprophet.internal` | `prophet-cli auth registry-login --scope dev` |

### Local Vault Instance (Optional)

Developers who want to test Vault integration locally can run a Vault dev server in minikube:

```bash
# Deploy Vault dev server (NOT FIPS-validated; dev mode only)
prophet-cli dev vault start

# This deploys Vault in dev mode (single node, in-memory, no TLS)
# It is not a substitute for the production Vault configuration
```

**Important**: The Vault dev server started by `prophet-cli dev vault start` uses Vault's `-dev` flag, which disables seal/unseal and persists nothing. It is not FIPS-validated and must not be used to store real credentials.

---

## Network Isolation for minikube

### Host Network Isolation

The minikube VM runs inside Docker (with the docker driver). Developers must not expose minikube services to interfaces other than `127.0.0.1`. The following configuration is enforced by the `socioprophet-fips` profile:

```
minikube tunnel  # Maps LoadBalancer services to 127.0.0.1 only
```

### Internal DNS

The local Dex OIDC provider and internal services are resolved via `/etc/hosts` or a local DNS resolver. `prophet-cli` configures these entries on initial cluster setup:

```
127.0.0.1   dex.socioprophet.local
127.0.0.1   registry.socioprophet.local
127.0.0.1   vault.socioprophet.local
```

### NetworkPolicy in minikube

The Calico CNI addon enforces NetworkPolicy resources in minikube. Developers should apply the same default-deny baseline used in production to their test namespaces:

```bash
# Apply baseline policies to a dev namespace
kubectl apply -f standards/orchestration/examples/network-policies/default-deny.yaml \
  --namespace my-dev-namespace
```

---

## Allowed and Disallowed Operations

### Allowed Operations

| Operation | Notes |
|---|---|
| Running any workload from `registry.socioprophet.internal` (dev-tagged images) | Must use `dev-*` or `snapshot-*` tagged images |
| Deploying test fixtures and synthetic data | No real customer data |
| Port-forwarding services to `127.0.0.1` | For browser-based testing |
| Enabling/disabling minikube addons | Via `prophet-cli` only |
| Running `kubectl exec` for debugging | On locally built images only |
| Running Vault dev server | See Local Secret Management section |

### Disallowed Operations

| Operation | Reason | Alternative |
|---|---|---|
| Using `kubectl` with a production kubeconfig on the minikube cluster | Risk of cross-cluster action | Use separate kubeconfig contexts |
| Storing production secrets in any minikube Secret or ConfigMap | Security incident risk | Use synthetic secrets |
| Exposing minikube services on `0.0.0.0` | Exposes services to local network | Use `127.0.0.1` only |
| Disabling Pod Security Standards | Undermines policy testing | Use a separate namespace |
| Running containers as root (UID 0) | Violates least-privilege | Fix the container image |
| Building and running unsigned images in production-mirror namespaces | Bypasses image signing check | Sign images with `cosign sign` |
| Running `minikube start` without the `socioprophet-fips` profile | Creates non-compliant cluster | Use `prophet-cli dev cluster create` |

---

## Sync with Production Security Policies

The `socioprophet-fips` minikube profile tracks production security policy. When production policies change, `prophet-cli` will notify developers at next cluster start and offer to apply updates.

### Policy Synchronization Mechanism

1. The `prophet-cli` tool checks a policy manifest at `standards/orchestration/examples/minikube-policy-manifest.json` on cluster start.
2. If the manifest version is newer than the version last applied to the local cluster, `prophet-cli` prompts the developer to apply the updated policies.
3. Applying the updated policies runs `kubectl apply -f standards/orchestration/examples/` against the `socioprophet-fips` cluster.

### Checking Policy Sync Status

```bash
prophet-cli dev cluster policy-status --profile socioprophet-fips

# Example output:
# Profile: socioprophet-fips
# Local policy version: 2025-11-01
# Latest policy version: 2026-01-15
# Status: OUT OF DATE — run 'prophet-cli dev cluster policy-update' to sync
```

### What Gets Synced

| Policy Category | Sync Mechanism |
|---|---|
| NetworkPolicies | `kubectl apply -f` |
| Pod Security Standard labels | `kubectl label namespace` |
| RBAC ClusterRoles and Roles | `kubectl apply -f` |
| Admission webhook configurations | `kubectl apply -f` (local webhook only) |
| Audit policy | Requires cluster restart |

---

## Security Scanning in Local Development Workflows

### Pre-Commit Image Scanning

Before pushing a container image to the registry, developers must scan it with Trivy:

```bash
# Scan a locally built image
trivy image --severity HIGH,CRITICAL my-service:dev

# Integrated via Makefile target
make scan-image IMAGE=my-service:dev
```

The `make scan-image` target fails the build if any CRITICAL CVEs are found without a documented exception in `security/exceptions.yaml`.

### Local SBOM Generation

```bash
# Generate SBOM for a locally built image
syft my-service:dev -o spdx-json > sbom-my-service.spdx.json

# Attach SBOM as OCI artifact
cosign attach sbom --sbom sbom-my-service.spdx.json my-service:dev

# Via Makefile:
make sbom IMAGE=my-service:dev
```

### Pre-Deployment Security Checks

Before deploying a workload to the `socioprophet-fips` minikube cluster, the `prophet-cli` tool runs:

1. `kubesec scan <manifest.yaml>` — Kubernetes manifest security scoring.
2. `kube-score score <manifest.yaml>` — Best-practice compliance.
3. `trivy config <manifest.yaml>` — IaC misconfiguration detection.
4. Admission webhook dry-run: `kubectl apply --dry-run=server -f <manifest.yaml>`.

Any HIGH or CRITICAL findings block deployment and must be resolved or excepted via `security/exceptions.yaml`.

```bash
# Run all pre-deployment checks
prophet-cli dev deploy --dry-run --manifest my-service/k8s/

# Deploy after checks pass
prophet-cli dev deploy --manifest my-service/k8s/
```

### Dependency Scanning

```bash
# Scan Go dependencies for known vulnerabilities
govulncheck ./...

# Scan Python dependencies
pip-audit -r requirements.txt

# Scan Node.js dependencies
npm audit --audit-level=high
```

These checks are also run in the CI pipeline but are encouraged locally before pushing to reduce PR cycle time.
