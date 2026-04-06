# NIST SP 800-207 Zero-Trust Architecture

**Status:** Active  
**Authority:** SocioProphet/socioprophet-standards-storage  
**Last Reviewed:** 2026-04-06  
**Next Review:** 2026-07-01  
**Reference:** https://csrc.nist.gov/publications/detail/sp/800-207/final

---

## Overview

This document specifies the zero-trust architecture (ZTA) for the SocioProphet platform,
grounded in NIST SP 800-207. Zero trust is a security model that eliminates implicit trust
and continuously validates every request regardless of network location.

This document uses RFC 2119 language: **MUST**, **SHOULD**, **MAY**.

---

## Core Principles

### 1. Never Trust, Always Verify

No implicit trust **MUST** be granted based on network location, IP address, or prior
successful authentication. Every request to any resource **MUST** present fresh credentials
and be evaluated against current policy.

### 2. Continuous Verification

Authentication and authorization are not one-time events. Every API call, build invocation,
and data access **MUST** be independently authenticated and authorized. Token TTLs **MUST**
be short (≤ 60 minutes for session tokens).

### 3. Least Privilege

Access grants **MUST** be scoped to the minimum permissions required for a specific operation.
An agent performing a manifest fetch receives a read-only token; an agent executing a build
receives a build-scoped token. No ambient authority.

### 4. Assume Breach

System design **MUST** assume that any component may be compromised at any time. Blast radius
**MUST** be limited through micro-segmentation, short-lived credentials, and continuous
revocation capability. Lateral movement **MUST** require re-authentication through the policy
engine.

### 5. Micro-Segmentation

Network and service boundaries **MUST** be enforced at the workload level, not just at the
network perimeter. Each trust domain operates under its own policy scope.

---

## Implementation in Workspace Controller Context

The workspace controller (SocioProphet/sociosphere) is the primary zero-trust policy
enforcement point. It implements ZTA through:

- **Policy Engine** — Centralized policy decision point evaluating every request.
- **OIDC Token Binding** — Each operation bound to a scoped, signed OIDC token.
- **Cryptographic Verification** — Manifests and artifacts verified before execution.
- **Immutable Audit Trail** — All decisions recorded with non-repudiation proof.

---

## Zero-Trust Interaction Patterns

### Pattern 1: Manifest Fetch (Read-Only)

Used when the workspace controller retrieves a build manifest or configuration document.

```
Actor (workspace controller)
  │
  ├── 1. Request OIDC token from identity provider
  │        Scope: read:manifests
  │        TTL: 15 minutes
  │        MFA: NOT required (read-only operation)
  │        Crypto: ECDSA P-256 signed ID token
  │
  ├── 2. Fetch manifest from manifest store
  │        Auth: Bearer token (OIDC)
  │        Transport: TLS 1.3
  │        Policy check: AC-3, AC-6
  │
  ├── 3. Verify manifest cryptographic signature
  │        Algorithm: ECDSA P-256
  │        Verification key: retrieved from trust anchor store
  │
  ├── 4. Emit audit event: ManifestFetched
  │        Fields: principal_id, manifest_id, timestamp, TSA token,
  │                signature verification result, correlation_id
  │
  └── 5. Proceed only if signature valid
```

**NIST 800-53 Controls:** AC-3, AC-6, AU-2, AU-3, AU-10, SC-8, SC-13  
**Zero-trust tenets:** Never Trust Always Verify, Least Privilege, Continuous Verification

### Pattern 2: Build Execution (MFA-Protected)

Used when the workspace controller initiates a build operation.

```
Actor (human or CI service)
  │
  ├── 1. Authenticate via OIDC
  │        Scope: execute:builds
  │        TTL: 30 minutes
  │        MFA: REQUIRED (privileged operation)
  │        Crypto: ECDSA P-256 signed ID token
  │
  ├── 2. Policy engine evaluates request
  │        Checks: identity, scope, time-of-day, resource quota, anomaly score
  │        Logs: PolicyEvaluated event
  │
  ├── 3. Build token issued (build-scoped)
  │        Bound to: requesting principal, target build, expiry
  │        Crypto: HKDF-SHA-256 derived from session key
  │
  ├── 4. Build executor receives token + signed manifest
  │        Verifies: token signature, manifest signature, token-manifest binding
  │
  ├── 5. Build executes in isolated environment
  │        No outbound network access except approved registries
  │        Filesystem: ephemeral, cleared after build
  │
  ├── 6. Build artifact signed at completion
  │        Algorithm: ECDSA P-256
  │        SBOM generated and stored in audit trail
  │
  ├── 7. Emit audit events throughout:
  │        BuildStarted, BuildCompleted, ArtifactSigned,
  │        SBOMGenerated, BuildEnvironmentCleared
  │
  └── 8. Build token revoked immediately after use
```

**NIST 800-53 Controls:** AC-2, AC-3, AC-6, AU-2, AU-10, AU-12, IA-2, SC-8, SC-13, SI-7  
**Zero-trust tenets:** All five core tenets

---

## Micro-Segmentation Architecture

### Trust Domains

The platform is divided into four trust domains with explicit inter-domain policies.

#### Control Plane
- **Components:** Policy engine, identity provider, manifest store, key management service
- **Trust Level:** Highest — breaching this domain is a critical incident
- **Inbound auth:** mTLS + OIDC; IP allowlist for management interfaces
- **Outbound:** Audit sink only

#### Build Plane
- **Components:** Build executors, artifact registries, SBOM stores
- **Trust Level:** High — executes untrusted build instructions in isolation
- **Inbound auth:** Build token (scoped, short-lived) + mTLS
- **Outbound:** Artifact registry (write); Approved package registries (read-only)

#### Data Plane
- **Components:** Storage backends (object store, database, graph store)
- **Trust Level:** High — contains sensitive persistent data
- **Inbound auth:** mTLS + OIDC data-access tokens
- **Outbound:** Audit sink only

#### Operations Plane
- **Components:** Monitoring agents, alerting, audit trail sinks
- **Trust Level:** Medium — read access to sensitive telemetry
- **Inbound auth:** mTLS + OIDC monitoring tokens
- **Outbound:** Alert channels (one-way, no secrets)

### Boundary Enforcement Matrix

Cross-domain traffic rules. All unlisted pairs are **DENY by default**.

| Source | Target | Auth Required | Notes |
|--------|--------|--------------|-------|
| Control Plane | Build Plane | mTLS + build token | Token bound to specific build |
| Control Plane | Data Plane | mTLS + data token | Scoped per operation |
| Control Plane | Operations Plane | mTLS + ops token | Read-only metrics push |
| Build Plane | Data Plane | mTLS + build token | Write artifacts only |
| Build Plane | Operations Plane | mTLS | Telemetry push only |
| Data Plane | Operations Plane | mTLS | Metrics push only |
| Operations Plane | Control Plane | mTLS + alert token | Alert acknowledgement only |
| External | Control Plane | OIDC + MFA | Human users; rate-limited |
| External | Build Plane | ❌ DENY | No direct external access |
| External | Data Plane | ❌ DENY | No direct external access |

### Network Policies

```yaml
# Example: Build Plane ingress policy (Kubernetes NetworkPolicy style)
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: build-plane-ingress
  namespace: build-plane
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          plane: control
    ports:
    - protocol: TCP
      port: 8443  # mTLS build token endpoint
```

Traffic not matching the ingress rules is dropped by default. No egress to Control Plane
except through approved audit-sink endpoints.

---

## Continuous Monitoring and Anomaly Detection

### Behavioral Baselines

The system establishes baselines for normal operations during a calibration period. Deviations
trigger anomaly scoring.

| Metric | Baseline Approach | Alert Threshold |
|--------|------------------|----------------|
| Token request rate per principal | 7-day rolling average | > 3× baseline |
| Build duration | 90th-percentile per build type | > 2× p90 |
| Cross-domain API call volume | 7-day rolling average | > 5× baseline |
| Failed authentication attempts | Hourly bucket | > 10 per hour per principal |
| New IP address for known principal | Historical IP set | Any new IP in production |

### Real-Time Anomaly Scoring

Each request is assigned an anomaly score (0–100) based on:

- **Identity risk** (0–30): Is the principal authenticating from a new device/IP? Is the token
  recently issued? Has MFA been completed?
- **Behavioural risk** (0–40): Does the operation pattern match historical baseline? Is the
  request volume unusual?
- **Contextual risk** (0–30): Is the request time unusual? Is the resource sensitivity high?

| Score Range | Action |
|------------|--------|
| 0–30 | Allow |
| 31–60 | Allow with enhanced audit logging |
| 61–80 | Require step-up MFA challenge |
| 81–100 | Deny; trigger security alert |

### Automated Response Actions

| Trigger | Response |
|---------|---------|
| Anomaly score ≥ 81 | Deny request; page on-call security team; quarantine principal token |
| > 10 failed auth in 1 hour | Temporary lockout (30 min); alert security team |
| New admin-scope token from unknown IP | Require MFA re-enrollment; alert |
| Build plane → Control plane direct call | Block; incident P0 |
| Audit trail integrity violation | Halt affected service; P0 incident |

---

## Incident Response and Rapid Revocation

### Revocation Triggers

Any of the following events **MUST** trigger immediate credential revocation:

- Anomaly score ≥ 81 on principal
- Confirmed credential compromise report
- Departure of personnel with privileged access
- Detection of unauthorized cross-domain access
- Audit trail integrity violation

### Revocation Process

| Step | Action | Timeline |
|------|--------|---------|
| 1 | Revoke all active tokens for principal | < 1 minute |
| 2 | Revoke client certificates via OCSP/CRL update | < 5 minutes |
| 3 | Invalidate all session state | < 1 minute |
| 4 | Block principal at policy engine | Immediate (real-time) |
| 5 | Notify security team and management | < 10 minutes |
| 6 | Preserve audit trail snapshot for forensics | < 15 minutes |

### Post-Incident Forensic Analysis

After any security incident:

1. **Collect** — Export signed, timestamped audit trail for the relevant time window.
2. **Verify** — Replay hash chain to confirm integrity of audit evidence.
3. **Analyze** — Reconstruct action sequence using `event_id`, `session_id`, `principal_id`.
4. **Document** — Produce incident report referencing specific audit record IDs.
5. **Remediate** — Address root cause; update policies and baselines.
6. **Review** — Schedule post-incident review within 5 business days.

Full forensic procedures: [standards/audit-forensics/NIST-800-88.md](../audit-forensics/NIST-800-88.md)

---

## Compliance Mapping to NIST 800-53

| Zero-Trust Tenet | NIST 800-53 Controls |
|----------------|---------------------|
| Never Trust, Always Verify | AC-3, IA-2, IA-8, SC-8 |
| Continuous Verification | AC-17, IA-2, SC-13 |
| Least Privilege | AC-6, AC-2, SC-12 |
| Assume Breach | SI-4, AU-9, AU-10, SC-28 |
| Micro-Segmentation | SC-8, SC-17, AC-3 |
| Continuous Monitoring | SI-4, AU-2, AU-12 |
| Rapid Revocation | AC-2, IA-5, AU-10 |

---

## Attestation and Quarterly Review

Every quarter, the following attestations **MUST** be completed:

- [ ] All trust domain boundaries enforced as documented in the Boundary Enforcement Matrix.
- [ ] Anomaly detection baselines recalibrated against current traffic.
- [ ] Revocation process tested via tabletop exercise.
- [ ] No expired certificates in production trust stores.
- [ ] Audit trail integrity verified by replaying hash chain.
- [ ] Cross-domain network policies verified against current running configuration.
- [ ] OIDC token TTLs confirmed at configured maximums (session ≤ 60 min, refresh ≤ 24 hr).

Results of quarterly attestation **MUST** be recorded in an immutable audit event:
`ZeroTrustAttestationCompleted` with attestor identity, timestamp, and TSA token.

---

## References

| Standard | URL |
|---------|-----|
| NIST SP 800-207 (Zero Trust Architecture) | https://csrc.nist.gov/publications/detail/sp/800-207/final |
| NIST SP 800-53 Rev. 5 | https://csrc.nist.gov/publications/detail/sp/800-53/rev-5/final |
| NIST SP 800-63B (Authentication) | https://csrc.nist.gov/publications/detail/sp/800-63/3/final |
| RFC 8446 (TLS 1.3) | https://tools.ietf.org/html/rfc8446 |
| RFC 7636 (PKCE) | https://tools.ietf.org/html/rfc7636 |
| RFC 6238 (TOTP) | https://tools.ietf.org/html/rfc6238 |
| RFC 3161 (TSP) | https://tools.ietf.org/html/rfc3161 |
| FIPS 186-5 (ECDSA) | https://csrc.nist.gov/publications/detail/fips/186/5/final |
| FIPS 140-3 | https://csrc.nist.gov/publications/detail/fips/140/3/final |
| DISA Zero Trust Reference Architecture | https://public.cyber.mil/announce/disa-releases-zero-trust-reference-architecture/ |
