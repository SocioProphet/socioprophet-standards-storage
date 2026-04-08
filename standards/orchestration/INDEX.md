# Orchestration Layer FIPS Compliance — Index

- Last updated: 2026-01-27
- Status: Active governance document
- Owner: SocioProphet Platform Security
- Scope: Kubernetes orchestration, container runtimes, service mesh, secrets management

---

## Table of Contents

1. [Introduction](#introduction)
2. [Systems Covered](#systems-covered)
3. [Document Registry](#document-registry)
4. [Compliance Status Summary](#compliance-status-summary)
5. [Cryptographic Standards Applied](#cryptographic-standards-applied)
6. [Disallowed Algorithms](#disallowed-algorithms)
7. [Implementation Timeline: Q2–Q4 2026](#implementation-timeline-q2q4-2026)
8. [Regulatory and Framework Anchors](#regulatory-and-framework-anchors)
9. [Ownership and Review Cadence](#ownership-and-review-cadence)

---

## Introduction

The SocioProphet orchestration layer comprises all infrastructure components responsible for deploying, scheduling, networking, and securing containerized workloads. These systems sit between the application layer (sociosphere) and the underlying compute and storage fabric, and they collectively represent one of the highest-risk surfaces in the platform: they control identity federation, east-west network traffic, secret distribution, and audit event emission.

This index establishes the governance scope for FIPS 140-2/140-3 compliance across the orchestration layer. Every system listed below must operate with FIPS-approved cryptographic modules for all operations involving authentication, authorization, data-in-transit protection, data-at-rest encryption, and audit log integrity.

The orchestration layer governance documents in this directory are normative. They supersede any contradictory configuration guidance from upstream vendor documentation where that guidance would introduce non-FIPS-approved algorithms or weaken the security posture defined by the SocioProphet platform.

### Compliance Philosophy

The orchestration layer applies a **defense-in-depth** model:

- Each system independently enforces FIPS-approved algorithms; no single system is trusted to be the sole enforcement point.
- All inter-system communication uses mTLS with FIPS-approved cipher suites.
- Secrets are never stored in environment variables, container filesystems, or ConfigMaps; they are dynamically injected from Vault at runtime.
- All audit events are cryptographically signed and forwarded to an immutable append-only store within 30 seconds of emission.
- Zero-trust principles (NIST SP 800-207) are applied at every layer: no implicit trust is granted based on network location.

### FIPS Module Boundary

The FIPS module boundary for the orchestration layer is defined as:

- **In-boundary**: all cryptographic operations performed by kube-apiserver, etcd, container runtimes (containerd), service mesh proxies (Envoy/linkerd2-proxy), Vault, and Kubernetes admission controllers.
- **Out-of-boundary**: application-layer cryptography handled by the sociosphere service layer (governed separately by the FIPS compliance index).
- **Interface points**: SPIFFE/SPIRE workload identity issuance, Vault PKI engine certificate issuance, and OIDC token validation at the kube-apiserver.

---

## Systems Covered

| System | Role | Version Baseline | FIPS Module |
|---|---|---|---|
| Kubernetes (kube-apiserver, etcd, kubelet) | Container orchestration | v1.29+ | BoringCrypto / go-fips |
| KubeFed | Multi-cluster federation | v0.10+ | BoringCrypto / go-fips |
| KinD (Kubernetes in Docker) | Local development clusters | v0.22+ | BoringCrypto build tag |
| minikube | Developer laptop clusters | v1.32+ | FIPS-profile flag |
| Istio | Service mesh (production) | v1.21+ | BoringSSL-backed Envoy |
| Linkerd | Service mesh (alternative/edge) | stable-2.15+ | Rustls / ring |
| Docker / containerd | Container runtime | containerd v1.7+ | FIPS-validated snapshotter |
| HashiCorp Vault | Secrets management | v1.15+ | FIPS 140-2 edition |

### System Dependency Graph

```
┌─────────────────────────────────────────────────────┐
│              SocioProphet Workloads                 │
└────────────────────┬────────────────────────────────┘
                     │ Pod scheduling
          ┌──────────▼──────────┐
          │     Kubernetes      │◄──── KubeFed (multi-cluster)
          │  (kube-apiserver)   │◄──── KinD / minikube (dev)
          └────────┬────────────┘
                   │ Pod spec
          ┌────────▼────────────┐
          │    containerd       │◄──── Image signing (Cosign)
          │  (container runtime)│◄──── SBOM / Trivy scanning
          └────────┬────────────┘
                   │ Network
          ┌────────▼────────────┐
          │   Istio / Linkerd   │◄──── Cert-manager / SPIRE
          │   (service mesh)    │
          └────────┬────────────┘
                   │ Secrets
          ┌────────▼────────────┐
          │   HashiCorp Vault   │◄──── OIDC / Kubernetes auth
          │   (secrets manager) │
          └─────────────────────┘
```

---

## Document Registry

| File | System(s) | Status | Last Review |
|---|---|---|---|
| [KUBERNETES-SECURITY.md](./KUBERNETES-SECURITY.md) | Kubernetes | Active | 2026-01-27 |
| [KUBEFED-STANDARDS.md](./KUBEFED-STANDARDS.md) | KubeFed | Active | 2026-01-27 |
| [KIND-STANDARDS.md](./KIND-STANDARDS.md) | KinD | Active | 2026-01-27 |
| [MINIKUBE-STANDARDS.md](./MINIKUBE-STANDARDS.md) | minikube | Active | 2026-01-27 |
| [CONTAINER-RUNTIME-SECURITY.md](./CONTAINER-RUNTIME-SECURITY.md) | Docker / containerd | Active | 2026-01-27 |
| [SERVICE-MESH-STANDARDS.md](./SERVICE-MESH-STANDARDS.md) | Istio / Linkerd | Active | 2026-01-27 |
| [SECRETS-MANAGEMENT.md](./SECRETS-MANAGEMENT.md) | HashiCorp Vault | Active | 2026-01-27 |
| [AUDIT-OBSERVABILITY.md](./AUDIT-OBSERVABILITY.md) | Cross-system audit | Active | 2026-01-27 |
| [INTEGRATION-CHECKLIST.md](./INTEGRATION-CHECKLIST.md) | All systems | Active | 2026-01-27 |

---

## Compliance Status Summary

| System | FIPS 140-2 | FIPS 140-3 Readiness | mTLS Enforced | Secrets via Vault | Audit Logging | CIS Benchmark |
|---|---|---|---|---|---|---|
| Kubernetes | ✅ Compliant | 🔄 In Progress | ✅ Yes | ✅ Yes | ✅ Yes | ✅ Level 2 |
| KubeFed | ✅ Compliant | 🔄 In Progress | ✅ Yes | ✅ Yes | 🔄 Partial | ⬜ Planned |
| KinD | ✅ Compliant (dev) | ⬜ Planned | ✅ Yes | 🔄 Dev-mode | ✅ Yes | ⬜ N/A (dev) |
| minikube | ✅ Compliant (dev) | ⬜ Planned | 🔄 Configured | 🔄 Dev-mode | 🔄 Partial | ⬜ N/A (dev) |
| Istio | ✅ Compliant | 🔄 In Progress | ✅ STRICT | ✅ Yes | ✅ Yes | ✅ Istio Security Best Practices |
| Linkerd | ✅ Compliant | 🔄 In Progress | ✅ Auto mTLS | ✅ Yes | ✅ Yes | ✅ Linkerd Hardening |
| containerd | ✅ Compliant | 🔄 In Progress | N/A | ✅ Yes | ✅ Yes | ✅ CIS Docker |
| Vault | ✅ FIPS Edition | ✅ FIPS 140-3 Edition | ✅ Yes | Authoritative | ✅ Yes | ✅ CIS Vault |

**Legend**: ✅ Done · 🔄 In Progress · ⬜ Planned

---

## Cryptographic Standards Applied

All orchestration layer components must use the following approved cryptographic primitives. Deviation requires a written exception signed by the Platform Security team.

### Symmetric Encryption

| Algorithm | Key Length | Approved Use |
|---|---|---|
| AES-GCM | 256-bit | etcd encryption at rest, Vault seal, container image layer encryption |
| AES-CBC with PKCS#7 | 256-bit | Legacy etcd providers only (migration target: AES-GCM) |
| ChaCha20-Poly1305 | 256-bit | Linkerd proxy data plane only (via ring crate FIPS build) |

### Asymmetric and Key Exchange

| Algorithm | Key Size | Approved Use |
|---|---|---|
| ECDSA | P-256, P-384 | mTLS certificates, Cosign image signing, SPIFFE SVIDs |
| RSA-PSS | 3072-bit minimum | Legacy certificate authorities (migration target: ECDSA) |
| ECDH | P-256 | TLS 1.3 key exchange (via X25519 is disallowed) |
| Ed25519 | 256-bit | Git commit signing only; not used in FIPS module boundary |

### Hash Functions

| Algorithm | Approved Use |
|---|---|
| SHA-256 | Certificate fingerprints, image digests, HMAC-SHA-256 |
| SHA-384 | TLS 1.3 HMAC, PKI certificate signatures |
| SHA-512 | Audit log integrity hashes |
| SHA-3 (256, 512) | Future: post-quantum transition planning |

### TLS Configuration

All TLS endpoints in the orchestration layer must enforce:

```
TLS Minimum Version: TLSv1.2 (production); TLSv1.3 preferred
Allowed Cipher Suites (TLS 1.2):
  - TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384
  - TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384
  - TLS_ECDHE_ECDSA_WITH_AES_128_GCM_SHA256
  - TLS_ECDHE_RSA_WITH_AES_128_GCM_SHA256
TLS 1.3 (automatically compliant):
  - TLS_AES_256_GCM_SHA384
  - TLS_AES_128_GCM_SHA256
  - TLS_CHACHA20_POLY1305_SHA256 (Linkerd only)
```

---

## Disallowed Algorithms

The following algorithms are explicitly prohibited across all orchestration layer components. Any configuration that enables these algorithms must be treated as a critical security finding and remediated immediately.

| Algorithm | Reason | Migration Path |
|---|---|---|
| MD5 | Cryptographically broken | SHA-256 or SHA-384 |
| SHA-1 | Collision attacks demonstrated | SHA-256 or SHA-384 |
| DES / 3DES | Inadequate key length, SWEET32 | AES-256-GCM |
| RC4 | Statistically biased keystream | AES-256-GCM |
| TLS 1.0 / TLS 1.1 | Known protocol weaknesses | TLS 1.2 minimum |
| RSA-PKCS1 v1.5 (decrypt) | Padding oracle (PKCS#1 v1.5) | RSA-OAEP or ECDH |
| X25519 / Curve25519 | Not FIPS-approved (yet) | P-256 ECDH |
| DSA | Weak parameter generation history | ECDSA P-256 |
| SSLv2 / SSLv3 | POODLE, DROWN | TLS 1.2+ |

---

## Implementation Timeline: Q2–Q4 2026

### Q2 2026 (April – June)

| Milestone | Owner | Target Date | Status |
|---|---|---|---|
| Kubernetes kube-apiserver FIPS build deployment (all clusters) | Platform Eng | 2026-04-15 | 🔄 In Progress |
| etcd AES-256-GCM encryption at rest for all namespaces | Platform Eng | 2026-04-30 | 🔄 In Progress |
| Vault FIPS 140-3 edition upgrade (primary cluster) | Security Eng | 2026-05-15 | ⬜ Planned |
| Istio BoringSSL Envoy rollout across all production namespaces | Platform Eng | 2026-05-31 | ⬜ Planned |
| Cosign image signing enforced at admission (all registries) | DevSecOps | 2026-06-15 | ⬜ Planned |
| KubeFed mTLS inter-cluster hardening | Platform Eng | 2026-06-30 | ⬜ Planned |

### Q3 2026 (July – September)

| Milestone | Owner | Target Date | Status |
|---|---|---|---|
| Vault FIPS 140-3 upgrade (DR and secondary clusters) | Security Eng | 2026-07-15 | ⬜ Planned |
| SPIRE workload identity rollout (replaces self-signed SVIDs) | Security Eng | 2026-07-31 | ⬜ Planned |
| KinD / minikube FIPS-build enforcement in CI pipelines | DevSecOps | 2026-08-15 | ⬜ Planned |
| OpenSearch audit log pipeline — all clusters | Observability | 2026-08-31 | ⬜ Planned |
| Linkerd ambient mesh evaluation (FIPS posture assessment) | Platform Eng | 2026-09-15 | ⬜ Planned |
| CIS Kubernetes Benchmark Level 2 — automated scanning | Security Eng | 2026-09-30 | ⬜ Planned |

### Q4 2026 (October – December)

| Milestone | Owner | Target Date | Status |
|---|---|---|---|
| Full FIPS 140-3 compliance attestation — all in-boundary systems | Security Eng | 2026-10-31 | ⬜ Planned |
| Third-party penetration test — orchestration layer | External | 2026-11-15 | ⬜ Planned |
| Post-quantum cryptography readiness assessment | Research | 2026-11-30 | ⬜ Planned |
| Annual compliance review and documentation refresh | Security Eng | 2026-12-15 | ⬜ Planned |
| FIPS module certificate submissions (CMVP) | Security Eng | 2026-12-31 | ⬜ Planned |

---

## Regulatory and Framework Anchors

The orchestration layer governance is anchored to the following frameworks and standards:

| Framework | Applicable Controls | Document References |
|---|---|---|
| NIST SP 800-53 Rev 5 | AC-2, AC-3, AC-17, AU-2, AU-9, IA-2, IA-5, SC-8, SC-28, SI-3, SI-7 | INTEGRATION-CHECKLIST.md |
| NIST SP 800-190 | Container security controls: image signing, runtime isolation, secrets | CONTAINER-RUNTIME-SECURITY.md |
| NIST SP 800-204 | Service mesh security (microservices) | SERVICE-MESH-STANDARDS.md |
| NIST SP 800-207 | Zero-trust architecture implementation | SERVICE-MESH-STANDARDS.md, KUBERNETES-SECURITY.md |
| CIS Kubernetes Benchmark v1.9 | Level 2 hardening for kube-apiserver, etcd, kubelet | KUBERNETES-SECURITY.md |
| CIS Docker Benchmark v1.6 | Container runtime hardening | CONTAINER-RUNTIME-SECURITY.md |
| FIPS 140-2 / 140-3 | Cryptographic module validation | All documents |
| STIG Kubernetes v1r10 | DoD hardening guidance (informative) | KUBERNETES-SECURITY.md |

---

## Ownership and Review Cadence

| Role | Responsibility |
|---|---|
| Platform Security Lead | Owns this index; approves all exceptions; signs off on quarterly reviews |
| Platform Engineering | Implements configuration standards; maintains CI enforcement |
| DevSecOps | Maintains image signing, scanning pipelines, and CI/CD security controls |
| Observability Engineering | Owns audit log pipelines, dashboards, and alerting rules |
| Security Engineering | Owns Vault, SPIRE, cert-manager; conducts compliance assessments |

**Review cadence**: This document and all documents in this directory are reviewed quarterly. Emergency amendments are permitted with dual approval from the Platform Security Lead and one other Security Engineering principal. All changes are committed to this repository with a signed commit and linked to an ADR if the change represents a policy decision.
