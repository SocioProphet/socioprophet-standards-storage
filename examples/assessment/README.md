# Evidence-Native Assessment Fixture Set v0

This fixture set demonstrates the smallest fully linked evidence-native assessment chain:

1. `EvidenceRef`
2. `Claim`
3. `ClaimConflict`
4. `ControlRequirement`
5. `ControlCellEvaluation`
6. `Finding`
7. `AssessmentReceipt`
8. `AssessmentReport`

## Subject under assessment

- subject id: `vendor:acme-cloud`
- framework: `nist-800-53-rev5`
- control: `AC-2`
- row id: `ac-2-account-management`

## Fixture order

- `evidence_ref.vendor_policy.example.json`
- `claim.admin_accounts_reviewed_quarterly.example.json`
- `claim_conflict.access_review_evidence_missing.example.json`
- `control_requirement.nist_ac_2.example.json`
- `control_cell_evaluation.nist_ac_2.partial.example.json`
- `finding.nist_ac_2.partial.example.json`
- `assessment_receipt.vendor_acme_nist_ac_2.example.json`
- `assessment_report.vendor_acme_nist_summary.example.json`
- `fixture_manifest.vendor_acme_nist_ac_2.example.json`

## Intent

The fixture demonstrates a common partial-compliance shape:
- the vendor supplies a policy document
- the policy document asserts quarterly account reviews
- required proof classes also demand an access review record and an identity export
- those proofs are missing
- the evaluation therefore becomes `partial`
- a finding is emitted
- the assessment receipt is still sealed with explicit lineage and replay linkage
