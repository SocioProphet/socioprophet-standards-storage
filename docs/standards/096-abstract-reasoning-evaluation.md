# Abstract Reasoning Evaluation (Normative)

This document uses RFC 2119 language: **MUST**, **SHOULD**, **MAY**.

## 1. Scope

This standard defines how SocioProphet measures abstract reasoning claims for model, planner, and hybrid system lanes.

## 2. Core rule

A system MUST NOT be credited with abstract-reasoning success solely because:
- it returned a correct answer,
- it returned a plausible explanation,
- it generated compilable code.

Abstract-reasoning success MUST be evaluated against rule recovery, semantic correctness, and resistance to counterexample.

## 3. Required dimensions

Every abstract benchmark run MUST record:
- representation mode,
- answer mode,
- example count,
- compile result when code is used,
- semantic correctness,
- explanation validity when explanation text is produced,
- counterexample search result,
- contamination risk.

## 4. Representation modes

Benchmark cases MUST declare one of:
- `natural_language`
- `symbolic`
- `mixed`

Systems SHOULD be evaluated across more than one representation mode when the task family permits it.

## 5. Answer modes

Benchmark cases MUST declare one of:
- `open_ended`
- `multiple_choice`
- `program_induction`

Multiple-choice performance MUST NOT be reported without being distinguished from open-ended performance.

## 6. Contamination and legacy risk

Cases MUST carry a contamination-risk tag.

Legacy benchmark families or list-processing patterns with likely training overlap SHOULD be tagged as high-risk unless hidden-holdout or perturbation procedures are documented.

## 7. Result policy

A run MAY be marked `pass` only when:
- semantic correctness passes,
- all hard verification requirements pass,
- contamination status is acceptable for the stated claim level.

## 8. Non-goal

This standard does not define transport or runtime execution behavior.
It defines only the evaluation and reporting contract for abstract reasoning claims.
