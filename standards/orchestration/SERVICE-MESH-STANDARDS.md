# Service Mesh Standards

## Rationale

A service mesh (Istio or Linkerd) provides automatic mutual TLS (mTLS) between workloads, fine-grained traffic policies, and a unified observability layer. This standard defines the minimum configuration required for any service mesh deployed within the SocioProphet governance framework to satisfy NIST 800-53 SC-8 (Transmission Confidentiality), AC-3 (Access Enforcement), and AU-2/AU-12 (Audit) controls.

---

## mTLS Enforcement

### Mandatory Mutual TLS

- mTLS MUST be enforced for all pod-to-pod communication within the mesh.
- For Istio, a `PeerAuthentication` resource MUST be applied at the mesh level:

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

- For Linkerd, the default automatic mTLS MUST not be disabled; the `--set global.controllerLogLevel` MUST be set to `warn` or higher to avoid log noise without reducing security.
- `PERMISSIVE` mode MUST NOT be used in production namespaces; it is acceptable only during a time-bounded migration window with a documented end date.

### Certificate Automation

- Certificate issuance and rotation MUST be managed by cert-manager integrated with the cluster's CA (Vault PKI secrets engine or an external CA).
- Certificate issuance latency MUST be monitored; failures MUST alert within 5 minutes.
- The cert-manager `ClusterIssuer` MUST be configured with ECDSA-P256 or RSA-4096 keys.

### Certificate Rotation

- Workload certificates MUST rotate on a maximum 30-day cycle.
- Certificate rotation MUST be zero-downtime (the mesh control plane handles rotation transparently).
- CA root certificate rotation MUST be planned and tested before the CA certificate expires; the CA MUST have a minimum 1-year validity.

### Minimum Key Strength

- ECDSA-P256 is the preferred algorithm.
- RSA-4096 is acceptable where ECDSA is not supported.
- RSA-2048 MUST NOT be used for new certificate issuance.

---

## Traffic Policies

### Virtual Services

- Traffic routing MUST be expressed as Istio `VirtualService` or equivalent Linkerd `TrafficSplit` resources.
- Direct pod IP routing MUST NOT bypass the service mesh for mesh-managed namespaces.

### Destination Rules

- Istio `DestinationRule` resources MUST specify a `trafficPolicy.tls.mode` of `ISTIO_MUTUAL` for all traffic destined to mesh-managed services.
- Load balancing algorithm MUST be declared; `ROUND_ROBIN` is the default and is acceptable.

### Traffic Mirroring for Canary Testing

- Traffic mirroring (shadowing) MAY be used for canary validation.
- Mirrored traffic MUST NOT reach external dependencies (databases, payment systems) that have side effects.
- Mirroring configuration MUST be removed within 7 days of completing the canary validation.

### Circuit Breakers

- `DestinationRule` resources for critical backend services MUST include `outlierDetection` settings to implement circuit-breaking.
- Circuit-break events MUST be logged and surfaced as metrics in the observability stack.

---

## Authorization Policies

### Default Deny

- A default-deny `AuthorizationPolicy` MUST be applied at the mesh level or per namespace:

```yaml
apiVersion: security.istio.io/v1beta1
kind: AuthorizationPolicy
metadata:
  name: deny-all
  namespace: <namespace>
spec: {}
```

### Explicit Allow Rules

- For each service pair that requires communication, a separate `AuthorizationPolicy` MUST grant access using `source.principal` (SPIFFE identity) and specific `paths` and `methods`.
- Wildcard `source.principal` (`*`) MUST NOT be used in production `AuthorizationPolicy` resources.

### Service-to-Service Access Matrix

- An access matrix document MUST be maintained in `docs/service-access-matrix.md` listing every permitted service-to-service communication path.
- The access matrix MUST be reviewed and updated whenever a new service is deployed or an existing service's API changes.
- The access matrix MUST be version-controlled and its history MUST be retained.

### Linkerd Authorization

- Linkerd `AuthorizationPolicy` and `MeshTLSAuthentication` resources MUST be used to enforce service-to-service access control.
- All allowed communication MUST reference named `MeshTLSAuthentication` objects rather than wildcard trust expressions.

---

## Observability

### Distributed Tracing

- The mesh MUST emit distributed traces to Jaeger or Zipkin.
- Trace sampling MUST be set to a value that captures sufficient data for anomaly detection without creating unacceptable performance overhead (default: 1% for high-traffic services, 100% for low-traffic critical paths).
- Trace IDs MUST be propagated across all service calls using standard B3 or W3C Trace Context headers.

### Metrics Collection

- Envoy (Istio) or Linkerd proxy metrics MUST be scraped by Prometheus.
- Minimum metrics to collect: `istio_requests_total`, `istio_request_duration_milliseconds`, `istio_tcp_connections_opened_total`, `istio_tcp_connections_closed_total`.
- Dashboards for these metrics MUST be deployed in Grafana and accessible to the platform operations team.

### Audit Logging of mTLS Connections

- The mesh access log MUST be enabled and forwarded to the central log store.
- Each access log entry MUST include: source principal (SPIFFE ID), destination service, HTTP method/path (for HTTP traffic), response code, and timestamp.

### Anomaly Detection

- Baseline normal traffic patterns for each service MUST be established within 30 days of mesh deployment.
- AlertManager rules MUST fire when: request error rate exceeds 5x the 7-day baseline, mTLS certificate errors occur, or `AuthorizationPolicy` deny events spike above threshold.
- Automated workload quarantine (add a deny-all `AuthorizationPolicy`) MUST be available as an incident response action.

---

## Sidecar Injection

### Automatic Injection

- Sidecar injection MUST be enabled for all production namespaces via the `istio-injection: enabled` label (Istio) or equivalent Linkerd annotation.
- Pods in injection-enabled namespaces MUST NOT use `sidecar.istio.io/inject: "false"` without security team approval.

### Resource Limits for Sidecar Proxies

- Envoy/Linkerd proxy sidecars MUST have `resources.limits` and `resources.requests` specified.
- Default limits MUST be set in the mesh control-plane configuration and reviewed quarterly.

### Sidecar Configuration Versioning

- The mesh control-plane version MUST be pinned and updated on a regular cadence (maximum 6 months behind the latest stable release).
- Sidecar proxy versions MUST be consistent within a cluster; version skew greater than one minor version MUST be resolved within 30 days.

---

## References

- NIST SP 800-53 Rev. 5: https://csrc.nist.gov/publications/detail/sp/800-53/rev-5
- Istio Security: https://istio.io/latest/docs/concepts/security/
- Linkerd Security: https://linkerd.io/2.13/features/automatic-mtls/
- cert-manager: https://cert-manager.io/docs/
- Jaeger Tracing: https://www.jaegertracing.io/
- SPIFFE/SPIRE: https://spiffe.io/
