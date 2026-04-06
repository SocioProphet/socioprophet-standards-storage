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
