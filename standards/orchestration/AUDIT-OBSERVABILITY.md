# Audit Logging and Observability — SocioProphet Orchestration Layer

- Last updated: 2026-01-27
- Status: Active governance document
- Owner: Observability Engineering / Platform Security
- Applies to: All SocioProphet Kubernetes clusters and supporting infrastructure

---

## Table of Contents

1. [kube-apiserver Audit Policy](#kube-apiserver-audit-policy)
2. [Audit Sink Configuration](#audit-sink-configuration)
3. [Prometheus and Grafana Compliance Dashboards](#prometheus-and-grafana-compliance-dashboards)
4. [Alertmanager Rules for Security Events](#alertmanager-rules-for-security-events)
5. [Jaeger Distributed Tracing](#jaeger-distributed-tracing)
6. [OpenSearch Indexes for Audit Logs](#opensearch-indexes-for-audit-logs)
7. [Anomaly Detection Rules](#anomaly-detection-rules)
8. [Forensics Procedures](#forensics-procedures)
9. [Retention Policy](#retention-policy)
10. [SIEM Integration Patterns](#siem-integration-patterns)

---

## kube-apiserver Audit Policy

The full audit policy is defined in [KUBERNETES-SECURITY.md](./KUBERNETES-SECURITY.md). This section documents the rationale for stage and level choices and the enrichment pipeline.

### Audit Stages

| Stage | Description | Captured |
|---|---|---|
| `RequestReceived` | The request was received by the API server | No — omitted to reduce volume |
| `ResponseStarted` | Response headers sent; body not yet | No — captured only for watch operations |
| `ResponseComplete` | Full response sent | Yes — primary capture point |
| `Panic` | API server panic | Yes — always captured |

### Audit Levels by Resource Sensitivity

| Level | Resources | Rationale |
|---|---|---|
| `RequestResponse` | secrets, tokens, RBAC resources, admission webhook configs | Full request and response body; highest sensitivity |
| `Request` | pods (create/delete/patch), namespaces, persistent volumes | Request body only; response is large and lower value |
| `Metadata` | Everything else | Minimal log volume; captures who/what/when |
| `None` | System components (kube-proxy, scheduler) doing list/watch | Very high volume; no security value |

---

## Audit Sink Configuration

### Vector Pipeline

Audit logs from each kube-apiserver are collected by a Vector DaemonSet and forwarded to the central OpenSearch cluster.

```yaml
# vector-config.yaml (ConfigMap for Vector DaemonSet)
sources:
  kube_audit:
    type: file
    include:
      - /var/log/kubernetes/audit.log
    read_from: beginning
    ignore_older_secs: 3600

transforms:
  enrich_audit:
    type: remap
    inputs: [kube_audit]
    source: |
      . = parse_json!(.message)
      .cluster = "${CLUSTER_NAME}"
      .region = "${CLUSTER_REGION}"
      .environment = "${ENVIRONMENT}"
      .compliance_scope = "fips-140-2"
      .ingest_timestamp = now()
      # Compute SHA-256 integrity hash for tamper detection
      .integrity_hash = sha256(encode_json(.))

  filter_noise:
    type: filter
    inputs: [enrich_audit]
    condition: '.level != "None"'

sinks:
  opensearch_audit:
    type: elasticsearch
    inputs: [filter_noise]
    endpoint: https://opensearch.socioprophet.internal:9200
    index: "k8s-audit-%Y.%m.%d"
    bulk:
      action: index
    tls:
      enabled: true
      verify_certificate: true
      ca_file: /etc/vector/opensearch-ca.crt
      crt_file: /etc/vector/vector-client.crt
      key_file: /etc/vector/vector-client.key
    auth:
      strategy: basic
      user: "${OPENSEARCH_USER}"
      password: "${OPENSEARCH_PASSWORD}"
    batch:
      max_bytes: 10485760
      timeout_secs: 5
```

### Fluentd (Legacy Clusters)

For clusters not yet migrated to Vector, Fluentd with the `fluent-plugin-opensearch` plugin is used. The Fluentd configuration mirrors the enrichment and filtering logic above.

---

## Prometheus and Grafana Compliance Dashboards

### Compliance Dashboard Panels

The `SocioProphet - FIPS Compliance` Grafana dashboard (ID: `SP-FIPS-001`) includes:

| Panel | Metric | Description |
|---|---|---|
| mTLS Coverage % | `istio_requests_total{connection_security_policy="mutual_tls"}` / total | % of requests using mTLS |
| Unsigned Image Attempts | `kube_audit_total{verb="create",resource="pods",rejected_by="image-policy"}` | Attempts to deploy unsigned images |
| RBAC Policy Violations | `kube_audit_total{level="RequestResponse",username=~"system:anonymous"}` | Anonymous access attempts |
| Secret Access Rate | `kube_audit_total{resource="secrets",verb!~"list|watch"}` | Trend of secret reads/writes |
| Vault Token TTL Distribution | `vault_token_ttl_bucket` | Token lifetime compliance |
| Cert Expiry Forecast | `(x509_cert_expiry - time()) / 86400` | Days until certificate expiry |
| etcd Encryption Status | Custom probe (checks `encryption-config` hash) | Drift detection for encryption config |
| Pod Security Violations | `kube_pod_container_security_context_privileged` | Privileged containers running |

### Grafana Alert Rules

Grafana alerts are federated to Alertmanager. All compliance dashboard panels have corresponding alert rules with a 5-minute evaluation interval.

---

## Alertmanager Rules for Security Events

```yaml
groups:
  - name: security-events
    interval: 1m
    rules:
      - alert: AnonymousKubernetesAccess
        expr: |
          increase(apiserver_audit_event_total{user="system:anonymous"}[5m]) > 0
        labels:
          severity: critical
          team: security
        annotations:
          summary: "Anonymous access attempt on {{ $labels.cluster }}"
          runbook: "https://docs.socioprophet.internal/runbooks/anonymous-k8s-access"

      - alert: ClusterAdminBindingCreated
        expr: |
          increase(apiserver_audit_event_total{
            verb="create",
            objectRef_resource="clusterrolebindings",
            objectRef_name=~".*cluster-admin.*"
          }[5m]) > 0
        labels:
          severity: critical
          team: security
        annotations:
          summary: "cluster-admin binding created on {{ $labels.cluster }}"

      - alert: SecretMassRead
        expr: |
          increase(apiserver_audit_event_total{
            verb="get",
            objectRef_resource="secrets"
          }[5m]) > 100
        labels:
          severity: warning
          team: security
        annotations:
          summary: "High rate of secret reads: {{ $value }} in 5 min on {{ $labels.cluster }}"

      - alert: PrivilegeEscalationAttempt
        expr: |
          increase(apiserver_audit_event_total{
            verb="create",
            objectRef_resource="pods",
            annotations_authorization_k8s_io_decision="forbid"
          }[5m]) > 5
        labels:
          severity: warning
          team: security
        annotations:
          summary: "Multiple forbidden pod creation attempts on {{ $labels.cluster }}"

      - alert: VaultSealStatusCritical
        expr: vault_core_unsealed == 0
        for: 1m
        labels:
          severity: critical
          team: security
        annotations:
          summary: "Vault is sealed on {{ $labels.instance }}"

      - alert: AuditLogIngestionLag
        expr: |
          time() - vector_component_received_events_total{component_name="kube_audit"} > 120
        for: 5m
        labels:
          severity: warning
          team: observability
        annotations:
          summary: "Audit log ingestion lag > 2 minutes on {{ $labels.cluster }}"
```

---

## Jaeger Distributed Tracing

### Trace Correlation for Audit Events

Audit events emitted by the kube-apiserver include a `requestID` field. Istio and Linkerd traces include the same `x-request-id` header (propagated from the originating request). The audit pipeline adds this field as a trace tag, enabling cross-system correlation.

### Jaeger Configuration

```yaml
apiVersion: jaegertracing.io/v1
kind: Jaeger
metadata:
  name: socioprophet-tracing
  namespace: observability
spec:
  strategy: production
  storage:
    type: opensearch
    options:
      es.server-urls: https://opensearch.socioprophet.internal:9200
      es.index-prefix: jaeger
      es.tls.enabled: true
      es.tls.ca: /etc/ssl/certs/opensearch-ca.crt
  collector:
    maxReplicas: 5
    resources:
      requests:
        cpu: 100m
        memory: 128Mi
  sampling:
    options:
      default_strategy:
        type: probabilistic
        param: 0.01  # 1% sampling in production
      per_service_strategies:
        - service: kube-apiserver
          type: probabilistic
          param: 0.05  # 5% for API server (higher for audit correlation)
```

### Trace Retention

Traces are retained in OpenSearch for 90 days. Traces linked to security incidents (via incident ticket ID tag) are retained indefinitely in a separate index.

---

## OpenSearch Indexes for Audit Logs

### Index Template

```json
{
  "index_patterns": ["k8s-audit-*"],
  "template": {
    "settings": {
      "number_of_shards": 3,
      "number_of_replicas": 1,
      "index.lifecycle.name": "audit-log-policy",
      "index.lifecycle.rollover_alias": "k8s-audit",
      "codec": "best_compression"
    },
    "mappings": {
      "dynamic": false,
      "properties": {
        "@timestamp":         { "type": "date" },
        "level":              { "type": "keyword" },
        "verb":               { "type": "keyword" },
        "user.username":      { "type": "keyword" },
        "user.groups":        { "type": "keyword" },
        "sourceIPs":          { "type": "ip" },
        "objectRef.resource": { "type": "keyword" },
        "objectRef.namespace":{ "type": "keyword" },
        "objectRef.name":     { "type": "keyword" },
        "responseStatus.code":{ "type": "integer" },
        "requestReceivedTimestamp": { "type": "date" },
        "cluster":            { "type": "keyword" },
        "region":             { "type": "keyword" },
        "environment":        { "type": "keyword" },
        "integrity_hash":     { "type": "keyword", "index": false }
      }
    }
  }
}
```

### Index Lifecycle Policy (ILM)

```json
{
  "policy": {
    "phases": {
      "hot": {
        "min_age": "0ms",
        "actions": {
          "rollover": { "max_age": "1d", "max_size": "50gb" }
        }
      },
      "warm": {
        "min_age": "30d",
        "actions": {
          "forcemerge": { "max_num_segments": 1 },
          "shrink": { "number_of_shards": 1 }
        }
      },
      "cold": {
        "min_age": "90d",
        "actions": {
          "freeze": {}
        }
      },
      "delete": {
        "min_age": "2557d",
        "actions": {
          "delete": {}
        }
      }
    }
  }
}
```

The delete phase is set to 2557 days (≈ 7 years) to satisfy the 7-year minimum retention requirement.

---

## Anomaly Detection Rules

### Excess Privilege Detection

An OpenSearch anomaly detection job runs hourly on the audit log index, looking for:

- Service accounts reading secrets outside their expected namespaces.
- Users performing more than 3× their baseline `get secrets` rate in a 1-hour window.
- API calls from IP addresses not previously seen for a given service account.

```json
{
  "name": "excess-secret-reads",
  "description": "Detects unusual secret read volume per user",
  "time_field": "@timestamp",
  "indices": ["k8s-audit-*"],
  "feature_attributes": [
    {
      "feature_name": "secret_read_count",
      "feature_enabled": true,
      "aggregation_query": {
        "secret_reads": {
          "filter": {
            "bool": {
              "must": [
                { "term": { "objectRef.resource": "secrets" } },
                { "term": { "verb": "get" } }
              ]
            }
          }
        }
      }
    }
  ],
  "detection_interval": { "period": { "interval": 10, "unit": "Minutes" } },
  "window_delay": { "period": { "interval": 1, "unit": "Minutes" } }
}
```

### Unusual Access Pattern Rules

| Rule | Detection Method | Alert |
|---|---|---|
| Service account used from external IP | Audit log `sourceIPs` not in cluster CIDR | Critical |
| `exec` into production pod | `verb=create, resource=pods/exec` | Warning |
| New ClusterRoleBinding created | Audit log RBAC resources | Critical |
| Vault root token generation attempted | Vault audit log `sys/generate-root` | Critical |
| Image policy admission rejection spike | `>10 rejections in 5 minutes` | Warning |

---

## Forensics Procedures

### Evidence Collection

When a security incident is declared, the following evidence must be collected before any remediation that might alter logs:

```bash
# 1. Export audit logs for the incident time window from OpenSearch
curl -X POST "https://opensearch.socioprophet.internal:9200/k8s-audit-*/_search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": {
      "range": {
        "@timestamp": {
          "gte": "2026-01-27T00:00:00Z",
          "lte": "2026-01-27T23:59:59Z"
        }
      }
    },
    "size": 10000
  }' > incident-audit-$(date +%Y%m%d).json

# 2. Compute SHA-256 hash of the evidence file
sha256sum incident-audit-$(date +%Y%m%d).json > incident-audit-$(date +%Y%m%d).json.sha256

# 3. Sign the hash with the Vault Transit signing key
vault write transit/sign/audit-log-signing \
  hash_algorithm=sha2-256 \
  input=$(base64 < incident-audit-$(date +%Y%m%d).json.sha256) \
  > incident-audit-$(date +%Y%m%d).json.sig
```

### Evidence Packaging

All evidence must be packaged in a tamper-evident archive:

```bash
# Package evidence
tar czf incident-evidence-$(date +%Y%m%d)-${INCIDENT_ID}.tar.gz \
  incident-audit-*.json \
  incident-audit-*.sha256 \
  incident-audit-*.sig

# Upload to evidence store (write-once S3 bucket)
aws s3 cp \
  incident-evidence-$(date +%Y%m%d)-${INCIDENT_ID}.tar.gz \
  s3://socioprophet-incident-evidence/${INCIDENT_ID}/ \
  --sse aws:kms \
  --sse-kms-key-id arn:aws:kms:us-east-1:ACCOUNT:key/EVIDENCE-KEY-ID
```

The evidence S3 bucket is configured with Object Lock (GOVERNANCE mode, 7-year retention) to prevent deletion.

---

## Retention Policy

| Log Type | Minimum Retention | Storage Tier | Legal Hold |
|---|---|---|---|
| kube-apiserver audit logs | 7 years | Hot: 30d → Warm: 90d → Cold: remainder | Applicable for incidents |
| Vault audit logs | 7 years | Same tiering as above | Applicable for incidents |
| Service mesh access logs | 90 days | Hot: 7d → Warm: 90d → Delete | N/A |
| Prometheus metrics | 13 months | Prometheus TSDB (local) + Thanos remote | N/A |
| Jaeger traces | 90 days | OpenSearch jaeger-* indexes | 7 years if linked to incident |
| Container runtime logs | 30 days | Node-local (logrotate) + aggregated 30d | N/A |

---

## SIEM Integration Patterns

### Splunk Integration

For organizations requiring Splunk SIEM integration, the Vector pipeline can be configured with a secondary sink:

```yaml
sinks:
  splunk_hec:
    type: splunk_hec_logs
    inputs: [filter_noise]
    endpoint: https://splunk.socioprophet.internal:8088
    token: "${SPLUNK_HEC_TOKEN}"
    index: k8s_audit
    source: kube-apiserver
    sourcetype: _json
    tls:
      enabled: true
      verify_certificate: true
```

### Generic SIEM (CEF/LEEF)

For SIEM systems requiring Common Event Format (CEF):

```yaml
transforms:
  to_cef:
    type: remap
    inputs: [filter_noise]
    source: |
      .cef_header = "CEF:0|SocioProphet|Kubernetes|1.0|" +
        string!(.verb) + "-" + string!(.objectRef.resource) + "|" +
        string!(.verb) + " " + string!(.objectRef.resource) + "|" +
        if .responseStatus.code >= 400 { "8" } else { "3" } end + "|"
      .cef_extension = "src=" + join!(array!(.sourceIPs), ",") +
        " suser=" + string!(.user.username) +
        " outcome=" + string!(.responseStatus.code)
```
