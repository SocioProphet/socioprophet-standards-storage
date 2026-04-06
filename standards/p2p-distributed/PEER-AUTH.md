# Peer Authentication & Authorization

This document uses RFC 2119 language: **MUST**, **SHOULD**, **MAY**.

## Peer Identification

- Every peer **MUST** possess an ECDSA-P256 key pair.
- Peer ID **MUST** be `SHA-256(public_key)` (32-byte hex string).
- A peer **MUST** prove its identity by signing a challenge nonce with its private key during the
  TLS 1.3 handshake; the verifier **MUST** check the signature against the claimed public key.
- Peer IDs **MUST NOT** be reused after key rotation; the old Peer ID is deprecated alongside the
  old key (see [CRYPTO-BINDINGS.md](CRYPTO-BINDINGS.md)).

## Capability-Based Access Control

- Read access is granted to any peer that knows the discovery key:
  `discovery_key = SHA-256(public_key)`.
- Write access (append to a hypercore) **MUST** be limited to explicitly authorised writers.
- Append-only semantics **MUST** be enforced at the storage layer; overwrite operations **MUST**
  be rejected.
- Capability revocation **MUST** be recorded as a signed deprecation entry in the writer's log.
- Applications **MUST NOT** rely solely on network-level controls for access enforcement;
  cryptographic capability checks **MUST** be the authoritative gate.

## Peer Reputation

- Implementations **SHOULD** track peer behaviour metrics: availability, data integrity, response
  latency, and anomalous request rates.
- Peers that fail integrity checks or exceed anomaly thresholds **MUST** be downgraded or banned.
- Reputation changes **MUST** be recorded in the local audit log
  (see [AUDIT-LOGGING.md](AUDIT-LOGGING.md)).
- Reputation data **MAY** be shared with trusted peers via a gossip protocol; gossip messages
  **MUST** be signed by the originating peer.

## Bootstrap & Trust Establishment

- Initial peer discovery **MUST** use a DHT keyed by the discovery key, or a rendezvous server
  authenticated via OIDC or mTLS (see [PEER-DISCOVERY.md](PEER-DISCOVERY.md)).
- First-time trust establishment **SHOULD** be verified out-of-band (QR code, voice fingerprint,
  or equivalent).
- Public keys of critical peers (e.g. archival peers, rendezvous servers) **MUST** be pinned.
- All trust establishment events **MUST** be written to the local audit log.

## Decentralised PKI

- P2P systems operate without a central certificate authority.
- A peer's public key is its self-signed certificate; peer reputation replaces the traditional
  trust anchor.
- Applications relying on P2P identity **MUST** be transparent about the decentralised trust model
  and **MUST** expose verification status to end users.
- Certificate pinning **MUST** be applied for peers that hold privileged roles (archivers,
  rendezvous servers, bootstrap nodes).

## References

- [INDEX.md](INDEX.md) — P2P standards master index
- [CRYPTO-BINDINGS.md](CRYPTO-BINDINGS.md) — Algorithm and key management details
- [PEER-DISCOVERY.md](PEER-DISCOVERY.md) — Secure bootstrapping procedures
- NIST SP 800-53 Rev. 5, IA-2, IA-3: <https://csrc.nist.gov/publications/detail/sp/800-53/rev-5>
