# Crypto Profiles and Hash Domains (Normative)

## 1. Purpose
This standard prevents a common category error: treating all hashes and signatures in the system as if they live in the same domain and serve the same job. The stack needs at least two distinct domains:
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

## 3. Transport/receipt hash domain
Use this domain for:
- TriTRPC frame/receipt derivation
- transport-local verification artifacts
- hot-path receipt computations that do not become long-lived governance identifiers unless explicitly re-published in semantic form

## 4. Profiles
### 4.1 Default profile
The default profile prioritizes deterministic interoperability and current repository behavior. It **MAY** preserve the existing TriTRPC choices for the hot path, provided the choices are published and fixture-tested.

### 4.2 FIPS profile
The FIPS profile exists for environments that require approved/validated module paths. Requirements:
- Cryptographic operations that claim FIPS posture **MUST** execute inside a validated module boundary or an explicitly documented validated-provider deployment.
- The profile **MUST** publish its approved hash, AEAD, and signature suite.
- The profile **MUST** publish build/runtime guidance proving how the validated path is actually selected.
