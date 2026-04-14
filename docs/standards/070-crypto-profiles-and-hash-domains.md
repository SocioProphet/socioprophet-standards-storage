# Crypto Profiles and Hash Domains (Normative)

This document uses RFC 2119 language: **MUST**, **SHOULD**, **MAY**.

## 1. Purpose
This standard prevents a common category error: treating all hashes and signatures in the system as if they live in the same domain and serve the same job.

The stack needs at least two distinct domains:
1. **semantic/governance object identity**
2. **transport/receipt verification**

## 2. Semantic/governance hash domain
Use this domain for:
- `aum_digest`
- `policy_hash`
- governance `payload_hash`
- proof artifact content addressing
- HDT decision summary hashes
- cross-repo artifact references

Requirements:
- The minimum interoperable profile **MUST** be `sha256`.
- Objects in this domain **MUST** be derived from a canonical representation.
- Any schema that constrains these fields **SHOULD** use explicit algorithm-prefixed encodings (for example `sha256:<hex>`).

Rationale:
The zero-trust governance schema family already constrains key fields using a `sha256:<hex>` format.
This domain should remain boring, portable, and compatible with tighter federal/compliance profiles.

## 3. Transport/receipt hash domain
Use this domain for:
- TriTRPC frame/receipt derivation
- transport-local verification artifacts
- hot-path receipt computations that do not become long-lived governance identifiers unless explicitly re-published in semantic form

Requirements:
- The default transport profile **MAY** use the existing fast transport-oriented choices already present in TriTRPC.
- The FIPS profile **MUST** use a documented approved/validated module path.
- Transport receipts that need to survive as governance references **MUST** be bridged into the semantic/governance domain with a stable, published mapping rule.

## 4. Profiles
### 4.1 Default profile
The default profile prioritizes deterministic interoperability and current repository behavior.
It **MAY** preserve the existing TriTRPC choices for the hot path, provided the choices are published and fixture-tested.

### 4.2 FIPS profile
The FIPS profile exists for environments that require approved/validated module paths.
Requirements:
- Cryptographic operations that claim FIPS posture **MUST** execute inside a validated module boundary or an explicitly documented validated-provider deployment.
- The profile **MUST** publish its approved hash, AEAD, and signature suite.
- The profile **MUST** publish build/runtime guidance proving how the validated path is actually selected.
- Any algorithm available in the default profile but absent from the FIPS profile **MUST** be called out explicitly.

## 5. Canonicalization
- Any JSON object participating in signing or cross-language hash comparison **MUST** use a canonical JSON profile.
- Any artifact family that does not use JSON **MUST** publish an equally precise canonical signed-bytes rule.

## 6. Test vectors
Each profile **MUST** publish:
- canonical examples,
- cross-language verification vectors,
- negative vectors (tamper, reorder, malformed canonicalization),
- profile selection tests.

## 7. Migration rule
No repo **MAY** silently repurpose a transport-local hash as a governance identifier without publishing:
1. the canonical mapping rule,
2. the algorithm/profile used,
3. the compatibility consequences.
