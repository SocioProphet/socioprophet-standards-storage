# Container Runtime Security Standards

## Rationale

The container runtime (Docker, containerd) is the lowest-level component of the orchestration stack that executes workload code. A compromised or misconfigured runtime can undermine all higher-level security controls. This standard defines the minimum security configuration for container runtimes used within the SocioProphet governance framework.

---

## Runtime Configuration

### TLS for Docker API

- The Docker daemon MUST NOT expose its API socket without TLS when the socket is accessible over a network interface.
- Docker daemon TLS MUST use TLS 1.3, with ECDSA-P256 or RSA-4096 server and client certificates.
- mTLS MUST be enforced for all Docker API connections: both server and client certificates are required.
- The Docker daemon socket (`/var/run/docker.sock`) MUST NOT be bind-mounted into workload containers except for privileged infrastructure tooling (e.g., KinD node setup); such mounts MUST be documented.

### Containerd Configuration

- containerd MUST be configured with `SystemdCgroup = true` to use cgroup v2 for resource isolation.
- containerd snapshotter MUST use `overlayfs` or `fuse-overlayfs`; VFS snapshotter MUST NOT be used in production.
- The containerd configuration file (`/etc/containerd/config.toml`) MUST be version-controlled and reviewed on every infrastructure change.

### Seccomp Profiles

- The `RuntimeDefault` seccomp profile MUST be applied to all containers as a baseline.
- Workloads with elevated system-call requirements MUST use a custom seccomp profile that adds only the specific syscalls required; `unconfined` MUST NOT be used.
- Custom seccomp profiles MUST be reviewed by the security team before deployment.

### AppArmor / SELinux

- Where the host OS supports AppArmor, container workloads MUST be confined with an AppArmor profile.
- Where the host OS uses SELinux, containers MUST be labelled with an appropriate SELinux context (`container_t` or stricter).
- Unconfined AppArmor or SELinux labels (`unconfined_u:unconfined_r:unconfined_t`) MUST NOT be used in production.

---

## Image Security

### Image Signing

- All images published by the SocioProphet organisation MUST be signed using `cosign` with ECDSA-P256 keys.
- Signing keys MUST be stored in Vault or a hardware security module (HSM).
- The public key for each signing key MUST be published to a transparency log (Rekor or equivalent).

### Image Verification Before Runtime

- Before pulling an image, the runtime MUST verify the image signature against the known public key.
- For Kubernetes environments, the `ImagePolicyWebhook` or Kyverno `VerifyImages` policy MUST perform this check at admission.
- For standalone Docker hosts, a `notary` or `cosign` verification step MUST be inserted in the deployment pipeline before the image is run.

### Signature Validation on Every Pull

- Signature validation MUST occur on every image pull, not only at initial deployment.
- Pull-time validation failures MUST block container start and generate an audit event.

### SBOM Generation

- A Software Bill of Materials (SBOM) in SPDX or CycloneDX format MUST be generated for every image and published alongside the image in the registry.
- SBOMs MUST be signed with the same key as the image.
- SBOMs MUST be stored for the same retention period as the image (minimum 7 years for release images).

---

## Container Build Security

### Dockerfile Security Scanning

- Dockerfiles MUST be scanned with `hadolint` or equivalent in the CI pipeline.
- `hadolint` warnings at severity `error` MUST block the build.
- Build pipelines MUST also run a full image vulnerability scan (Trivy or Grype) after the image is built.

### Multi-Stage Builds

- All production images MUST use multi-stage Dockerfile builds to minimise the final image layer size.
- Build-time dependencies (compilers, test tools) MUST NOT be present in the final image stage.

### No Secrets in Image Layers

- `ARG` and `ENV` instructions MUST NOT be used to pass secrets into image layers.
- Secrets required during the build MUST be passed via BuildKit secret mounts (`RUN --mount=type=secret`).
- Completed images MUST be scanned for embedded secrets with `trufflehog` or equivalent before publication.

### Base Image Pinning

- Base images MUST be pinned to a specific digest (e.g., `FROM debian:bookworm@sha256:<digest>`), not a mutable tag such as `latest` or `stable`.
- Pinned digests MUST be updated within 30 days of a new base image release that resolves a security advisory.
- A `Renovate` or `Dependabot` configuration MUST be in place to automate base image update proposals.

---

## Runtime Protection

### No Privileged Containers

- `--privileged=true` (or `securityContext.privileged: true`) MUST NOT be set for any production workload.
- Requests for privileged containers MUST be blocked by admission policy and generate an audit alert.

### Read-Only Root Filesystem

- All containers MUST use `readOnlyRootFilesystem: true` in their security context where the workload allows it.
- Workloads that require write access to the root filesystem MUST mount an explicit `emptyDir` or persistent volume for the writable paths and document the justification.

### No Host Network

- `hostNetwork: true` MUST NOT be set for any production workload.
- Host network access is permitted only for designated infrastructure DaemonSets (e.g., CNI plugin, node exporter) and MUST be approved by the security team.

### Resource Limits

- Every container MUST declare `resources.limits.cpu` and `resources.limits.memory`.
- Containers without resource limits MUST be blocked by admission policy (e.g., Kyverno or OPA Gatekeeper).
- Resource limits MUST be based on load-tested baselines; over-provisioning MUST NOT be used as a substitute for proper sizing.

### Dropped Capabilities

- Containers MUST drop all Linux capabilities (`capabilities.drop: ["ALL"]`) and add back only those that are explicitly documented as necessary.
- `CAP_SYS_ADMIN`, `CAP_NET_ADMIN`, and `CAP_SYS_PTRACE` MUST NOT be granted to application workloads.

---

## Registry Integration

### Private Registry Authentication

- Image pulls from private registries MUST use TLS 1.3.
- Registry credentials MUST be sourced from Vault and rotated on a 30-day cycle.
- Pull credentials MUST be scoped to read-only access; push credentials MUST be separate and restricted to CI pipelines.

### Image Scanning Per Pull

- A registry proxy or admission webhook MUST scan each image for vulnerabilities at pull time using Trivy, Grype, or equivalent.
- Images with Critical CVEs that have no mitigating control MUST be blocked.

### Artifact Attestation

- Build provenance attestations (SLSA provenance, in-toto attestations) MUST be generated for every image.
- Attestations MUST be signed and stored in the registry alongside the image.
- The supply chain level MUST be documented and SHOULD achieve SLSA Level 2 or higher.

---

## References

- NIST SP 800-53 Rev. 5: https://csrc.nist.gov/publications/detail/sp/800-53/rev-5
- cosign: https://docs.sigstore.dev/cosign/overview/
- Trivy: https://trivy.dev/
- hadolint: https://github.com/hadolint/hadolint
- SLSA Framework: https://slsa.dev/
- Docker Security: https://docs.docker.com/engine/security/
- containerd: https://containerd.io/docs/
