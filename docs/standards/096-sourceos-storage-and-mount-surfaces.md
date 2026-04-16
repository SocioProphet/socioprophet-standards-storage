# 096 — SourceOS storage and mount surfaces

## Status
Draft

## Purpose

This standard defines the storage and mount-surface doctrine for SourceOS substrate lanes, especially workstation/edge hosts using a staged Nix control plane.

## Core rule

A SourceOS substrate lane MUST classify storage and mounts into explicit surface classes. Implementations MUST NOT treat all host paths and service mounts as equivalent.

## Required classes

### 1. Immutable input

Examples:

- rendered configs
- policy packs
- stage descriptors
- static reference assets

Requirements:

- mounted read-only where consumed
- not used as mutable service state
- excluded from rollback semantics that are intended for mutable runtime state

### 2. Mutable state

Examples:

- queue state
- sqlite databases
- resumable job state
- local caches that influence runtime behavior

Requirements:

- mounted read-write only where needed
- rollback is explicit, not automatic
- snapshot policy must be declared

### 3. Audit and evidence

Examples:

- stage artifacts
- promote artifacts
- rollback artifacts
- health evidence

Requirements:

- append-oriented where possible
- retained long enough to support replay and post-event review
- separated from mutable runtime state where practical

### 4. Substrate-sensitive state

Examples:

- boot-adjacent descriptors
- snapshot metadata
- privileged recovery assets
- host-level operational controls

Requirements:

- must not be exposed to ordinary rootless application mounts
- mutations require privileged substrate operations
- snapshot and recovery policy must be explicit

## Container and runtime policy

For rootless container workloads:

- SELinux relabel requirements must be declared where applicable
- substrate-sensitive mounts are forbidden by default
- immutable input and mutable state mounts should remain distinguishable in runtime configuration

## Snapshot policy

A substrate lane MUST declare snapshot policy for each relevant class.

Allowed policy values include:

- `none`
- `manual`
- `pre_post_promotion`
- `pre_post_host_upgrade`

## Benchmark implication

Storage and mount classes should be measurable. Workstation substrate benchmarks should track at least:

- stage-to-promote latency,
- rollback execution time,
- evidence write overhead,
- snapshot creation overhead,
- service startup variance by mount class.

## Cross-repo alignment

- `SociOS-Linux/SourceOS` implements the mount classes.
- `SourceOS-Linux/sourceos-spec` should expose typed resources reflecting these surfaces.
- `SociOS-Linux/workstation-contracts` should require mount-class declarations for the relevant lane.

## Non-goal

This standard does not prescribe one filesystem or one snapshot implementation. It prescribes the class model and declaration discipline.
