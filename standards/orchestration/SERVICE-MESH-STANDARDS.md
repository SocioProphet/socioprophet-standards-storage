# Service Mesh Security Standards — Istio and Linkerd

- Last updated: 2026-01-27
- Status: Active governance document
- Owner: Platform Engineering / Platform Security
- Applies to: All SocioProphet production and staging service mesh deployments

---

## Table of Contents

1. [mTLS Enforcement](#mtls-enforcement)
2. [Authorization Policies](#authorization-policies)
3. [Certificate Management](#certificate-management)
4. [Traffic Observability](#traffic-observability)
5. [Canary Deployments and Traffic Management Security](#canary-deployments-and-traffic-management-security)
6. [Egress Control](#egress-control)
7. [Rate Limiting and Circuit Breaker Policies](#rate-limiting-and-circuit-breaker-policies)
8. [Ambient Mesh vs Sidecar Proxy](#ambient-mesh-vs-sidecar-proxy)
9. [Mesh Health Monitoring and Alerting](#mesh-health-monitoring-and-alerting)

---

## mTLS Enforcement

### Istio — PeerAuthentication STRICT Mode

All namespaces in the SocioProphet platform enforce STRICT mTLS via PeerAuthentication resources. Permissive mode is prohibited in production and staging. A global mesh-wide policy is set at the root, and per-namespace policies override it only to add restrictions, never to relax them.

```yaml
# Mesh-wide STRICT mTLS (applied in istio-system namespace)
apiVersion: security.istio.io/v1beta1
kind: PeerAuthentication
metadata:
  name: default
  namespace: istio-system
spec:
  mtls:
    mode: STRICT
---
# Per-namespace policy (same mode, explicit for auditability)
apiVersion: security.istio.io/v1beta1
kind: PeerAuthentication
metadata:
  name: default
  namespace: socioprophet-prod
spec:
  mtls:
    mode: STRICT
```

Istio's Envoy proxies use BoringSSL (FIPS-validated) for all TLS operations. The TLS cipher suite configuration in the mesh restricts to FIPS-approved suites via `EnvoyFilter`:

```yaml
apiVersion: networking.istio.io/v1alpha3
kind: EnvoyFilter
metadata:
  name: fips-cipher-suites
  namespace: istio-system
spec:
  configPatches:
    - applyTo: CLUSTER
      patch:
        operation: MERGE
        value:
          typed_extension_protocol_options:
            envoy.extensions.upstreams.http.v3.HttpProtocolOptions:
              tls_socket:
                common_tls_context:
                  tls_params:
                    tls_minimum_protocol_version: TLSv1_2
                    cipher_suites:
                      - ECDHE-ECDSA-AES256-GCM-SHA384
                      - ECDHE-RSA-AES256-GCM-SHA384
                      - ECDHE-ECDSA-AES128-GCM-SHA256
                      - ECDHE-RSA-AES128-GCM-SHA256
```

### Linkerd — Automatic mTLS

Linkerd applies mTLS automatically to all meshed pods via the `linkerd2-proxy` sidecar. No explicit PeerAuthentication resources are required. The proxy uses the `rustls` crate with the `ring` backend (FIPS build) for TLS operations.

```bash
# Verify mTLS is active for a pod
linkerd viz edges deployment/my-service -n socioprophet-prod

# Check the TLS status
linkerd viz tap deployment/my-service -n socioprophet-prod --output json | jq .tls_status
```

---

## Authorization Policies

### Istio AuthorizationPolicy

Every service in the `socioprophet-prod` and `socioprophet-staging` namespaces must have an explicit `AuthorizationPolicy`. A global deny-all policy is applied at the namespace level; individual service policies add allow rules.

```yaml
# Namespace-level deny-all
apiVersion: security.istio.io/v1beta1
kind: AuthorizationPolicy
metadata:
  name: deny-all
  namespace: socioprophet-prod
spec: {}
---
# Per-service allow policy
apiVersion: security.istio.io/v1beta1
kind: AuthorizationPolicy
metadata:
  name: allow-graph-service
  namespace: socioprophet-prod
spec:
  selector:
    matchLabels:
      app: graph-service
  action: ALLOW
  rules:
    - from:
        - source:
            principals:
              - "cluster.local/ns/socioprophet-prod/sa/api-gateway"
              - "cluster.local/ns/socioprophet-prod/sa/search-service"
      to:
        - operation:
            methods: [GET, POST]
            ports: ["8080"]
      when:
        - key: request.auth.claims[iss]
          values: ["https://auth.socioprophet.internal/oidc"]
```

### Linkerd Server and ServerAuthorization

```yaml
apiVersion: policy.linkerd.io/v1beta3
kind: Server
metadata:
  name: graph-service-server
  namespace: socioprophet-prod
spec:
  podSelector:
    matchLabels:
      app: graph-service
  port: 8080
  proxyProtocol: HTTP/2
---
apiVersion: policy.linkerd.io/v1beta3
kind: ServerAuthorization
metadata:
  name: graph-service-authz
  namespace: socioprophet-prod
spec:
  server:
    name: graph-service-server
  client:
    meshTLS:
      serviceAccounts:
        - name: api-gateway
        - name: search-service
```

---

## Certificate Management

### Istio CA and cert-manager Integration

The Istio control plane is configured to use an intermediate CA issued by cert-manager (which in turn uses the Vault PKI engine as the root CA). This replaces the default Istio self-signed CA.

```yaml
# cert-manager Certificate for Istio CA
apiVersion: cert-manager.io/v1
kind: Certificate
metadata:
  name: istiod-ca
  namespace: istio-system
spec:
  isCA: true
  secretName: istiod-ca-tls
  duration: 8760h  # 1 year
  renewBefore: 720h
  commonName: istiod.istio-system.svc
  keyAlgorithm: ecdsa
  keySize: 384
  usages: [cert sign, crl sign, server auth, client auth]
  issuerRef:
    name: vault-intermediate-issuer
    kind: ClusterIssuer
```

Workload certificates (SVIDs) issued by Istio CA have a maximum validity of 24 hours and are automatically rotated by the Envoy proxy.

### SPIFFE/SPIRE Integration

All service identities are expressed as SPIFFE IDs (`spiffe://socioprophet.internal/ns/<namespace>/sa/<serviceaccount>`). SPIRE is deployed as the authoritative SVID issuer; Istio is configured to use SPIRE as its upstream CA via the `ExternalCA` plugin.

```bash
# Verify SPIFFE identity for a running pod
istioctl proxy-config secret <pod-name>.<namespace> | grep CERTIFICATE

# Check SPIRE node attestation status
kubectl exec -n spire spire-server-0 -- /opt/spire/bin/spire-server agent list
```

---

## Traffic Observability

### Prometheus Metrics

Istio and Linkerd both expose Prometheus metrics for all service-to-service traffic. Key metrics monitored:

| Metric | Description | Alert Threshold |
|---|---|---|
| `istio_requests_total` | Total requests by source, destination, response code | 5xx rate > 1% for 5 min |
| `istio_request_duration_milliseconds` | Request latency histogram | p99 > 2s for 5 min |
| `linkerd_tcp_open_connections` | Active TCP connections | > 10,000 per pod |
| `linkerd_response_latency_ms` | Response latency | p99 > 2s for 5 min |
| `envoy_cluster_upstream_rq_retry` | Retry rate | > 5% of requests |

### Jaeger Distributed Tracing

All services must propagate the following trace headers: `x-request-id`, `x-b3-traceid`, `x-b3-spanid`, `x-b3-parentspanid`, `x-b3-sampled`. Sampling rate is 1% in production (100% for error traces).

```yaml
# Istio telemetry configuration
apiVersion: telemetry.istio.io/v1alpha1
kind: Telemetry
metadata:
  name: mesh-tracing
  namespace: istio-system
spec:
  tracing:
    - providers:
        - name: jaeger
      randomSamplingPercentage: 1.0
```

### Access Logs

Istio access logs are emitted in JSON format and forwarded to the OpenSearch audit pipeline (see [AUDIT-OBSERVABILITY.md](./AUDIT-OBSERVABILITY.md)).

---

## Canary Deployments and Traffic Management Security

Canary deployments use Istio `VirtualService` traffic splitting. Security requirements:

- Canary versions must pass all image signing and vulnerability scanning requirements before receiving any traffic.
- Traffic weights must start at ≤ 5% for new deployments.
- Canary deployments must not have elevated RBAC permissions compared to the stable version.
- A/B testing based on headers is permitted only with approved `RequestAuthentication` JWT validation.

```yaml
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: graph-service
  namespace: socioprophet-prod
spec:
  hosts: [graph-service]
  http:
    - match:
        - headers:
            x-canary:
              exact: "true"
      route:
        - destination:
            host: graph-service
            subset: canary
    - route:
        - destination:
            host: graph-service
            subset: stable
          weight: 95
        - destination:
            host: graph-service
            subset: canary
          weight: 5
```

---

## Egress Control

All egress to external services (outside the cluster) must go through an egress gateway. Direct pod-to-internet traffic is blocked by the default-deny NetworkPolicy.

```yaml
# ServiceEntry — only pre-approved external services
apiVersion: networking.istio.io/v1beta1
kind: ServiceEntry
metadata:
  name: external-auth-provider
  namespace: socioprophet-prod
spec:
  hosts:
    - auth.external-partner.com
  ports:
    - number: 443
      name: https
      protocol: HTTPS
  resolution: DNS
  location: MESH_EXTERNAL
---
# Route external traffic through egress gateway
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: external-auth-provider-egress
  namespace: socioprophet-prod
spec:
  hosts: [auth.external-partner.com]
  gateways:
    - mesh
    - istio-system/egress-gateway
  http:
    - route:
        - destination:
            host: istio-egressgateway.istio-system.svc.cluster.local
            port:
              number: 443
```

---

## Rate Limiting and Circuit Breaker Policies

### Envoy Rate Limiting

```yaml
apiVersion: networking.istio.io/v1alpha3
kind: EnvoyFilter
metadata:
  name: rate-limit-graph-service
  namespace: socioprophet-prod
spec:
  workloadSelector:
    labels:
      app: graph-service
  configPatches:
    - applyTo: HTTP_FILTER
      match:
        context: SIDECAR_INBOUND
      patch:
        operation: INSERT_BEFORE
        value:
          name: envoy.filters.http.local_ratelimit
          typed_config:
            "@type": type.googleapis.com/udpa.type.v1.TypedStruct
            value:
              stat_prefix: local_rate_limiter
              token_bucket:
                max_tokens: 1000
                tokens_per_fill: 1000
                fill_interval: 1s
```

### Circuit Breaker (DestinationRule)

```yaml
apiVersion: networking.istio.io/v1beta1
kind: DestinationRule
metadata:
  name: graph-service-circuit-breaker
  namespace: socioprophet-prod
spec:
  host: graph-service
  trafficPolicy:
    outlierDetection:
      consecutiveGatewayErrors: 5
      interval: 10s
      baseEjectionTime: 30s
      maxEjectionPercent: 50
    connectionPool:
      http:
        http1MaxPendingRequests: 100
        http2MaxRequests: 1000
```

---

## Ambient Mesh vs Sidecar Proxy

The SocioProphet platform currently uses sidecar proxy mode (Istio) and sidecar injection (Linkerd). Ambient mesh (Istio) is under evaluation for Q3 2026.

| Dimension | Sidecar | Ambient Mesh |
|---|---|---|
| FIPS status | Validated (BoringSSL Envoy) | Under assessment |
| mTLS enforcement | Per-pod Envoy | ztunnel (node-level) + waypoint |
| Resource overhead | ~50 MB + ~0.5 vCPU per pod | Lower per-pod; higher per-node |
| AuthorizationPolicy | L4 + L7 per pod | L4 in ztunnel; L7 requires waypoint |
| Recommendation | **Production: use sidecar** | Not approved for production until FIPS assessment complete |

---

## Mesh Health Monitoring and Alerting

```yaml
groups:
  - name: service-mesh
    rules:
      - alert: IstioHighErrorRate
        expr: |
          sum(rate(istio_requests_total{response_code=~"5.."}[5m])) by (destination_service)
          /
          sum(rate(istio_requests_total[5m])) by (destination_service) > 0.01
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High error rate on {{ $labels.destination_service }}"

      - alert: MtlsPolicyViolation
        expr: |
          sum(istio_requests_total{connection_security_policy="none"}) by (source_workload, destination_workload) > 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Plaintext traffic detected: {{ $labels.source_workload }} → {{ $labels.destination_workload }}"

      - alert: CertificateExpiryWarning
        expr: |
          (istio_agent_cert_expiry_seconds - time()) / 86400 < 7
        for: 1h
        labels:
          severity: warning
        annotations:
          summary: "Istio workload certificate expiring in < 7 days"
```
