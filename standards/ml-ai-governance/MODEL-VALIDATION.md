# Model Validation & Testing

## Overview

This standard defines the validation and testing requirements that every model artifact MUST pass
before promotion from staging to production. It covers functional testing, safety testing,
security testing, compliance validation, and the approval workflow.

Requirements use **MUST/SHOULD/MAY** per RFC 2119.

---

## 1. Functional Testing

### 1.1 Unit Tests

- Every model MUST have unit tests that verify expected output shapes and types for a minimal
  set of canonical inputs.
- Tests MUST cover boundary inputs: empty, maximum-size, minimum-size, and type-edge cases.
- Unit tests MUST be version-controlled alongside the model training code.

### 1.2 Integration Tests

- Integration tests MUST exercise the model with representative real-data samples drawn from
  the validation split.
- Inference latency for each canonical input MUST be measured during integration testing.

### 1.3 Performance Tests

- p50, p95, and p99 inference latency MUST be measured under the anticipated peak request rate.
- Throughput (requests/second) MUST be measured and MUST exceed the defined SLA minimum.

### 1.4 Regression Tests

- Before each promotion, metrics MUST be compared against the currently deployed version.
- Regression in accuracy, latency, or fairness metrics beyond configured thresholds MUST block
  promotion.

---

## 2. Safety Testing

### 2.1 Adversarial Examples

- A representative adversarial example suite (FGSM, PGD, or equivalent) MUST be run against
  classification and regression models.
- Models MUST not exhibit accuracy drops greater than the configured robustness threshold on the
  adversarial suite.

### 2.2 Edge Cases

- Tests MUST include very large inputs (max tensor dimensions), very small inputs (single token
  or single pixel), and zero-valued inputs.
- Outputs for these cases MUST be finite (no NaN, ±Inf) and within the documented output range.

### 2.3 Out-of-Distribution Detection

- Models that are expected to operate on distribution-limited inputs SHOULD implement an
  out-of-distribution (OOD) detector.
- OOD detection accuracy MUST be measured and documented before deployment.

### 2.4 Fairness Testing

- Fairness testing MUST be executed as defined in [FAIRNESS-BIAS-AUDIT.md](FAIRNESS-BIAS-AUDIT.md).
- Validation MUST not complete without a passing fairness audit result.

### 2.5 Interpretability Validation

- For models deployed in high-stakes decision contexts, at least one global interpretability
  analysis (SHAP or LIME) MUST be documented and attached to the model record in CK.

---

## 3. Security Testing

### 3.1 Model Extraction Attack Hardening

- Inference endpoints for proprietary models MUST implement rate limiting and query complexity
  restrictions to raise the cost of model extraction attacks.
- Rate limit configuration MUST be documented in the deployment record.

### 3.2 Training Data Poisoning Resilience

- Training pipelines MUST include data validation checks (schema enforcement, anomaly detection
  on class distribution) designed to detect poisoning attempts.
- The results of data validation checks MUST be stored in the training job provenance record.

### 3.3 Adversarial Evasion Robustness

- Robustness results from §2.1 MUST be reviewed by the security team for high-risk models.
- Models that fail the robustness threshold MUST be retrained or hardened before deployment.

### 3.4 Differential Privacy Validation

- When differential privacy has been applied, the privacy budget (ε, δ) MUST be verified against
  the values recorded in the provenance record.
- A post-hoc privacy accounting analysis (Rényi DP or Moments Accountant) SHOULD be performed
  and stored.

---

## 4. Compliance Testing

### 4.1 SBOM Completeness Validation

- An automated check MUST verify that the CycloneDX SBOM enumerates all direct and transitive
  dependencies present in the training environment.
- Incomplete SBOMs MUST block promotion.

### 4.2 Dependency Vulnerability Scanning

- All SBOM components MUST be checked against the OSV database (or equivalent) for known CVEs.
- Critical or high CVEs in runtime dependencies MUST block promotion unless an approved
  exception with a remediation date exists.

### 4.3 Code Review Completion Verification

- An automated check MUST confirm that the training script PR has the required approval(s) before
  the model can be promoted.

### 4.4 Signature Verification

- The model artifact signature (ECDSA-P256) MUST be verified as part of the automated compliance
  checks.
- Promotion MUST be blocked if signature verification fails.

### 4.5 Audit Trail Completeness

- An automated check MUST confirm that all required audit events (training start/end, data
  access, SBOM generation, test results) are present in the CK backend before promotion proceeds.

---

## 5. Approval Workflow

### 5.1 Deployment Request

1. Data scientist commits model artifacts and provenance record to the CK staging environment.
2. An automated compliance pipeline runs §4 checks.
3. If all checks pass, a deployment request is raised in the governance system.

### 5.2 Human Approval

- At least one ML governance team member MUST approve deployment to production.
- The approver MUST review: SBOM, fairness audit results, security test results, and metric
  regression report.
- Approval decision and rationale MUST be recorded in the CK audit trail.

### 5.3 Risk-Based Security Review

- Models classified as high-risk (PII inputs, consequential decisions) MUST receive an
  additional security review from the security team.
- The security reviewer MAY approve, reject, or request changes.

### 5.4 Promotion to Staging → Production

- Staging promotion MUST pass automated compliance checks (§4).
- Production promotion MUST pass automated compliance checks AND human approval (§5.2).
- Promotion events MUST be logged as immutable CK audit entries.

---

## References

- NIST SP 800-53 Rev. 5 CA-7 (Continuous Monitoring)
- NIST SP 800-53 Rev. 5 SI-2 (Flaw Remediation)
- NIST SP 800-53 Rev. 5 SI-7 (Software Integrity)
- OWASP Machine Learning Security Top 10
