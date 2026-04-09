# Evidence bootstrap schemas

This directory is a temporary bootstrap landing for the initial evidence-plane contract seeds.

These schema assets are expected to move into the future dedicated evidence repo family once repository creation is available.

## Initial scope

The first seed objects are expected to include:

- `ConnectorProfile`
- `AcquisitionRun`
- `EvidenceBlob`
- `EvidenceItem`
- `EvidenceEntity`
- `EvidenceEvent`
- `ParserRun`
- `ValidationResult`

## Bootstrap rules

- use `kind` as the runtime discriminator
- keep IDs stable and portable
- prefer strict schemas with `additionalProperties: false`
- preserve JSON Schema / Avro parity where practical
- treat raw blob custody as primary and chunking as derivative

## Status

Temporary staging only. Permanent home should be the future `evidence-contracts` repo.
