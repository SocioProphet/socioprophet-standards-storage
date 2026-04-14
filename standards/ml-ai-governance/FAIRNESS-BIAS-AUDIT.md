# Fairness & Bias Audit

## Overview

This standard defines the requirements for auditing, measuring, mitigating, and monitoring
fairness and bias in ML/AI models deployed on the SocioProphet platform. All models whose
predictions influence decisions about individuals MUST comply with this standard.

Requirements use **MUST/SHOULD/MAY** per RFC 2119.

---

## 1. Training Data Audit

### 1.1 Dataset Documentation

- Every training dataset MUST have a datasheet (following Datasheets for Datasets methodology)
  covering: data sources, collection methods, intended use, out-of-scope uses, and known
  limitations.
- The datasheet MUST be stored in the CK backend as CK metadata.

### 1.2 Class Imbalance Detection and Mitigation

- Class distribution MUST be computed and stored in the dataset provenance record.
- Where class imbalance exceeds a 5:1 ratio, a mitigation strategy (oversampling, undersampling,
  class weights) MUST be documented and applied.

### 1.3 Protected Attribute Identification

- Protected attributes (race, gender, age, disability, religion, national origin, and others
  mandated by applicable law) MUST be identified in the dataset schema before training.
- If protected attributes are present, the dataset MUST be classified as Secret and subject to
  all controls in [TRAINING-DATA-SECURITY.md](TRAINING-DATA-SECURITY.md).

### 1.4 Fairness Metrics Computation

- The following fairness metrics MUST be computed on the validation set before any deployment:
  - **Demographic Parity Difference**: |P(Ŷ=1|A=0) − P(Ŷ=1|A=1)|
  - **Equalized Odds Difference (EOD)**: max(|TPR₀ − TPR₁|, |FPR₀ − FPR₁|)
  - **Calibration by group**: |E[Ŷ|Y=1, A=a] − E[Ŷ|Y=0, A=a]|
- Metrics MUST be computed for each protected attribute separately.
- Results MUST be stored in the CK model metadata under `fairness_metrics`.

### 1.5 Audit Trail of Data Decisions

- Decisions about dataset composition, exclusion of records, and class rebalancing MUST be
  recorded in the preprocessing audit trail.

---

## 2. Model Bias Testing

### 2.1 Performance Stratified by Protected Attributes

- Model performance metrics (accuracy, precision, recall, F1) MUST be computed separately for
  each sub-group defined by protected attributes.
- Sub-group performance MUST be compared against the overall population metric.

### 2.2 Equalized Odds Violation Detection

- If the equalized odds difference exceeds 0.10 for any protected attribute, the model MUST NOT
  be promoted to production until a mitigation strategy is applied and the threshold is met.

### 2.3 Calibration Testing

- Calibration plots (reliability diagrams) MUST be generated for each protected group.
- Expected Calibration Error (ECE) MUST be computed and stored in the model record.

### 2.4 Fairness Constraints in Training

- Where feasible, adversarial debiasing or fairness-aware training constraints SHOULD be applied.
- If applied, the constraint type, strength, and impact on the fairness–accuracy tradeoff MUST
  be documented.

### 2.5 Threshold Bias in Classification Models

- Where a classification threshold affects sub-group outcomes differently, threshold optimisation
  MUST be performed per sub-group or the disparity MUST be explicitly acknowledged and approved
  by the ML governance team.

---

## 3. Explainability

### 3.1 Feature Importance Analysis

- Global feature importance analysis (SHAP values or permutation importance) MUST be performed
  before deployment for all supervised learning models.
- Feature importance results MUST be stored in the CK model metadata under `feature_importance`.

### 3.2 Prediction Explanation

- For high-stakes decisions, individual prediction explanations (SHAP or LIME) MUST be available
  via the inference API.
- Explanation requests and outputs MUST be logged in the inference audit log.

### 3.3 Interpretable Models

- Where task requirements allow, interpretable models (decision tree, logistic regression, linear
  regression) SHOULD be preferred over black-box models, and the choice MUST be justified.

### 3.4 Model Card Creation

- A model card MUST be created for every model before deployment, covering:
  - Model overview and intended use
  - Training data summary
  - Evaluation results (overall and per sub-group)
  - Fairness analysis and mitigations applied
  - Known limitations
  - Ethical considerations
- Model cards MUST be stored in CK metadata and made available to stakeholders.

### 3.5 Audit Logging of Explanations

- All explanation API calls MUST be logged: requester identity, model version, input hash,
  explanation method, and timestamp.

---

## 4. Mitigation

### 4.1 Documented Mitigation Strategies

- When bias is detected, the mitigation strategy chosen (data augmentation, reweighting,
  algorithmic fairness constraints, post-processing threshold adjustment) MUST be documented.

### 4.2 Retraining Frequency

- Models deployed in high-stakes decision contexts MUST be retrained at least annually with
  updated data.
- The retraining trigger (scheduled, drift-triggered, incident-triggered) MUST be documented.

### 4.3 Fairness–Accuracy Tradeoffs

- Where applying a fairness constraint reduces overall accuracy, the tradeoff MUST be
  quantified, documented, and approved by the ML governance team.
- The approval decision MUST be stored in the CK audit trail.

### 4.4 Stakeholder Feedback Incorporation

- Feedback from affected communities or domain experts about model outcomes MUST be tracked.
- Material feedback that identifies harm MUST be escalated to the ML governance team and
  addressed within 30 days.

### 4.5 Audit Trail of Mitigation Changes

- Every bias mitigation action (retraining, threshold change, data correction) MUST generate an
  immutable audit event.

---

## 5. Continuous Monitoring

### 5.1 Post-Deployment Fairness Tracking

- Fairness metrics (§1.4) MUST be recomputed at least monthly using production prediction logs.
- Metric computation requires ground-truth labels; where unavailable, proxy metrics or periodic
  human review MUST be used.

### 5.2 Drift Detection

- If any fairness metric changes by more than 0.05 compared to the deployment baseline, a drift
  alert MUST be raised.
- Drift alerts MUST be routed to the ML governance team within 1 hour.

### 5.3 User Complaint Tracking

- A tracked channel for user complaints related to model decisions MUST be maintained.
- Complaints MUST be reviewed weekly and escalated if a pattern of disparate impact is detected.

### 5.4 Periodic Re-Auditing

- A full fairness re-audit (§1–§4) MUST be performed at least quarterly for each production
  model.
- Re-audit results MUST be stored in CK and compared to the original audit results.

### 5.5 Incident Response

- Confirmed fairness incidents (disparate impact causing harm) MUST trigger immediate suspension
  of the model pending remediation.
- The incident response MUST be documented and completed within 72 hours.
- Post-incident review MUST be conducted and findings stored in the CK audit trail.

---

## References

- NIST AI Risk Management Framework (AI RMF 1.0): https://airc.nist.gov/Home
- Datasheets for Datasets: https://arxiv.org/abs/1803.09010
- Model Cards for Model Reporting: https://arxiv.org/abs/1810.03993
- Fairlearn: https://fairlearn.org/
- NIST SP 800-53 Rev. 5 CA-7 (Continuous Monitoring)
- EU AI Act (for applicable jurisdictions)
