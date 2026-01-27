# ADR-030: Split Knowledge Context into a sibling standards repo

- Date: 2026-01-27
- Status: Proposed
- Decision owner: SocioProphet
- Contexts affected: knowledge, artifacts, search, vectors, graphs, publication

## Context
We need a dedicated standards package for knowledge engineering (micro-publications, meriotopographic relations, masking/tokenization/IR/vector, office/editor integration) that evolves independently but remains governed by platform-wide invariants (formats, interfaces, benchmark discipline).

## Decision
Create a sibling standards repository (socioprophet-standards-knowledge) that inherits platform requirements from socioprophet-standards-storage and is vendored into the docs site at pinned commits.

## Options considered
1) Put Knowledge Context specs directly into this repo.
2) Create a separate knowledge standards repo with the same skeleton and validation gates.

## Tradeoffs
- Separate repo improves modularity, versioning, and reuse across shipping repos.
- Requires explicit cross-repo dependency pinning and a docs vendoring step.

## Measurement plan
- Add a knowledge workload suite (lexical IR, vector retrieval, edge traversal, masking cost, conversion fidelity) and report p50/p95/p99 for candidate backends.

## Consequences
- This repo becomes the index + governance layer; the knowledge repo becomes the detailed spec package.
- Next: define Knowledge Context schemas + triRPC contracts + workload suite in the new repo.
