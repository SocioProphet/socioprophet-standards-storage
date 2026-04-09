# Evidence-Native Assessment Contracts v0

## Purpose

This standard freezes the first canonical contract pack for evidence-native assessment across the SocioProphet stack.

The target operating loop is:

1. ingest evidence
2. normalize claims
3. evaluate controls
4. emit cited findings
5. route remediation
6. seal an assessment receipt
7. support deterministic reassessment and replay

This standard is intentionally narrow. It does **not** attempt to define every possible GRC, vendor-risk, privacy, or security workflow. It defines the minimum interoperable contract pack needed for a first governed assessment slice.

## Canonical repository roles

- `socioprophet-standards-storage` is the canonical source for contract definitions, conformance rules, and benchmark posture.
- `socioprophet-standards-knowledge` carries the semantic / JSON-LD context used to interpret the contract pack.
- `policy-fabric` authors policy intent and compiles control requirements.
- `agentplane` executes evaluator bundles, emits execution evidence, and seals receipts.
- `prophet-platform` hosts the long-running assessment services and platform bindings.
- `socioprophet` renders the public and operator-facing surfaces.

## Canonical entities

The v0 contract pack contains the following entities.

### 1. EvidenceRef

`EvidenceRef` is the immutable handle for an evidence fragment.

It MUST identify:
- source system
- source URI or equivalent locator
- content digest
- extraction / locator range
- extraction tool identity and version
- locality / confidentiality / retention classification

An `EvidenceRef` is the primitive citation surface. No downstream finding or control decision may cite opaque prose instead of one or more `EvidenceRef` objects.

### 2. Claim

`Claim` is a normalized assertion derived from one or more evidence fragments.

A `Claim` MUST carry:
- subject
- predicate
- evidence references
- extractor identity and version

A `Claim` SHOULD carry:
- object or value
- modality
- confidence
- normalized text
- claim type

Every `Claim` MUST reference at least one `EvidenceRef`.

### 3. ClaimConflict

`ClaimConflict` records a contradiction, scope mismatch, staleness dispute, policy mismatch, or proof insufficiency between claims or between a claim and a control requirement.

The system MUST represent conflicts explicitly rather than burying them inside free-text rationales.

### 4. ControlRequirement

`ControlRequirement` is the normalized control-row contract used by policy authors and evaluators.

It MUST identify:
- framework id and version
- control id
- row id
- title
- required proof classes
- blocker / decision policy

This entity is the bridge between authored policy in `policy-fabric` and runtime evaluation in `agentplane`.

### 5. ControlCellEvaluation

`ControlCellEvaluation` is the row-level evaluation result.

It MUST carry:
- row / control reference
- trace id
- status
- decision
- evaluator identity and version
- supporting evidence refs or explicit missing proof classes

It SHOULD also carry:
- claim refs
n- conflict refs
- exception refs
- incident refs
- rationale
- confidence

Every non-pass result MUST include enough structured evidence to support audit review.

### 6. Finding

`Finding` is the reviewable remediation object derived from one or more control evaluations.

A `Finding` MUST carry:
- severity
- disposition
- evidence refs
- remediation summary
- closure criteria

A `Finding` is a review surface, not the source of truth for the evaluation itself.

### 7. AssessmentReceipt

`AssessmentReceipt` is the sealed record for one governed assessment run.

It MUST carry:
- receipt id
- trace id
- assessment scope
- policy bundle id and version
- evaluator versions
- evidence digests
- evaluation refs
- finding refs
- replay manifest ref
- replayable flag
- sealed timestamp

`AssessmentReceipt` is the canonical audit / replay seam.

### 8. AssessmentReport

`AssessmentReport` is a derived stakeholder view over one or more receipts.

It MUST reference a receipt.
It MUST NOT become the canonical source of truth.
A platform may generate multiple report views from the same receipt for operators, auditors, executives, or third parties.

## Normative invariants

### Evidence invariants

1. Every `Claim` MUST reference one or more `EvidenceRef` objects.
2. Every `ControlCellEvaluation` MUST either cite supporting evidence or explicitly state which proof classes are missing.
3. Every `Finding` MUST cite one or more `EvidenceRef` objects.
4. Every `AssessmentReceipt` MUST carry evidence digests for the evidence actually used in the run.

### Decision invariants

1. Every non-pass `ControlCellEvaluation` MUST be traceable to a `ControlRequirement` row.
2. Every deny / warn / require-approval decision MUST be structurally recoverable from the recorded evaluation object.
3. Exceptions and incidents MUST be linked structurally where present; they MUST NOT exist only as prose.

### Replay invariants

1. Every `AssessmentReceipt` MUST include a replay manifest reference.
2. A report without a receipt reference is non-conformant.
3. A finding without evaluation lineage is non-conformant.

### Model / evaluator invariants

1. Extractor and evaluator identity and version MUST be recorded.
2. Implementations SHOULD record model routing or evaluator selection policy when non-deterministic routing is possible.
3. Evidence handling policy MUST be explicit for locality, confidentiality, and retention.

## Conformance by repository

### policy-fabric

`policy-fabric` MUST:
- author or import `ControlRequirement` rows
- compile row-derived decision policy into execution-oriented structure
- validate that required proof classes are well-formed
- preserve exception and promotion semantics

### agentplane

`agentplane` MUST:
- execute evaluator bundles against pinned policy bundles
- emit execution evidence and replay inputs
- preserve trace ids through the assessment run
- seal or assemble `AssessmentReceipt` artifacts

### prophet-platform

`prophet-platform` MUST:
- expose runtime services that consume and produce these contracts
- keep platform bindings separate from normative schema ownership
- preserve typed transport and service compatibility across runtime services

### socioprophet

`socioprophet` MUST:
- treat reports as derived views
- expose drill-down from UI findings to evaluations and evidence references
- avoid standalone scores without methodology and receipt linkage

## Benchmark posture

Implementations SHOULD benchmark the following dimensions before making strong product claims:
- claim extraction precision / recall
- contradiction detection precision / recall
- control decision reproducibility
- evidence sufficiency false-positive / false-negative rates
- reassessment drift stability
- receipt completeness / replay success rate

## Machine-readable contract pack

The initial machine-readable pack lives at:

- `schemas/assessment/evidence-native-assessment-contract-pack.schema.json`

The initial semantic context lives in:

- `SocioProphet/socioprophet-standards-knowledge:contexts/evidence-native-assessment.context.jsonld`

## Non-goals for v0

This standard does not yet define:
- framework-specific ontology exhaustively
- questionnaire UX
- third-party scoring formulas
- portfolio analytics rollups beyond receipt-derived summaries
- narrative report rendering templates

Those may be added later, but they are downstream of this canonical contract pack.
