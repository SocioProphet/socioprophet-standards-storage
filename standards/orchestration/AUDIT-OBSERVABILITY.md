# Orchestration Audit and Observability Standards

## Rationale

Comprehensive audit logging and observability are foundational to NIST 800-53 compliance and forensic readiness. This standard defines the minimum audit event coverage, observability stack requirements, and forensic readiness controls for all orchestration components within the SocioProphet governance framework. Requirements align with NIST SP 800-88 and NIST 800-53 AU-2, AU-12, CA-7, and SI-4 controls.

---

## Kubernetes API Audit Logging

### Scope

- All Kubernetes API calls MUST be logged; there are no exemptions for read operations on sensitive resources (secrets, configmaps, serviceaccounts).
- The following resource types MUST be audited at `RequestResponse` level: `secrets`, `configmaps`, `serviceaccounts`, `clusterrolebindings`, `rolebindings`, `pods/exec`, `pods/attach`, `pods/portforward`.
- All other resources MUST be audited at `Metadata` level as a minimum.

### Audit Policy Example

```yaml
apiVersion: audit.k8s.io/v1
kind: Policy
rules:
  - level: RequestResponse
    resources:
      - group: ""
        resources: ["secrets", "configmaps", "serviceaccounts"]
      - group: "rbac.authorization.k8s.io"
        resources: ["clusterrolebindings", "rolebindings"]
  - level: RequestResponse
    verbs: ["exec", "attach", "portforward"]
    resources:
      - group: ""
        resources: ["pods"]
  - level: Metadata
    omitStages:
      - "RequestReceived"
```

### Immutable External Storage

- Audit logs MUST be forwarded to an external store (e.g., S3 with Object Lock in `COMPLIANCE` mode, GCS with Bucket Lock, or a WORM-capable log management system) within 60 seconds of generation.
- Logs MUST NOT be stored exclusively in cluster-local volumes; a cluster compromise MUST NOT allow log deletion.

### Audit Event Fields

Every audit event MUST include:

| Field | Description |
|---|---|
| `user.username` | Identity of the requesting principal |
| `user.groups` | Group memberships |
| `sourceIPs` | Client IP address(es) |
| `verb` | API verb (get, list, create, update, patch, delete, exec, etc.) |
| `objectRef.resource` | Resource kind |
| `objectRef.namespace` | Resource namespace |
| `objectRef.name` | Resource name |
| `responseStatus.code` | HTTP status code |
| `requestReceivedTimestamp` | Wall-clock time of request receipt |
| `stageTimestamp` | Wall-clock time of audit stage |

### Retention

- Hot storage: 90 days, queryable.
- Archived storage: 7 years, accessible within 72 hours.

---

## Pod and Container Audit Events

### Container Lifecycle Events

- Container creation and termination events MUST be captured either via the Kubernetes API audit log (`pods` resource at `Metadata` level) or via a runtime security tool (Falco or equivalent).
- Container image pull events MUST be logged and include the image digest.

### Privilege Escalation Attempts

- Any attempt by a process inside a container to escalate privileges (e.g., `setuid`, `ptrace`, kernel module load) MUST be detected and logged by a runtime security tool.
- High-priority alerts MUST be generated within 5 minutes of detection.
- Falco MUST be deployed with the default ruleset and the SocioProphet custom rules (see `ops/falco/rules/`).

### Network Policy Violations

- Dropped network traffic (packets rejected by `NetworkPolicy`) MUST be logged by the CNI plugin.
- CNI drop logs MUST be forwarded to the central log store.

### Image Pull Events

- Every image pull MUST be logged with: image reference, digest, pull timestamp, node name, and namespace.
- Pulls of images that are not in the approved image registry MUST generate an alert.

---

## Observability Stack

### Metrics — Prometheus

- Prometheus MUST be deployed in all production clusters.
- Prometheus data retention MUST be at least 90 days (long-term storage via Thanos or Cortex is recommended for multi-cluster aggregation).
- Alerting rules MUST be defined for: API server availability, etcd latency, node disk pressure, pod crash loops, and Vault agent injection failures.

### Log Aggregation — Loki

- Loki (or a compatible log aggregation system) MUST be deployed to aggregate logs from all cluster components and workloads.
- Log retention MUST match audit log requirements: 90 days hot, 7 years archived.
- Logs MUST be indexed by: namespace, pod name, container name, log level, and timestamp.

### Distributed Tracing — Jaeger

- Jaeger (or a compatible distributed tracing system) MUST be deployed.
- All service-to-service requests within the service mesh MUST emit spans.
- Trace data MUST be retained for at least 30 days.

### Dashboards — Grafana

- Grafana MUST be deployed and pre-provisioned with dashboards for: Kubernetes cluster overview, workload resource utilisation, API server audit event volume, Vault secret access, and service mesh traffic.
- Dashboard access MUST be controlled by RBAC; read-only access for all platform engineers, edit access for platform architects only.

### Incident Response — AlertManager

- AlertManager MUST be deployed and configured with routing rules that direct alerts to the correct on-call channel (PagerDuty, OpsGenie, or equivalent).
- All critical security alerts (privilege escalation, policy violations, Vault audit failures) MUST have a maximum 5-minute response SLA during on-call hours.
- Alert silences MUST be approved by the on-call lead and MUST have an expiry time not exceeding 24 hours.

---

## Anomaly Detection

### Baseline Establishment

- Normal cluster activity baselines MUST be established within 30 days of a new cluster entering production.
- Baselines MUST cover: API call rates per verb/resource, network traffic volume per service pair, secret access frequency per workload.

### Alert Conditions

Alerts MUST fire for:
- API call rate for sensitive verbs (`exec`, `portforward`, `delete` on `secrets`) exceeds 5x the 7-day baseline.
- Authentication failures exceed 10 per minute for any principal.
- A new service account or role binding is created outside of the approved CI/CD pipeline.
- An image without a valid signature is admitted to a production namespace.
- Vault audit logging becomes unavailable.

### Automated Response

- A quarantine `AuthorizationPolicy` (deny-all) MUST be applicable as an automated response action.
- Automated quarantine MUST be triggered for: workloads with detected active exploit behaviour (runtime security alert), workloads whose service account token has been used from an unexpected IP.
- Automated quarantine events MUST create a ticket in the incident management system and page the on-call engineer.

---

## Forensic Readiness

### Cryptographic Signing of Audit Logs

- Audit log batches MUST be cryptographically signed using ECDSA-P256 before archival.
- Signatures MUST be stored alongside the log batches in the archive.
- Signature verification MUST be documented as part of the evidence preservation procedure.

### RFC 3161 Timestamps

- Audit log batches MUST be timestamped by an RFC 3161-compliant Time Stamping Authority (TSA) before archival.
- TSA certificates MUST be retained for the same period as the audit logs they timestamp.

### Hash Chain for Integrity Verification

- Audit log files MUST be chained using a cryptographic hash (SHA-256 minimum) where each file header includes the hash of the previous file.
- Hash chain verification MUST be tested quarterly as part of the DR test procedure.

### Evidence Preservation

- An evidence preservation procedure MUST be documented in the incident response runbook.
- The procedure MUST cover: how to collect a forensic snapshot of cluster state (pod descriptions, audit logs, network flow logs), how to verify log integrity (signature and hash chain), and the chain of custody documentation template.
- Evidence MUST be preserved in immutable storage for a minimum of 3 years after incident closure.

---

## References

- NIST SP 800-53 Rev. 5: https://csrc.nist.gov/publications/detail/sp/800-53/rev-5
- NIST SP 800-88 (Media Sanitization / Audit): https://csrc.nist.gov/publications/detail/sp/800-88
- RFC 3161 (Time-Stamp Protocol): https://tools.ietf.org/html/rfc3161
- Kubernetes Audit Logging: https://kubernetes.io/docs/tasks/debug/debug-cluster/audit/
- Falco Runtime Security: https://falco.org/
- Prometheus: https://prometheus.io/docs/
- Loki: https://grafana.com/oss/loki/
- Jaeger: https://www.jaegertracing.io/
- Grafana: https://grafana.com/
- Thanos: https://thanos.io/
