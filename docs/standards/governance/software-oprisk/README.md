# Software Operational Risk Governance Pack

This package defines the initial SocioProphet governance standard for **software operational risk**, **software supply-chain operational risk**, **outage evidence**, and **reserve / capital-oriented measurement**.

It is intended to give the platform a canonical place to express:

- normative terminology for software operational risk;
- a shared event taxonomy for outages, degradation, integrity failures, and upstream drift;
- a graph-oriented supply-chain model for nth-party and concentration risk;
- a measurement model for expected annual loss, tail loss, and reserve sizing;
- a repeatable external outage corpus method;
- an implementation crosswalk for Agentplane, Sociosphere, SourceOS, and related repos.

## Why this package exists

The platform already has standards work for storage, contracts, governance, measurement, FIPS, and execution. What was missing was a canonical place to define the **operational-risk** layer for software and agentic systems.

The motivating design posture is:

1. borrow governance discipline from banking rather than inventing ad hoc “risk scores”;  
2. translate that discipline into dependency graphs, outage histories, and controls for software systems;  
3. measure the result in financial terms that can support reserve sizing, avoided-loss claims, and control ROI.

## Normative scope

This package covers the following domains:

- platform outages and service degradation;
- software supply-chain failures and upstream dependency events;
- concentration and common-mode dependency risk;
- release, packaging, registry, CI/CD, and model-provider exposure;
- operational resilience, impact tolerance, and recovery design;
- external outage corpus construction and evidence grading;
- reserve / economic-capital style estimation for software-dependent operations.

This package does **not** replace canonical wire, identity, or runtime specifications. It cross-references them.

## Repository placement

The governance and measurement standard lives here because this repository is already the canonical home for:

- platform standards,
- benchmark methodology,
- governance packages,
- and cross-repository decision surfaces.

### Downstream implementation owners

- `SocioProphet/agentplane` — execution-plane evidence, upstream drift receipts, outage / failure artifact integration.
- `SocioProphet/sociosphere` — automation, watcher pipelines, policy enforcement, and control telemetry.
- `SociOS-Linux/source-os` — runtime / package-manager / distro update posture and dependency-surface enforcement.
- `SourceOS-Linux/*` — typed contracts and implementation of runtime / governance schemas where needed.

## Package contents

- `README.md` — package overview and scope.
- `framework.md` — core framework, taxonomy, formulas, and control model.
- `outage-corpus-method.md` — external outage corpus methodology and evidence ladder.
- `upstream-alignment.md` — live-repo alignment notes and recommended split across active orgs.

## Immediate next standards outputs

1. Add a machine-readable incident schema in `schemas/` or a companion standards repo.
2. Add a benchmark workload for outage-loss simulation.
3. Add a graph concentration / nth-party measurement profile.
4. Add control-mapping crosswalks to implementation repositories.
