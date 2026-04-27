# Open Courseware Corpus Standard v1

Status: draft
Owner: SocioProphet standards storage
Depends on:
- SocioProphet/socioprophet-standards-knowledge: `standards/agent-education-equivalence-standard.v1.md`
- SocioProphet/socioprophet-standards-knowledge: `standards/foundational-training-cycle-standard.v1.md`
- SocioProphet/socioprophet-standards-knowledge: `standards/evaluation-fabric-standard.v1.md`
- `standards/evidence-bundle-standard.v1.md`
- `standards/evaluation-record-standard.v1.md`
- SocioProphet/sociosphere: `standards/angel-of-the-lord/README.md`

## Purpose

This standard defines how SocioProphet may use public open courseware, public course catalogs, public syllabi, public assignments, and public exams as corpora for agent education and degree-equivalent mastery mapping.

The standard is designed for Michael-agent and related SocioProphet agents. It uses the institutions' own public materials where lawfully accessible and preserves provenance, licensing, source constraints, assessment evidence, and regenerative curriculum enrichment history.

This standard does not claim institutional enrollment, credit, certification, or degree award.

## Core rule

Use the institution's own public materials as the primary corpus whenever available:

```text
public course catalog -> degree requirement map -> public courseware -> assignments/labs -> published exams/tests -> agent assessment -> evidence bundle -> transfer evaluation -> Angel hardening -> enriched regenerated curriculum
```

Third-party summaries may supplement, but they must not replace public primary-source course materials when primary material exists.

## Regenerative curriculum doctrine

References, course maps, curricula, tests, transfer tasks, and rubrics are not static. They must be captured, regenerated, enriched, and re-evaluated each pass.

Every pass should:

1. preserve the prior corpus snapshot;
2. ingest newly available or newly discovered public source material;
3. improve source metadata, learning-objective extraction, and assessment mapping;
4. rerun or reference prior accepted assessments;
5. compare against prior accepted grades and transfer tasks;
6. apply Angel of the Lord hardening findings;
7. produce enrichment deltas;
8. update curriculum, rubrics, remediation queues, and transfer tasks;
9. preserve evidence for all changes.

## Required object: CoursewareCorpus

```yaml
id: stable identifier
institution_name: MIT | Harvard | Stanford | Berkeley | CMU | Oxford | Cambridge | Princeton | Caltech | other
corpus_name: human readable corpus name
source_type: open_courseware | public_catalog | syllabus_archive | exam_archive | assignment_archive | textbook | lecture_notes | mixed
canonical_url: public URL
accessed_at: ISO-8601 datetime
license_or_terms: known license, terms, or access constraints
permitted_uses: indexing | citation | local_metadata | educational_use | redistribution_allowed | redistribution_restricted | unknown
materials:
  - CourseMaterial references
source_record_ref: SourceRecord reference
corpus_snapshot_ref: CurriculumCorpusSnapshot reference
confidence_rating: high | medium | low | contested | unknown
notes: limitations, missing materials, or access constraints
```

## Required object: CurriculumCorpusSnapshot

```yaml
id: stable identifier
corpus_ref: CoursewareCorpus reference
snapshot_version: semantic or monotonic version
snapshot_time: ISO-8601 datetime
source_records: list of SourceRecord references
material_refs: list of CourseMaterial references
content_hash_manifest: EvidenceArtifact reference
prior_snapshot_ref: previous CurriculumCorpusSnapshot reference, if any
enrichment_delta_ref: CurriculumEnrichmentDelta reference, if any
review_state: draft | reviewed | accepted | rejected | deprecated
```

## Required object: CurriculumEnrichmentDelta

```yaml
id: stable identifier
prior_snapshot_ref: CurriculumCorpusSnapshot reference
new_snapshot_ref: CurriculumCorpusSnapshot reference
change_type: source_added | source_removed | metadata_improved | objective_refined | assessment_added | rubric_refined | transfer_task_added | angel_remediation | licensing_update | other
changes: list of structured changes
evidence_bundle_ref: EvidenceBundle reference
angel_findings_addressed: list of Angel finding refs
regression_check_ref: EpochRegressionCheck reference, if applicable
accepted_by: review role, standards gate, Academy gate, or Sociosphere gate
```

## Required object: CourseMaterial

```yaml
id: stable identifier
course_id: institutional course number where available
title: course title
term: term or version where available
material_type: catalog_entry | syllabus | lecture | reading | assignment | lab | quiz | exam | solution | project | video | transcript | notebook | other
url: public URL
content_hash: hash where stored or mirrored lawfully
license_or_terms: known license or access terms
assessment_role: instructional | practice | graded_equivalent | exam_equivalent | project_equivalent | unknown
mapped_requirements: EducationRequirement references
source_record_ref: SourceRecord reference
```

## Required object: PublishedAssessment

```yaml
id: stable identifier
course_material_ref: CourseMaterial reference
assessment_type: problem_set | quiz | midterm | final_exam | test | lab | project | paper | oral_defense_equivalent | code_review | other
questions_or_tasks: references or extracted metadata
solutions_available: true | false | partial | unknown
integrity_policy: open_practice | proctored_equivalent_required | holdout_variant_required | human_review_required
passing_criteria: rubric or scoring rule
attempt_records: list of AssessmentAttempt references
prior_epoch_required: true | false
```

## Required object: AssessmentAttempt

```yaml
id: stable identifier
agent_id: michael_agent | socioprophet_agent | other
published_assessment_ref: PublishedAssessment reference
attempt_mode: open_book | closed_book_simulated | timed_simulated | project_review | oral_defense_simulated | code_review | regression_rerun | stochastic_repeat
started_at: ISO-8601 datetime
completed_at: ISO-8601 datetime
outputs: EvidenceArtifact references
score: numeric, rubric, or pass/fail
prior_score_ref: prior accepted AssessmentAttempt reference, if applicable
delta_from_prior: numeric, rubric, pass/fail, or qualitative delta
reviewer: human, agent, Angel, or review role
review_state: draft | reviewed | accepted | rejected | remediation_required | blocked
remediation_refs: weak objectives or follow-up cycles
```

## Corpus usage policy

Allowed:

- store metadata and source records;
- cite and link to public course materials;
- extract learning objectives;
- map courses to internal education requirements;
- record assessment attempts and outputs;
- store agent-produced solutions and reflections when allowed;
- use public exams/tests as assessment corpora when terms permit;
- regenerate enriched curriculum metadata, rubrics, mappings, and transfer tasks from public corpora and internal evidence.

Restricted:

- do not redistribute copyrighted course materials unless the license permits redistribution;
- do not imply institutional endorsement;
- do not claim enrollment, credit, certification, or degree award;
- do not bypass access controls or scrape restricted systems;
- do not treat answer keys as proof of mastery without independent attempt, review, holdout assessment, transfer task, and Angel review where required.

## Assessment integrity

When published exams and solutions are available, the training system MUST distinguish between practice and evaluation.

Recommended modes:

1. Practice mode: public problems and solutions may be used for learning.
2. Timed simulation: public exams are attempted under time and resource constraints.
3. Holdout variant: analogous problems are generated or selected to test transfer.
4. Regression rerun: prior accepted exams/tests/projects are re-evaluated to prevent hidden regression.
5. Human, agent, or Angel review: evidence is reviewed against rubric.
6. Transfer task: concept is applied to SocioProphet platform, MLOps, ontology, SourceOS, or Atlas work.

## Degree-equivalent mapping

A courseware corpus supports degree-equivalent mapping only when it is connected to:

- public degree or program requirements;
- learning objectives;
- assignments/labs/exams/projects;
- assessment attempts;
- evidence bundles;
- transfer evaluations;
- prior-assessment regression checks;
- Angel epoch grading where Michael-agent or high-consequence work is involved;
- review gates.

## Michael-agent application

Michael-agent education ledgers SHOULD prefer primary public sources such as MIT OpenCourseWare and public Harvard catalog/course materials where available.

For each requirement, Michael-agent should record:

```yaml
source_course_materials: list of CourseMaterial ids
corpus_snapshot_ref: CurriculumCorpusSnapshot reference
published_assessments: list of PublishedAssessment ids
attempt_records: list of AssessmentAttempt ids
prior_regression_check_ref: EpochRegressionCheck reference
transfer_evidence: EvidenceArtifact references
angel_epoch_grade_ref: AngelEpochGrade reference
review_state: accepted | remediation_required | incomplete | blocked
```

## Regeneration and enrichment loop

Each curriculum pass should generate:

- new or updated CoursewareCorpus metadata;
- CurriculumCorpusSnapshot;
- CurriculumEnrichmentDelta;
- updated CourseMap records;
- updated PublishedAssessment mappings;
- updated rubrics and transfer tasks;
- EvaluationRecord and EpochRegressionCheck records;
- Angel findings and remediation records where applicable.

The curriculum should improve each pass, but no enrichment may mask regression. Prior accepted grades, exams, tests, projects, and transfer tasks must remain non-regressed within the applicable monotonic progress policy.

## Relationship to evidence bundles

Every CoursewareCorpus, CurriculumCorpusSnapshot, CurriculumEnrichmentDelta, CourseMaterial, PublishedAssessment, and AssessmentAttempt must be backed by SourceRecord and EvidenceBundle objects under the Evidence Bundle Standard.
