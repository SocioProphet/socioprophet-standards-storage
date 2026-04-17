# 097 — SourceOS foreign volume and cross-OS mount interop

## Status
Draft

## Purpose

This standard defines the foreign-volume and cross-OS mount doctrine for SourceOS substrate lanes.

It complements `096-sourceos-storage-and-mount-surfaces.md` by specifying how foreign filesystems and foreign operating-system volumes are classified, mounted, imported, and constrained.

## Core rule

A SourceOS substrate lane MUST treat foreign volumes as a distinct policy domain.
Implementations MUST NOT treat foreign operating-system volumes as ordinary mutable runtime state.

## Required foreign-volume classes

### 1. Foreign system volume

Examples:
- macOS APFS system and data volumes
- journaled HFS+ host volumes
- another Linux host's ordinary system volume

Requirements:
- default posture MUST be read-only
- default Linux mount flags MUST include `nodev`, `nosuid`, and `noexec`
- implementations MUST prefer import workflows over in-place mutation
- foreign system volumes MUST NOT be used as mutable SourceOS runtime state

### 2. Exchange volume

Examples:
- explicitly designated exFAT exchange partitions
- removable media used only for interchange

Requirements:
- read-write MAY be allowed when the exchange role is explicit
- `nodev` and `nosuid` SHOULD remain enabled by default
- exchange volumes MUST NOT carry substrate-sensitive state, audit stores, or host runtime state

### 3. Foreign evidence or import volume

Examples:
- disks mounted for migration, acquisition, or investigation
- snapshots mounted only to extract content into governed native storage

Requirements:
- default posture SHOULD be read-only
- mounts SHOULD emit sufficient evidence to reconstruct filesystem type, assigned class, and resulting posture
- implementations SHOULD copy into governed native storage instead of editing in place

### 4. Substrate-sensitive foreign asset

Examples:
- boot-adjacent foreign assets
- recovery descriptors
- privileged recovery partitions

Requirements:
- mutations require privileged substrate operations
- these assets MUST NOT be exposed to ordinary rootless container mounts
- recovery and rollback implications MUST be explicit

## Filesystem-specific baseline posture

### APFS

APFS host volumes SHOULD be treated as foreign system volumes.
Read-write posture MUST NOT be assumed safe by default.

### HFS+ (journaled)

Journaled HFS+ host volumes SHOULD be treated as foreign system volumes.
Read-write posture MUST NOT be the default.

### exFAT

exFAT SHOULD be treated as an exchange-volume candidate, not as substrate-sensitive or audit-critical state.

### ext4, xfs, btrfs from another Linux host or distro

These surfaces SHOULD be treated as foreign Linux volumes.
Default posture SHOULD be read-only unless ownership, trust domain, and rollback expectations are declared explicitly.

## Apple dual-boot rule

On Apple dual-boot devices:
- macOS system and data volumes are foreign system volumes
- a shared exchange partition is a separate exchange surface, not an extension of the SourceOS runtime
- boot-adjacent foreign assets are substrate-sensitive imports

## Container and runtime policy

For rootless container workloads:
- foreign system volumes are forbidden by default
- exchange volumes MAY be bound into explicit import or export jobs where the class is declared
- substrate-sensitive foreign assets are forbidden by default

## Exception policy

A SourceOS substrate lane MAY permit explicit read-write exceptions for foreign filesystems only when:
- the exception class is declared
- the operator intent is explicit
- the implementation path is tested and documented
- evidence captures the granted exception and resulting posture

## Related Standards

- `010-storage-contexts.md` — canonical storage contexts and boundaries
- `060-storage-decision-guidance.md` — when to add optional storage tiers
- `096-sourceos-storage-and-mount-surfaces.md` — substrate storage and mount-surface class model

## Implementation Evidence

Initial downstream realization should appear in `SociOS-Linux/source-os` as a storage-topic tranche carrying:
- Linux estate planning and workstreams
- a foreign-filesystem policy matrix
- later Linux-facing realization templates once the policy matrix stabilizes

## Non-goal

This standard does not require one specific filesystem driver, one package manager, or one snapshot backend.
It prescribes the policy boundaries, posture defaults, and declaration discipline for foreign-volume handling.
