# P2P & Distributed Systems FIPS Compliance Standards — Index

This document uses RFC 2119 language: **MUST**, **SHOULD**, **MAY**.

## Overview

Peer-to-peer and distributed systems present unique challenges for FIPS 140-2/140-3 compliance.
Unlike client-server architectures, P2P systems have no central authority; trust is established
through cryptographic proofs, append-only audit logs, and capability-based access control.

All systems listed below **MUST** satisfy the controls in this index before deployment in a
government or regulated environment.

## System Categorization

| Category | Systems |
|---|---|
| Append-only logs | Hypercore, multifeed, kappa-core |
| Distributed filesystems | Hyperdrive |
| Data sharing protocols | Dat, dat-node, hashbase, homebase |
| Peer discovery | hyperdiscovery, hyperdb |
| Replication utilities | replicator, mirror-folder, hypercore-archiver |
| Collaborative applications | hypermerge, multifeed-index |

## Cryptographic Requirements by System Type

- Append-only logs **MUST** use ECDSA-P256 signatures on every entry and link entries via SHA-256
  hash chains.
- Distributed filesystems **MUST** enforce Merkle-tree verification (SHA-256 leaf and parent hashes)
  for all stored files.
- Replication utilities **MUST** verify SHA-256 hashes before accepting replicated blocks.
- All inter-peer communication **MUST** use TLS 1.3 with forward-secrecy key exchange (ECDH over
  P-256 or P-384).
- Session encryption **MUST** use AES-256-GCM.

See [CRYPTO-BINDINGS.md](CRYPTO-BINDINGS.md) for the full specification.

## Peer Authentication and Authorization Framework

- Peer identity **MUST** be the public key (or its SHA-256 hash).
- Write access **MUST** be limited to authorised writers; all other peers have read-only capability.
- Capabilities **MUST** be granted via the discovery-key mechanism; discovery key = SHA-256(public_key).
- Revocation **MUST** be recorded as an immutable entry in the peer's append-only log.

See [PEER-AUTH.md](PEER-AUTH.md) for the full specification.

## Data Integrity Verification Standards

- Every append-only log entry **MUST** contain the SHA-256 hash of the previous entry.
- Files stored in Hyperdrive **MUST** be verified against a Merkle tree root hash on every read.
- Replicated data **MUST** be verified block-by-block (64 KB default block size) using SHA-256.
- Peers **MUST** re-verify stored data periodically (proof-of-storage challenge-response).

See [DATA-INTEGRITY.md](DATA-INTEGRITY.md) for the full specification.

## Audit Logging Requirements

- All peer connection, replication, signature-verification, and key-rotation events **MUST** be
  recorded in a local append-only audit log.
- Audit log entries **MUST** be signed with ECDSA-P256 and linked via SHA-256 hash chain.
- Minimum retention: **90 days** local; **7 years** for archived compliance logs.
- Anomalies (hash mismatches, signature failures, unusual peer behaviour) **MUST** be logged
  immediately.

See [AUDIT-LOGGING.md](AUDIT-LOGGING.md) for the full specification.

## Supply Chain Integrity

- Every P2P component **MUST** have a CycloneDX SBOM covering direct and transitive dependencies.
- SBOMs **MUST** be signed with ECDSA-P256.
- Automated vulnerability scanning (OWASP / Grype / Snyk) **MUST** run daily.
- All release artefacts **MUST** be signed and verifiable with a published public key.

See [SUPPLY-CHAIN.md](SUPPLY-CHAIN.md) for the full specification.

## Related Standards Documents

| Document | Purpose |
|---|---|
| [CRYPTO-BINDINGS.md](CRYPTO-BINDINGS.md) | Algorithm selection, key management, signature schemes |
| [PEER-AUTH.md](PEER-AUTH.md) | Trust establishment, capability-based access, decentralised PKI |
| [DATA-INTEGRITY.md](DATA-INTEGRITY.md) | Hash chains, Merkle trees, proof-of-storage |
| [AUDIT-LOGGING.md](AUDIT-LOGGING.md) | Immutable audit trail, retention, anomaly logging |
| [SUPPLY-CHAIN.md](SUPPLY-CHAIN.md) | SBOM, dependency scanning, component signing |
| [PEER-DISCOVERY.md](PEER-DISCOVERY.md) | Discovery key protocol, DHT, bootstrap security |
| [REPLICATION.md](REPLICATION.md) | Pull/push replication, conflict resolution, sync verification |
| [DISASTER-RECOVERY.md](DISASTER-RECOVERY.md) | Backups, off-site replication, recovery testing |
| [INTEGRATION-CHECKLIST.md](INTEGRATION-CHECKLIST.md) | Per-system compliance checklist |

## NIST 800-53 Control Alignment

| Control | Requirement |
|---|---|
| AC-3 | Capability-based access control via discovery key |
| IA-2 | Public-key peer identity with cryptographic proof |
| SC-8 | TLS 1.3 and AES-256-GCM for all inter-peer traffic |
| SC-12 | ECDSA-P256 key management and rotation procedures |
| SC-13 | Approved algorithms only (see CRYPTO-BINDINGS.md) |
| SI-2 | Daily dependency scanning and patching |
| SI-7 | SBOM, component signing, and immutable audit logging |
| SI-12 | Audit log retention: 90 days local, 7 years archived |

## References

- NIST SP 800-53 Rev. 5: <https://csrc.nist.gov/publications/detail/sp/800-53/rev-5>
- NIST SP 800-88: <https://csrc.nist.gov/publications/detail/sp/800-88>
- RFC 8446 (TLS 1.3): <https://tools.ietf.org/html/rfc8446>
- Hypercore Protocol: <https://github.com/hypercore-protocol/hypercore>
- Hyperdrive: <https://github.com/hypercore-protocol/hyperdrive>
- Dat Project: <https://www.datproject.org/>
