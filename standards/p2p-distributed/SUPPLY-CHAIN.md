# Supply Chain Integrity for P2P Systems

This document uses RFC 2119 language: **MUST**, **SHOULD**, **MAY**.

## SBOM Generation

- Every P2P component **MUST** have a Software Bill of Materials (SBOM) in CycloneDX format.
- SBOMs **MUST** cover both direct and transitive runtime dependencies.
- SBOMs **MUST** be regenerated on every release and on every dependency update.
- Each SBOM file **MUST** be signed with the project's ECDSA-P256 release key; the signature
  **MUST** be published alongside the SBOM.
- The signed SBOM **MUST** be attached to the corresponding GitHub Release artifact.

## Dependency Scanning

- Automated vulnerability scanning (e.g. OWASP Dependency-Check, Grype, or Snyk) **MUST** run in
  CI on every pull request and on a scheduled daily basis.
- Transitive dependencies **MUST** be included in every scan.
- Critical or high-severity CVEs **MUST** block merge until resolved or formally risk-accepted.
- Medium-severity CVEs **MUST** be remediated within 30 days.
- Scan results **MUST** be retained in the audit log for the project.

## Component Signing

- All release artifacts (npm packages, GitHub Release tarballs, Docker images) **MUST** be signed
  with the project's ECDSA-P256 key.
- The signing public key **MUST** be published in the repository and pinned (certificate pinning)
  for automated consumers.
- Signature verification **MUST** be enforced at installation time in automated pipelines.
- If a signing key is compromised, a revocation notice **MUST** be published immediately, and all
  artifacts signed with the compromised key **MUST** be re-signed with a new key and re-released.

## Source Code Integrity

- All commits that modify production code **MUST** be signed with a GPG or SSH key.
- Release tags **MUST** be signed; unsigned tags **MUST NOT** be used to trigger production
  deployments.
- A change log (CHANGELOG.md or equivalent) **MUST** be maintained as an auditable record of all
  releases.
- All changes to main/production branches **MUST** require at least one code review approval
  before merge.

## Build Integrity

- Builds **MUST** be reproducible: given the same source commit and toolchain, the output
  **MUST** be byte-for-byte identical.
- Build artifacts **MUST** be signed with ECDSA-P256 immediately after production.
- Build environments **MUST** be isolated (e.g. ephemeral containers or sandboxed VMs) to prevent
  supply chain injection.
- All build events (start, finish, artifact hashes, signing events) **MUST** be written to an
  append-only build-event audit log.

## Distribution Integrity

- Published packages (npm, PyPI, GitHub Releases) **MUST** include SHA-256 checksums.
- Consumers **MUST** verify checksums and signatures before installing or deploying.
- Package registries used **SHOULD** support package-level signing (e.g. npm provenance, PyPI
  Trusted Publishers).
- Build provenance attestations (SLSA level 2 or higher) **SHOULD** be generated and published
  with each release.

## References

- [INDEX.md](INDEX.md) — P2P standards master index
- [AUDIT-LOGGING.md](AUDIT-LOGGING.md) — Audit trail for supply chain events
- NIST SP 800-53 Rev. 5, SI-2, SI-7: <https://csrc.nist.gov/publications/detail/sp/800-53/rev-5>
- CycloneDX specification: <https://cyclonedx.org/>
- SLSA framework: <https://slsa.dev/>
