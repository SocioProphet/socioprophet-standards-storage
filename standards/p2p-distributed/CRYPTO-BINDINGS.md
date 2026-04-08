# Cryptographic Bindings for P2P Systems

This document uses RFC 2119 language: **MUST**, **SHOULD**, **MAY**.

## Approved Algorithms

| Purpose | Algorithm | Notes |
|---|---|---|
| Digital signatures | ECDSA-P256 | ECDSA-P384 for high-security deployments |
| Hashing | SHA-256 | SHA-384 or SHA-512 MAY be used for higher assurance |
| Key exchange | ECDH over P-256 (or P-384) | Forward secrecy required |
| Symmetric encryption | AES-256-GCM | NIST-approved AEAD construction |
| Message authentication | HMAC-SHA-256 | |
| Transport | TLS 1.3 | TLS 1.2 MUST NOT be used for new deployments |

Unapproved algorithms (MD5, SHA-1, RSA-1024, DES, 3DES, RC4) **MUST NOT** be used.

## Hypercore Entry Signatures

- Each log entry **MUST** be signed by the writer's ECDSA-P256 private key.
- Entry hash: `SHA-256(entry_data)`.
- Signature: `ECDSA_sign(private_key, entry_hash)`.
- Peers **MUST** verify the signature before accepting any entry.
- The public key **MUST** serve as the peer's canonical identity.
- Signature verification **MUST** occur on every peer discovery handshake.

## Hyperdrive File Integrity

- Each file **MUST** be hashed with SHA-256 at write time and the hash stored in the metadata entry.
- Files **MUST** be split into 64 KB blocks; each block **MUST** have an individual SHA-256 hash.
- A Merkle tree **MUST** be maintained over block hashes.
  - Leaf node: `SHA-256(block_content)`.
  - Parent node: `SHA-256(left_child_hash || right_child_hash)`.
  - Root hash = complete directory fingerprint.
- The block map (root hash + per-block hashes) **MUST** be signed by the writer with ECDSA-P256.
- Peers **MUST** verify each block against its hash on download.

## Discovery Key Binding

- Discovery key: `SHA-256(public_key)`.
- Peers **MUST** advertise only the discovery key over the network; the raw public key **MUST NOT**
  be broadcast to unauthenticated observers.
- Only peers that know the discovery key can locate one another, preventing unauthorised peer lookup.

## Peer-to-Peer Encryption

- All inter-peer connections **MUST** use TLS 1.3.
- Session key establishment **MUST** use ECDH over P-256 (or P-384), providing forward secrecy.
- All application data **MUST** be encrypted with AES-256-GCM.
- Message authentication **MUST** use HMAC-SHA-256 where an additional integrity layer is required
  outside of the TLS record layer.

## Multi-Writer Consensus (multifeed)

- Each writer **MUST** maintain a separate append-only log (hypercore) with ECDSA-P256 signatures.
- A CRDT or equivalent conflict-free replicated data structure **MUST** be used for consensus.
- Cryptographic binding between feeds **MUST** be recorded in each writer's log.
- Conflict resolution events **MUST** be appended to the audit log (see [AUDIT-LOGGING.md](AUDIT-LOGGING.md)).

## Key Rotation

- Key rotation **MUST** be announced as a signed entry in the peer's immutable append-only log.
- Old keys **MUST** be deprecated rather than deleted; their deprecation entry **MUST** be signed
  by both the old and new key.
- Peers **MUST** verify the rotation announcement before trusting the new key.
- An audit trail of all key changes **MUST** be maintained and retained per
  [AUDIT-LOGGING.md](AUDIT-LOGGING.md).
- Compromised keys **MUST** be revoked immediately; a revocation notice **MUST** be published and
  gossiped to all known peers within 1 hour.

## References

- [INDEX.md](INDEX.md) — P2P standards master index
- NIST SP 800-186 (Elliptic Curves): <https://csrc.nist.gov/publications/detail/sp/800-186>
- NIST FIPS 186-5 (DSS): <https://csrc.nist.gov/publications/detail/fips/186/5>
- RFC 8446 (TLS 1.3): <https://tools.ietf.org/html/rfc8446>
