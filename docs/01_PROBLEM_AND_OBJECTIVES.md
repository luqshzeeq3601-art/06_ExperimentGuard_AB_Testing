# 01. Problem and Objectives

## 1. Problem

A team may ship a product change because retention looks higher or a p-value is below 0.05. That can be misleading when the effect is too small to matter, uncertainty is wide, experiment allocation is wrong, or users were filtered based on post-treatment behaviour.

The problem is deciding whether a change has enough trustworthy evidence to support rollout and explaining the decision clearly to a product manager.

## 2. Case question

**Does moving the Cookie Cats progression gate from level 30 to level 40 meaningfully increase seven-day retention?**

- Control A: `gate_30`; treatment B: `gate_40`.
- Analysis unit: one assigned user.
- Primary outcome: source-defined `retention_7`.
- Effect: treatment rate minus control rate.
- Dataset source and assignment details must be verified during execution. A public snapshot cannot independently prove original randomisation or complete follow-up.

## 3. Users

| User | Need | Output |
|---|---|---|
| Product manager | Judge practical benefit and uncertainty | Short decision memo |
| Analyst | Reproduce data checks and estimates | CLI, notebook, and tables |
| ML engineer | Evaluate an intervention after prediction | Tested reusable analysis package |
| Portfolio reviewer | Audit claims and methods | Protocol, sources, and verification evidence |

## 4. Objectives

| ID | Problem resolved | Objective | Completion evidence |
|---|---|---|---|
| O1 | Invalid data undermine conclusions | Validate rows and check assignment ratio | Quality report; critical failures block decision |
| O2 | Raw rates ignore uncertainty | Estimate day-7 difference, 95% interval, two-sided test | Tested estimates with counts and denominators |
| O3 | Significance is confused with value | Apply frozen practical threshold and decision rules | Supported/not-supported/inconclusive/blocked result |
| O4 | Under-sized tests waste effort | Plan future sample sizes for explicit MDEs | Per-arm requirements for 0.25/0.5/1.0 pp uplifts |
| O5 | Notebook logic drifts | Centralise logic and prove reproducibility | Fresh CLI and notebook produce matching results |
| O6 | Statistics fail to answer the business question | Produce concise recommendation and next action | One-to-two-page memo with limitations |

## 5. Success targets

1. Counts exactly reconcile; statistical values match independent reference calculations within declared tolerances.
2. Invalid inputs and SRM failure cannot produce a supported decision.
3. Same source hash, configuration hash, dependency versions, and seed reproduce analytical JSON excluding run ID/timestamps.
4. Package imports, lint, meaningful tests, CLI, and fresh-kernel notebook pass.
5. A reviewer can locate estimate, interval, practical threshold, decision, and limitations without reading code.

A positive or statistically significant treatment result is not a success target. Improved retention and realised revenue are not claimed because this project does not operate a live experiment.

## 6. Portfolio purpose

- Adds experimentation, causal reasoning, and uncertainty to Projects 1 and 2's prediction skills.
- The workbook associates A/B analysis with AirAsia; this is historical workbook context, not current vacancy verification.
- A future randomised ChurnGuard campaign could use this pattern. The existing churn dataset cannot establish offer effectiveness.
