# Compliance Validation

This document uses RFC 2119 language: **MUST**, **SHOULD**, **MAY**.

## 1. Scope

This standard defines automated and manual validation procedures to confirm that data-layer
systems maintain continuous FIPS 140-2/140-3 compliance, satisfying NIST SP 800-53 CA-7 and
CA-2.

## 2. Automated Checks (CI/CD Integration)

The following checks MUST be executed in the CI/CD pipeline on every merge to the main branch
and on a daily scheduled run:

### 2.1 TLS Configuration Verification

- Use `testssl.sh` or an equivalent tool to scan each data-system endpoint.
- Assert that:
  - TLS 1.3 is offered.
  - TLS 1.0 and 1.1 are not offered.
  - No weak cipher suites (RC4, DES, 3DES, NULL, EXPORT) are present.
- Pipeline step MUST fail if any assertion fails.

### 2.2 Algorithm Whitelist Validation

- Scan all configuration files (`.conf`, `.yaml`, `.env`, `.properties`) for disallowed
  algorithm strings: `md5`, `sha1`, `des`, `3des`, `rc4`, `aes128`, `aes-128`.
- Pipeline step MUST fail on any match outside of comments.

### 2.3 Encryption at Rest Verification

- For each system, verify that the encryption flag is enabled:
  - PostgreSQL: `SHOW ssl;` returns `on`.
  - MongoDB: query `db.adminCommand({getParameter:1, enableEncryption:1})`.
  - Elasticsearch: `GET /_cluster/settings` confirms `xpack.security.enabled: true`.
  - Redis: `CONFIG GET tls-port` returns a non-zero port.
  - MinIO: `mc encrypt info` confirms SSE enabled on each regulated bucket.
- Failures MUST block deployment and page on-call.

### 2.4 Audit Logging Enablement Check

- For each system, verify that audit logging is active:
  - PostgreSQL: `SHOW shared_preload_libraries` includes `pgaudit`.
  - MongoDB: `db.adminCommand({getCmdLineOpts:1})` confirms `--auditDestination` is set.
  - Elasticsearch: `GET /_cluster/settings` confirms `xpack.security.audit.enabled: true`.
  - Redis: `CONFIG GET acllog-max-len` returns a non-zero value.
  - MinIO: confirm audit webhook endpoint is reachable and returning 200.
- Failures MUST block deployment.

## 3. Manual Assessments

### 3.1 Quarterly Encryption Configuration Audit

- The Security Officer MUST review all encryption configurations against this standard.
- Review MUST include: algorithm verification, key-rotation evidence, certificate expiry
  dates, and HSM integration status.
- Findings MUST be documented and remediation timelines assigned for any gap.

### 3.2 Semi-Annual Penetration Testing

- An internal or third-party penetration test MUST be conducted every 6 months.
- Scope MUST include: network segmentation, authentication bypass attempts, TLS downgrade
  attacks, audit-log tampering attempts, and backup integrity.
- Findings MUST be tracked to closure; Critical findings MUST be remediated within 7 days.

### 3.3 Annual Third-Party Assessment

- An independent assessor MUST review the full data-layer compliance posture annually.
- Assessment MUST cover all NIST 800-53 controls listed in [INDEX.md](INDEX.md).
- Assessment report MUST be retained for 7 years.

### 3.4 Access Control Review (Quarterly)

- All database accounts, roles, and privileges MUST be reviewed quarterly per
  [ACCESS-CONTROL.md](ACCESS-CONTROL.md).
- Inactive accounts (>90 days) MUST be disabled.
- Results MUST be documented and retained.

## 4. Reporting

### 4.1 Monthly Compliance Summary

- A monthly report MUST be generated covering:
  - Pass/fail status of all automated checks.
  - Any policy exceptions currently in effect.
  - Open findings from the most recent penetration test or audit.
  - Key rotation and certificate expiry status.
- The report MUST be distributed to the Security Officer and relevant system owners.

### 4.2 Incident Reporting

- Any compliance failure detected by automated checks MUST be treated as a security incident.
- The incident MUST be reported within 1 hour of detection to the Security Officer.
- Root cause analysis MUST be completed within 5 business days.
- Corrective action MUST be verified by re-running the relevant automated check.

### 4.3 Attestation

- Prior to each major release, the Security Officer MUST sign a compliance attestation
  confirming that all data-layer systems satisfy the standards in this directory.
- Attestations MUST be retained for 7 years and linked from the release notes.

## 5. Tooling

| Tool | Purpose | Frequency |
|---|---|---|
| `testssl.sh` | TLS configuration scan | CI/CD + daily |
| Config-file algorithm scanner | Detect disallowed strings | CI/CD |
| `make validate` (this repo) | Repository structure validation | CI/CD |
| Database-native status queries | Encryption/audit enablement | CI/CD + daily |
| Penetration testing suite | Active attack simulation | Semi-annual |
| Third-party audit | Independent NIST 800-53 assessment | Annual |
