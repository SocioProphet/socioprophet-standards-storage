# Secrets Management Integration Standards

## Rationale

Secrets (credentials, API keys, certificates, encryption keys) are the primary target of attackers who have gained a foothold in the orchestration layer. Centralising secrets management in HashiCorp Vault provides a single authoritative store with fine-grained access control, dynamic secret generation, and an immutable audit trail. This standard defines the minimum configuration for Vault integration within the SocioProphet governance framework.

---

## Vault Deployment

### High-Availability Cluster

- Vault MUST be deployed in high-availability mode with a minimum of 3 nodes.
- The Raft integrated storage backend MUST be used; Consul storage backend MAY be used if Consul is already part of the infrastructure.
- Vault nodes MUST be distributed across at least 3 availability zones to survive a single zone failure.

### Encrypted Storage

- Vault's storage backend MUST use AES-256-GCM for encryption at rest.
- Auto-unseal MUST be configured using a cloud KMS (AWS KMS, GCP Cloud KMS, Azure Key Vault) or an HSM; manual unseal keys MUST only be used as a break-glass fallback.
- Auto-unseal credentials MUST be stored separately from Vault itself and rotated annually.

### TLS for All Vault Communication

- All Vault API endpoints MUST be served over TLS 1.3.
- mTLS MUST be enabled for Vault Agent-to-Vault-server communication.
- TLS certificates for Vault nodes MUST use ECDSA-P256 or RSA-4096 and MUST be rotated before expiry using an automated process.

### Audit Logging

- Vault audit logging MUST be enabled on all nodes using the `file` or `syslog` audit device.
- Audit logs MUST be forwarded to an external, immutable store within 60 seconds.
- Audit log retention MUST be: 90 days hot storage, 7 years archived.
- Vault MUST be configured to `fail_on_error = true` for the audit device so that Vault rejects requests when the audit log is unavailable rather than silently skipping audit entries.

---

## Kubernetes Integration

### JWT/OIDC Auth Method

- The Kubernetes JWT auth method MUST be enabled in Vault and configured with the Kubernetes API server's OIDC issuer URL.
- Each Kubernetes cluster MUST have its own auth mount path (e.g., `auth/k8s-prod-us-east-1`).
- JWT token reviewer binding MUST use a dedicated `ServiceAccount` with `TokenReview` permission only; this service account MUST NOT have any other permissions.

### Service Account to Vault Identity Mapping

- Vault roles MUST map a specific Kubernetes service account, namespace, and cluster to a Vault policy.
- Wildcard service account names or namespaces in Vault role definitions MUST NOT be used in production.
- Role TTLs MUST be set to a maximum of 1 hour for token-based access.

### Secret Projection into Pods

- The Vault Agent Injector MUST be used to inject secrets as files into pod filesystems via init and sidecar containers.
- The External Secrets Operator MAY be used as an alternative for teams that require Kubernetes `Secret` objects as the projection mechanism.
- Secrets MUST be mounted as files, not environment variables, to prevent inadvertent exposure in process lists or crash dumps.
- The injected file paths MUST be within a `tmpfs` mount (memory-backed) where the workload runtime supports it.

### Dynamic Secret Generation

- Databases MUST use Vault dynamic secrets (database secrets engine) rather than static credentials.
- Cloud credentials (AWS, GCP, Azure) MUST be generated dynamically via the respective Vault secrets engine.
- Dynamic secrets MUST have the shortest TTL that is operationally practical (maximum 1 hour for cloud credentials, maximum 24 hours for database credentials).

---

## Secret Rotation

### Automated Rotation

- All long-lived secrets (certificates, API keys, service account tokens) MUST be rotated on a maximum 30-day cycle.
- Rotation MUST be automated; manual rotation is only acceptable as a break-glass procedure.
- Vault's built-in rotation for database and cloud credentials MUST be used where available.

### Zero-Downtime Rotation

- Rotation MUST be zero-downtime using one of: dual-active credentials (old and new valid simultaneously during transition), rolling restarts with Vault Agent secret refresh, or Vault's `lease_renewable` mechanism.
- Rotation procedures MUST be tested in a non-production environment before being applied to production.

### Audit Logging of Rotations

- Every secret rotation event MUST be captured in the Vault audit log with: secret path, rotating principal, timestamp, and result.
- Rotation failures MUST generate a high-priority alert within 5 minutes.

### Emergency Rotation

- An emergency rotation runbook MUST be documented in the operations repository.
- Emergency rotation MUST be executable within 1 hour of a suspected secret compromise.
- Emergency rotation procedures MUST be tested annually.

---

## Backup and Recovery

### Encrypted Vault Backups

- Vault Raft snapshots MUST be taken automatically every 6 hours and stored encrypted.
- Snapshot encryption MUST use a key separate from the Vault unseal key.
- Snapshots MUST be stored in at least two geographically separate locations.

### Off-Site Backup Storage

- Backups MUST be stored in a cloud object store with server-side encryption and versioning enabled.
- Backup access MUST require MFA and MUST be logged in the central audit store.

### Quarterly Recovery Testing

- Vault recovery from snapshot MUST be tested quarterly in an isolated environment.
- Recovery tests MUST verify: all secret paths accessible, all auth methods functional, audit logging operational.
- Recovery test results MUST be documented and retained for 3 years.

### Disaster Recovery Plan

- A Vault disaster recovery plan MUST be maintained in the operations repository.
- The plan MUST cover: primary cluster failure, region failure, unseal key compromise, and certificate authority compromise.
- The plan MUST be reviewed annually and after any significant infrastructure change.

---

## Access Control

### RBAC for Vault Access

- Vault policies MUST follow the principle of least privilege; each policy MUST grant access only to the exact secret paths required.
- Human operator policies MUST be separate from machine/workload policies.
- Root token MUST be revoked after initial cluster setup; a break-glass root token MUST be generated only under dual-control procedures.

### Workload Identity Binding

- Each workload's Vault role MUST be bound to its Kubernetes service account, namespace, and cluster.
- Cross-workload secret access MUST NOT be achieved by sharing service account tokens.

### Audit Trail of Secret Access

- All secret read, write, list, and delete operations MUST be captured in the Vault audit log.
- Audit events MUST include: requesting identity, secret path, operation type, client IP, timestamp, and result.

### Quarterly Review of Vault Policies

- All Vault policies MUST be reviewed quarterly.
- Policies for workloads that have been decommissioned MUST be revoked within 30 days.
- Review results MUST be recorded as an immutable audit entry.

---

## References

- NIST SP 800-53 Rev. 5: https://csrc.nist.gov/publications/detail/sp/800-53/rev-5
- HashiCorp Vault Documentation: https://developer.hashicorp.com/vault/docs
- Vault Kubernetes Auth Method: https://developer.hashicorp.com/vault/docs/auth/kubernetes
- Vault Agent Injector: https://developer.hashicorp.com/vault/docs/platform/k8s/injector
- External Secrets Operator: https://external-secrets.io/
- Vault Database Secrets Engine: https://developer.hashicorp.com/vault/docs/secrets/databases
