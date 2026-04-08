# P2P Disaster Recovery

This document uses RFC 2119 language: **MUST**, **SHOULD**, **MAY**.

## Local Backups

- All Hypercore and Hyperdrive data **MUST** be backed up to local storage on a schedule no less
  frequent than every 24 hours.
- Backup files **MUST** be encrypted at rest with AES-256-GCM.
- Backup integrity **MUST** be verified after each backup job using SHA-256 checksums.
- Local backup retention: minimum **30 days** (configurable to longer).
- Backup events (start, finish, checksum, encryption status) **MUST** be written to the audit log.

## Off-Site Backups

- Critical data **MUST** be replicated to at least one trusted off-site peer or archival service.
- All data transmitted to off-site backups **MUST** be encrypted in transit using TLS 1.3.
- Off-site backup data **MUST** be encrypted at rest (AES-256-GCM).
- Off-site backup events **MUST** be recorded in the local audit log, including the destination
  peer ID and a hash of the transmitted data.

## Recovery Procedures

1. **Local restore** (preferred): restore from most recent local backup.
   - Decrypt backup with AES-256-GCM key retrieved from secure key store.
   - Verify SHA-256 checksum against the value recorded at backup time.
   - Re-verify the hash chain and Merkle tree of restored data before resuming operations.
2. **Off-site restore** (if local backup unavailable):
   - Retrieve encrypted backup from the trusted off-site peer.
   - Decrypt and verify as above.
3. All recovery events **MUST** be appended to the audit log with the source, scope, and
   verification result.

## Hypercore Archiver

- Deployments that include `hypercore-archiver` **MUST** configure it to archive all hypercores
  that are in scope for the compliance boundary.
- The archiver **MUST** verify each new entry against the writer's ECDSA-P256 signature before
  storing it.
- Archived data **MUST** be re-verified (full hash-chain walk) at least weekly.
- Archival events and verification results **MUST** be written to the audit log.

## Recovery Testing

- Recovery procedures **MUST** be tested at least quarterly.
- Tests **MUST** simulate an actual data-loss scenario (delete local data, restore from backup).
- Each test **MUST** measure and record the Recovery Time Objective (RTO) achieved.
- Test results and lessons learned **MUST** be documented and retained for at least 1 year.
- Failures discovered during testing **MUST** be treated as high-priority incidents and resolved
  before the next scheduled test.

## References

- [INDEX.md](INDEX.md) — P2P standards master index
- [AUDIT-LOGGING.md](AUDIT-LOGGING.md) — Audit events for backup and recovery
- [DATA-INTEGRITY.md](DATA-INTEGRITY.md) — Data verification after restore
- [REPLICATION.md](REPLICATION.md) — Off-site replication procedures
- NIST SP 800-34 (Contingency Planning): <https://csrc.nist.gov/publications/detail/sp/800-34/rev-1>
- NIST SP 800-53 Rev. 5, CP-9, CP-10: <https://csrc.nist.gov/publications/detail/sp/800-53/rev-5>
