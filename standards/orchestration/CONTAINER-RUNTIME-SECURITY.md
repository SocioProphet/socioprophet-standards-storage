# Container Runtime Security — Docker and containerd

- Last updated: 2026-01-27
- Status: Active governance document
- Owner: Platform Engineering / DevSecOps
- Applies to: All SocioProphet container images, registries, and runtime configurations

---

## Table of Contents

1. [Image Signing with Sigstore/Cosign](#image-signing-with-sigstoreecosign)
2. [Image Vulnerability Scanning](#image-vulnerability-scanning)
3. [Supply Chain Security and SBOM Generation](#supply-chain-security-and-sbom-generation)
4. [containerd Runtime Configuration](#containerd-runtime-configuration)
5. [OCI Image Specification Compliance](#oci-image-specification-compliance)
6. [Rootless Container Requirements](#rootless-container-requirements)
7. [Seccomp and AppArmor/SELinux Profiles](#seccomp-and-apparmorse-linux-profiles)
8. [Image Registry Authentication and Authorization](#image-registry-authentication-and-authorization)
9. [Base Image Selection Criteria](#base-image-selection-criteria)

---

## Image Signing with Sigstore/Cosign

All container images produced by SocioProphet CI pipelines must be signed using Cosign with ECDSA-P256 keys. Unsigned images are blocked from deployment to production and staging clusters by the admission webhook described in [KUBERNETES-SECURITY.md](./KUBERNETES-SECURITY.md).

### Signing Architecture

```
CI Pipeline
    │
    ├── Build image → push to registry.socioprophet.internal
    │
    ├── Generate SBOM (Syft) → attach to image
    │
    ├── Sign image (Cosign keyless via OIDC)
    │     ├── Transparency log: Rekor instance (socioprophet.internal)
    │     └── Certificate: Fulcio CA issues short-lived cert
    │
    └── Attest SBOM (cosign attest) → attach attestation
```

### Keyless Signing in CI (GitHub Actions OIDC)

```bash
# In GitHub Actions workflow
- name: Sign image with Cosign (keyless)
  env:
    COSIGN_EXPERIMENTAL: "1"
    SIGSTORE_REKOR_URL: https://rekor.socioprophet.internal
    SIGSTORE_FULCIO_URL: https://fulcio.socioprophet.internal
  run: |
    cosign sign \
      --rekor-url=https://rekor.socioprophet.internal \
      --fulcio-url=https://fulcio.socioprophet.internal \
      --oidc-issuer=https://token.actions.githubusercontent.com \
      registry.socioprophet.internal/services/${IMAGE_NAME}@${IMAGE_DIGEST}
```

The OIDC token issued by GitHub Actions is exchanged with the Fulcio CA for a short-lived ECDSA-P256 signing certificate. The certificate includes the repository URL and workflow identity as Subject Alternative Names, providing identity binding without long-lived key material.

### Signature Verification

```bash
# Verify a signature before deployment
cosign verify \
  --rekor-url=https://rekor.socioprophet.internal \
  --certificate-issuer=https://token.actions.githubusercontent.com \
  --certificate-identity-regexp="^https://github.com/SocioProphet/.*" \
  registry.socioprophet.internal/services/my-service:v1.2.3
```

### Key-Based Signing (for non-CI contexts)

For images built outside CI (e.g., emergency patches), a hardware-backed signing key stored in Vault Transit is used:

```bash
# Retrieve the public key for verification
vault read -field=public_key transit/keys/cosign-platform-signing-key > platform-signing.pub

# Sign with Vault-backed key (via vault-plugin-cosign or cosign KMS integration)
cosign sign \
  --key hashivault://transit/cosign-platform-signing-key \
  registry.socioprophet.internal/services/my-service@${DIGEST}
```

The Vault Transit signing key uses ECDSA-P256, consistent with the FIPS-approved algorithm requirements in [INDEX.md](./INDEX.md).

---

## Image Vulnerability Scanning

### Trivy Integration

Trivy is the primary vulnerability scanner for SocioProphet container images. It is run at three points:

1. **During CI** — blocks the build if CRITICAL CVEs are found without approved exceptions.
2. **At image promotion** — scanned again before images are promoted from `staging` tag to `release` tag.
3. **Continuously** — a scheduled scanner (Trivy Operator) scans all running images in production clusters daily.

```yaml
# Trivy scan in GitHub Actions
- name: Scan image with Trivy
  uses: aquasecurity/trivy-action@0.19.0
  with:
    image-ref: registry.socioprophet.internal/services/${{ env.IMAGE_NAME }}:${{ env.IMAGE_TAG }}
    format: sarif
    exit-code: 1
    severity: CRITICAL
    vuln-type: os,library
    scanners: vuln,secret,misconfig
    output: trivy-results.sarif
    ignore-unfixed: false
    trivyignores: .trivyignore

- name: Upload Trivy SARIF results
  uses: github/codeql-action/upload-sarif@v3
  with:
    sarif_file: trivy-results.sarif
```

### Grype Integration

Grype provides a second-opinion scan and is used for comparing results with Trivy, especially for OS package vulnerabilities on non-distroless images.

```bash
# Grype scan
grype registry.socioprophet.internal/services/my-service:v1.2.3 \
  --output sarif \
  --file grype-results.sarif \
  --fail-on critical
```

### Vulnerability Exception Policy

Exceptions to the no-CRITICAL-CVE policy are granted by the Platform Security Lead and documented in `security/exceptions.yaml`:

```yaml
# security/exceptions.yaml
exceptions:
  - cve: CVE-2025-12345
    image: services/legacy-connector
    reason: "Vendor patch not yet available; mitigated by network policy restricting egress"
    approved_by: platform-security-lead@socioprophet.io
    approved_date: 2026-01-15
    expires: 2026-04-15
    ticket: PLAT-9876
```

### Trivy Operator (Continuous Scanning)

```yaml
apiVersion: helm.cattle.io/v1
kind: HelmChart
metadata:
  name: trivy-operator
  namespace: trivy-system
spec:
  chart: trivy-operator
  repo: https://aquasecurity.github.io/helm-charts/
  targetNamespace: trivy-system
  valuesContent: |-
    trivy:
      ignoreUnfixed: false
      severity: HIGH,CRITICAL
    operator:
      scanJobTimeout: 5m
      vulnerabilityReportsPlugin: Trivy
      configAuditReportsPlugin: Trivy
    serviceMonitor:
      enabled: true
```

---

## Supply Chain Security and SBOM Generation

### SBOM Requirements

All container images published to `registry.socioprophet.internal` must have an SPDX-format SBOM attached as an OCI artifact. The SBOM must be generated from the build context at the time of the image build, not from the installed packages post-build.

### Syft Integration

```bash
# Generate SPDX JSON SBOM from an image
syft registry.socioprophet.internal/services/my-service:v1.2.3 \
  -o spdx-json \
  --file sbom-my-service-v1.2.3.spdx.json

# Attach SBOM as OCI artifact
cosign attach sbom \
  --sbom sbom-my-service-v1.2.3.spdx.json \
  --type spdx \
  registry.socioprophet.internal/services/my-service:v1.2.3

# Attest the SBOM (links attestation to signature)
cosign attest \
  --predicate sbom-my-service-v1.2.3.spdx.json \
  --type spdxjson \
  --key hashivault://transit/cosign-platform-signing-key \
  registry.socioprophet.internal/services/my-service:v1.2.3
```

### SBOM Verification

```bash
# Verify attestation and retrieve SBOM
cosign verify-attestation \
  --type spdxjson \
  --key hashivault://transit/cosign-platform-signing-key \
  registry.socioprophet.internal/services/my-service:v1.2.3 | \
  jq -r .payload | base64 -d | jq .predicate
```

### SLSA Provenance

For critical platform components, SLSA Level 3 provenance attestations are generated using `slsa-github-generator`. The provenance attests to the build inputs (source digest, CI workflow) and is stored alongside the image signature in Rekor.

---

## containerd Runtime Configuration

### /etc/containerd/config.toml

```toml
version = 2

[plugins."io.containerd.grpc.v1.cri"]
  # Disable privileged containers at runtime level (defense-in-depth)
  [plugins."io.containerd.grpc.v1.cri".containerd]
    default_runtime_name = "runc"
    snapshotter = "overlayfs"

    [plugins."io.containerd.grpc.v1.cri".containerd.runtimes.runc]
      runtime_type = "io.containerd.runc.v2"
      [plugins."io.containerd.grpc.v1.cri".containerd.runtimes.runc.options]
        SystemdCgroup = true
        # Use default seccomp profile
        SeccompProfile = "/etc/containerd/seccomp-default.json"

  [plugins."io.containerd.grpc.v1.cri".registry]
    [plugins."io.containerd.grpc.v1.cri".registry.mirrors]
      [plugins."io.containerd.grpc.v1.cri".registry.mirrors."docker.io"]
        endpoint = ["https://registry.socioprophet.internal/proxy/dockerhub"]
      [plugins."io.containerd.grpc.v1.cri".registry.mirrors."ghcr.io"]
        endpoint = ["https://registry.socioprophet.internal/proxy/ghcr"]
    [plugins."io.containerd.grpc.v1.cri".registry.configs]
      [plugins."io.containerd.grpc.v1.cri".registry.configs."registry.socioprophet.internal".tls]
        ca_file = "/etc/containerd/registry-ca.crt"

[plugins."io.containerd.internal.v1.opt"]
  path = "/opt/containerd"
```

### Snapshotter Configuration

The `overlayfs` snapshotter is used in production. The `devmapper` snapshotter is available for workloads requiring strong isolation guarantees. The `native` snapshotter is not permitted in production (does not support overlayfs security features).

---

## OCI Image Specification Compliance

All SocioProphet images must comply with the OCI Image Specification v1.1.0. Required annotations:

```json
{
  "org.opencontainers.image.created": "2026-01-27T00:00:00Z",
  "org.opencontainers.image.authors": "platform@socioprophet.io",
  "org.opencontainers.image.url": "https://github.com/SocioProphet/<repo>",
  "org.opencontainers.image.source": "https://github.com/SocioProphet/<repo>",
  "org.opencontainers.image.version": "<semver>",
  "org.opencontainers.image.revision": "<git-sha>",
  "org.opencontainers.image.vendor": "SocioProphet",
  "org.opencontainers.image.licenses": "PROPRIETARY",
  "socioprophet.io/sbom-attached": "true",
  "socioprophet.io/signed": "true",
  "socioprophet.io/fips-compliant": "true"
}
```

Images that are missing `socioprophet.io/fips-compliant: "true"` are rejected at admission.

---

## Rootless Container Requirements

All production SocioProphet containers must run as non-root. This is enforced at three layers:

1. **Dockerfile**: `USER nonroot:nonroot` (or equivalent UID ≥ 1000) as the final user directive.
2. **Pod Security Standards**: `runAsNonRoot: true` enforced by the Restricted profile.
3. **Admission webhook**: Kyverno policy rejects Pods with `runAsUser: 0` or missing `runAsNonRoot: true`.

### Dockerfile Pattern

```dockerfile
FROM gcr.io/distroless/static-debian12:nonroot AS runtime

# All application files are owned by nonroot
COPY --chown=nonroot:nonroot --from=builder /app/binary /app/binary

USER nonroot:nonroot
EXPOSE 8080
ENTRYPOINT ["/app/binary"]
```

### containerd Rootless Mode

For CI environments, containerd can be run in rootless mode on the host. This adds a defense-in-depth layer: a container escape would only gain the privileges of the host user running containerd, not root.

---

## Seccomp and AppArmor/SELinux Profiles

### Default Seccomp Profile

The containerd default seccomp profile (`/etc/containerd/seccomp-default.json`) is based on the Docker/Moby default profile with the following additional restrictions:

- `ptrace` is blocked.
- `personality` is blocked (prevents 32-bit mode).
- `keyctl`, `add_key`, `request_key` are blocked (kernel keyring access).
- `bpf` is blocked unless explicitly allowed.

### Custom Seccomp Profiles

Services that require additional syscalls must declare a custom seccomp profile as a Kubernetes `SeccompProfile`:

```yaml
securityContext:
  seccompProfile:
    type: Localhost
    localhostProfile: profiles/my-service-seccomp.json
```

Custom profiles are stored in `standards/orchestration/seccomp-profiles/` and reviewed by Platform Security before deployment.

### AppArmor

AppArmor profiles are applied to all containerd containers on nodes where AppArmor is available (Ubuntu/Debian-based nodes). The default profile is `runtime/default`. Services requiring additional restrictions use a service-specific profile in `/etc/apparmor.d/socioprophet.d/`.

### SELinux

On RHEL/CentOS nodes, SELinux is enforced in `Enforcing` mode. containerd sets the SELinux label `container_t` on all container processes. The Vault agent sidecar uses `svirt_sandbox_file_t` for its tmpfs mounts.

---

## Image Registry Authentication and Authorization

### Registry Architecture

```
registry.socioprophet.internal (Harbor)
  ├── services/          — production service images
  ├── infra/             — infrastructure images (kindest-node, minikube ISO, etc.)
  ├── proxy/dockerhub/   — Docker Hub pull-through cache
  ├── proxy/ghcr/        — GitHub Container Registry pull-through cache
  └── dev/               — developer scratch images (auto-expired after 7 days)
```

### Authentication Methods

| Context | Method | TTL |
|---|---|---|
| CI (GitHub Actions) | OIDC token exchange (Harbor OIDC) | 1 hour |
| Production nodes | Robot account (read-only, per-cluster) | 365 days (rotated annually) |
| Developer machines | OIDC via `prophet-cli auth registry-login` | 8 hours |
| Vault Agent | Robot account (read-only, for image pull only) | 365 days |

### Authorization Matrix

| Role | `services/` | `infra/` | `dev/` | `proxy/` |
|---|---|---|---|---|
| CI build pipeline | push, pull | — | push, pull | — |
| Production kubelet | pull | pull | — | pull |
| Developer | pull | pull | push, pull | pull |
| Security scanner | pull | pull | pull | pull |

### Image Pull Secret Injection

Production nodes authenticate to the registry using a registry pull secret injected by Vault Agent:

```yaml
apiVersion: v1
kind: Pod
spec:
  imagePullSecrets:
    - name: registry-pull-secret
  # registry-pull-secret is an ExternalSecret synced from Vault
```

---

## Base Image Selection Criteria

### Approved Base Images

| Image | Use Case | Size | Notes |
|---|---|---|---|
| `gcr.io/distroless/static-debian12:nonroot` | Go static binaries | ~2 MB | Preferred for Go services |
| `gcr.io/distroless/base-debian12:nonroot` | Go/Rust with glibc deps | ~20 MB | When glibc is required |
| `registry.access.redhat.com/ubi9/ubi-minimal` | RPM-based; compliance-heavy workloads | ~90 MB | Use when UBI FIPS certification is required |
| `registry.access.redhat.com/ubi9/ubi-micro` | Minimal RPM base | ~30 MB | For scripts/tools |
| `python:3.12-slim-bookworm` | Python services | ~120 MB | Pinned to SHA digest |
| `node:20-bookworm-slim` | Node.js services | ~200 MB | Pinned to SHA digest |

### Prohibited Base Images

| Image | Reason |
|---|---|
| `ubuntu:latest` (or any `:latest` tag) | Unpinned; security regressions uncontrolled |
| `alpine` | musl libc; some FIPS-validated binaries not compatible |
| `scratch` | Unless using statically compiled Go with CGO_ENABLED=0 and verified FIPS module inclusion |
| Any image from Docker Hub without proxy cache | Direct Docker Hub pulls bypass our rate limiting and mirror |
| Any image older than 6 months without documented exception | Likely contains unpatched CVEs |

### Base Image Pinning

All `FROM` statements in Dockerfiles must pin to a SHA-256 digest, not a tag:

```dockerfile
# Correct: pinned to digest
FROM gcr.io/distroless/static-debian12@sha256:3f2b64ef7...

# Incorrect: tag only (prohibited)
FROM gcr.io/distroless/static-debian12:nonroot
```

The `prophet-cli` tool provides `prophet-cli image pin-digests --dockerfile Dockerfile` to automate digest pinning.
