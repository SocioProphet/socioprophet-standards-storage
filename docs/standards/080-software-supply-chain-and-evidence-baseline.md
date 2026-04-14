# Software Supply Chain and Evidence Baseline (Normative)

This document uses RFC 2119 language: **MUST**, **SHOULD**, **MAY**.

## 1. Purpose
This standard defines the minimum software supply-chain evidence that every governed repository and release process in the SourceOS / SocioProphet stack must produce.

The goal is not badge collection. The goal is replayable, inspectable, machine-checkable release evidence.

## 2. Minimum required release evidence
Every releaseable repository **MUST** produce, at minimum:

1. a Software Bill of Materials (SBOM),
2. a provenance / build attestation,
3. a cryptographic signature over release artifacts or release manifests,
4. vulnerability scan output plus any approved exceptions,
5. a versioned changelog or equivalent release note,
6. a stable mapping from repository version to published evidence artifacts.

## 3. SBOM requirements
- Repositories **MUST** support at least one open SBOM format.
- The preferred interoperable set is:
  - SPDX for broad ecosystem portability,
  - CycloneDX where service/operational inventory detail is required.
- SBOMs **MUST** include direct and transitive dependencies where the build system can resolve them.
- SBOMs **SHOULD** be emitted per release artifact, not just per repository.

## 4. Provenance requirements
- A provenance statement **MUST** identify:
  - source repository,
  - source revision,
  - build workflow or builder,
  - artifact identifiers,
  - build time.
- The provenance format **SHOULD** be aligned with broadly adopted supply-chain attestation practice (for example, SLSA-style provenance or equivalent).
- Provenance **MUST** be signed or otherwise integrity-protected.

## 5. Artifact signing
- Release artifacts or release manifests **MUST** be signed.
- Signature verification instructions **MUST** be published in-repo.
- Repositories **MUST NOT** require human memory of an ad hoc signing ritual to verify authenticity.

## 6. Vulnerability and exception evidence
- Repositories **MUST** run dependency and secret scanning before release.
- Any unresolved vulnerability that is intentionally accepted **MUST** have:
  - an identifier,
  - an owner,
  - an expiry/review date,
  - a mitigation note.
- Exception records **SHOULD** be linkable from release evidence.

## 7. CI gates
The default CI supply-chain gate **MUST** fail when:
- SBOM generation fails,
- provenance generation fails,
- signature generation fails,
- required vulnerability scans fail or policy thresholds are exceeded,
- required evidence artifacts are missing from the release output.

## 8. Repository-local requirements
Every governed repository **MUST** document:
- the command(s) that generate release evidence,
- where release evidence is stored,
- how to verify signatures,
- which evidence is expected for pull requests vs tagged releases.

## 9. Relationship to other standards
- This standard complements the identity control plane composition and governance-artifact bindings.
- It does not define protocol semantics.
- It defines the minimum release evidence posture expected before higher-assurance compliance profiles are claimed.
