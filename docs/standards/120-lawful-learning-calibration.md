# Standard 120: Calibrated Lawful Learning

## Status

Draft.

## Scope

This standard defines the contract for calibrated lawful learning systems across SocioProphet. It covers state construction, constraint enforcement, gate calibration, hyperparameter tuning, evidence ledger generation, and observer-stable evidence.

The authoritative doctrine starts in `SocioProphet/ProCybernetica`. This standard should become normative only after ProCybernetica reconciliation.

## Conformance requirements

A conforming lawful learning implementation MUST:

1. define a 26-dimensional spectral-unitary-spatial state or explicitly declare a reduced state;
2. enforce constraints through hard activation, slack penalties, or augmented Lagrangian terms;
3. avoid meaningless positive rescaling of inequalities;
4. learn or validate all thresholds and penalties;
5. disclose hyperparameter search ranges;
6. include negative controls for arithmetic priors;
7. record canonical serialized evidence;
8. distinguish illustrative examples from executed results;
9. include failure-mode handling;
10. define the operational truth score `T=L*E`.

## Valid gate mechanisms

A positive gate multiplying an inequality is not a valid strength mechanism:

```math
w_rC_r\theta\ge0,\quad w_r>0
```

is equivalent to:

```math
C_r\theta\ge0.
```

Conforming implementations MUST use one of:

- hard activation;
- slack-penalized activation;
- augmented Lagrangian enforcement.

The preferred soft model is:

```math
C_r\theta+\xi_r\ge0,\qquad \xi_r\ge0,
```

with:

```math
\mathcal L_{slack}=\sum_r\mu_r(w_r)\xi_r^2.
```

## Tuning requirements

Thresholds, temperatures, penalties, and interaction counts MUST be learned, tuned, or explicitly justified.

Recommended selection rule:

```math
\psi^*=\arg\min_\psi ValLoss(\psi)
```

subject to lawful feasibility, support minimums, gate stability limits, and interaction count caps.

When multiple feasible candidates are statistically indistinguishable, select the simplest feasible model under the one-standard-error rule.

## Evidence requirements

Ledger records MUST use canonical serialization:

- fixed byte order;
- fixed dtype;
- fixed field order;
- fixed rounding policy;
- prior digest linkage.

Production records SHOULD be digitally signed.

Hash functions MUST be described as tamper-evident under collision-resistance assumptions. They MUST NOT be described as injective.

## Observer-stable evidence

Implementations SHOULD define observer maps from model states to evidence states and specify which transformations preserve evidence equivalence.

## Non-requirements

This standard does not require use of prime/even priors unless justified by validation. It does not require global hyperbolic geodesic convexity. It does not treat hash functions as injective. It does not permit illustrative numerical examples to be represented as executed empirical results.

## Depends on

- `SocioProphet/ProCybernetica#23`
