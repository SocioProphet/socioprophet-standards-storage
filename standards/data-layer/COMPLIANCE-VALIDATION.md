# Compliance Validation — Data Layer FIPS 140-2/140-3 Standard

- Last updated: 2026-01-27
- Status: Active governance document
- Owner: DevSecOps Team + Security Engineering
- Standard references: FIPS 140-2, FIPS 140-3, NIST SP 800-53 CA-7, CA-8, SA-11

---

## Table of Contents

1. [Overview](#overview)
2. [Automated Validation Scripts](#automated-validation-scripts)
3. [Encryption Verification Procedures](#encryption-verification-procedures)
4. [TLS Configuration Verification](#tls-configuration-verification)
5. [Audit Log Completeness Checks](#audit-log-completeness-checks)
6. [Access Control Review Procedures](#access-control-review-procedures)
7. [CI/CD Integration](#cicd-integration)
8. [Manual Audit Procedures](#manual-audit-procedures)
9. [Evidence Collection for FIPS Certification](#evidence-collection-for-fips-certification)
10. [Compliance Reporting Format](#compliance-reporting-format)
11. [Remediation Procedures](#remediation-procedures)

---

## Overview

Compliance validation provides systematic assurance that the data layer maintains its FIPS 140-2/140-3 posture continuously, not just at point-in-time audits. Validation is layered:

1. **Automated continuous checks** — run every 15 minutes in CI/CD and as Kubernetes CronJobs; results feed the INTEGRATION-CHECKLIST.md status.
2. **Scheduled automated scans** — comprehensive checks run nightly; results archived in OpenSearch.
3. **Quarterly manual audits** — human-led reviews of access grants, key rotation evidence, and backup restore verification.
4. **Annual external assessment** — third-party FIPS compliance audit; evidence package compiled from all layers above.

### Validation Architecture

```
                 ┌─────────────────────────────────────────────┐
                 │         Validation Orchestrator              │
                 │   (Kubernetes CronJob / GitHub Actions)      │
                 └──────────────────┬──────────────────────────┘
                                    │
           ┌────────────────────────┼────────────────────────┐
           ▼                        ▼                        ▼
   ┌───────────────┐      ┌───────────────────┐    ┌──────────────────┐
   │  Per-System   │      │  TLS/Certificate  │    │  Audit Log       │
   │  Encryption   │      │  Verification     │    │  Completeness    │
   │  Checker      │      │  Suite            │    │  Checker         │
   └───────┬───────┘      └────────┬──────────┘    └──────────┬───────┘
           │                       │                           │
           └───────────────────────┼───────────────────────────┘
                                   ▼
                    ┌──────────────────────────────┐
                    │   OpenSearch Compliance       │
                    │   Dashboard + Alerting        │
                    └──────────────────────────────┘
```

---

## Automated Validation Scripts

### Master Validation Runner

```python
#!/usr/bin/env python3
"""
data_layer_compliance_check.py — master compliance validation runner.
Run as: python3 data_layer_compliance_check.py --output json --systems all
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from typing import Optional

from validators import (
    PostgreSQLValidator,
    MongoDBValidator,
    ElasticsearchValidator,
    RedisValidator,
    MinIOValidator,
    RocksDBValidator,
)

SYSTEMS = {
    "postgres":       PostgreSQLValidator,
    "mongodb":        MongoDBValidator,
    "elasticsearch":  ElasticsearchValidator,
    "redis":          RedisValidator,
    "minio":          MinIOValidator,
    "rocksdb":        RocksDBValidator,
}


def run_all(config: dict) -> dict:
    results = {
        "schema_version": "1.0",
        "run_id": datetime.now(timezone.utc).isoformat(),
        "overall_status": "PASS",
        "systems": {}
    }

    for name, ValidatorClass in SYSTEMS.items():
        if name not in config.get("enabled_systems", list(SYSTEMS.keys())):
            continue
        validator = ValidatorClass(config[name])
        system_result = validator.validate()
        results["systems"][name] = system_result

        if system_result["status"] != "PASS":
            results["overall_status"] = "FAIL"

    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="/etc/compliance/config.yaml")
    parser.add_argument("--output", choices=["json", "text"], default="text")
    parser.add_argument("--systems", default="all")
    args = parser.parse_args()

    import yaml
    with open(args.config) as f:
        config = yaml.safe_load(f)

    if args.systems != "all":
        config["enabled_systems"] = args.systems.split(",")

    results = run_all(config)

    if args.output == "json":
        print(json.dumps(results, indent=2))
    else:
        for system, result in results["systems"].items():
            status = "✅" if result["status"] == "PASS" else "❌"
            print(f"{status} {system}: {result['status']} "
                  f"({result['checks_passed']}/{result['checks_total']} checks passed)")

    sys.exit(0 if results["overall_status"] == "PASS" else 1)
```

### PostgreSQL Validator

```python
# validators/postgres.py
import psycopg2
import subprocess
from vault_client import VaultClient


class PostgreSQLValidator:
    def __init__(self, config: dict):
        self.host = config["host"]
        self.port = config.get("port", 5432)
        self.vault = VaultClient(config["vault"])
        self.checks_passed = 0
        self.checks_total = 0
        self.findings = []

    def _check(self, check_id: str, description: str, passed: bool,
               detail: str = "", severity: str = "HIGH") -> bool:
        self.checks_total += 1
        if passed:
            self.checks_passed += 1
        else:
            self.findings.append({
                "check_id": check_id,
                "description": description,
                "severity": severity,
                "detail": detail,
            })
        return passed

    def validate(self) -> dict:
        creds = self.vault.get_dynamic_creds("postgres/monitoring")
        conn = psycopg2.connect(
            host=self.host, port=self.port,
            dbname="socioprophet", user=creds["username"],
            password=creds["password"],
            sslmode="verify-full",
            sslrootcert="/etc/ssl/certs/internal-ca.crt",
        )
        cur = conn.cursor()

        # Check SCRAM-SHA-256
        cur.execute("SHOW password_encryption;")
        pw_enc = cur.fetchone()[0]
        self._check("PG-AC-01", "Password encryption is SCRAM-SHA-256",
                    pw_enc == "scram-sha-256",
                    detail=f"Current: {pw_enc}")

        # Check no MD5 users
        cur.execute("""
            SELECT COUNT(*) FROM pg_shadow
            WHERE passwd IS NOT NULL AND passwd NOT LIKE 'SCRAM-SHA-256$%%'
        """)
        md5_count = cur.fetchone()[0]
        self._check("PG-AC-02", "No MD5-hashed user passwords",
                    md5_count == 0,
                    detail=f"Found {md5_count} MD5 password(s)")

        # Check SSL
        cur.execute("SHOW ssl;")
        ssl_on = cur.fetchone()[0]
        self._check("PG-EIT-01", "SSL is enabled",
                    ssl_on == "on", detail=f"ssl = {ssl_on}")

        # Check TLS min version
        cur.execute("SHOW ssl_min_protocol_version;")
        tls_ver = cur.fetchone()[0]
        self._check("PG-EIT-02", "TLS minimum version is TLSv1.3",
                    tls_ver == "TLSv1.3", detail=f"ssl_min_protocol_version = {tls_ver}")

        # Check pgaudit
        cur.execute("SELECT COUNT(*) FROM pg_extension WHERE extname = 'pgaudit';")
        pgaudit = cur.fetchone()[0]
        self._check("PG-AL-01", "pgaudit extension is installed",
                    pgaudit == 1, detail="pgaudit not found in pg_extension")

        # Check no SUPERUSER service accounts
        cur.execute("""
            SELECT string_agg(usename, ', ')
            FROM pg_user
            WHERE usesuper = true AND usename NOT IN ('postgres', 'rds_superuser')
        """)
        supers = cur.fetchone()[0]
        self._check("PG-AC-05", "No unauthorized SUPERUSER accounts",
                    supers is None, detail=f"Unauthorized SUPERUSERs: {supers}")

        # Check RLS on multi-tenant tables
        cur.execute("""
            SELECT COUNT(*) FROM pg_class
            WHERE relname IN ('incidents', 'users', 'audit_records')
            AND relrowsecurity = true
        """)
        rls_count = cur.fetchone()[0]
        self._check("PG-AC-03", "Row-level security on multi-tenant tables",
                    rls_count == 3,
                    detail=f"Only {rls_count}/3 expected tables have RLS")

        cur.close()
        conn.close()

        status = "PASS" if not self.findings else "FAIL"
        return {
            "status": status,
            "checks_passed": self.checks_passed,
            "checks_total": self.checks_total,
            "findings": self.findings,
        }
```

### MongoDB Validator

```python
# validators/mongodb.py
from pymongo import MongoClient
import ssl


class MongoDBValidator:
    def __init__(self, config: dict):
        self.host = config["host"]
        self.port = config.get("port", 27017)
        self.vault = VaultClient(config["vault"])
        self.checks_passed = 0
        self.checks_total = 0
        self.findings = []

    def validate(self) -> dict:
        creds = self.vault.get_secret("mongodb/monitoring-agent")
        client = MongoClient(
            host=self.host, port=self.port,
            tls=True,
            tlsCAFile="/etc/ssl/certs/internal-ca.crt",
            tlsCertificateKeyFile="/etc/ssl/certs/monitoring-agent.pem",
            username=creds["username"],
            password=creds["password"],
            authMechanism="SCRAM-SHA-256",
        )
        db = client.admin

        # Check authorization enabled
        cmd_opts = db.command("getCmdLineOpts")
        security = cmd_opts.get("parsed", {}).get("security", {})
        self._check("MG-AC-01", "Authorization enabled",
                    security.get("authorization") == "enabled")

        # Check JavaScript disabled
        self._check("MG-H-02", "Server-side JavaScript disabled",
                    security.get("javascriptEnabled") == False,
                    detail="JavaScript is enabled — reduces attack surface when disabled")

        # Check TLS mode
        net = cmd_opts.get("parsed", {}).get("net", {}).get("tls", {})
        self._check("MG-EIT-01", "TLS mode is requireTLS",
                    net.get("mode") == "requireTLS",
                    detail=f"Current mode: {net.get('mode')}")

        # Check FIPS mode
        server_status = db.command("serverStatus")
        fips_enabled = server_status.get("security", {}).get("FIPSMode", False)
        self._check("MG-EIT-03", "FIPS mode enabled",
                    fips_enabled, detail="FIPS mode is not active")

        # Check no root role service accounts
        result = list(db["system.users"].find(
            {"roles": {"$elemMatch": {"role": {"$in": ["root", "dbOwner", "userAdmin"]}}}}
        ))
        self._check("MG-AC-03", "No service accounts with dangerous built-in roles",
                    len(result) == 0,
                    detail=f"Users with dangerous roles: {[u['user'] for u in result]}")

        client.close()
        return {
            "status": "PASS" if not self.findings else "FAIL",
            "checks_passed": self.checks_passed,
            "checks_total": self.checks_total,
            "findings": self.findings,
        }

    def _check(self, check_id, description, passed, detail="", severity="HIGH"):
        self.checks_total += 1
        if passed:
            self.checks_passed += 1
        else:
            self.findings.append({
                "check_id": check_id,
                "description": description,
                "severity": severity,
                "detail": detail,
            })
        return passed
```

### Redis Validator

```bash
#!/bin/bash
# redis-compliance-check.sh

REDIS_HOST="redis.internal"
REDIS_PORT="6380"
CA_CERT="/etc/ssl/certs/internal-ca.crt"
CLIENT_CERT="/etc/ssl/certs/monitoring-agent.crt"
CLIENT_KEY="/etc/ssl/private/monitoring-agent.key"

redis_cmd() {
  redis-cli -h "${REDIS_HOST}" -p "${REDIS_PORT}" \
    --tls --cacert "${CA_CERT}" \
    --cert "${CLIENT_CERT}" --key "${CLIENT_KEY}" \
    "$@"
}

PASS=0
FAIL=0

check() {
  local id="$1" desc="$2" result="$3" expected="$4"
  if [ "${result}" = "${expected}" ]; then
    echo "✅ ${id}: ${desc}"
    PASS=$((PASS + 1))
  else
    echo "❌ ${id}: ${desc} — got '${result}', expected '${expected}'"
    FAIL=$((FAIL + 1))
  fi
}

# Check plain-text port is disabled
PORT=$(redis_cmd CONFIG GET port | tail -1)
check "RD-EIT-01" "Plain-text port disabled" "${PORT}" "0"

# Check protected-mode
PROTECTED=$(redis_cmd CONFIG GET protected-mode | tail -1)
check "RD-H-01" "Protected mode enabled" "${PROTECTED}" "yes"

# Check TLS port active
TLS_PORT=$(redis_cmd CONFIG GET tls-port | tail -1)
check "RD-EIT-02" "TLS port 6380 active" "${TLS_PORT}" "6380"

# Check ACL log enabled
ACL_LOG_MAX=$(redis_cmd CONFIG GET acllog-max-len | tail -1)
check "RD-AL-01" "ACL log max-len > 0" "$([[ ${ACL_LOG_MAX} -gt 0 ]] && echo yes || echo no)" "yes"

# Check default user is disabled
DEFAULT_USER=$(redis_cmd ACL LIST | grep "^user default" | grep " off ")
check "RD-AC-01" "Default user disabled" \
  "$([[ -n ${DEFAULT_USER} ]] && echo disabled || echo enabled)" "disabled"

# Check FLUSHALL is disabled (renamed to empty string)
FLUSH_RESULT=$(redis_cmd FLUSHALL 2>&1)
check "RD-AC-03" "FLUSHALL command disabled" \
  "$([[ "${FLUSH_RESULT}" == *"ERR"* ]] && echo disabled || echo enabled)" "disabled"

echo ""
echo "Redis compliance: ${PASS} passed, ${FAIL} failed"
[ "${FAIL}" -eq 0 ] && exit 0 || exit 1
```

---

## Encryption Verification Procedures

### Verify AES-256-GCM at Rest (Generic)

```bash
#!/bin/bash
# verify-encryption-at-rest.sh <system>
SYSTEM="$1"

case "${SYSTEM}" in
  postgres)
    # Verify LUKS on PostgreSQL data volume
    LUKS_STATUS=$(cryptsetup status /dev/mapper/pg_data_encrypted 2>&1)
    echo "${LUKS_STATUS}" | grep -q "cipher: aes-xts-plain64" && \
      echo "✅ PostgreSQL data volume: AES-XTS-256 LUKS confirmed" || \
      echo "❌ PostgreSQL data volume: LUKS cipher not confirmed"

    # Verify pg_tde key via Vault
    vault read transit/postgres-tde > /dev/null 2>&1 && \
      echo "✅ PostgreSQL TDE key accessible in Vault" || \
      echo "❌ PostgreSQL TDE key not accessible"
    ;;

  minio)
    # Verify SSE-KMS on all production buckets
    for bucket in socioprophet-artifacts socioprophet-restricted-data socioprophet-backups; do
      ENCRYPT_INFO=$(mc encrypt info myminio/${bucket} 2>&1)
      echo "${ENCRYPT_INFO}" | grep -q "SSE-KMS" && \
        echo "✅ MinIO bucket ${bucket}: SSE-KMS confirmed" || \
        echo "❌ MinIO bucket ${bucket}: SSE-KMS NOT configured"
    done
    ;;

  elasticsearch)
    FIPS_STATUS=$(curl -sk https://es.internal:9200/_nodes/settings \
      -u "monitoring:${ES_MONITORING_PASSWORD}" \
      | python3 -c "import sys,json; d=json.load(sys.stdin); \
        nodes=d['nodes']; \
        fips=[v['settings'].get('xpack',{}).get('security',{}).get('fips_mode',{}).get('enabled','false') \
              for v in nodes.values()]; \
        print('true' if all(f=='true' for f in fips) else 'false')")
    [ "${FIPS_STATUS}" = "true" ] && \
      echo "✅ Elasticsearch: FIPS mode enabled on all nodes" || \
      echo "❌ Elasticsearch: FIPS mode not enabled on all nodes"
    ;;
esac
```

---

## TLS Configuration Verification

### Comprehensive TLS Checker

```python
#!/usr/bin/env python3
"""tls_checker.py — verify TLS 1.3 configuration for all data layer endpoints."""

import ssl
import socket
from dataclasses import dataclass, field
from typing import List


@dataclass
class TLSCheckResult:
    host: str
    port: int
    protocol: str = ""
    cipher: str = ""
    cert_cn: str = ""
    cert_expiry: str = ""
    findings: List[str] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return len(self.findings) == 0


ENDPOINTS = [
    ("postgres.internal",       5432,  "starttls_postgres"),
    ("mongo.internal",          27017, "direct"),
    ("es.internal",             9200,  "direct"),
    ("redis.internal",          6380,  "direct"),
    ("minio.internal",          9000,  "direct"),
]

REQUIRED_PROTOCOL = "TLSv1.3"
APPROVED_CIPHERS = {"TLS_AES_256_GCM_SHA384", "TLS_CHACHA20_POLY1305_SHA256"}


def check_endpoint(host: str, port: int, mode: str) -> TLSCheckResult:
    result = TLSCheckResult(host=host, port=port)

    ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    ctx.minimum_version = ssl.TLSVersion.TLSv1_3
    ctx.maximum_version = ssl.TLSVersion.TLSv1_3
    ctx.load_verify_locations("/etc/ssl/certs/internal-ca.crt")
    ctx.load_cert_chain(
        "/etc/ssl/certs/monitoring-agent.crt",
        "/etc/ssl/private/monitoring-agent.key"
    )

    try:
        with socket.create_connection((host, port), timeout=10) as sock:
            with ctx.wrap_socket(sock, server_hostname=host) as ssock:
                result.protocol = ssock.version()
                result.cipher = ssock.cipher()[0]
                cert = ssock.getpeercert()
                result.cert_cn = cert.get("subject", [[("commonName", "unknown")]])[0][0][1]
                result.cert_expiry = cert.get("notAfter", "unknown")

        if result.protocol != REQUIRED_PROTOCOL:
            result.findings.append(
                f"Protocol {result.protocol} != required {REQUIRED_PROTOCOL}"
            )
        if result.cipher not in APPROVED_CIPHERS:
            result.findings.append(
                f"Cipher {result.cipher} not in approved set {APPROVED_CIPHERS}"
            )

    except ssl.SSLError as e:
        result.findings.append(f"TLS connection failed: {e}")

    return result


def main():
    all_passed = True
    for host, port, mode in ENDPOINTS:
        result = check_endpoint(host, port, mode)
        status = "✅" if result.passed else "❌"
        print(f"{status} {host}:{port} — {result.protocol} / {result.cipher}")
        for finding in result.findings:
            print(f"   ⚠️  {finding}")
        if not result.passed:
            all_passed = False

    return 0 if all_passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
```

---

## Audit Log Completeness Checks

```python
#!/usr/bin/env python3
"""audit_completeness_check.py — verify audit log coverage for each system."""

from opensearchpy import OpenSearch
from datetime import datetime, timedelta, timezone
import sys

client = OpenSearch(
    hosts=["https://opensearch.internal:9200"],
    http_auth=("audit-checker", OPENSEARCH_AUDIT_CHECKER_PASSWORD),
    use_ssl=True,
    verify_certs=True,
    ca_certs="/etc/ssl/certs/internal-ca.crt",
)

REQUIRED_EVENT_TYPES = {
    "postgres":       ["authenticate", "ddl", "connection", "role"],
    "mongodb":        ["authenticate", "authCheck", "createUser", "dropUser"],
    "elasticsearch":  ["AUTHENTICATION_SUCCESS", "ACCESS_DENIED", "SECURITY_CONFIG_CHANGE"],
    "redis":          ["auth_failure", "acl_denied"],
    "minio":          ["s3:ObjectCreated", "s3:ObjectRemoved"],
}

CHECK_WINDOW_HOURS = 24  # Check last 24 hours

def check_system_audit_coverage(system: str, event_types: list) -> dict:
    since = datetime.now(timezone.utc) - timedelta(hours=CHECK_WINDOW_HOURS)
    findings = []

    for event_type in event_types:
        result = client.count(
            index=f"{system}-audit-*",
            body={
                "query": {
                    "bool": {
                        "filter": [
                            {"term": {"system": system}},
                            {"wildcard": {"event_type": f"*{event_type}*"}},
                            {"range": {"timestamp": {"gte": since.isoformat()}}}
                        ]
                    }
                }
            }
        )
        count = result["count"]
        if count == 0:
            findings.append({
                "event_type": event_type,
                "count": count,
                "severity": "MEDIUM",
                "detail": f"No {event_type} events in last {CHECK_WINDOW_HOURS}h — possible logging gap"
            })

    return {
        "system": system,
        "status": "PASS" if not findings else "WARN",
        "findings": findings
    }


def main():
    all_passed = True
    for system, event_types in REQUIRED_EVENT_TYPES.items():
        result = check_system_audit_coverage(system, event_types)
        status = "✅" if result["status"] == "PASS" else "⚠️"
        print(f"{status} {system}: audit coverage {result['status']}")
        for f in result["findings"]:
            print(f"   ⚠️  Missing events: {f['event_type']} — {f['detail']}")
        if result["status"] != "PASS":
            all_passed = False

    return 0 if all_passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
```

---

## Access Control Review Procedures

### Quarterly Access Grant Review Script

```python
#!/usr/bin/env python3
"""quarterly_access_review.py — enumerate all grants and flag overprovisioned accounts."""

import psycopg2, json
from vault_client import VaultClient

vault = VaultClient()

def review_postgres_grants():
    creds = vault.get_dynamic_creds("postgres/auditor")
    conn = psycopg2.connect(host="postgres.internal", port=5432,
                            dbname="socioprophet",
                            user=creds["username"], password=creds["password"],
                            sslmode="verify-full",
                            sslrootcert="/etc/ssl/certs/internal-ca.crt")
    cur = conn.cursor()

    # Find all roles and their granted permissions
    cur.execute("""
        SELECT grantee, table_schema, table_name,
               array_agg(privilege_type ORDER BY privilege_type) AS privileges
        FROM information_schema.role_table_grants
        WHERE grantee NOT IN ('PUBLIC', 'postgres', 'pg_monitor', 'pg_read_all_stats')
        GROUP BY grantee, table_schema, table_name
        ORDER BY grantee, table_schema, table_name
    """)
    grants = cur.fetchall()

    # Flag suspicious broad grants
    for grantee, schema, table, privileges in grants:
        if set(privileges).issuperset({"SELECT", "INSERT", "UPDATE", "DELETE", "TRUNCATE"}):
            print(f"⚠️  REVIEW: {grantee} has broad DML on {schema}.{table}: {privileges}")
        else:
            print(f"   {grantee}: {schema}.{table} — {privileges}")

    # Find users with superuser
    cur.execute("SELECT usename FROM pg_user WHERE usesuper = true")
    supers = [r[0] for r in cur.fetchall()]
    print(f"\nSuperusers: {supers}")
    if len(supers) > 1 or (supers and supers[0] != "postgres"):
        print("⚠️  REVIEW: Unexpected superuser accounts found")

    cur.close()
    conn.close()


if __name__ == "__main__":
    review_postgres_grants()
```

---

## CI/CD Integration

### GitHub Actions Compliance Workflow

```yaml
# .github/workflows/data-layer-compliance.yml
name: Data Layer Compliance Validation

on:
  schedule:
    - cron: '*/15 * * * *'   # Every 15 minutes
  push:
    paths:
      - 'standards/data-layer/**'
      - 'ops/database/**'

jobs:
  tls-validation:
    name: TLS Configuration Validation
    runs-on: [self-hosted, compliance-runner]
    steps:
      - uses: actions/checkout@v4
      - name: Install dependencies
        run: pip install -r requirements-dev.txt
      - name: Run TLS checker
        run: |
          python3 tools/compliance/tls_checker.py \
            --output json \
            --report-path compliance-reports/tls-$(date +%Y%m%d-%H%M%S).json
      - name: Upload report
        uses: actions/upload-artifact@v4
        with:
          name: tls-compliance-report
          path: compliance-reports/tls-*.json

  encryption-validation:
    name: Encryption at Rest Validation
    runs-on: [self-hosted, compliance-runner]
    needs: []
    steps:
      - uses: actions/checkout@v4
      - name: Verify encryption at rest
        run: |
          bash tools/compliance/verify-encryption-at-rest.sh all \
            2>&1 | tee compliance-reports/encryption-$(date +%Y%m%d).log
      - name: Fail on any encryption gap
        run: |
          grep -c "❌" compliance-reports/encryption-*.log && exit 1 || exit 0

  audit-completeness:
    name: Audit Log Completeness
    runs-on: [self-hosted, compliance-runner]
    steps:
      - uses: actions/checkout@v4
      - name: Check audit log coverage
        run: |
          python3 tools/compliance/audit_completeness_check.py \
            --output json \
            --alert-on-warning
        env:
          OPENSEARCH_AUDIT_CHECKER_PASSWORD: ${{ secrets.OPENSEARCH_AUDIT_CHECKER_PASSWORD }}

  access-review:
    name: Access Grant Anomaly Detection
    runs-on: [self-hosted, compliance-runner]
    if: github.event_name == 'schedule' && (github.event.schedule == '0 0 * * *')  # Daily only
    steps:
      - uses: actions/checkout@v4
      - name: Run access grant review
        run: python3 tools/compliance/quarterly_access_review.py

  compliance-dashboard-update:
    name: Update Compliance Dashboard
    runs-on: [self-hosted, compliance-runner]
    needs: [tls-validation, encryption-validation, audit-completeness]
    if: always()
    steps:
      - name: Post results to OpenSearch compliance index
        run: |
          python3 tools/compliance/post_compliance_results.py \
            --run-id "${{ github.run_id }}" \
            --results compliance-reports/
```

### Kubernetes CronJob (for in-cluster checks)

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: data-layer-compliance
  namespace: compliance
spec:
  schedule: "*/15 * * * *"
  concurrencyPolicy: Forbid
  jobTemplate:
    spec:
      template:
        spec:
          serviceAccountName: compliance-checker
          restartPolicy: Never
          containers:
            - name: compliance-runner
              image: socioprophet/compliance-runner:latest
              command: ["python3", "/app/data_layer_compliance_check.py"]
              args: ["--output", "json", "--config", "/etc/compliance/config.yaml"]
              volumeMounts:
                - name: compliance-config
                  mountPath: /etc/compliance
                - name: ssl-certs
                  mountPath: /etc/ssl/certs
                  readOnly: true
              env:
                - name: VAULT_ADDR
                  value: https://vault.internal:8200
                - name: VAULT_ROLE
                  value: compliance-checker
          volumes:
            - name: compliance-config
              configMap:
                name: compliance-config
            - name: ssl-certs
              secret:
                secretName: compliance-tls-certs
```

---

## Manual Audit Procedures

### Quarterly Manual Audit Checklist

The following procedures must be executed by a qualified security engineer each quarter:

**Week 1 — Cryptographic Review**
- [ ] Verify all encryption key versions in Vault are ≤ 90 days old.
- [ ] Sample 10 backup archives; decrypt each to verify integrity and accessibility.
- [ ] Review TLS certificate expiry dates for all data layer services; confirm no certificate expires within 60 days.
- [ ] Verify that the FIPS-validated module list matches the deployed versions (compare against NIST CMVP certificate list).

**Week 2 — Access Control Review**
- [ ] Run `quarterly_access_review.py` and review all flagged grants.
- [ ] Review all service accounts created in the last 90 days; confirm documented business purpose.
- [ ] Verify that all expired temporary grants have been revoked.
- [ ] Review ACL configurations for Redis; confirm no unauthorized key-pattern access.
- [ ] Verify MFA is enforced for all operator accounts in all systems.

**Week 3 — Audit Log Review**
- [ ] Sample 100 random audit log records from each system; verify correct format and required fields.
- [ ] Run hash-chain verification on the last 1,000 records in each system's audit index.
- [ ] Verify Fluentd forwarding pipeline has no gaps (compare event counts against system uptime).
- [ ] Confirm audit log WORM policy is active on all archive buckets.

**Week 4 — Backup and Recovery Validation**
- [ ] Perform a test restore for at least one system (rotate through all six systems over six quarters).
- [ ] Document restore time against RTO target; escalate if over target.
- [ ] Verify all backup jobs completed successfully in the last 30 days.
- [ ] Update `INTEGRATION-CHECKLIST.md` with results and sign off.

---

## Evidence Collection for FIPS Certification

The following evidence artifacts must be collected and archived quarterly for the annual FIPS certification review:

| Evidence Type | Source | Collection Method | Archive Location |
|---|---|---|---|
| FIPS module versions | All systems | `openssl version -a`, `python3 -c "import ssl; print(ssl.OPENSSL_VERSION)"` | `audit-forensics/fips-modules-YYYYQN.json` |
| TLS configuration snapshots | All endpoints | `tls_checker.py --output json` | `audit-forensics/tls-config-YYYYQN.json` |
| Encryption key rotation log | Vault | `vault audit list` + key metadata | `audit-forensics/key-rotation-YYYYQN.json` |
| Access grant snapshot | All systems | `quarterly_access_review.py --output json` | `audit-forensics/access-grants-YYYYQN.json` |
| Audit log completeness report | OpenSearch | `audit_completeness_check.py --output json` | `audit-forensics/audit-coverage-YYYYQN.json` |
| Backup integrity verification | MinIO + per-system | HMAC check results | `audit-forensics/backup-integrity-YYYYQN.json` |
| Penetration test results | External auditor | PDF report + remediation tracker | `audit-forensics/pentest-YYYY.pdf` |
| INTEGRATION-CHECKLIST.md snapshot | This repo | `git show HEAD:standards/data-layer/INTEGRATION-CHECKLIST.md` | `audit-forensics/checklist-YYYYQN.md` |

```bash
#!/bin/bash
# collect-quarterly-evidence.sh YYYY QN (e.g., 2026 Q2)
YEAR="$1"
QUARTER="$2"
OUTPUT_DIR="standards/audit-forensics/evidence-${YEAR}${QUARTER}"
mkdir -p "${OUTPUT_DIR}"

# TLS evidence
python3 tools/compliance/tls_checker.py --output json \
  > "${OUTPUT_DIR}/tls-config.json"

# FIPS module evidence
python3 -c "import ssl, json; print(json.dumps({'openssl': ssl.OPENSSL_VERSION}))" \
  > "${OUTPUT_DIR}/fips-modules.json"

# Access grant snapshot
python3 tools/compliance/quarterly_access_review.py --output json \
  > "${OUTPUT_DIR}/access-grants.json"

# Checklist snapshot
git show HEAD:standards/data-layer/INTEGRATION-CHECKLIST.md \
  > "${OUTPUT_DIR}/integration-checklist.md"

# Archive to MinIO compliance store
mc cp -r "${OUTPUT_DIR}/" \
  "myminio/socioprophet-compliance-archive/evidence/${YEAR}${QUARTER}/"

echo "Evidence collected and archived: ${OUTPUT_DIR}"
```

---

## Compliance Reporting Format

The compliance report is a structured JSON document produced by the master validation runner and archived with each quarterly evidence package:

```json
{
  "schema_version": "1.0",
  "report_type": "quarterly_compliance",
  "period": { "year": 2026, "quarter": "Q2" },
  "generated_at": "2026-06-30T23:59:00Z",
  "generated_by": "compliance-runner@socioprophet-internal",
  "overall_status": "PARTIAL_COMPLIANCE",
  "summary": {
    "total_checks": 120,
    "checks_passed": 98,
    "checks_failed": 12,
    "checks_not_applicable": 10,
    "pass_rate_percent": 89.1
  },
  "systems": {
    "postgres":      { "status": "PARTIAL", "pass_rate": 85.7, "findings_count": 3 },
    "mongodb":       { "status": "PARTIAL", "pass_rate": 87.5, "findings_count": 3 },
    "elasticsearch": { "status": "PASS",    "pass_rate": 100.0, "findings_count": 0 },
    "redis":         { "status": "PARTIAL", "pass_rate": 75.0, "findings_count": 4 },
    "minio":         { "status": "PASS",    "pass_rate": 100.0, "findings_count": 0 },
    "rocksdb":       { "status": "FAIL",    "pass_rate": 20.0, "findings_count": 8 }
  },
  "critical_findings": [],
  "high_findings": [
    {
      "check_id": "RK-EAR-01",
      "system": "rocksdb",
      "description": "EncryptionProvider not initialized",
      "remediation_id": "REM-2026-042",
      "target_date": "2026-09-30"
    }
  ],
  "evidence_archive": "myminio/socioprophet-compliance-archive/evidence/2026Q2/"
}
```

---

## Remediation Procedures

### Finding Severity and Response Timeline

| Severity | Response SLA | Escalation Path |
|---|---|---|
| Critical (C) | 24 hours | Immediate CISO notification; emergency change |
| High (H) | 72 hours | Platform DBA Team lead + Security Engineering |
| Medium (M) | 14 days | Assigned team; tracked in issue tracker |
| Low (L) | 60 days | Batch remediation in next maintenance window |
| Informational (I) | 180 days | Backlog; review at next quarterly audit |

### Remediation Tracking

Each finding generates a remediation record:

```json
{
  "remediation_id": "REM-2026-042",
  "finding_id": "RK-EAR-01",
  "system": "rocksdb",
  "severity": "HIGH",
  "description": "RocksDB EncryptionProvider not initialized — block-level encryption not active",
  "root_cause": "RocksDB integration was deprioritized in Q2 2026 sprint planning",
  "assigned_to": "application-team@socioprophet-internal",
  "target_date": "2026-09-30",
  "status": "IN_PROGRESS",
  "resolution_steps": [
    "Implement CTREncryptionProvider wrapper in RocksDB initialization code",
    "Integrate HKDF key derivation from Vault master key",
    "Deploy to staging and run compliance check",
    "Deploy to production after DR window",
    "Update INTEGRATION-CHECKLIST.md RK-EAR-01 to ✅"
  ],
  "verification_method": "Run `data_layer_compliance_check.py --systems rocksdb` — expect PASS",
  "created_at": "2026-06-30T23:59:00Z",
  "updated_at": "2026-07-01T10:00:00Z"
}
```

### Exception Process

For findings that cannot be remediated within the SLA due to technical or business constraints:

1. Submit a risk acceptance request to the CISO with: finding ID, business justification, compensating controls in place, and a revised remediation date.
2. CISO must approve within 48 hours of submission.
3. Approved exceptions are archived in `standards/audit-forensics/exceptions/`.
4. Exceptions are reviewed and must be re-approved at each quarterly audit.
5. No exception may extend beyond 12 months without a formal risk re-assessment.
