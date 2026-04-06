# Database Hardening Standards

This document uses RFC 2119 language: **MUST**, **SHOULD**, **MAY**.

## 1. Scope

This standard defines security hardening procedures for all data-layer systems, satisfying
NIST SP 800-53 SC-7, SI-2, CM-6, and CM-7.

## 2. Network Isolation

- Data systems MUST NOT be directly reachable from the public internet.
- Access MUST be restricted to the application-tier network segment; direct DBA shell access
  from developer workstations MUST require a bastion host, MFA, and a time-limited access request
  recorded in the audit log.
- Firewall / security-group rules MUST use IP-address whitelisting; open-world rules
  (`0.0.0.0/0`) are prohibited.
- Each data system MUST listen on a non-standard port OR be protected by a network-layer ACL
  that limits exposure to only approved source CIDRs.

## 3. Authentication Hardening

- Default credentials supplied by the vendor MUST be replaced before the system is connected
  to any network.
- Service account credentials MUST be stored in the platform secrets manager; they MUST NOT
  appear in:
  - Source code or configuration files committed to VCS
  - Container images or build artifacts
  - Plaintext environment variable files stored on disk
- Password policies MUST comply with NIST SP 800-63B as defined in
  [ACCESS-CONTROL.md](ACCESS-CONTROL.md).
- Account lockout MUST be enforced after 10 consecutive failed authentication attempts.

## 4. Configuration Hardening

### 4.1 TLS / Encryption

- SSL/TLS MUST be enabled; plaintext connections MUST be rejected (see
  [ENCRYPTION-IN-TRANSIT.md](ENCRYPTION-IN-TRANSIT.md)).
- Weak cipher suites (RC4, DES, 3DES, export-grade ciphers) MUST be explicitly disabled.
- Server configuration MUST be verified with a TLS scanner (e.g., `testssl.sh`) after every
  certificate rotation.

### 4.2 Minimal Attack Surface

- All unnecessary services, plugins, and extensions MUST be disabled or uninstalled.
  Enable only what is required for the current use case.
- PostgreSQL: disable `pg_read_server_files`, `pg_write_server_files` for non-admin roles.
- MongoDB: disable `--httpInterface` (removed in 3.6, but confirm absent in config).
- Elasticsearch: disable the deprecated HTTP basic auth in favour of X-Pack.
- Redis: disable or rename dangerous commands (`FLUSHDB`, `FLUSHALL`, `CONFIG`, `DEBUG`,
  `SHUTDOWN`, `SLAVEOF`, `REPLICAOF`, `BGREWRITEAOF`, `BGSAVE`).

### 4.3 Audit Logging Level

- Logging MUST be set to capture all authentication, authorization, and data-modification
  events as defined in [AUDIT-LOGGING.md](AUDIT-LOGGING.md).
- Log verbosity MUST NOT be reduced below the audit-minimum level in production.

### 4.4 Memory Safety

- Redis: set `maxmemory` and `maxmemory-policy` to prevent unbounded memory growth that could
  cause OOM-based eviction of audit data.
- MongoDB: set `wiredTigerCacheSizeGB` appropriately to avoid swapping sensitive data to disk
  unencrypted.

## 5. Vulnerability Management

- Critical CVEs (CVSS 9.0+) MUST be patched within **7 days** of public disclosure.
- High CVEs (CVSS 7.0–8.9) MUST be patched within **30 days**.
- Medium and Low CVEs MUST be scheduled within the next regular maintenance window.
- Patches MUST be applied first in a staging environment with a defined test plan before
  production deployment.
- Rollback procedures MUST be documented and tested for every patch deployment.
- Patch activity MUST be recorded in the audit log with the CVE reference, patch version,
  operator, and deployment timestamp.

## 6. Hardening Verification

- A CIS Benchmark or equivalent hardening checklist MUST be run against each new system
  deployment and after major version upgrades.
- Results MUST be documented; any failed checks that are accepted as a risk MUST have a written
  exception signed by the Security Officer.
- Automated configuration-drift detection MUST alert within 1 hour of any out-of-band change
  to a hardening-relevant setting.
