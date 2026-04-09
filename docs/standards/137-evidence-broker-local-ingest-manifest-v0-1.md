# 137. Evidence Broker Local-File Ingest Manifest Contract (v0.1)

## Status

Bootstrap contract note.

## Purpose

This note defines the first stable manifest shape for the local-file ingest path.

The local-file path exists to prove custody, hashing, idempotent re-ingest, and parser-failure handling before any cloud connector work begins.

## Manifest structure

A local ingest manifest SHOULD contain:

- `manifestVersion`
- `acquisitionRunId`
- `connectorProfileId`
- `generatedAtUtc`
- `contentBlock`
- `contentRootDigest`
- `runMetadata`

### `contentBlock`

`contentBlock` SHOULD contain only stable content-derived sections:

- `blobs`
- `items`
- `events`

### `runMetadata`

`runMetadata` MAY contain operational details such as:

- `parserRuns`
- `validationResults`

## Digest rule

`contentRootDigest` SHALL be computed only from the canonicalized `contentBlock`.

The digest SHALL NOT include run-specific metadata such as:

- manifest generation time
- parser-run IDs
- validation-result IDs
- other non-content operational identifiers

## Canonicalization rule

Before hashing `contentBlock`:

1. each array in `contentBlock` SHALL be sorted by `id`
2. object keys SHALL be sorted lexicographically
3. the canonical JSON form SHALL be serialized without insignificant whitespace
4. SHA-256 SHALL be computed over the resulting UTF-8 bytes

## Required local-file acceptance checks

The first local-file broker slice is acceptable only if:

1. the same file re-ingested twice yields one canonical blob identity
2. raw blob custody survives parser failure
3. content-root digests remain stable across reruns of identical content
4. original timestamps remain preserved alongside normalized timestamps

## Summary

The local-file ingest manifest is the first executable custody contract. It exists to prove stable landing and replay before non-local connectors are introduced.
