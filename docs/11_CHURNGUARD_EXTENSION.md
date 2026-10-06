# 11. Future ChurnGuard Experiment

## 1. Purpose and boundary

ChurnGuard predicts risk. Offer effectiveness requires a separate randomised experiment. Cookie Cats demonstrates the workflow and does not validate a telco campaign. This is future design work, not a dependency for v1 delivery.

## 2. Proposed question

Among customers eligible for a retention campaign, does a chosen offer improve retention over a fixed outcome window enough to cover incremental costs?

Stakeholder must define eligibility, retention window, baseline, meaningful uplift, offer cost, and guardrails before assignment. This document does not authorise real offers or customer messaging.

## 3. Design

1. Freeze model version and compute risk from pre-treatment data.
2. Fix eligibility before assignment; do not compare targeted high-risk customers to unrelated low-risk users.
3. Randomly assign eligible customers to usual service or offer; record assignment probability independently of redemption.
4. If stratifying on pre-treatment risk, prespecify strata and analysis.
5. Retain users in assigned arms regardless of offer response.
6. Observe all assigned users through the full window and measure costs/guardrails.
7. Predicted churn is neither assignment nor measured retention outcome.

## 4. Required additional data

| Field | Reason |
|---|---|
| Pseudonymous ID | Stable assignment/analysis unit |
| Eligibility/assignment timestamps | Pre-treatment cohort and maturity |
| Arm/allocation probability | Intended assignment diagnostic |
| Frozen model/risk | Reproduce targeting without leakage |
| Offer delivery/redemption | Diagnostics, not primary filtering |
| Outcome window/retention | Actual campaign effect |
| Costs and customer guardrails | Assess net benefit and harm |

## 5. Analysis and value

- Primary: assigned-customer retention difference, B-minus-A.
- Planning: actual baseline and stakeholder-defined MDE.
- Guardrail error control specified before outcomes.
- Scenario value: population * estimated effect * assumed retained-customer value minus incremental costs, with uncertainty and assumptions labelled.
- Realised impact requires genuine campaign measurements; public game data cannot supply it.

No live integration, campaign, uplift model, or real-customer operation belongs to ExperimentGuard v1.
