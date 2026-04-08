# P2P Audit Logging

This document uses RFC 2119 language: **MUST**, **SHOULD**, **MAY**.

## Mandatory Audit Events

The following events **MUST** be recorded in the local audit trail:

| Event class | Minimum fields |
|---|---|
| Peer connection | peer_id, direction (in/out), timestamp, duration |
| Peer disconnection | peer_id, reason (clean/timeout/error), timestamp |
| Data replication | feed_key, block_range, source_peer, success, hash_verified |
| Signature verification | entry_index, result (pass/fail), peer_id, timestamp |
| Key rotation | old_key_hash, new_key_hash, rotation_type, timestamp |
| Anomaly detected | anomaly_type, peer_id, details, timestamp |
| Write attempt | writer_id, feed_key, entry_index, authorised (bool), timestamp |
| Policy violation | peer_id, violation_type, action_taken, timestamp |
| Audit log rotation | old_log_hash, new_log_start, timestamp |

## Immutable Log Storage

- The local audit log **MUST** use an append-only format; modification or deletion of existing
  entries **MUST** be prevented at the storage layer.
- Each audit entry **MUST** contain the SHA-256 hash of the previous entry (hash chain identical
  to the pattern in [DATA-INTEGRITY.md](DATA-INTEGRITY.md)).
- Each audit entry **MUST** be signed with the node's ECDSA-P256 key.
- Any break in the audit hash chain **MUST** itself be logged as a critical anomaly and trigger an
  alert.
- Minimum local retention: **90 days** (configurable to longer).

## Centralised Collection (optional)

- Nodes **MAY** export audit logs to a centralised syslog collector.
- Exported entries **MUST** retain the original ECDSA-P256 signatures so that authenticity can be
  verified independently of the exporting node.
- Centralised storage **MUST** use WORM (Write Once Read Many) semantics or equivalent immutable
  archival.
- Archived compliance logs **MUST** be retained for a minimum of **7 years**.

## Anomaly Logging

The following conditions **MUST** trigger an immediate anomaly log entry:

- Peer disconnects without a clean TLS shutdown.
- Data block hash mismatch on download or proof-of-storage check.
- Signature verification failure for any log entry or block map.
- Unusual peer behaviour: request rate exceeds the configured per-peer threshold.
- Clock skew between local time and peer-reported timestamp exceeds 5 minutes.
- Attempted write by an unauthorised peer.

Anomaly entries **MUST** include enough context to support forensic investigation (peer ID, entry
index or block reference, raw hash values compared).

## Compliance Events

The following compliance-relevant events **MUST** be logged with enhanced detail:

- Key generation: algorithm, key size, intended purpose, generating node ID.
- Key rotation: old key deprecated, new key announced, cross-signature recorded.
- Peer banning: peer ID, reason, evidence (anomaly log references).
- Reputation downgrade: peer ID, old score, new score, trigger event.
- Audit log rotation: hash of outgoing segment, start of new segment.
- Recovery from backup: source, scope, verification result
  (see [DISASTER-RECOVERY.md](DISASTER-RECOVERY.md)).

## References

- [INDEX.md](INDEX.md) — P2P standards master index
- [DATA-INTEGRITY.md](DATA-INTEGRITY.md) — Hash chain and Merkle tree specification
- [DISASTER-RECOVERY.md](DISASTER-RECOVERY.md) — Backup and recovery audit requirements
- NIST SP 800-92 (Log Management): <https://csrc.nist.gov/publications/detail/sp/800-92>
- NIST SP 800-88: <https://csrc.nist.gov/publications/detail/sp/800-88>
- NIST SP 800-53 Rev. 5, AU-2, AU-9, SI-12: <https://csrc.nist.gov/publications/detail/sp/800-53/rev-5>
