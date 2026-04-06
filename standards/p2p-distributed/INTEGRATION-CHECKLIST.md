# P2P Integration Checklist

Use this checklist when onboarding a P2P or distributed system into the SocioProphet compliance
boundary. All items marked **MUST** are mandatory; **SHOULD** items are strongly recommended.

## Hypercore

- [ ] ECDSA-P256 signatures applied to every log entry (MUST)
- [ ] SHA-256 hash chain linking all entries (MUST)
- [ ] TLS 1.3 used for all inter-peer communication (MUST)
- [ ] Local audit logging enabled (MUST)
- [ ] CycloneDX SBOM generated and signed (MUST)
- [ ] Automated dependency scanning in CI (MUST)
- [ ] Release artefacts signed with ECDSA-P256 (MUST)
- [ ] Backup and recovery procedures tested quarterly (MUST)

## Hyperdrive

- [ ] File integrity verification (SHA-256) enforced on every read (MUST)
- [ ] Merkle tree validation covering all stored files (MUST)
- [ ] TLS 1.3 used for all inter-peer communication (MUST)
- [ ] File-access events recorded in audit log (MUST)
- [ ] CycloneDX SBOM maintained and signed (MUST)
- [ ] Automated vulnerability scanning enabled (MUST)
- [ ] Replication verification (Merkle root comparison) after every sync (MUST)
- [ ] Backup and recovery tested quarterly (MUST)

## Dat Ecosystem (dat-node, hashbase, homebase)

- [ ] Discovery key protocol implemented (`SHA-256(public_key)`) (MUST)
- [ ] Peer authentication via public key identity enforced (MUST)
- [ ] DHT or rendezvous server securely configured (MUST)
- [ ] Bootstrap peer keys pinned and verified quarterly (MUST)
- [ ] Peer connection events recorded in audit log (MUST)
- [ ] Data integrity verified on every replication (MUST)
- [ ] Replication events audited (MUST)
- [ ] Disaster recovery procedures documented and tested (MUST)

## multifeed

- [ ] Multi-writer consensus mechanism (CRDT or equivalent) in place (MUST)
- [ ] Conflict resolution events recorded in audit log (MUST)
- [ ] Each feed has ECDSA-P256 signatures on every entry (MUST)
- [ ] Feed synchronisation verified after every sync (MUST)
- [ ] Per-writer audit trail of all append operations (MUST)
- [ ] SBOM includes all feed dependencies (MUST)
- [ ] Replication tested end-to-end (MUST)

## kappa-core

- [ ] P2P database operational with append-only semantics enforced (MUST)
- [ ] Query events recorded in audit log (SHOULD)
- [ ] Data integrity verified (hash chain and Merkle tree) (MUST)
- [ ] Replication working and verified (MUST)
- [ ] Backup procedures documented (MUST)
- [ ] Recovery tested quarterly (MUST)

## replicator / mirror-folder

- [ ] Replication logic reviewed and audited (MUST)
- [ ] SHA-256 hash verification on all replicated data (MUST)
- [ ] Per-peer bandwidth limits configured (SHOULD)
- [ ] Replication events (success and failure) recorded in audit log (MUST)
- [ ] Failure handling documented and tested (MUST)
- [ ] Performance metrics tracked (SHOULD)

## hypermerge / multifeed-index

- [ ] Writer identity verified with ECDSA-P256 (MUST)
- [ ] Index integrity verified against source feeds (MUST)
- [ ] Conflict and merge events recorded in audit log (MUST)
- [ ] SBOM generated and signed (MUST)
- [ ] Recovery procedures tested (MUST)

## hyperdiscovery / hyperdb

- [ ] Discovery key protocol enforced (MUST)
- [ ] DHT rate limiting enabled (MUST)
- [ ] All peer connection events in audit log (MUST)
- [ ] Database integrity (hash chain) verified (MUST)
- [ ] SBOM generated and signed (MUST)

## hypercore-archiver

- [ ] All in-scope hypercores configured for archival (MUST)
- [ ] ECDSA-P256 signature verified before storing each entry (MUST)
- [ ] Weekly full hash-chain re-verification scheduled (MUST)
- [ ] Archival events logged (MUST)
- [ ] Recovery from archive tested quarterly (MUST)

## Cross-Cutting Requirements

These requirements apply to **all** systems in this checklist:

- [ ] Approved algorithms only (see [CRYPTO-BINDINGS.md](CRYPTO-BINDINGS.md)) (MUST)
- [ ] NIST SP 800-53 controls AC-3, IA-2, SC-8, SC-12, SC-13, SI-2, SI-7, SI-12 satisfied (MUST)
- [ ] Integration review sign-off by security team before production deployment (MUST)
- [ ] Compliance status recorded in the integration map (SHOULD)
