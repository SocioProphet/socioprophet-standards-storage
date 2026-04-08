# Forensic-Ready Audit Trail Standard (NIST SP 800-88 / NIST SP 800-92)

This document uses RFC 2119 language: **MUST**, **SHOULD**, **MAY**.

## 1. Overview

This standard defines requirements for forensic-ready, tamper-evident audit logging across all SocioProphet platform components, drawing from:

- **NIST SP 800-88** — Guidelines for Media Sanitization (integrity and chain-of-custody)
- **NIST SP 800-92** — Guide to Computer Security Log Management
- **NIST SP 800-53 AU controls** — Audit and Accountability family

A forensic-ready audit trail means that log evidence can withstand legal scrutiny: it is authentic, complete, protected, and has an unbroken chain of custody.

## 2. Audit Event Requirements

### 2.1 Mandatory Event Categories

All platform components MUST log the following event categories:

| Category | Events |
|----------|--------|
| Authentication | Login, logout, failed login, MFA success/failure, token refresh |
| Authorization | Access granted, access denied, policy evaluation |
| Session management | Session created, session expired, session revoked |
| Data access | Read (sensitive data), write, delete, bulk export |
| Configuration changes | Create, update, delete of any configuration object |
| Cryptographic operations | Key created, key rotated, key deleted, encryption/decryption invoked |
| Administrative actions | User provisioned, user deprovisioned, role assigned, role revoked |
| System events | Service started, service stopped, health check failed, dependency unavailable |
| Security events | Policy violation, anomaly detected, intrusion attempt |

### 2.2 Mandatory Audit Record Fields

Every audit record MUST contain:

```json
{
  "event_id":        "<UUID v4>",
  "timestamp":       "<ISO 8601 with nanosecond precision>",
  "rfc3161_timestamp": "<RFC 3161 signed timestamp token, base64>",
  "actor": {
    "id":            "<OIDC sub or SPIFFE URI>",
    "type":          "<user | service | system>",
    "ip":            "<source IP address>",
    "user_agent":    "<client user agent or service name>"
  },
  "action":          "<verb: create | read | update | delete | login | logout | deny | …>",
  "resource": {
    "type":          "<resource type: pod | database | secret | file | …>",
    "id":            "<resource identifier>",
    "namespace":     "<Kubernetes namespace or logical scope>"
  },
  "result":          "<success | failure | partial>",
  "reason":          "<human-readable reason for result>",
  "correlation_id":  "<trace/span ID for distributed tracing>",
  "signature":       "<ECDSA-P256 signature over canonical JSON, base64>"
}
```

Fields MUST NOT be omitted; use `null` only when a field is genuinely not applicable.

### 2.3 Signature Requirements

- Each audit record MUST be signed with an ECDSA-P256 key managed by Vault.
- The signing key MUST be separate from the application key material.
- Signature verification MUST be possible without trusting the audit service itself.
- Signature key rotation MUST NOT break verification of existing records (use versioned keys).

### 2.4 Timestamp Integrity

- All timestamps MUST use RFC 3161 Trusted Timestamping from an authoritative TSA.
- The TSA MUST be a publicly trusted TSA (e.g., DigiCert, Sectigo) or an internal TSA with externally verifiable root.
- Timestamps MUST have nanosecond precision.
- Clock synchronization MUST use NTP with at least 3 stratum-2 sources; drift MUST NOT exceed 100ms.

## 3. Log Storage Requirements

### 3.1 Immutability

- Audit logs MUST be stored in append-only, write-once-read-many (WORM) storage.
- No process MUST have `DELETE` or `UPDATE` permissions on the audit log store.
- Log retention MUST be enforced by storage policy, not application code.
- Object lock (S3/MinIO Object Lock, Elasticsearch frozen tier with ILM) MUST be configured.

### 3.2 Retention Schedule

| Log Category | Retention |
|--------------|-----------|
| Security audit events | 7 years |
| Access control events | 7 years |
| Configuration changes | 7 years |
| Cryptographic key operations | 7 years (+ key lifecycle beyond deletion) |
| System/operational logs | 2 years |
| Debug/trace logs | 90 days |

### 3.3 Centralization

- All audit logs MUST be forwarded to a centralized, isolated log store within 60 seconds of generation.
- The centralized store MUST be logically separated from the systems being audited (separation of duty).
- Log transport MUST use TLS 1.3 with mutual authentication.
- Log loss during transport disruption MUST be bounded to a maximum of 60 seconds via local buffering.

### 3.4 Log Integrity Verification

- An automated integrity verification job MUST run daily.
- Verification MUST confirm:
  - Every record has a valid ECDSA-P256 signature
  - No gaps exist in the event sequence (via monotonic sequence numbers)
  - RFC 3161 timestamps are within expected drift bounds
- Verification failures MUST generate a `CRITICAL` alert within 5 minutes.

## 4. Chain of Custody

- Audit evidence exported for legal or regulatory purposes MUST include:
  - The complete audit record set for the relevant time window
  - Signature verification keys (public keys only) and their certificate chain
  - RFC 3161 timestamp verification instructions
  - Hash of the exported package (SHA-256)
- A chain-of-custody document MUST be created for any evidence export, recording who requested it, when, why, and who received it.
- Evidence exports MUST themselves be logged as audit events.

## 5. Access to Audit Logs

- Audit log read access MUST be restricted to authorized security personnel and automated compliance tools.
- Read access to audit logs MUST be logged in a separate meta-audit log.
- Application components MUST NOT have read access to their own audit logs.
- Log purging or archiving operations MUST require dual authorization (two-person integrity).

## 6. Media Sanitization (NIST 800-88)

When decommissioning storage media that held audit logs:

- Physical media holding audit logs MUST be sanitized using NIST 800-88 Clear or Purge methods before disposal.
- Cryptographic erasure (AES-256-GCM key destruction) is acceptable for encrypted-at-rest media.
- A sanitization certificate MUST be obtained and retained for 7 years.
- Cloud storage decommission MUST include provider-issued data deletion confirmation.

## 7. Compliance with AU Controls

| NIST Control | Requirement | Implementation |
|--------------|-------------|----------------|
| AU-2  | Event selection | Section 2.1 (mandatory event categories) |
| AU-3  | Audit record content | Section 2.2 (mandatory fields) |
| AU-4  | Audit log storage capacity | Section 3.3 (retention + centralization) |
| AU-5  | Response to audit failure | Alert within 5 min (Section 3.4) |
| AU-6  | Audit record review | Weekly log review + anomaly detection |
| AU-7  | Audit record reduction | Central store with search/query capability |
| AU-8  | Time stamps | RFC 3161 (Section 2.4) |
| AU-9  | Audit info protection | WORM storage + ECDSA signatures (Section 3.1) |
| AU-10 | Non-repudiation | ECDSA-P256 per-record signatures (Section 2.3) |
| AU-11 | Audit record retention | 7-year retention (Section 3.2) |
| AU-12 | Audit record generation | All components emit audit events (Section 2.1) |

## 8. Forensic Investigation Procedures

When a security incident or compliance investigation is initiated:

1. Preserve: Immediately snapshot/freeze relevant log windows.
2. Authenticate: Verify ECDSA signatures and RFC 3161 timestamps.
3. Chain of custody: Begin chain-of-custody documentation.
4. Analyze: Use the centralized log store query tools to reconstruct the event timeline.
5. Report: Generate a forensic report with verified evidence artifacts.
6. Remediate: Address root causes and log remediation actions.

## Related Standards

- `090-fips-nist-compliance.md` — Cryptographic requirements (ECDSA-P256, SHA-256)
- `091-nist-800-53-control-mappings.md` — AU control implementation locations
- `094-data-layer-fips-compliance.md` — Per-database audit logging configuration

## Implementation Evidence

- Audit event schema: `SocioProphet/sociosphere/observability/audit-schema.json`
- Audit pipeline: `SocioProphet/sociosphere/observability/audit-pipeline.yaml`
- Log immutability policy: `SocioProphet/sociosphere/observability/log-immutability.yaml`
- Integrity verification job: `SocioProphet/sociosphere/observability/audit-integrity-check.yaml`
- RFC 3161 TSA integration: `SocioProphet/sociosphere/observability/tsa-config.yaml`
