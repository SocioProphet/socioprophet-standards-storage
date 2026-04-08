# Zero-Trust Architecture Standard (NIST SP 800-207)

This document uses RFC 2119 language: **MUST**, **SHOULD**, **MAY**.

## 1. Overview

This standard defines zero-trust architecture (ZTA) requirements for the SocioProphet platform, based on NIST SP 800-207 "Zero Trust Architecture". Zero trust removes the assumption of implicit trust within any network perimeter.

**Core principle**: Never trust, always verify. Every request to every resource MUST be authenticated, authorized, and encrypted regardless of its origin.

## 2. Zero-Trust Tenets (NIST 800-207)

The SocioProphet platform MUST implement all seven NIST 800-207 zero-trust tenets:

1. **All data sources and computing services are resources** — Every service (database, API, queue) is treated as a resource that requires authentication.
2. **All communication is secured regardless of network location** — There is no trusted network; all connections MUST be encrypted.
3. **Access to individual enterprise resources is granted on a per-session basis** — No persistent access; authorization is re-evaluated per request.
4. **Access to resources is determined by dynamic policy** — Context-aware access decisions based on identity, device, behavior.
5. **The enterprise monitors and measures the integrity and security posture of all owned and associated assets** — Continuous telemetry from all resources.
6. **All resource authentication and authorization is dynamic and strictly enforced** — Authorization happens before access, not after connection.
7. **The enterprise collects as much information as possible about the current state of assets, network infrastructure, and communications** — Comprehensive observability.

## 3. Identity Verification Requirements

- Every request MUST carry a verifiable identity (OIDC token or mTLS client certificate).
- Identity claims MUST be cryptographically verified by the Policy Enforcement Point (PEP).
- Workload identity MUST use short-lived certificates (SPIFFE/SPIRE) with a **maximum** 24-hour validity period (consistent with `095-orchestration-fips-compliance.md`).
- User identity tokens MUST have a maximum lifetime of 1 hour with refresh allowed.
- Identity verification MUST happen at the network edge AND at the application layer.

## 4. Policy Enforcement Architecture

```
Request → Policy Enforcement Point (PEP)
            ↓
          Policy Decision Point (PDP)
            ↓
          Policy Information Point (PIP)
          [identity store, device posture, context]
```

- A **Policy Enforcement Point (PEP)** MUST be deployed at every service boundary.
- The **Policy Decision Point (PDP)** MUST be highly available (3+ replicas) with failsafe-deny.
- Policy decisions MUST be logged as audit events (see `093-forensic-audit-nist-800-88.md`).
- PDP SHOULD be implemented via Open Policy Agent (OPA) or a compatible FIPS-compliant policy engine.

## 5. Network Segmentation Requirements

- **Default-deny**: All inter-service network traffic MUST be denied by default.
- Explicit allow rules MUST be defined per source-destination-port combination.
- Network policies MUST be managed as code in the GitOps repository.
- Lateral movement between namespaces MUST be blocked unless explicitly permitted.
- External access MUST be via authenticated zero-trust gateway only.

## 6. Micro-Segmentation via Service Mesh

- A service mesh (Istio or Linkerd) MUST enforce mTLS for all inter-pod communication.
- **AuthorizationPolicy** resources MUST use `action: DENY` as the default rule.
- Service-to-service communication MUST be restricted to the minimum required paths.
- All service mesh sidecar certificates MUST be issued by the internal PKI (cert-manager + Vault).
- Service mesh telemetry MUST feed into the central observability stack.

## 7. Device Posture Assessment

- Service workloads MUST attest their integrity via container image signing (Cosign/Sigstore).
- Unsigned or tampered container images MUST be rejected at the admission controller.
- Node posture MUST be assessed via CIS Kubernetes Benchmark Level 2 minimum.
- Pod Security Standards (PSS) at `restricted` level MUST be enforced for all production workloads.

## 8. Continuous Monitoring and Analytics

- All service mesh traffic MUST be recorded as telemetry (latency, errors, request count).
- Anomaly detection SHOULD alert within 5 minutes of detecting unusual access patterns.
- Behavioral baselines MUST be established for each service and updated weekly.
- Security events MUST flow to the centralized SIEM within 60 seconds.
- Access pattern deviations (e.g., service accessing new endpoints) MUST trigger alerts.

## 9. Data Plane Enforcement

- Data access requests MUST be authorized at the application layer, not only at the network layer.
- Database queries MUST be authenticated (no anonymous access).
- Field-level access control SHOULD be implemented for sensitive data (PII, secrets).
- Row-level security (RLS) MUST be implemented in PostgreSQL for multi-tenant data.

## 10. Supply Chain Zero-Trust

- All container images MUST be pulled from a verified, authenticated registry.
- Image provenance MUST be verified via Sigstore/Cosign before execution.
- Software Bill of Materials (SBOM) MUST be generated for all deployable artifacts.
- Third-party dependencies MUST be scanned for vulnerabilities before inclusion.
- Vendored dependencies MUST be pinned to content-hashed versions.

## 11. Certificate and PKI Requirements

- Internal PKI MUST use ECDSA-P256 root CA and issuing CAs.
- Certificate rotation MUST be automated (cert-manager or Vault PKI engine).
- SPIFFE/SPIRE SHOULD be used for workload identity bootstrapping.
- All certificates MUST include SPIFFE URI SANs for Kubernetes workloads.
- Certificate transparency MUST be enabled for the internal PKI audit trail.

## 12. Compliance Verification

Zero-trust posture MUST be verified by:
- CI/CD gates: mTLS posture test on every deployment
- Daily: Automated network policy audit (verify default-deny)
- Weekly: Service mesh authorization policy review
- Monthly: Identity and access review (inactive accounts, over-privileged services)
- Quarterly: Full zero-trust gap analysis against NIST 800-207

## Related Standards

- `050-security-oidc-policy.md` — Identity and authorization baseline
- `090-fips-nist-compliance.md` — Cryptographic requirements
- `091-nist-800-53-control-mappings.md` — NIST 800-53 control mappings (AC-17, CA-9, SC-7)
- `095-orchestration-fips-compliance.md` — Kubernetes implementation

## Implementation Evidence

- Default-deny network policies: `SocioProphet/sociosphere/k8s/network-policies/default-deny.yaml`
- Service mesh AuthorizationPolicies: `SocioProphet/sociosphere/mesh/authorization-policies.yaml`
- OPA policy bundle: `SocioProphet/sociosphere/policy/opa-bundle/`
- SPIFFE/SPIRE configuration: `SocioProphet/sociosphere/k8s/spiffe/`
- Admission controller (image signing): `SocioProphet/sociosphere/k8s/admission/image-signing.yaml`
- Zero-trust gateway: `SocioProphet/sociosphere/k8s/ingress/ztna-gateway.yaml`
