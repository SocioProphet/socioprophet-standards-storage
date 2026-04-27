# Evaluation Record Standard v1

Status: draft
Owner: SocioProphet standards storage
Depends on:
- `standards/evidence-bundle-standard.v1.md`
- `standards/open-courseware-corpus-standard.v1.md`
- SocioProphet/socioprophet-standards-knowledge: `standards/evaluation-fabric-standard.v1.md`
- SocioProphet/sociosphere: `standards/angel-of-the-lord/README.md`

## Purpose

This standard defines how evaluation records are stored for people, agents, models, services, curricula, ontologies, OS/fleet lifecycle systems, Atlas bundles, and Prophet Platform capabilities.

The storage standard is deliberately evidence-first. Scores without artifacts are insufficient. Reviews without sources are insufficient. Claims without reproducible records are insufficient. Forward progress without regression evidence is insufficient.

## Required object: EvaluationRecord

```yaml
id: stable identifier
evaluation_track_ref: EvaluationTrack reference
subject_ref: person, agent, model, service, release, repo, ontology, curriculum module, or platform capability
subject_type: human | agent | model | service | os_release | boot_release | ontology | curriculum | platform_capability | atlas_bundle | other
evaluation_task_refs: list of EvaluationTask references
attempt_refs: list of EvaluationAttempt references
rubric_refs: list of Rubric references
metric_refs: list of Metric references
prior_regression_check_ref: EpochRegressionCheck reference where epochs exist
result_summary: concise result statement
result: pass | pass_with_findings | remediation_required | fail | blocked | restricted_handling | unknown
evidence_bundle_ref: EvidenceBundle reference
angel_epoch_grade_ref: AngelEpochGrade reference, if applicable
review_state: draft | reviewed | accepted | rejected | deprecated
created_at: ISO-8601 datetime
updated_at: ISO-8601 datetime
```

## Required object: EvaluationAttempt

```yaml
id: stable identifier
evaluation_task_ref: EvaluationTask reference
subject_ref: evaluated subject
attempt_mode: open_book | closed_book_simulated | timed | sandboxed | tool_allowed | no_tool | project_review | benchmark_run | service_probe | lifecycle_run | ontology_validation | regression_rerun | stochastic_repeat | other
started_at: ISO-8601 datetime
completed_at: ISO-8601 datetime
inputs: artifact references
outputs: EvidenceArtifact references
raw_scores: map of metric ids to values
rubric_scores: map of rubric criteria to values
reviewer_refs: human, agent, CI job, Sociosphere, Delivery Excellence, standards, or Angel references
review_notes_ref: EvidenceArtifact reference
status: completed | incomplete | invalidated | remediation_required | blocked
```

## Required object: RemediationRecord

```yaml
id: stable identifier
evaluation_record_ref: EvaluationRecord reference
finding_ref: Angel finding, rubric finding, metric miss, regression finding, or review issue
severity: blocker | high | medium | low | info
owner: repo, team, person, or agent
required_action: what must change
due_state: next epoch, before merge, before release, before publication, before transition, or custom
evidence_required: EvidenceArtifact requirements
status: open | in_progress | resolved | accepted_risk | rejected | deprecated
resolution_evidence_ref: EvidenceBundle reference
```

## Required object: TransferEvaluationRecord

```yaml
id: stable identifier
source_learning_ref: course, module, benchmark, case study, training cycle, or evaluation record
target_context: repo, platform primitive, model, ontology, SourceOS lifecycle, Atlas bundle, or curriculum artifact
invariants_tested: what should transfer unchanged
adaptations_observed: what changed in the new context
tasks: EvaluationTask references
result: pass | pass_with_findings | remediation_required | fail | unknown
evidence_bundle_ref: EvidenceBundle reference
```

## Required object: EpochRegressionCheck

Epoch regression checks persist proof that prior accepted grades, exams, tests, projects, and transfer tasks remain non-regressed at the current epoch.

```yaml
id: stable identifier
subject_ref: evaluated subject
subject_type: human | agent | model | service | os_release | boot_release | ontology | curriculum | platform_capability | atlas_bundle | other
current_epoch_ref: current epoch
baseline_epoch_ref: prior accepted epoch
monotonicity_policy_ref: MonotonicProgressPolicy reference
prior_tasks_evaluated: list of prior EvaluationTask refs
baseline_records: list of prior EvaluationRecord refs
current_records: list of current EvaluationRecord refs
attempt_refs: list of EvaluationAttempt refs, including regression_rerun or stochastic_repeat attempts
deltas:
  metric_deltas: map of metric id to baseline/current/delta
  rubric_deltas: map of rubric criterion to baseline/current/delta
  grade_deltas: map of grade item to baseline/current/delta
allowed_delta_applied: numeric, rubric-band, or stochastic tolerance applied
stochastic_summary:
  repeats: integer
  aggregation_method: mean | median | worst_case | confidence_bound | custom
  confidence_bound: description or value
regressions_found: list of regression findings
result: no_regression | within_allowed_delta | remediation_required | blocked | unknown
evidence_bundle_ref: EvidenceBundle reference
```

## Required object: RegressionEvaluationRecord

```yaml
id: stable identifier
subject_ref: evaluated subject
baseline_ref: prior EvaluationRecord, release, model, curriculum, ontology, or capability
current_ref: current artifact or run
regression_tasks: EvaluationTask references
metrics_compared: list of Metric references
regressions_found: list
result: no_regression | acceptable_regression | remediation_required | blocked | unknown
evidence_bundle_ref: EvidenceBundle reference
```

## Storage requirements by lane

### Human and agent education

Must store:

- course material references;
- assessment attempt outputs;
- rubric results;
- remediation records;
- transfer evaluation records;
- prior exam/test/project regression checks for epoch-bearing subjects;
- Angel epoch grade for agent education.

### Michael-agent education

Must additionally store:

- all prior accepted exam/test/project grades;
- current-epoch rerun or regression evidence against prior accepted assessments;
- stochastic tolerance evidence where applicable;
- remediation records for any grade drop outside allowed tolerance;
- Angel grade confirming whether the regression is material.

### Model and MLOps

Must store:

- dataset references;
- experiment references;
- model artifact references;
- evaluation metrics;
- serving deployment references;
- observability and feedback records;
- stochastic repeated-run evidence where metrics vary;
- retraining or rollback decisions.

### OS and fleet lifecycle

Must store:

- build manifest;
- release-set or boot-release-set reference;
- device/fleet fingerprint;
- install/update/rollback result;
- compliance result;
- regression record against prior release behavior;
- Angel grade where publication, release, or fleet transition is affected.

### Ontology and knowledge systems

Must store:

- source records;
- extraction records;
- ontology diff;
- validation output;
- query regression records;
- review state.

## Minimum retention

Evaluation records supporting accepted claims, releases, education completions, platform transitions, or model deployments SHOULD be retained append-only. Restricted material may be stored under restricted handling, but its existence and sanitized summary should still be recorded where policy permits.

Prior accepted grade baselines for epoch-bearing agents and models SHOULD be retained append-only so monotonic progress can be verified.

## Acceptance rule

An evaluation result may not be marked `accepted` unless:

1. all required task attempts are recorded;
2. evidence bundle exists;
3. metrics or rubrics are recorded;
4. remediation is closed or explicitly accepted;
5. Angel findings are resolved where Angel grading is required;
6. transfer or regression evaluation is complete where relevant;
7. prior accepted exams, tests, projects, and transfer tasks remain non-regressed within the applicable monotonic progress policy;
8. stochastic deltas are documented with repeated-run or confidence-bound evidence where applicable.
