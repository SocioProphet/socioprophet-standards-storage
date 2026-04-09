# 135. Canonical Evidence Lake and Ingest Architecture (v0.1)

## Status

Proposed baseline for implementation.

## Purpose

This standard defines the first canonical landing architecture for large mixed-format evidence corpora imported from hostile or untrusted source systems such as Google Drive, iCloud Drive, local disks, exported notes, device console logs, browser console captures, and miscellaneous file archives.

The immediate goal is not graph projection or high-order semantic modeling. The immediate goal is to establish a trustworthy evidence repository that:

1. preserves raw source material immutably,
2. hashes everything on arrival,
3. deduplicates by content rather than by path,
4. records all source aliases and provenance,
5. routes blobs into parser and chunking workflows, and
6. keeps the object store and the metadata/control plane cleanly separated.

## Phase-1 decision

### Canonical system of record

Source systems such as Google Drive and iCloud Drive SHALL be treated as ingress systems only. They SHALL NOT remain the long-term canonical system of record.

The canonical landing architecture SHALL be:

- **raw object store** for immutable bytes,
- **Postgres** for metadata, provenance, routing, and processing control,
- **brokered ingest** for staging, hashing, normalization, and validation,
- **deferred projections** for search, vector, and graph layers.

### Recommended phase-1 storage pair

The phase-1 implementation target SHOULD be:

- **SeaweedFS** as the canonical S3-compatible raw object store,
- **Postgres** as the metadata and orchestration plane.

Rationale:

- SeaweedFS is lightweight enough to stand up quickly while remaining object-store-native.
- Postgres provides transactional metadata management plus `jsonb` for structured provider metadata and processing directives.
- This pair keeps custody simple while deferring graph and heavy search specialization.

### Connector strategy

The primary ingress adapter SHOULD be **rclone**.

- Google Drive and iCloud Drive SHALL be treated as source connectors.
- Local file ingest SHALL be implemented first.
- Google Drive via rclone SHOULD be the first non-local connector.
- iCloud Drive via rclone SHOULD follow only after the local-file and Google Drive paths are stable.

## Canonical landing rules

### Raw object identity

Raw objects SHALL be content-addressed by SHA-256.

Canonical object keys SHOULD follow this pattern:

`raw/sha256/ab/cd/<full-sha256>`

Raw object keys SHALL NOT be renamed into human-readable or provider-derived names.

### Human-readable names and source aliases

Human-readable names, source paths, provider IDs, revision IDs, import labels, and processing instructions SHALL live in Postgres, not in the canonical raw object key.

### Deduplication

Deduplication SHALL occur at the blob layer using content hash identity.

If multiple source files or provider objects resolve to the same SHA-256:

- one canonical raw object SHALL be retained,
- all source aliases SHALL be preserved,
- provenance SHALL record each import edge.

This preserves duplication evidence rather than destroying it.

## Processing order

The implementation SHALL follow this order:

1. ingest from source connector,
2. stage immutably into the object store,
3. compute SHA-256,
4. register metadata and provenance in Postgres,
5. deduplicate exact content,
6. classify file type and size,
7. dispatch parser and chunking jobs,
8. emit normalized evidence items/events/entities/validation results,
9. later project to search, vector, and graph layers.

Graph projection is explicitly out of scope for phase 1.

## Minimal phase-1 Postgres tables

The minimum table family SHALL be:

- `connector_profiles`
- `acquisition_runs`
- `evidence_blobs`
- `blob_sources`
- `evidence_items`
- `evidence_entities`
- `evidence_events`
- `parser_runs`
- `validation_results`
- `processing_jobs`

Later tables MAY include:

- `notice_records`
- `persistence_findings`
- `harm_records`
- `exhibit_candidates`

## Chunking policy

Chunking SHALL be derivative, not primary.

The raw blob SHALL always be preserved whole before any chunking occurs.

Recommended phase-1 policies:

- **small text and logs**: parse whole where cost is acceptable,
- **medium text**: chunk by line or record with overlap,
- **very large logs**: stream parse plus sidecar line index and rolling chunk windows,
- **documents (PDF/notes/doc exports)**: preserve raw blob plus extracted text derivative plus page/section chunks,
- **binary/media**: preserve raw blob and generate metadata/OCR/transcript derivatives only.

## Repo topology

### SocioProphet

SocioProphet SHALL own the evidence-plane implementation repos:

- `evidence-contracts`
- `evidence-broker`
- `evidence-connectors-gdrive`
- `evidence-connectors-icloud`
- `evidence-validator`
- `evidence-storage-infra`

### SourceOS-Linux

`sourceos-spec` SHALL remain the umbrella metadata-plane and governance contract layer. It SHALL NOT absorb the operational evidence-plane runtime contracts directly.

### SociOS-Linux

SociOS-Linux SHALL continue to own desktop-facing account UX, mounted filesystem surfaces, and operator-facing capture/integration paths.

## Phase-1 acceptance gates

Phase 1 is complete when all of the following are true:

1. a local file can be ingested into the object store and registered in Postgres,
2. the same file re-ingested twice yields one canonical blob record,
3. all source aliases are preserved,
4. a parser failure preserves raw blob custody,
5. content-root manifests remain stable across reruns of identical content,
6. Google Drive ingest can land into the same broker/object-store/Postgres path without changing the canonical evidence model.

## Non-goals for phase 1

The following are intentionally deferred:

- graph-native storage as the primary system of record,
- advanced semantic reasoning over the whole corpus,
- broad workflow automation unrelated to custody and enrichment,
- aggressive source-system deletion before parity validation.

## Migration posture

Source drives SHALL NOT be reduced or deleted until:

- mirror parity is demonstrated,
- hash parity and manifest parity checks pass,
- a cooling-off validation window is complete.

## Summary

The key architectural rule is simple:

**source systems are ingress only; object storage plus Postgres becomes the evidence repository; chunking and enrichment are derivatives; graph comes later.**
