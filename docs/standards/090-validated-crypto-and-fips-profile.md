# Validated Crypto and FIPS Profile (Normative)

This document uses RFC 2119 language: **MUST**, **SHOULD**, **MAY**.

## 1. Purpose
This standard defines how repositories in the SourceOS / SocioProphet stack may claim a FIPS-ready or validated-crypto posture without collapsing into hand-wavy marketing.

## 2. Core rule
A repository, build, or deployment **MUST NOT** claim a FIPS posture merely because it uses an approved algorithm.

Claims about FIPS posture **MUST** identify:
- the cryptographic module or provider path,
- the operational environment in which that module/provider is valid,
- the configuration path that activates the approved profile,
- the evidence proving the profile was selected at runtime.

## 3. Crypto profile split
Repositories **MUST** distinguish between at least two profiles:

### 3.1 Default profile
The default profile may optimize for current interoperability and performance.
It **MUST** still publish its algorithms, key handling assumptions, and verification instructions.

### 3.2 FIPS / validated profile
The FIPS profile exists for environments requiring approved/validated module paths.
The FIPS profile **MUST** publish:
- approved hash algorithms,
- approved signature algorithms,
- approved AEAD / encryption modes,
- TLS and transport expectations,
- the module/provider selection method,
- self-test / runtime verification expectations where applicable.

## 4. Boundary publication
Every repository that performs cryptographic operations **MUST** publish a crypto-boundary note that answers:
- which operations occur inside the validated/provider boundary,
- which operations occur outside it,
- which artifacts rely on semantic/governance hashes,
- which artifacts rely on transport/receipt hashes,
- what changes when the FIPS profile is enabled.

## 5. Build and runtime evidence
A FIPS-profile-capable repository **MUST** have at least one CI or integration path that proves:
- the intended validated/provider profile can be selected,
- the application or verifier does not silently fall back to a non-approved path,
- release evidence records which profile was exercised.

## 6. Hash domain alignment
The FIPS profile **MUST** preserve the semantic/governance hash domain as a stable long-lived identifier domain.
If transport/receipt hashing differs from the semantic/governance domain, the repository **MUST** publish the mapping and the boundary between them.

## 7. Release claims
Release notes or public docs **MUST NOT** use vague language such as "FIPS compliant" without a linked profile note and evidence path.
The minimum acceptable language is profile-specific and evidence-backed.

## 8. Relationship to release evidence
Any repository claiming the FIPS profile **MUST** include, in release evidence:
- profile identifier,
- module/provider reference,
- verification instructions,
- any caveats or operational constraints.
