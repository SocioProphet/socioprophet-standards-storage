# Rebase notes

This package was resliced after upstream inspection.

## Why this shape
`socioprophet-standards-storage` already owns platform-wide standards, contracts, schemas, and benchmark framing.
The semantic-proof core therefore lands here.

## What moved out
The following original pack surfaces were removed from this landing bundle and staged elsewhere:

- `PolicyIR`
- `RuleIR`
- Rego-like lowering fixtures
- Rule DSL lowering fixtures
- lowerer source packages

Those are better treated as agent-governance semantics than generic proof canon.
