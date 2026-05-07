# 143. Operation Plane Artifact Storage, Sync, and Diagnostic Redaction (v0.1)

## Purpose

This standard defines storage-side requirements for Workspace Operation Plane artifacts, including upload/import, content-addressing, local-first synchronization, retention, quarantine/admission, and diagnostic redaction.

## Normative storage model

Operation Plane implementations MUST separate artifact metadata from artifact content.

- Artifact metadata MUST be stored as structured records and MUST include `artifact_id`, `content_hash`, lifecycle state, and provenance fields.
- Artifact content MUST be stored in a content-addressable blob surface and referenced from metadata.
- The same `content_hash` MAY be referenced by multiple artifact records.

### Required metadata fields

Each artifact record MUST include at least:

- `artifact_id`: stable logical identifier (UUID/ULID or equivalent stable ID)
- `content_hash`: stable hash in canonical hash-domain format (e.g., `sha256:<hex>`)
- `content_uri`: dereferenceable URI for artifact bytes
- `storage_backend`: backend class identifier (e.g., `sourceos-local`, `s3`, `minio`, `ipfs`)
- `source_connector`: connector/system of origin (`upload`, `import`, `bearbrowser`, `turtleterm`, `agent`, etc.)
- `source_object`: source-native object path/ID
- `source_revision`: source-native revision token/version/etag/commit when available
- `admission_state`: `pending`, `admitted`, `rejected`
- `quarantine_state`: `none`, `quarantined`, `released`
- `availability_state`: `local`, `remote`, `syncing`, `conflicted`, `quarantined`
- `retention_policy`: named policy or inline retention descriptor
- `deleted_at`: nullable timestamp
- `tombstone`: boolean indicating logical deletion record retention

## Upload/import conflict and dedupe semantics

For upload/import flows:

1. Systems MUST perform content dedupe by `content_hash`.
2. If incoming `content_hash` already exists, systems MUST create or update metadata references without duplicating bytes.
3. If incoming bytes differ but target logical slot is the same, systems MUST preserve both revisions and mark `availability_state=conflicted` until resolved.
4. Conflict resolution MUST be explicit and auditable (automatic winner selection MAY be used only when policy-defined and receipted).
5. Quarantined artifacts MUST NOT be admitted to normal execution surfaces until `admission_state=admitted` and `quarantine_state=released`.

## Retention, deletion, and tombstones

- Retention MUST be policy-driven and evaluable per artifact class.
- Deletion MUST default to logical delete first (`deleted_at` + `tombstone=true`) for replay/audit continuity.
- Physical byte purge MAY occur after retention and legal/forensic holds are satisfied.
- Tombstones MUST retain enough metadata to prevent ID reuse ambiguity and sync resurrection errors.

## Local-first availability and sync states

Implementations MUST use the following availability states with these meanings:

- `local`: bytes and metadata available locally; sync not yet required or already satisfied.
- `remote`: authoritative copy known remotely; bytes not currently local.
- `syncing`: transfer and/or metadata reconciliation in progress.
- `conflicted`: concurrent or divergent revisions require resolution.
- `quarantined`: artifact blocked from normal use pending security/policy review.

State transitions MUST emit receipts sufficient for replay in SourceOS local-first sync.

## Diagnostic export redaction standard

Diagnostic exports MUST default to redaction for sensitive values. Redaction MUST preserve field presence and type shape where practical.

Redaction rules:

- Cookies: MUST redact full cookie values.
- Bearer tokens: MUST redact full token values.
- OAuth tokens (access/refresh/id): MUST redact full token values.
- API keys: MUST redact full key values.
- Secrets (generic credential/material): MUST redact full secret values.
- Source snippets: MUST redact snippet body unless explicit debug override policy allows scoped reveal.
- Prompts: MUST redact full prompt text; MAY retain bounded metadata (length, hash).
- Tenant identifiers: MUST redact direct tenant IDs in export payloads; MAY keep irreversible salted digest for correlation.

Recommended replacement marker: `"[REDACTED:<class>]"`.

## Required examples

### 1) Uploaded file artifact

```json
{
  "artifact_id": "art_01JX8M0S6W8G23X9ZQ9X1F1Q7N",
  "artifact_type": "uploaded_file",
  "content_hash": "sha256:2ea9ab9198d1638f94a7f6b8e8f6ffb8cf0c44d4fd2c3f2a0e2cbe6f7c7d76d2",
  "content_uri": "sourceos://artifacts/sha256/2e/a9/2ea9ab...",
  "storage_backend": "sourceos-local",
  "source_connector": "upload",
  "source_object": "workspace://uploads/quarterly-report.pdf",
  "source_revision": "etag:W/\"v3-9f2a\"",
  "availability_state": "local",
  "admission_state": "admitted",
  "quarantine_state": "none",
  "retention_policy": "workspace-default-90d",
  "deleted_at": null,
  "tombstone": false
}
```

### 2) Imported folder artifact

```json
{
  "artifact_id": "art_01JX8M26X6R9CM2F2S49GJ6VB2",
  "artifact_type": "imported_folder",
  "content_hash": "sha256:ef5f1f9c8e8f92cb5f14ab987a33c0e95321e86ec9d3f327f6bc7cdb3759d8ab",
  "content_uri": "s3://workspace-imports/folders/ef/5f/ef5f1f...",
  "storage_backend": "s3",
  "source_connector": "import",
  "source_object": "gdrive://folder/1Q2W3E",
  "source_revision": "gdrive-change-8471932",
  "availability_state": "syncing",
  "admission_state": "pending",
  "quarantine_state": "none",
  "retention_policy": "workspace-import-180d",
  "deleted_at": null,
  "tombstone": false
}
```

### 3) Downloaded browser artifact

```json
{
  "artifact_id": "art_01JX8M33K5S4M2TC1Y2B8H0KPV",
  "artifact_type": "downloaded_browser_artifact",
  "content_hash": "sha256:b1d84d9786af4cf15f5562d4d7f763f64669d68e0f0418ab9772b0e7f2d4bb1c",
  "content_uri": "minio://bearbrowser-downloads/b1/d8/b1d84d...",
  "storage_backend": "minio",
  "source_connector": "bearbrowser",
  "source_object": "https://example.org/specs/interop.zip",
  "source_revision": "http-etag:\"5f9e4b\"",
  "availability_state": "remote",
  "admission_state": "pending",
  "quarantine_state": "none",
  "retention_policy": "browser-download-30d",
  "deleted_at": null,
  "tombstone": false
}
```

### 4) Terminal transcript artifact

```json
{
  "artifact_id": "art_01JX8M3CYXG8KT5M3VQK3W6CA9",
  "artifact_type": "terminal_transcript",
  "content_hash": "sha256:4ac0d4cc63a4ebf3d9f0dc0ad91bb5dcab20d168e5f99c278d70f4e7a57c2aa5",
  "content_uri": "sourceos://artifacts/sha256/4a/c0/4ac0d4...",
  "storage_backend": "sourceos-local",
  "source_connector": "turtleterm",
  "source_object": "session://term/7f2d3c1a",
  "source_revision": "lineage:42",
  "availability_state": "local",
  "admission_state": "admitted",
  "quarantine_state": "none",
  "retention_policy": "terminal-transcript-14d",
  "deleted_at": null,
  "tombstone": false
}
```

### 5) Agent-generated patch artifact

```json
{
  "artifact_id": "art_01JX8M4EVT2WBNVYH63RBM8Y0Y",
  "artifact_type": "agent_generated_patch",
  "content_hash": "sha256:c06d58b0e36d39f3530e91f2d6875f5f0f90a74f8ff26122ed5bbf48f35f8a7e",
  "content_uri": "sourceos://artifacts/sha256/c0/6d/c06d58...",
  "storage_backend": "sourceos-local",
  "source_connector": "agent",
  "source_object": "agent://run/01JX8M4AJ3",
  "source_revision": "attempt:3",
  "availability_state": "conflicted",
  "admission_state": "pending",
  "quarantine_state": "none",
  "retention_policy": "agent-patch-30d",
  "deleted_at": null,
  "tombstone": false
}
```

### 6) Memory bundle artifact

```json
{
  "artifact_id": "art_01JX8M4ZHJ2CP2R7CT1XY9NX6K",
  "artifact_type": "memory_bundle",
  "content_hash": "sha256:946b93495dc839b844d4f8fd6f5e7d9beaa7a4f19e5377d0378ee54f0a1a2f29",
  "content_uri": "sourceos://artifacts/sha256/94/6b/946b93...",
  "storage_backend": "sourceos-local",
  "source_connector": "agent",
  "source_object": "memory://bundle/2026-05-07",
  "source_revision": "snapshot:17",
  "availability_state": "syncing",
  "admission_state": "admitted",
  "quarantine_state": "none",
  "retention_policy": "memory-bundle-365d",
  "deleted_at": null,
  "tombstone": false
}
```

### 7) Quarantined artifact

```json
{
  "artifact_id": "art_01JX8M59QCR9D7T0QX7AMN3M2G",
  "artifact_type": "uploaded_file",
  "content_hash": "sha256:721cf7b86ad4a34e89ce8996f4af53f5b14bcaf723f9f2f84088a55d7d58495d",
  "content_uri": "quarantine://objects/72/1c/721cf7...",
  "storage_backend": "sourceos-local",
  "source_connector": "upload",
  "source_object": "workspace://uploads/suspicious-macro.docm",
  "source_revision": "etag:W/\"v1-12ab\"",
  "availability_state": "quarantined",
  "admission_state": "rejected",
  "quarantine_state": "quarantined",
  "retention_policy": "security-quarantine-30d",
  "deleted_at": null,
  "tombstone": false
}
```

### 8) Redacted diagnostic bundle metadata

```json
{
  "bundle_id": "diag_01JX8M6D0SQ7P5FYF1S6SX6Q14",
  "exported_at": "2026-05-07T06:00:00Z",
  "artifact_refs": [
    "art_01JX8M0S6W8G23X9ZQ9X1F1Q7N",
    "art_01JX8M3CYXG8KT5M3VQK3W6CA9"
  ],
  "redaction": {
    "cookies": "[REDACTED:cookie]",
    "bearer_token": "[REDACTED:bearer_token]",
    "oauth_access_token": "[REDACTED:oauth_token]",
    "api_key": "[REDACTED:api_key]",
    "secret": "[REDACTED:secret]",
    "source_snippet": "[REDACTED:source_snippet]",
    "prompt_text": "[REDACTED:prompt]",
    "tenant_id": "[REDACTED:tenant_id]",
    "tenant_digest": "sha256:9d8cf419f865f9a89b44d28edbe09f958d8c1dcd80f6dbf84f3f3f44adf48ff2"
  }
}
```

## Alignment notes

- This storage contract aligns with the core artifact identity and provenance direction in `SocioProphet/prophet-core-contracts#1` by requiring stable IDs, content hashes, and source provenance fields.
- The local-first state model (`local`, `remote`, `syncing`, `conflicted`, `quarantined`) is designed to support Drive-grade upload/import behavior plus SourceOS synchronization semantics.
- The redaction profile is implementation-specific enough for `sourceos-devtools`, BearBrowser, TurtleTerm, and operation diagnostics export pipelines.

## Related standards

- `docs/standards/010-storage-contexts.md`
- `docs/standards/096-local-first-desktop-sync-and-governance.md`
- `docs/standards/096-sourceos-storage-and-mount-surfaces.md`
- `docs/standards/138-evidence-receipt-spine.md`
