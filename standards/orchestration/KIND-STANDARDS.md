# KinD (Kubernetes in Docker) Standards — SocioProphet Platform

- Last updated: 2026-01-27
- Status: Active governance document
- Owner: DevSecOps / Platform Engineering
- Applies to: CI/CD pipelines (GitHub Actions) and local developer KinD clusters

---

## Table of Contents

1. [KinD Cluster Configuration for Local Development](#kind-cluster-configuration-for-local-development)
2. [Audit Logging in KinD Clusters](#audit-logging-in-kind-clusters)
3. [RBAC Configuration for Dev Environments](#rbac-configuration-for-dev-environments)
4. [Secret Management in KinD](#secret-management-in-kind)
5. [Network Policy Enforcement in KinD](#network-policy-enforcement-in-kind)
6. [CI/CD Integration: GitHub Actions KinD Provisioning](#cicd-integration-github-actions-kind-provisioning)
7. [Security Controls for CI Environments](#security-controls-for-ci-environments)
8. [Ephemeral Cluster Cleanup Procedures](#ephemeral-cluster-cleanup-procedures)

---

## KinD Cluster Configuration for Local Development

KinD clusters used for local development and CI must be provisioned from a standard configuration that enforces FIPS-compatible settings. Developers must not create ad-hoc KinD clusters outside this specification.

### FIPS-Compliant KinD Node Image

The SocioProphet KinD node image is built from the upstream `kindest/node` image with the following modifications:

- Compiled with `GOFLAGS=-tags=fips` and `CGO_ENABLED=1` against the BoringCrypto `crypto/tls` implementation.
- All OpenSSL dynamic libraries replaced with the FIPS-validated OpenSSL 3.0 FIPS module.
- The image is published to `registry.socioprophet.internal/infra/kindest-node-fips:<version>` and signed with Cosign.

### Standard KinD Cluster Configuration

```yaml
# kind-config.yaml — SocioProphet standard KinD configuration
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
name: socioprophet-dev
networking:
  apiServerAddress: 127.0.0.1
  apiServerPort: 6443
  podSubnet: 10.244.0.0/16
  serviceSubnet: 10.96.0.0/16
  disableDefaultCNI: false
  kubeProxyMode: iptables
nodes:
  - role: control-plane
    image: registry.socioprophet.internal/infra/kindest-node-fips:v1.29.2
    kubeadmConfigPatches:
      - |
        kind: ClusterConfiguration
        apiServer:
          extraArgs:
            anonymous-auth: "false"
            authorization-mode: "Node,RBAC"
            audit-log-path: /var/log/kubernetes/audit.log
            audit-policy-file: /etc/kubernetes/audit-policy.yaml
            audit-log-maxage: "7"
            audit-log-maxsize: "50"
            tls-min-version: VersionTLS12
            tls-cipher-suites: "TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384,TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384,TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256,TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256"
            encryption-provider-config: /etc/kubernetes/encryption-config.yaml
            profiling: "false"
          extraVolumes:
            - name: audit-policy
              hostPath: /etc/kubernetes/audit-policy.yaml
              mountPath: /etc/kubernetes/audit-policy.yaml
              readOnly: true
              pathType: File
            - name: audit-log
              hostPath: /var/log/kubernetes
              mountPath: /var/log/kubernetes
              pathType: DirectoryOrCreate
            - name: encryption-config
              hostPath: /etc/kubernetes/encryption-config.yaml
              mountPath: /etc/kubernetes/encryption-config.yaml
              readOnly: true
              pathType: File
        etcd:
          local:
            extraArgs:
              cipher-suites: "TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384,TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384"
  - role: worker
    image: registry.socioprophet.internal/infra/kindest-node-fips:v1.29.2
  - role: worker
    image: registry.socioprophet.internal/infra/kindest-node-fips:v1.29.2
```

### Pod Security Standards for KinD

Development namespaces in KinD use the `Baseline` Pod Security Standard (not `Restricted`) to ease developer iteration, with the exception of namespaces that mirror production configuration. Production-mirror namespaces use `Restricted`.

```yaml
# For dev namespaces
pod-security.kubernetes.io/enforce: baseline
pod-security.kubernetes.io/warn: restricted

# For production-mirror namespaces
pod-security.kubernetes.io/enforce: restricted
pod-security.kubernetes.io/enforce-version: latest
```

---

## Audit Logging in KinD Clusters

KinD clusters emit audit logs to a file on the control-plane node. In CI environments, these logs are captured and uploaded as GitHub Actions artifacts. In local dev environments, they are available at the path configured in the kubeadm patch above.

### Audit Policy for KinD

A simplified audit policy is used for KinD (compared to production) to reduce log volume:

```yaml
# /etc/kubernetes/audit-policy.yaml (KinD)
apiVersion: audit.k8s.io/v1
kind: Policy
omitStages:
  - RequestReceived
rules:
  - level: RequestResponse
    resources:
      - group: ""
        resources: [secrets]
  - level: Request
    resources:
      - group: rbac.authorization.k8s.io
        resources: [clusterroles, clusterrolebindings, roles, rolebindings]
  - level: Request
    resources:
      - group: ""
        resources: [pods]
    verbs: [create, delete, patch, update]
  - level: None
    users: [system:kube-proxy, system:kube-scheduler]
    verbs: [get, watch, list]
  - level: Metadata
    omitManagedFields: true
```

### Accessing Audit Logs

```bash
# Get the container ID of the control-plane node
CONTAINER=$(docker ps --filter "name=socioprophet-dev-control-plane" --format "{{.ID}}")

# Tail the audit log
docker exec "${CONTAINER}" cat /var/log/kubernetes/audit.log | jq .

# In CI: copy logs out before cluster teardown
docker cp "${CONTAINER}:/var/log/kubernetes/audit.log" ./audit-ci-run-${GITHUB_RUN_ID}.log
```

---

## RBAC Configuration for Dev Environments

### Developer Cluster Admin

For KinD clusters, developers have cluster-admin access. This is acceptable because:

- KinD clusters are ephemeral (CI) or local (dev); they contain no production data.
- No production secrets or credentials are present in KinD clusters.
- The risk surface is the developer's own machine or CI runner.

However, all RBAC policy testing should be done in a dedicated namespace with the minimum required permissions, mirroring production.

### Testing RBAC Policies Locally

```bash
# Impersonate a production service account to test RBAC
kubectl auth can-i create pods \
  --as=system:serviceaccount:socioprophet-prod:socioprophet-workload \
  --namespace=socioprophet-prod

# Test a federated ClusterRole
kubectl auth can-i list secrets \
  --as=system:serviceaccount:external-secrets:external-secrets-sa \
  --all-namespaces
```

---

## Secret Management in KinD

No production secrets may be stored in or used by KinD clusters. This policy is enforced at two levels:

1. **Organizational**: Documented policy prohibiting production secret use in dev clusters.
2. **Technical**: The CI service account used to provision GitHub Actions KinD clusters has no access to production Vault paths.

### Dev Secret Patterns

| Secret Type | KinD Approach | Notes |
|---|---|---|
| Database credentials | Seeded from a test-data fixture; no real DB | Use `scripts/seed-test-secrets.sh` |
| OIDC client credentials | Stub OIDC provider (`dex` in-cluster) | See ci/dex-config.yaml |
| TLS certificates | Self-signed, generated at cluster bootstrap | Not trusted outside the cluster |
| Image pull secrets | CI-scoped registry token (read-only, 24h TTL) | Injected by GitHub Actions OIDC |
| API keys | Test keys with no real-world access | Defined in `test/fixtures/` |

### Injecting Test Secrets into KinD

```bash
# Create dev secrets from test fixtures (no real values)
kubectl create secret generic db-credentials \
  --from-literal=password="$(cat test/fixtures/db-password.txt)" \
  --namespace=socioprophet-prod

# Or use the dev setup script
make kind-setup-secrets
```

---

## Network Policy Enforcement in KinD

KinD uses Kindnet as its default CNI, which supports NetworkPolicy resources. The same default-deny baseline from [KUBERNETES-SECURITY.md](./KUBERNETES-SECURITY.md) must be applied to production-mirror namespaces in KinD.

### Enabling Calico in KinD for Full NetworkPolicy Testing

For tests that require full NetworkPolicy semantics (e.g., egress rules, CIDR-based policies), Kindnet can be replaced with Calico:

```yaml
# In kind-config.yaml
networking:
  disableDefaultCNI: true
```

```bash
# After cluster creation, install Calico
kubectl apply -f https://raw.githubusercontent.com/projectcalico/calico/v3.27.0/manifests/calico.yaml
```

### Policy Smoke Tests

The CI pipeline runs a suite of NetworkPolicy smoke tests after cluster provisioning:

```bash
# Run network policy tests
kubectl run test-pod --image=busybox --rm -it --restart=Never \
  --namespace=socioprophet-prod -- wget -qO- http://vault.vault.svc.cluster.local:8200/v1/sys/health

# Expected: connection refused (default-deny egress blocks this)
```

---

## CI/CD Integration: GitHub Actions KinD Provisioning

### Workflow Template

```yaml
# .github/workflows/kind-integration.yaml
name: Integration Tests (KinD)

on:
  pull_request:
    branches: [main, release/*]

jobs:
  integration-test:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      id-token: write  # For OIDC image pull

    steps:
      - uses: actions/checkout@v4

      - name: Authenticate to registry (OIDC)
        uses: docker/login-action@v3
        with:
          registry: registry.socioprophet.internal
          username: ${{ secrets.REGISTRY_USERNAME }}
          password: ${{ secrets.REGISTRY_TOKEN }}

      - name: Create KinD cluster
        uses: helm/kind-action@v1.10.0
        with:
          version: v0.22.0
          config: ci/kind-config.yaml
          cluster_name: socioprophet-ci-${{ github.run_id }}
          wait: 120s

      - name: Load FIPS node image
        run: |
          docker pull registry.socioprophet.internal/infra/kindest-node-fips:v1.29.2
          kind load docker-image \
            registry.socioprophet.internal/infra/kindest-node-fips:v1.29.2 \
            --name socioprophet-ci-${{ github.run_id }}

      - name: Apply baseline security policies
        run: |
          kubectl apply -f ci/network-policies/
          kubectl apply -f ci/pod-security-labels/
          kubectl apply -f ci/rbac/

      - name: Seed test secrets
        run: make kind-setup-secrets

      - name: Run integration tests
        run: make test-integration

      - name: Collect audit logs
        if: always()
        run: |
          CONTAINER=$(docker ps --filter "name=socioprophet-ci-${{ github.run_id }}-control-plane" --format "{{.ID}}")
          docker cp "${CONTAINER}:/var/log/kubernetes/audit.log" ./audit.log

      - name: Upload audit logs
        if: always()
        uses: actions/upload-artifact@v4
        with:
          name: audit-log-${{ github.run_id }}
          path: audit.log
          retention-days: 30
```

---

## Security Controls for CI Environments

### GitHub Actions Runner Hardening

- All CI runners are ephemeral GitHub-hosted runners (or equivalent self-hosted runners that are provisioned fresh per job and destroyed after).
- Runners are never reused between pull requests from different contributors.
- The runner's Docker daemon is configured to use the rootless mode where possible.

### Least-Privilege CI Tokens

| Token | Scope | TTL | Storage |
|---|---|---|---|
| Registry pull token | Read-only, `registry.socioprophet.internal` | 24 hours | GitHub Actions secret (rotated weekly) |
| Cosign signing key | N/A in CI (keyless via OIDC) | Per-job | GitHub OIDC token |
| KinD cluster kubeconfig | Local only, expires with cluster | Job duration | In-memory only |

### Supply Chain Security in CI

- All GitHub Actions are pinned to specific SHA digests, not tags or branches.
- The `actions/checkout`, `helm/kind-action`, and `docker/login-action` actions are vetted on a quarterly basis.
- SBOM generation runs as part of the CI pipeline (see [CONTAINER-RUNTIME-SECURITY.md](./CONTAINER-RUNTIME-SECURITY.md)).

---

## Ephemeral Cluster Cleanup Procedures

### Automatic Cleanup

KinD clusters created in CI are automatically deleted at the end of the GitHub Actions job, regardless of job outcome. The `kind-action` handles this via a post-job step.

### Manual Cleanup

If a CI job is cancelled mid-run or a cluster is left behind, run:

```bash
# List all kind clusters
kind get clusters

# Delete a specific stale cluster
kind delete cluster --name socioprophet-ci-<run-id>

# Delete all socioprophet-ci-* clusters
kind get clusters | grep "^socioprophet-ci-" | xargs -I{} kind delete cluster --name {}
```

### Cleanup Verification

A weekly scheduled workflow checks for stale KinD clusters on the CI runner pool:

```bash
# Run by .github/workflows/cleanup-stale-kind.yaml
kind get clusters | grep "^socioprophet-ci-" | while read cluster; do
  echo "Stale cluster found: ${cluster}" | tee -a stale-clusters.log
  kind delete cluster --name "${cluster}"
done
```

If stale clusters are found, an alert is sent to the `#platform-alerts` Slack channel, since this may indicate a job that failed to clean up properly.

### Data Retention for CI Artifacts

| Artifact | Retention Period | Storage |
|---|---|---|
| Audit logs from CI runs | 30 days | GitHub Actions artifacts |
| Test results | 30 days | GitHub Actions artifacts |
| Container images built in CI (untagged) | 7 days | Registry garbage collection |
| Integration test reports | 90 days | GitHub Actions artifacts |
