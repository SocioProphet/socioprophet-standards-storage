# Peer Discovery & Bootstrapping

This document uses RFC 2119 language: **MUST**, **SHOULD**, **MAY**.

## Discovery Key Protocol

- Peers **MUST** advertise their discovery key (`SHA-256(public_key)`) rather than their raw
  public key over any network-visible channel.
- The mapping from discovery key to public key **MUST** be revealed only after a successful TLS
  1.3 handshake, preventing unauthenticated enumeration of peer identities.
- Any system that publishes raw public keys in DHT records or discovery announcements **MUST NOT**
  be used.

## Distributed Hash Table (DHT)

- DHT entries **MUST** store peer location (IP address, port) keyed by discovery key.
- DHT responses **SHOULD** be anonymised (e.g. responses omit requester addresses from forwarded
  records) to reduce correlation attacks.
- DHT nodes **MUST** enforce rate limits to mitigate Sybil and enumeration attacks.
- Network-layer anonymity (e.g. Tor) **MAY** be layered on top of DHT for deployments with strict
  network-observer threat models; this **MUST** be documented in the deployment architecture.

## Direct Peer Connection

- Once a peer address is resolved, the connection **MUST** be established with TLS 1.3
  (see [CRYPTO-BINDINGS.md](CRYPTO-BINDINGS.md)).
- The TLS handshake **MUST** include peer authentication (both sides present their public key and
  sign the transcript).
- All application data **MUST** remain encrypted for the session's lifetime.
- Connections **MUST** use cipher suites with forward secrecy; RSA key exchange **MUST NOT** be
  used.

## Rendezvous Servers

- Rendezvous servers **MAY** be used to assist initial peer discovery when DHT is unavailable.
- Rendezvous servers **MUST** be authenticated via OIDC or mTLS before use.
- Rendezvous servers **MUST NOT** retain peer address information beyond the active session
  (ephemeral relay only).
- All rendezvous server interactions **MUST** be recorded in the local audit log.

## Bootstrap Security

- Initial bootstrap peers **MUST** be obtained via a secure, out-of-band channel (configuration
  file signed by an operator, QR code, or verified voice fingerprint).
- Public keys of bootstrap peers **MUST** be pinned in the node configuration.
- Pinned keys **MUST** be re-verified at least quarterly; any mismatch **MUST** trigger an alert
  and audit log entry.
- Nodes **MUST NOT** automatically trust new bootstrap peers discovered solely through the network
  without an explicit operator action or out-of-band verification step.

## References

- [INDEX.md](INDEX.md) — P2P standards master index
- [CRYPTO-BINDINGS.md](CRYPTO-BINDINGS.md) — TLS 1.3 and key exchange specification
- [PEER-AUTH.md](PEER-AUTH.md) — Peer identity and capability-based access
- [AUDIT-LOGGING.md](AUDIT-LOGGING.md) — Audit events for discovery and bootstrap
- RFC 8446 (TLS 1.3): <https://tools.ietf.org/html/rfc8446>
