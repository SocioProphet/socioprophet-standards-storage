# Evidence Bundle Standard v1

Status: draft
Owner: SocioProphet standards storage
Scope: provenance, source records, research logs, evidence artifacts, claim status, and reproducibility metadata for systems learning loops and adjacent platform work.

## Purpose

This standard prevents hand-waving. Any learning-loop, public-sector innovation profile, MLOps feedback loop, SourceOS lifecycle loop, agent learning loop, or platform capability-transition claim must be backed by an evidence bundle.

An evidence bundle is not a blob of notes. It is a structured object that preserves sources, claims, confidence, artifacts, and review state.

## Required object: EvidenceBundle

```yaml
id: stable identifier
title: human readable title
scope: learning_loop | program_profile | mlops_loop | os_lifecycle | agent_learning | platform_contract | ontology_update
summary: concise statement of what this bundle supports
created_at: ISO-8601 datetime
updated_at: ISO-8601 datetime
owner: repo, team, or agent steward
source_records: list of SourceRecord references
claims: list of ClaimRecord references
artifacts: list of EvidenceArtifact references
confidence_rating: high | medium | low | contested | unknown
review_state: draft | reviewed | accepted | rejected | deprecated
last_reviewed: ISO-8601 date
reviewers: list of people, teams, or agent roles
related_standards: list of standard paths or URIs
```

## Required object: SourceRecord

```yaml
id: stable identifier
title: source title
publisher: source publisher, institution, repository, or author
url: canonical URL when available
accessed_at: ISO-8601 datetime
publication_date: ISO-8601 date, if known
source_type: official | primary | academic | press | repository | documentation | secondary | internal | unknown
stability: stable | versioned | mutable | unknown
trust_rating: high | medium | low | contested | unknown
summary: short source summary
supports_claims: list of ClaimRecord ids
notes: known limitations, ambiguity, or caveats
```

## Required object: ClaimRecord

```yaml
id: stable identifier
claim: atomic factual or interpretive claim
claim_type: factual | inferred | interpretive | speculative | deprecated | disputed
status: established | supported | partially_supported | unsupported | disputed | stale
supporting_sources: list of SourceRecord ids
contradicting_sources: list of SourceRecord ids, if any
confidence_rating: high | medium | low | contested | unknown
last_checked: ISO-8601 date
```

## Required object: EvidenceArtifact

```yaml
id: stable identifier
artifact_type: citation | dataset | log | model_card | dataset_card | manifest | transcript | build_output | attestation | ontology | schema | notebook | report | other
path_or_uri: repository path, content URI, artifact URL, or storage pointer
content_hash: sha256 or stronger hash when available
produced_by: person, tool, workflow, or agent
produced_at: ISO-8601 datetime
reproducibility_status: reproducible | partially_reproducible | not_reproducible | unknown
```

## Claim discipline

No program profile, institutional learning-loop entry, model-serving claim, MLOps lifecycle claim, OS lifecycle claim, or agent learning claim is accepted unless every material assertion maps to at least one ClaimRecord.

Claims about current organizations, current program status, funding, active maintainership, or modern technology recommendations must be periodically rechecked.

## Confidence ratings

- `high`: backed by official, primary, current, or otherwise authoritative sources.
- `medium`: backed by credible secondary sources or multiple convergent sources.
- `low`: partial evidence, old source, ambiguous claim, or single secondary source.
- `contested`: material disagreement or conflicting evidence exists.
- `unknown`: insufficient evidence.

## Case-study sensitivity

Public-sector, defense, and national-security case studies may be represented only as public-source institutional learning records. Evidence bundles must avoid unsupported operational extrapolation.

The bundle must state:

```yaml
public_sources_only: true
operational_guidance: false
classified_or_restricted_sources: false
```

## Reproducibility requirements

For model and platform work, an EvidenceBundle should include:

- source index;
- schema or ontology version;
- input artifact hashes;
- workflow or pipeline reference;
- output artifact hashes;
- evaluation or review record;
- rollback or deprecation path.

## Model serving note

Evidence bundles for model-serving standards must distinguish active serving runtimes from legacy references.

Default status vocabulary:

```yaml
runtime_status: primary | supported | experimental | legacy_reference | deprecated
```

Ray Serve and KubeRay are the preferred primary serving substrate for new SocioProphet MLOps serving-loop work. Clipper is legacy-reference only.
