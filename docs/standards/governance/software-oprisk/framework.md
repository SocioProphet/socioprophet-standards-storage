# Software Operational Risk Framework

## 1. Purpose

This document defines the initial framework for evaluating operational risk in software-dependent and agentic systems.

The framework borrows governance structure from operational-risk and operational-resilience literature, but translates the object of analysis from a bank or internal business line to a **software dependency and service graph**.

## 2. Core definition

**Software operational risk** is the risk of loss resulting from failed or inadequate software processes, people, systems, dependencies, controls, or external events that disrupt, degrade, corrupt, delay, or make untrustworthy a critical service.

For the purposes of this standard, the object of analysis is not just a service or application.
It is the **service path and dependency graph** required to deliver that service.

## 3. Canonical objects

### 3.1 Critical service
A critical service is a user-visible or business-critical capability that has a declared impact tolerance.
Examples:

- install;
- update;
- authenticate;
- execute privileged actions;
- publish artifacts;
- retrieve or use a model;
- restore / recover / roll back.

### 3.2 Node
A node is any entity whose failure, compromise, degradation, or misconfiguration can affect a service path.
Examples:

- repository,
- maintainer,
- CI system,
- registry,
- artifact store,
- signing authority,
- transparency log,
- package manager,
- OS distribution layer,
- model provider,
- tool / MCP server,
- cloud service,
- identity provider.

### 3.3 Edge
An edge is a dependency or authority relationship.
Examples:

- build dependency,
- runtime dependency,
- signing authority,
- update channel,
- credential trust,
- execution delegation,
- network path,
- policy approval dependency.

### 3.4 Common-mode cluster
A common-mode cluster is a set of nodes or edges that can fail or become unsafe together because they share a hidden dependency, authority, control path, or provider concentration.

## 4. Event taxonomy

All incidents SHOULD be classified under one or more of the following event families:

1. **Execution / process management failure**  
   Broken release, migration, deployment, rollback, or reconciliation behavior.
2. **System / platform disruption**  
   Cloud, control-plane, data-plane, DNS, identity, or regional outage.
3. **Supply-chain / upstream dependency failure**  
   Registry, package, maintainer, update, build, or artifact compromise or disruption.
4. **Integrity / trust failure**  
   Incorrect provenance, unsafe artifact, signature failure, policy bypass, or untrusted execution.
5. **External event**  
   Power, network, geopolitical, legal, or vendor-side disruption.
6. **Concentration / common-mode failure**  
   Failure caused or amplified by excessive dependence on a single provider, layer, or correlated cluster.
7. **Upstream drift / integration misalignment**  
   The client estate or execution surface diverges from fast-moving upstream repos, packages, branches, security fixes, or contract expectations.

## 5. Measurement model

### 5.1 Expected annual loss
For scenario set `i = 1..n`:

`AEL = Σ (frequency_i × severity_i)`

Frequency MAY be estimated from internal loss data, external outage corpus data, scenario analysis, or a weighted combination.
Severity SHOULD include at least the following components where applicable:

- lost revenue;
- gross-margin impact;
- idle labor;
- incident response and recovery engineering;
- SLA / credit exposure;
- reimbursement or compensation;
- legal / regulatory cost;
- churn tail and reputational after-effects where separately justified.

### 5.2 Service-path accumulation
For a critical service path with node risks `R_i`:

`PathRisk = 1 - Π (1 - R_i)`

This is an approximation that captures chain accumulation under imperfect independence assumptions.

### 5.3 Common-mode adjustment
For cluster `g`:

`CM_g = Concentration_g × BlastRadius_g × RecoveryLag_g`

The precise implementation MAY vary, but the standard requires explicit treatment of common-mode concentration rather than assuming independent failures.

### 5.4 Reserve / capital-style view
The framework distinguishes:

- **transparent benchmark reserve** — a board-facing / benchmark-oriented capital floor;
- **scenario reserve** — model-derived reserve from scenario distributions;
- **suggested reserve** — the binding or policy-selected reserve level.

The platform SHOULD disclose which reserve basis is binding in any output.

## 6. Control model

Controls MUST be assessed across three axes:

1. **frequency reduction** — how much the control reduces likelihood;
2. **duration reduction** — how much the control reduces outage length or time-to-recover;
3. **severity reduction** — how much the control reduces business impact.

Examples:

- lockfiles, signing, provenance, and policy gates mainly reduce frequency and integrity failures;
- redundancy, failover, and graceful degradation mainly reduce duration;
- contractual protections, segmentation, backup workflows, and restoration paths mainly reduce severity.

## 7. Evidence ladder

All financial / loss claims SHOULD be tagged with an evidence grade:

- **L1 — disclosed loss**  
  Company disclosure, filing, earnings call, or direct statement.
- **L2 — insurer / broker / analyst estimate**  
  Reputable third-party modeled estimate.
- **L3 — litigation / reimbursement / compensation evidence**  
  Publicly traceable cost-bearing evidence.
- **L4 — benchmark / imputed estimate**  
  Survey, benchmark, or modeled proxy without event-specific company disclosure.

Outputs MUST distinguish event-specific evidence from benchmark imputation.

## 8. Upstream-moving rule

Because the relevant repos, packages, registries, and providers are fast-moving, any implementation or assessment generated from this standard MUST:

1. check current upstream repo / branch / PR state before writing implementation guidance;
2. distinguish current upstream facts from cached assumptions;
3. record the checked upstream surface where practical;
4. treat upstream drift as an explicit risk driver.

## 9. Cross-repository allocation

- This standards repo owns **normative language**, taxonomy, formulas, and methodology.
- `agentplane` owns execution-plane evidence hooks and runtime artifact implications.
- `sociosphere` owns automation, harvesting, watcher pipelines, and control telemetry.
- `source-os` owns runtime / package-manager / distro posture and local-first execution boundary implications.

## 10. Minimum implementation backlog

1. External outage corpus harvester.  
2. Machine-readable incident schema.  
3. Upstream watchlist and drift KRI feed.  
4. Dependency graph / concentration model.  
5. Scenario engine and reserve outputs.  
6. Client-facing avoided-loss and reserve-release narratives.
