# Replication & Synchronisation

This document uses RFC 2119 language: **MUST**, **SHOULD**, **MAY**.

## Pull-Based Replication

1. Requesting peer (A) sends a block-range request to provider peer (B).
2. B responds with blocks and their SHA-256 hashes.
3. A **MUST** verify each received block against its hash before writing to local storage.
4. A block that fails hash verification **MUST NOT** be written to storage; A **MUST** re-request
   the block from B or an alternative peer and **MUST** log the failure.
5. After all blocks are received, A **MUST** verify the Merkle root hash against the signed value
   in the writer's log entry.

## Push-Based Replication

1. Writer announces new data (new entry or block range) to connected peers.
2. Interested peers request the announced blocks using the pull-based protocol above.
3. The same verification requirements (per-block hash, Merkle root, signature check) apply as for
   pull-based replication.

## Selective Replication

- Peers **MAY** replicate a subset of a feed or drive (per-block or per-entry selection).
- Selective replication choices **MUST** be recorded in the audit log so that data-completeness
  can be audited.
- Peers **MUST NOT** falsely represent themselves as holding complete data when only a subset has
  been replicated.

## Conflict Resolution (multifeed / multi-writer)

- Multi-writer scenarios **MUST** use a CRDT or equivalent conflict-free replicated data type to
  avoid data loss on concurrent writes.
- All conflict events (detected and resolved) **MUST** be appended to the audit log with the
  conflicting entry references and resolution outcome.
- Application-specific resolution rules **MUST** be documented and versioned; changes to
  resolution rules **MUST** be treated as breaking changes (see
  [../../docs/standards/000-platform-standards.md](../../docs/standards/000-platform-standards.md)).

## Sync Verification

- After a full synchronisation, the receiving peer **MUST** verify the complete dataset by
  comparing the Merkle root hash of each replicated feed against the signed value in the
  authoritative log.
- Incremental verification (per-block) **SHOULD** also be performed during transfer to detect
  failures early.
- All sync verification events (start, completion, result) **MUST** be written to the audit log.

## Bandwidth Management

- Implementations **SHOULD** enforce per-peer rate limits (configurable bytes/second threshold).
- Critical data (e.g. audit log replication) **SHOULD** be prioritised over bulk data replication.
- Bandwidth events (rate-limit reached, quota exceeded) **MUST** be recorded in the audit log.

## References

- [INDEX.md](INDEX.md) — P2P standards master index
- [DATA-INTEGRITY.md](DATA-INTEGRITY.md) — Block-level and Merkle tree verification
- [AUDIT-LOGGING.md](AUDIT-LOGGING.md) — Mandatory audit events for replication
- NIST SP 800-53 Rev. 5, SC-8: <https://csrc.nist.gov/publications/detail/sp/800-53/rev-5>
