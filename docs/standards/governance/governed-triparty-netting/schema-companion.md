# Governed Triparty Netting Fabric - Schema Companion v1

## Purpose

This schema companion turns the white paper's typed bundle appendix into a stricter machine-oriented package. It is not a smart-contract application binary interface and not a production wire protocol. It is a normative schema layer for implementations, adapters, test fixtures, and validation.

## Scope

The companion defines the minimum machine-readable structures for:
- IntentBundle
- AcceptanceBundle
- EscrowBundle
- FillBundle
- VerificationBundle
- DisputeBundle
- RevocationBundle
- ExportBundle

It also defines shared objects for:
- bundle metadata
- actor references
- proof references
- witness references
- challenge windows
- policy references
- monetary legs
- capability legs
- evidence references

## Bundle rules

1. Every bundle carries a globally unique `bundle_id`.
2. Every bundle carries a `bundle_type` and `bundle_version`.
3. Every bundle binds to a `cell_id` representing the governed triparty coordination cell.
4. Every bundle binds to a `nonce_domain` and `nonce_value`.
5. Every bundle carries `created_at` and, where relevant, `expires_at`.
6. Every bundle identifies its producing actor and any relevant counterparty or witness set.
7. Every release-affecting bundle carries or references proof material.
8. Export is always a separate bundle class and may not be implied by local admission.

## Non-goals

This companion does not define:
- chain-specific transaction encoding
- gas metering rules
- signature algorithms beyond typed reference placeholders
- final contract storage layout
- token economics coefficients

## Suggested repository placement

Canonical repository:
`SocioProphet/socioprophet-standards-storage`

Suggested path:
`schemas/governance/governed-triparty-netting/`

## Validation use

The schemas are intended to support:
- adapter fixtures
- conformance tests
- worked example validation
- partner-facing integration review
- future code generation or typed software development kit scaffolding
