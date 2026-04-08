# KinD Standards (Kubernetes in Docker)

## Rationale

KinD (Kubernetes in Docker) clusters are used for local development and ephemeral CI testing. Although KinD clusters run workloads that are not production, they MUST maintain a security baseline that mirrors production policies to ensure that security regressions are caught before they reach higher environments. This standard defines those requirements.

---

## Docker Image Security

### Base Images

- KinD node images MUST be sourced from the official KinD release registry (`kindest/node`) and pinned to a specific SHA digest.
- Custom images built on top of `kindest/node` MUST be scanned for vulnerabilities before use.
- Images with Critical CVEs MUST NOT be used in CI pipelines without a documented exception.

### Image Scanning

- All images pulled during KinD-based tests MUST be scanned with Trivy, Grype, or an equivalent tool as part of the CI pipeline step that precedes cluster creation.
- Scan results MUST be stored as CI artefacts and retained for 90 days.

### Docker Socket Access

- The Docker socket (`/var/run/docker.sock`) MUST NOT be mounted into workload containers during KinD testing, except for the KinD cluster-creation step itself.
- Any test that requires Docker socket access MUST document the justification and scope.

### Seccomp Profiles

- KinD node containers MUST run with the `RuntimeDefault` seccomp profile or a stricter custom profile.
- The seccomp profile MUST be specified in the KinD configuration file under `nodes[*].kubeadmConfigPatches`.

---

## KinD Cluster Configuration

### Audit Logging

- KinD clusters used in CI MUST enable Kubernetes API audit logging.
- Audit policy MUST be passed via `kubeadmConfigPatches` in the KinD configuration.
- Audit logs MUST be written to a host-mounted path so that they persist after cluster deletion and are captured as CI artefacts.

Example KinD configuration snippet:

```yaml
kind: Cluster
apiVersion: kind.x-k8s.io/v1alpha4
nodes:
  - role: control-plane
    kubeadmConfigPatches:
      - |
        kind: ClusterConfiguration
        apiServer:
          extraArgs:
            audit-log-path: /var/log/kubernetes/audit.log
            audit-policy-file: /etc/kubernetes/audit-policy.yaml
          extraVolumes:
            - name: audit-logs
              hostPath: /var/log/kubernetes
              mountPath: /var/log/kubernetes
              readOnly: false
              pathType: DirectoryOrCreate
```

### RBAC

- RBAC MUST be enabled (it is enabled by default in KinD; disabling it is prohibited).
- All test workloads MUST use dedicated `ServiceAccount` resources.
- The `default` service account MUST have `automountServiceAccountToken: false` set in all test namespaces.

### Pod Security Standards

- Test namespaces MUST be labelled with `pod-security.kubernetes.io/enforce: restricted` unless the test explicitly validates behaviour that requires a less restrictive profile, in which case the deviation MUST be documented.

### Network Policies

- Network policies MUST be enabled in KinD clusters by deploying a CNI plugin that supports `NetworkPolicy` (e.g., Calico or Kindnet with NetworkPolicy support).
- Default-deny `NetworkPolicy` resources MUST be applied to test namespaces to validate that production network policies work correctly.

---

## Secrets in Local Clusters

### No Real Secrets

- Real production credentials MUST NOT be used in KinD clusters.
- Test credentials MUST be synthetic (randomly generated, non-functional outside the test environment).
- CI pipelines MUST NOT pass real Vault tokens, cloud credentials, or signing keys into KinD clusters.

### Integration with External Secrets Provider

- If testing the External Secrets Operator or Vault Agent Injector, a test Vault instance (vault-dev-server or mock) MUST be used.
- Test Vault instances MUST NOT share namespaces, auth backends, or paths with production Vault.

### Credential Separation

- Test credentials MUST be clearly labelled with a `purpose: test` metadata annotation.
- CI pipeline environment variables that hold test credentials MUST be scoped to the job and MUST NOT be exported to child processes beyond the KinD cluster lifecycle.

---

## CI/CD Integration

### Ephemeral Clusters

- KinD clusters MUST be created at the start of each CI job and deleted at the end, regardless of test pass/fail status.
- Cluster names MUST include the CI run identifier to prevent collisions in parallel jobs.

### Automatic Cleanup

- The CI pipeline MUST include a `post` or `finally` step that runs `kind delete cluster --name <cluster-name>` unconditionally.
- If cleanup fails, the CI pipeline MUST report an error and alert the platform team.

### Audit Logs as CI Artefacts

- Audit log files from the host-mounted path MUST be collected and uploaded as CI artefacts before cluster deletion.
- Artefact retention MUST be at least 90 days.

### Test Isolation

- Each test suite MUST run in its own namespace with a unique name derived from the test run ID.
- Cross-namespace access between test suites MUST be prohibited by `NetworkPolicy` and RBAC.
- Shared cluster state (e.g., `ClusterRole` resources) MUST be cleaned up after each test suite.

---

## Local Development Guidelines

### Preferred Tool

- KinD is the preferred tool for local Kubernetes development; see [MINIKUBE-STANDARDS.md](MINIKUBE-STANDARDS.md) for developer-laptop-specific guidance.

### Mirror Production Policies

- Local KinD configurations SHOULD mirror production RBAC, `NetworkPolicy`, and pod security settings.
- Developers MUST test that their workloads pass the `restricted` pod security profile locally before submitting a pull request.

### Deviation Documentation

- Any deviation from production security settings in a local KinD cluster MUST be documented in the repository's `docs/local-dev-deviations.md` file with a justification.

---

## References

- KinD Documentation: https://kind.sigs.k8s.io/
- NIST SP 800-53 Rev. 5: https://csrc.nist.gov/publications/detail/sp/800-53/rev-5
- Kubernetes Pod Security Standards: https://kubernetes.io/docs/concepts/security/pod-security-standards/
- Trivy: https://trivy.dev/
- Calico Network Policies: https://docs.tigera.io/calico/latest/network-policy/
