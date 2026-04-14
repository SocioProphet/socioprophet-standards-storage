# Agent-plane Runtime-Law Fixtures

This directory is the fixture lane for the `agent-plane-runtime-law` workload suite.

## Intended fixture types

- `session-receipt/*.json` — successful, deferred, paused, and failed receipt examples
- `execution-decision/*.json` — allow, deny, ask, defer, rewrite cases
- `memory-entry/*.json` — `rule`, `learned`, and `recap` examples
- `promotion-reversal/*.json` — promotion and reversal linkages
- `runtime-surface/*.json` — PTY, workdir, background, reviewOnly, worktreeStrategy examples

## Why this exists

The workload catalog defines what must be measured.
These fixtures define what valid evidence artifacts should look like when the harness is implemented.

## Next step

Populate this directory with a minimal golden fixture set tied to the merged schema family in `SourceOS-Linux/sourceos-spec`.
