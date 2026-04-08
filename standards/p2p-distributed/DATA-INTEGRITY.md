# P2P Data Integrity & Verification

This document uses RFC 2119 language: **MUST**, **SHOULD**, **MAY**.

## Append-Only Log Integrity

- Every log entry **MUST** contain the SHA-256 hash of the immediately preceding entry, forming a
  cryptographic hash chain.
- The first entry (genesis) **MUST** contain a timestamp and a random nonce to prevent precomputed
  chain attacks.
- Any break in the hash chain **MUST** be treated as evidence of tampering; affected entries
  **MUST** be quarantined and the event logged immediately.
- Offline verification of the chain **MUST** be possible using only the genesis entry and a local
  copy of the log.

## Merkle Tree Verification

- Hyperdrive and equivalent distributed filesystems **MUST** maintain a Merkle tree over file
  blocks.
  - Leaf hash: `SHA-256(block_content)` (default block size: 64 KB).
  - Parent hash: `SHA-256(left_child_hash || right_child_hash)`.
  - Root hash is the complete directory fingerprint.
- The root hash **MUST** be signed by the writer (ECDSA-P256) and stored in the directory
  metadata entry.
- Peers **MUST** verify the root hash signature before trusting any Merkle proof.
- Partial-tree proofs **MUST** be supported so peers can verify individual blocks without
  downloading the entire tree.

## Proof of Storage

- Implementations **MUST** support a challenge-response protocol to verify that a peer actually
  holds claimed data:
  1. Challenger selects a random block index and sends a nonce.
  2. Prover returns `SHA-256(block_content || nonce)`.
  3. Challenger verifies the response against the known block hash and nonce.
- Proof-of-storage checks **MUST** be performed at least once every 24 hours for critical data.
- All verification events (success and failure) **MUST** be recorded in the audit log.

## Block-Level Integrity

- Files **MUST** be split into 64 KB blocks (configurable, but consistent within a deployment).
- Each block **MUST** have an individual SHA-256 hash stored in the block map.
- The block map **MUST** be signed by the writer with ECDSA-P256.
- Peers **MUST** verify each downloaded block against its hash before writing to local storage.
- A block failing verification **MUST NOT** be written to storage; the peer **MUST** re-request the
  block from another source and log the failure.

## Replication Verification

- Before accepting a replicated dataset, the receiving peer **MUST** compare the root Merkle hash
  against the value in the writer's signed log entry.
- Hash comparison **MUST** occur after replication completes (full-set verification) and **MAY**
  also occur incrementally during transfer (block-level verification).
- If the post-replication hash does not match the expected value, the peer **MUST** discard the
  data, log the anomaly, and re-request from an alternative peer.
- All replication verification events **MUST** be written to the audit log
  (see [AUDIT-LOGGING.md](AUDIT-LOGGING.md)).

## References

- [INDEX.md](INDEX.md) — P2P standards master index
- [CRYPTO-BINDINGS.md](CRYPTO-BINDINGS.md) — Hashing and signature algorithms
- [REPLICATION.md](REPLICATION.md) — Replication procedures and verification
- NIST SP 800-53 Rev. 5, SI-7: <https://csrc.nist.gov/publications/detail/sp/800-53/rev-5>
