# Zero-Trust Architecture — SocioProphet Platform

- Last updated: 2026-01-27
- Status: Active governance document
- Owner: SocioProphet Platform Security
- Normative reference: NIST SP 800-207

---

## Table of Contents

1. [Overview and Principles](#overview-and-principles)
2. [Core Zero-Trust Tenets](#core-zero-trust-tenets)
3. [Interaction Patterns](#interaction-patterns)
4. [Identity Plane](#identity-plane)
5. [Micro-Segmentation Architecture](#micro-segmentation-architecture)
6. [Identity-Aware Proxy Patterns](#identity-aware-proxy-patterns)
7. [Continuous Monitoring and Anomaly Detection](#continuous-monitoring-and-anomaly-detection)
8. [Incident Response and Rapid Revocation](#incident-response-and-rapid-revocation)
9. [Compliance Mapping](#compliance-mapping)
10. [Attestation and Review Procedures](#attestation-and-review-procedures)
11. [Implementation Phases](#implementation-phases)

---

## Overview and Principles

Zero-trust architecture (ZTA) rejects the assumption that any actor, device, or network path is implicitly trustworthy. The traditional perimeter model — where traffic inside the network boundary is trusted and traffic outside is not — is inadequate for modern distributed systems where workloads span cloud environments, service meshes, and multi-tenant Kubernetes clusters.

NIST SP 800-207 defines zero trust as a set of guiding principles for security architecture, not a single product or protocol. The SocioProphet implementation follows the logical components defined in SP 800-207: policy engine, policy administrator, policy enforcement points (PEPs), and the enterprise resources they protect.

### Architectural Model

```
  ┌────────────────────────────────────────────────────────────────┐
  │                     Enterprise Trust Plane                     │
  │                                                                │
  │   ┌────────────┐    ┌─────────────────┐    ┌──────────────┐   │
  │   │  Policy    │◄──►│  Policy         │◄──►│  Identity    │   │
  │   │  Engine    │    │  Administrator  │    │  Provider    │   │
  │   │  (OPA)     │    │  (Control Plane)│    │  (OIDC/SPIFFE│   │
  │   └────────────┘    └────────┬────────┘    └──────────────┘   │
  │                              │                                 │
  └──────────────────────────────┼─────────────────────────────────┘
                                 │ Policy decision
  ┌──────────────────────────────▼─────────────────────────────────┐
  │                     Data Plane                                 │
  │                                                                │
  │  Subject  ──►  PEP (Proxy)  ──►  Resource (Service)           │
  │  (User /      (Envoy / NGINX    (API, DB, Storage)            │
  │   Service)     sidecar)                                        │
  │                                                                │
  │  Every request is authenticated, authorized, and logged.       │
  └────────────────────────────────────────────────────────────────┘
```

Every connection — whether from a human operator, an external API client, a CI/CD pipeline, or an internal service — passes through a policy enforcement point. The PEP consults the policy engine for every request. There are no bypass paths.

---

## Core Zero-Trust Tenets

### Tenet 1: Never Implicit Trust (Default Deny)

No request is trusted by virtue of its origin network, IP address, or prior session state. Every request must present a valid credential, and every credential must be validated against current policy at the time of the request — not at session establishment.

**Implementation in SocioProphet:**

- The Kubernetes NetworkPolicy default posture is deny-all. Explicit allow rules are required for every communication path.
- The service mesh (Istio or Linkerd) applies default-deny authorization policy. Services must explicitly list the other services permitted to call them.
- The API gateway validates every inbound request against the JWT issuer's public keys (fetched dynamically; no static key pinning that would allow use of revoked keys).
- The OPA policy engine issues explicit `allow` decisions; absence of a matching rule is a `deny`.

**Why this matters:** An attacker who compromises a service inside the network perimeter cannot use that foothold to reach other services. Every lateral movement attempt requires a valid credential for the target service, which the attacker does not possess.

---

### Tenet 2: Continuous Verification (Periodic Re-Authentication)

Authentication is not a one-time event at session start. Credentials have short lifetimes and must be continuously refreshed. Long-lived sessions are broken into short credential windows.

**Implementation in SocioProphet:**

| Credential Type | TTL | Re-authentication Mechanism |
|---|---|---|
| OIDC access token | 15 minutes | Automatic token refresh using refresh token |
| OIDC refresh token | 8 hours | Full re-authentication at expiry |
| SPIFFE SVID (service) | 1 hour | SPIRE agent automatic rotation |
| mTLS certificate (service mesh) | 24 hours | Automated rotation via cert-manager |
| Operator session (privileged) | 4 hours | Forced re-authentication with MFA |

**Why this matters:** Short credential lifetimes limit the window of opportunity for an attacker who has captured a credential. A stolen access token is useless after 15 minutes if the attacker cannot also steal and use the refresh token.

---

### Tenet 3: Least Privilege (Minimal Permissions)

Every identity — human or service — is granted only the permissions required for its current task. Permissions are scoped as narrowly as possible: by resource, by operation, by time window, and by context.

**Implementation in SocioProphet:**

- Service accounts in Kubernetes have dedicated ServiceAccount objects; they do not share the default service account.
- RBAC is supplemented with ABAC (attribute-based) policies that can restrict access based on the resource's classification, the subject's clearance level, the time of day, and the network context.
- Ephemeral elevated permissions are granted via a time-bounded privilege escalation workflow that requires MFA and two-person approval for critical operations. Permissions are automatically revoked when the time window expires.
- The CI/CD pipeline has distinct service accounts for each stage (build, test, sign, deploy). A compromise of the build account cannot reach the deploy account's permissions.

**Scoped permission example for a signing service account:**

```yaml
# SPIFFE SVID scope
spiffeID: spiffe://socioprophet.org/ns/cicd/sa/signing-service

# Vault policy: can only access the signing key
path "transit/sign/artifact-signing-key" {
  capabilities = ["update"]  # sign only; cannot read key material
}
path "transit/verify/artifact-signing-key" {
  capabilities = ["update"]
}
# No other Vault paths permitted
```

---

### Tenet 4: Assume Breach (Design for Containment)

The architecture assumes that some component will eventually be compromised. The design goal is to minimize the blast radius — the set of resources an attacker can reach from a compromised component — and to detect and contain the breach as quickly as possible.

**Implementation in SocioProphet:**

- **Micro-segmentation:** Services communicate only with explicitly listed peers. A compromised service cannot reach services outside its defined communication graph.
- **Credential isolation:** Credentials are scoped to a single service's function. A leaked service credential cannot be used to impersonate other services or access their data.
- **Immutable audit trail:** All access and operations are logged to a WORM store. An attacker cannot cover their tracks.
- **Canary tokens:** Synthetic credentials and resources are deployed as tripwires. Any access to a canary token triggers an immediate high-severity alert.
- **Encryption everywhere:** Data at rest is encrypted with per-resource keys. Compromise of the storage layer without the key material yields only ciphertext.

---

## Interaction Patterns

### Manifest Fetch (External Client)

A client requests a resource manifest from the SocioProphet API. This is the standard external-client interaction pattern.

```
Client                    API Gateway              Manifest Service          Audit
  │                           │                         │                      │
  │ HTTPS GET /manifest/{id}  │                         │                      │
  │ Authorization: Bearer JWT │                         │                      │
  ├──────────────────────────►│                         │                      │
  │                           │ Validate JWT (ECDSA-P256)                      │
  │                           │ Check token TTL                                │
  │                           │ Consult OPA policy      │                      │
  │                           │   subject: user@org     │                      │
  │                           │   resource: manifest/{id}                      │
  │                           │   action: read          │                      │
  │                           │ OPA → allow             │                      │
  │                           │                         │                      │
  │                           │ GET /manifest/{id}      │                      │
  │                           │ mTLS (SVID validation)  │                      │
  │                           ├────────────────────────►│                      │
  │                           │                         │ Write AUDIT_ACCESS   │
  │                           │                         ├─────────────────────►│
  │                           │ 200 OK + payload        │                      │
  │                           │◄────────────────────────┤                      │
  │ 200 OK + payload          │                         │                      │
  │◄──────────────────────────┤                         │                      │
```

**Cryptographic operations in this flow:**

1. ECDSA-P256 JWT signature validation at the gateway
2. HKDF-SHA256 session key derivation for the TLS connection
3. SHA-256 of the manifest payload included in the audit event
4. ECDSA-P256 signing of the audit batch at ingest

---

### Build Execution (CI/CD Pipeline)

A CI/CD pipeline build job fetches source code, builds an artifact, and signs it. This pattern requires OIDC authentication to the build platform and MFA for any operation that touches signing material.

```
Pipeline Job               OIDC Provider         Signing Service       Transparency Log
    │                           │                       │                      │
    │ Request OIDC token        │                       │                      │
    │ (GitHub Actions OIDC)     │                       │                      │
    ├──────────────────────────►│                       │                      │
    │◄──────────────────────────┤                       │                      │
    │ JWT (audience: signing)   │                       │                      │
    │                           │                       │                      │
    │ POST /sign                │                       │                      │
    │ artifact_digest: SHA-256  │                       │                      │
    │ Authorization: Bearer JWT │                       │                      │
    ├──────────────────────────────────────────────────►│                      │
    │                           │                       │ Validate JWT         │
    │                           │                       │ Validate digest      │
    │                           │                       │ Sign: ECDSA-P256     │
    │                           │                       │ (HSM-backed key)     │
    │                           │                       │                      │
    │                           │                       │ Append to log        │
    │                           │                       ├─────────────────────►│
    │◄──────────────────────────────────────────────────┤                      │
    │ Signature envelope        │                       │                      │
    │ (sig + cert + timestamp)  │                       │                      │
```

**Security properties of this flow:**

- The pipeline job cannot access the signing key material directly; it can only request signatures from the signing service.
- The OIDC token's audience is scoped to the signing service only — it cannot be replayed to other services.
- Every signing event is appended to the transparency log for auditability and non-repudiation.
- The signing service enforces a per-job signature limit to prevent bulk signing abuse.

---

## Identity Plane

### Human Identity

Human identities are managed in the central IdP (identity provider). The IdP issues OIDC tokens after successful authentication and MFA verification.

| Layer | Technology | Configuration |
|---|---|---|
| Identity provider | Keycloak or equivalent OIDC-compliant IdP | FIPS mode; ECDSA-P256 signing keys |
| MFA | FIDO2 (preferred) / TOTP-SHA256 | Required for all users; mandatory for privileged access |
| Token format | JWT (RFC 7519) | ES256 algorithm; 15-minute access token TTL |
| Directory | LDAP-backed or native IdP directory | Synced with HR system; dormancy detection |

### Service Identity

Service identities are issued by the SPIFFE/SPIRE infrastructure. Each Kubernetes workload is automatically assigned a SPIFFE Verifiable Identity Document (SVID) in X.509 certificate format.

| Layer | Technology | Configuration |
|---|---|---|
| Identity issuer | SPIRE server | ECDSA-P256 SVIDs; 1-hour TTL |
| Trust domain | `spiffe://socioprophet.org` | Single trust domain; federation planned for multi-cluster |
| Attestation | Kubernetes node and workload attestors | Node identity verified at bootstrap; workload verified by pod spec |
| Rotation | SPIRE agent | Automatic rotation 5 minutes before expiry |

### Trust Hierarchy

```
Root CA (HSM-backed, offline)
    │
    ├── Intermediate CA (SPIRE; online, automated)
    │       └── SVID certificates (workload identity)
    │
    ├── Intermediate CA (IdP; online, automated)
    │       └── TLS certificates (service endpoints)
    │
    └── Intermediate CA (Code Signing; HSM-backed, online)
            └── Artifact signing certificates
```

---

## Micro-Segmentation Architecture

Micro-segmentation divides the platform into communication zones. Each zone contains services that have a legitimate reason to communicate. Inter-zone communication requires explicit policy and passes through a PEP.

### Zone Definitions

| Zone | Services | Trust Level | Allowed Ingress Sources |
|---|---|---|---|
| Edge | API Gateway, Ingress Proxy | Semi-trusted | Internet (filtered), CDN |
| Application | sociosphere API, manifest service, knowledge service | Internal | Edge zone (authenticated) |
| Data | PostgreSQL, MongoDB, Elasticsearch, Redis, MinIO, RocksDB | Restricted | Application zone only |
| Orchestration | Kubernetes control plane, Vault, cert-manager, SPIRE | High security | Internal operations network only |
| P2P | Hypercore, Hyperdrive, Dat, multifeed, kappa-core | Isolated | Application zone (via dedicated proxy) |
| ML/AI | Ray Core, Ray Serve, Ray Tune, Ray Train, Ray Data | Isolated | Application zone (via dedicated proxy) |
| Monitoring | Prometheus, Loki, Grafana, SIEM | Internal | All zones (read-only metrics egress) |
| Audit | Audit store, audit pipeline | Append-only | All zones (write-only audit ingress) |

### NetworkPolicy Enforcement

Each zone is implemented as a Kubernetes namespace (or namespace group). Kubernetes NetworkPolicy enforces zone isolation at the pod network level. The service mesh authorization policy enforces workload identity at the application level. Both layers are required — neither alone is sufficient.

```yaml
# Example: Data zone default-deny NetworkPolicy
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: data-zone-default-deny
  namespace: data
spec:
  podSelector: {}          # applies to all pods in namespace
  policyTypes:
    - Ingress
    - Egress
  ingress:
    - from:
        - namespaceSelector:
            matchLabels:
              zone: application
  egress:
    - to:
        - namespaceSelector:
            matchLabels:
              zone: monitoring
        ports:
          - port: 9090      # Prometheus metrics
```

### Communication Graph

The following table defines the permitted inter-zone communication paths. Unlisted paths are denied.

| Source Zone | Destination Zone | Protocol | Authentication |
|---|---|---|---|
| Edge | Application | mTLS 1.3 | OIDC JWT (forwarded) |
| Application | Data | mTLS 1.3 | SVID |
| Application | P2P Proxy | mTLS 1.3 | SVID |
| Application | ML/AI Proxy | mTLS 1.3 | SVID |
| Application | Audit | mTLS 1.3 | SVID (write-only) |
| Orchestration | All zones | mTLS 1.3 | SVID + OPA policy |
| All zones | Monitoring | mTLS 1.3 | SVID (metrics push) |
| All zones | Audit | mTLS 1.3 | SVID (audit write) |

---

## Identity-Aware Proxy Patterns

### Sidecar Proxy Model

Each workload in the service mesh has a sidecar proxy (Envoy) that intercepts all inbound and outbound network traffic. The sidecar is responsible for:

1. Terminating mTLS for inbound traffic and presenting the peer's SVID to the application as an HTTP header.
2. Initiating mTLS for outbound traffic using the workload's own SVID.
3. Consulting the policy engine (OPA) for each request before forwarding to the application.
4. Emitting access logs (with the peer SVID identity) to the audit pipeline.

The application code does not need to implement mTLS or identity validation; this is handled entirely by the sidecar.

### External Access via Identity-Aware Proxy

Human operators accessing internal tools (dashboards, admin panels, vault UI) do so through an identity-aware proxy (IAP) that enforces OIDC authentication and MFA before proxying the connection. The internal services do not have public IP addresses; they are reachable only through the IAP.

```
Operator Browser          Identity-Aware Proxy       Internal Tool
      │                          │                        │
      │ HTTPS GET /vault         │                        │
      ├─────────────────────────►│                        │
      │                          │ No session cookie      │
      │ 302 → OIDC login         │                        │
      │◄─────────────────────────┤                        │
      │                          │                        │
      │ [OIDC + MFA flow]        │                        │
      │                          │                        │
      │ HTTPS GET /vault         │                        │
      │ session cookie (signed)  │                        │
      ├─────────────────────────►│                        │
      │                          │ Validate session       │
      │                          │ Verify MFA completed   │
      │                          │ Check OPA policy       │
      │                          │                        │
      │                          │ GET /vault             │
      │                          │ (internal mTLS)        │
      │                          ├───────────────────────►│
      │                          │◄───────────────────────┤
      │◄─────────────────────────┤                        │
```

---

## Continuous Monitoring and Anomaly Detection

### Monitoring Layers

| Layer | What Is Monitored | Tool | Alert Threshold |
|---|---|---|---|
| Network traffic | Unusual inter-zone communication, port scans | Network policies + eBPF | Any denied connection attempt > 5/min |
| Authentication | Failed authentications, unusual login patterns | SIEM over audit stream | >10 failures/min per identity |
| Authorization | Denied access attempts | OPA decision log + SIEM | >5 denials/min per identity |
| Certificate health | Expiry approaching, revocation | cert-manager alerts | 30 days before expiry |
| Credential anomaly | Credential used from unusual IP or time | SIEM behavioral baseline | Deviation > 3σ from baseline |
| Audit chain | Hash chain break, missing events | Audit integrity monitor | Any gap or hash mismatch |
| Key operations | Unexpected key access or rotation | Vault audit log + SIEM | Any out-of-schedule key operation |

### Behavioral Baselines

The monitoring system maintains behavioral baselines for each service and human identity:

- Normal working hours per identity (derived from 30-day history)
- Normal request volume per identity and resource type
- Normal source IP ranges per identity
- Normal inter-service call graphs

Deviations beyond configurable thresholds (default 3σ) trigger alerts. The alert includes the baseline, the observed value, the identity, the resource, and the timestamp, enabling rapid triage.

### Alert Classification

| Severity | Example | Response SLA |
|---|---|---|
| Critical | Credential used after revocation; audit chain break; canary token access | Immediate; page on-call; auto-isolate if configured |
| High | >50 auth failures in 5 minutes; access to data zone from unauthorized source | 15 minutes; notify security operations |
| Medium | Credential used outside normal hours; certificate expiry < 14 days | 1 hour; create tracking issue |
| Low | Single auth failure; certificate expiry < 30 days | Next business day; log and monitor |

---

## Incident Response and Rapid Revocation

### Revocation Pipeline

When a credential is determined to be compromised or when a user's access must be terminated immediately, the revocation pipeline is activated. Target SLA: credential is revoked within 15 minutes of the revocation order.

**Revocation steps:**

1. Security operations or automated alert triggers a revocation request in the incident tracking system.
2. The revocation pipeline validates the request (requires two-person sign-off for anything other than automated emergency revocation).
3. The IdP immediately suspends the user account or service account.
4. The OCSP responder and CRL are updated to include the revoked certificate serial.
5. The SPIRE server is instructed to stop issuing new SVIDs for the compromised workload identity.
6. Active sessions are terminated by revoking all outstanding refresh tokens.
7. HashiCorp Vault access policies are updated to deny the compromised identity.
8. The revocation event is logged to the immutable audit trail with the initiator identity, reason, and all affected credentials.

### Isolation Procedures

If a workload is suspected to be compromised:

1. The Kubernetes NetworkPolicy for the workload's namespace is updated to deny-all ingress and egress (except audit pipeline writes).
2. The service mesh authorization policy revokes the workload's permissions.
3. The workload's SVID is revoked.
4. The workload pod is cordoned (no new traffic) and a forensic snapshot is taken before termination.
5. Logs from the workload's entire lifetime are preserved in the forensic evidence store.

### Evidence Preservation

During incident response, the following evidence is preserved per chain-of-custody requirements:

- Full audit stream for the affected identity from the 48 hours preceding the incident
- Network flow logs for the affected workload
- Application logs from the affected service (WORM copy)
- Any artifact signed by the compromised signing credential
- SVID issuance history from SPIRE for the compromised workload

All evidence is tagged with the incident ID, hashed with SHA-256, and the hash is recorded in the incident tracking system to ensure integrity.

---

## Compliance Mapping

This zero-trust architecture directly implements or contributes to the following NIST 800-53 controls:

| ZTA Component | NIST 800-53 Control | Contribution |
|---|---|---|
| Default-deny policy | AC-3, SC-7 | Access enforcement and boundary protection |
| OIDC + MFA | IA-2, IA-4, IA-5 | Identification, authentication, authenticator management |
| ABAC policy engine | AC-3, AC-5 | Fine-grained access enforcement, separation of duties |
| mTLS service mesh | SC-8, SC-13 | Transmission confidentiality, cryptographic protection |
| SPIFFE/SVID | IA-4, SC-12 | Service identifier management, key establishment |
| Short TTL credentials | IA-5, CA-7 | Authenticator management, continuous monitoring |
| Immutable audit trail | AU-2, AU-12 | Event logging, audit record generation |
| Continuous monitoring | CA-7, SI-2 | Continuous monitoring, flaw detection |
| Revocation pipeline | IA-5, AC-2 | Authenticator management, account management |
| Micro-segmentation | SC-7, AC-5 | Boundary protection, separation of duties |

Full control mapping details are in [../nist-800-53/CONTROL-MAPPINGS.md](../nist-800-53/CONTROL-MAPPINGS.md).

---

## Attestation and Review Procedures

### Quarterly Architecture Review

Each quarter, the platform security team performs a review of the zero-trust architecture against the current implementation:

1. **Communication graph audit:** Verify that the implemented NetworkPolicy and service mesh authorization policy match the documented communication graph. Identify any undocumented paths.
2. **Identity inventory audit:** Verify that all human and service identities in the IdP and SPIRE match the IaC-defined identity inventory. Identify orphaned identities.
3. **Policy drift detection:** Compare deployed OPA policy bundles against version-controlled policy source. Any drift is a critical finding.
4. **Certificate health review:** Review expiry dates and rotation logs for all certificates in the trust hierarchy.
5. **Anomaly baseline review:** Review the behavioral baselines for accuracy; update thresholds if legitimate patterns have shifted.

### Annual Architecture Attestation

The platform CISO signs an annual attestation that the zero-trust architecture is implemented as documented and that material deviations have been identified, risk-accepted, and scheduled for remediation. The attestation is signed with the CISO's ECDSA-P256 signing certificate and stored in the compliance evidence archive.

### Change Management

Any change to the zero-trust architecture that affects:

- The default-deny posture (any change to default NetworkPolicy or service mesh policy)
- The trust hierarchy (new or revoked CA certificates)
- The authentication requirements (TTL changes, MFA requirements)
- The communication graph (new inter-zone paths)

...requires a security change request, a threat model update, and approval by the platform security owner before merge.

---

## Implementation Phases

### Q2 2026 — Foundation

| Deliverable | Description | Status |
|---|---|---|
| Default-deny NetworkPolicy | All namespaces have default-deny NetworkPolicy | In Progress |
| Service mesh deployment | Istio or Linkerd deployed in all production namespaces | In Progress |
| OIDC integration | All human access uses OIDC + MFA | Implemented |
| SPIFFE/SPIRE deployment | All Kubernetes workloads have SVID identities | In Progress |
| IAP for internal tools | Identity-aware proxy in front of Vault, dashboards | In Progress |

### Q3 2026 — Hardening

| Deliverable | Description | Status |
|---|---|---|
| OPA policy engine | ABAC policy enforcement at service mesh | Planned |
| HSM-backed signing service | Artifact signing keys in HSM; separated from build pipeline | Planned |
| Canary tokens | Synthetic tripwire credentials deployed | Planned |
| Behavioral baselines | 30-day baseline established for all identities | Planned |
| SIEM integration | Audit stream connected to SIEM; alert rules active | Planned |

### Q4 2026 — Validation

| Deliverable | Description | Status |
|---|---|---|
| Penetration test | External ZTA-focused penetration test | Planned |
| Red team exercise | Internal red team exercise against micro-segmentation | Planned |
| Annual attestation | First annual CISO attestation of ZTA compliance | Planned |
| Communication graph automation | Automated comparison of deployed policy vs. documented graph | Planned |
| Full continuous monitoring | All monitoring layers active with defined response SLAs | Planned |
