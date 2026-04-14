# Worked Example - Bounded Triparty Release

## Scenario

Three systems participate in a governed coordination cell:
- **A** = initiating payer or principal,
- **B** = service or execution provider,
- **C** = witness / solver / policy-bearing coordination surface.

Directed gross demands are:
- \(f_{AB}=100\)
- \(f_{BC}=70\)
- \(f_{CA}=60\)

Trusted executable capacities after observable, attested, and risk-adjusted checks are:
- \(\tilde c_{AB}=85.5\)
- \(\tilde c_{BC}=47.6\)
- \(\tilde c_{CA}=54\)

## Step 1 - Evidentially nettable cycle

The evidentially nettable cycle is:

\[
\lambda_{evid} = \min(100, 70, 60, 85.5, 47.6, 54) = 47.6
\]

This means 47.6 units can be justified by the currently trusted cycle.

## Step 2 - Policy admission

Suppose one leg crosses into a wider scope and requires additional witness or admissibility constraints.
Policy admits only half of the evidential cycle:

\[
\lambda_{admit} = 0.5 \cdot 47.6 = 23.8
\]

## Step 3 - Proof and release

If proof, freshness, replay, and contradiction checks pass, then:

\[
\lambda_{release} = 23.8
\]

Only this admitted-and-proven amount is released.
The remainder is not silently forced through. It becomes residual edge settlement, refund, review, or deferral.

## Why this matters

A flatter architecture would do one of two bad things:
- release all 47.6 as soon as it is evidentially available,
- or reject the whole cycle.

The governed fabric does neither.
It distinguishes:
- what can be evidenced,
- what may be admitted,
- what may be released,
- what may be exported.

That is the core practical value of the architecture.
