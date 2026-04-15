# Upstream Alignment Notes

## 1. Why this note exists

This note records the current cross-repository allocation for the software operational-risk work so that standards capture stays aligned with the live upstream estate.

## 2. Current allocation

### 2.1 Normative home
**Canonical home:** `SocioProphet/socioprophet-standards-storage`

Reason:

- this repo already owns standards, benchmark methodology, governance packages, and cross-repository decision guidance;
- the operational-risk framework is primarily a normative and measurement artifact before it is an implementation artifact.

### 2.2 Execution-plane integration
**Execution-plane owner:** `SocioProphet/agentplane`

Expected responsibilities:

- execution / replay / promotion / reversal artifacts;
- runtime evidence hooks for outage / degradation / upstream-drift receipts;
- control telemetry surfaces that can consume standards defined here.

### 2.3 Automation and harvesting
**Automation owner:** `SocioProphet/sociosphere`

Expected responsibilities:

- scheduled harvesting of official status histories;
- upstream repo / package / branch / PR watchlists;
- control monitoring, KRI production, and evidence routing.

### 2.4 Runtime / distro posture
**Runtime owner:** `SociOS-Linux/source-os`

Expected responsibilities:

- package-manager and distribution update posture;
- local-first runtime dependency boundaries;
- operator-visible trust and recovery surfaces;
- mapping runtime installation / update controls back to the normative framework.

### 2.5 Typed contract lane
**Typed contract owner:** `SourceOS-Linux/*` and related specification repos

Expected responsibilities:

- machine-readable schemas where the standards are promoted from narrative to typed contract.

## 3. Current watch rule

Before implementation guidance is written into downstream repos, the writer MUST check the current upstream repo state, including at least:

- default branch;
- active PR surface;
- current docs / README positioning;
- and any recent movement that changes repository role or scope.

## 4. Immediate integration backlog

1. Add incident and watchlist schemas.  
2. Open downstream integration issues or PRs in `agentplane`, `sociosphere`, and `source-os`.  
3. Add a benchmark workload and reporting profile for reserve / outage-loss analysis.  
4. Wire the external outage corpus to automation harvesters.  
5. Define explicit upstream-drift KRIs.
