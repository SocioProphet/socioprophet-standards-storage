# Outage Corpus Method

## 1. Purpose

This document defines how the platform builds and maintains an external outage corpus for software operational-risk assessment.

The corpus exists to support:

- scenario calibration,
- frequency estimation,
- duration benchmarking,
- dependency / concentration analysis,
- and financially legible reserve or avoided-loss outputs.

## 2. Source hierarchy

The corpus SHOULD be built from the following source classes, in descending order of preferred operational truth:

1. official provider status histories and incident pages;
2. official postmortems and engineering writeups;
3. regulatory filings, earnings calls, or company disclosures;
4. insurer / broker / analyst loss estimates;
5. reputable reporting that adds independent timing, cost, or scope detail;
6. benchmark and survey overlays used only when event-specific cost evidence is absent.

## 3. Minimum incident fields

Each incident record SHOULD contain at least:

- provider / operator;
- product or service family;
- incident title;
- start time;
- end time or current state;
- duration;
- outage class / event family;
- affected layer (control plane, runtime, registry, CI/CD, identity, model provider, etc.);
- regions or tenant scope if known;
- root cause or preliminary cause if stated;
- evidence grade;
- direct loss value if disclosed or estimated;
- source URLs or canonical source identifiers;
- parsing / collection date.

## 4. Evidence rules

### 4.1 Timing and scope
Official status pages SHOULD be treated as the source of truth for start / end timing unless a postmortem explicitly supersedes them.

### 4.2 Cost
Cost estimates MUST distinguish:

- disclosed company loss,
- third-party modeled loss,
- reimbursements or litigation claims,
- benchmark-based imputations.

Benchmark-based imputations MUST NOT be presented as disclosed event losses.

### 4.3 Root cause
Root-cause assertions SHOULD be versioned when the provider later revises or deepens the explanation.

## 5. Aging and refresh

The corpus SHOULD be refreshed on a rolling basis and MUST support at least:

- a rolling 12-month view for near-term operational watch;
- a rolling 36-month view for baseline scenario calibration;
- incident aging and archive tags for older history.

## 6. Active source families

At minimum, the first harvester set SHOULD include:

- AWS status / health history,
- Azure status history,
- Google Cloud service health / incident history,
- Cloudflare status,
- GitHub status,
- npm status,
- model-provider status histories,
- and any platform-critical control-plane providers relevant to the environment under review.

## 7. Use in financial modeling

The outage corpus SHOULD feed:

- scenario frequency priors,
- duration assumptions,
- severity archetype overlays,
- concentration / common-mode watchlists,
- and client-facing benchmark narratives.

The corpus is an input, not a complete loss model.
It MUST be combined with client-specific revenue, margin, process, recovery, and control data.

## 8. Upstream-moving rule for corpus maintenance

Because provider status pages and repo/package surfaces evolve quickly, harvester jobs SHOULD record:

- retrieval timestamp,
- source version or page state if available,
- parse confidence,
- and any normalization assumptions applied during ingestion.
