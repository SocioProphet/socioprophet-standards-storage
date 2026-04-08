# Security Standard: Identity, Authorization, and Policy

## Identity
- User and service identity SHOULD use OIDC/OAuth2.
- Service-to-service traffic SHOULD use mTLS when operating in a hostile or multi-tenant environment.

## Authorization
- Access decisions MUST be centralized in a policy service.
- Policy decisions MUST be logged as immutable audit events (PolicyEvaluated/AccessGranted/AccessDenied).

## Data minimization
- ChatOps outputs MUST support redaction and least-privilege views.

## Related Standards

- `090-fips-nist-compliance.md` — FIPS 140-2/140-3 cryptographic requirements and approved algorithms
- `091-nist-800-53-control-mappings.md` — NIST 800-53 control mappings (AC-2, AC-3, IA-2, IA-5, IA-8)
- `092-zero-trust-nist-800-207.md` — Zero-trust architecture (NIST 800-207)
- `093-forensic-audit-nist-800-88.md` — Forensic-ready audit trail requirements
- `095-orchestration-fips-compliance.md` — Kubernetes OIDC and RBAC configuration

## Implementation Evidence

- OIDC provider integration: `SocioProphet/sociosphere/auth/oidc.py`
- RBAC policy configuration: `SocioProphet/sociosphere/auth/rbac-policy.yaml`
- Policy audit logging: `SocioProphet/sociosphere/observability/audit-pipeline.yaml`
- mTLS service mesh policy: `SocioProphet/sociosphere/mesh/mtls-policy.yaml`

