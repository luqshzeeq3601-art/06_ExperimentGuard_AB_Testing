# 03. Experiment Protocol

## 1. Status and freeze

This is a retrospective protocol for a publicly known educational case. It defines methods before local outcome analysis and is not prospective preregistration of the original experiment. Freeze configuration, SHA-256, and protocol version at T03. Log any subsequent deviations and their effect on interpretation.

## 2. Population and estimand

- Unit: one assigned user, once in the source CSV.
- A/control: `gate_30`; B/treatment: `gate_40`.
- Primary estimand: seven-day retention probability difference, B minus A.
- Retain all supplied assigned users after required schema validation, including zero-round users.
- Do not require reaching a gate or returning on day 1. These are post-assignment behaviours.
- This is intention-to-treat-style analysis of the snapshot. Do not claim complete original assignment coverage without evidence.
- No train/validation/test split is needed for experimental inference.

## 3. Metric hierarchy

| Role | Metric | Meaning |
|---|---|---|
| Primary | `retention_7` | Source-defined day-7 return; verify exact definition at acquisition |
| Secondary | `retention_1` | Early retention diagnostic; cannot overturn primary decision |
| Exploratory | `sum_gamerounds` | Engagement in source-defined window |
| Unavailable | Revenue, complaints, latency | No production-wide rollout decision without these guardrails |

Retention indicators are not cumulative survival. Day-1 false and day-7 true can be valid.

## 4. Frozen defaults

| Setting | Value | Basis |
|---|---|---|
| H0 | pB-pA=0 | One primary comparison |
| H1 | pB-pA != 0 | Two-sided improvement/harm detection |
| Alpha / interval | 0.05 / 95% | Analysis convention |
| Minimum meaningful effect | 0.005 | Assumed 0.5 percentage points |
| Planning baseline | 0.20 | Assumed 20%, not measured control rate |
| Planning treatment | 0.205 | Baseline plus default MDE |
| Target power | 0.80 | Prospective planning convention |
| Expected treatment fraction | 0.50 | Assumed until original metadata verifies it |
| SRM alpha | 0.001 | Conservative project choice |
| Seed / bootstrap replicates | 42 / 10,000 | Reproducible sensitivity |

Planning MDEs: 0.0025, 0.005, 0.01 = 0.25, 0.5, 1.0 percentage points. Defaults must be labelled assumptions in the report.

## 5. Integrity and SRM

1. Validate required schema, unique IDs, outcomes, legal values, nonempty arms.
2. Run `binomtest(nB, nA+nB, p=qB, alternative='two-sided')` against intended treatment fraction qB.
3. SRM p<0.001 blocks the decision. Investigate; never downsample or redefine expected allocation to match observed counts.
4. Unknown intended fraction means **SRM under assumed allocation**. Passing it does not prove randomisation.
5. Manifest assignment evidence is `verified`, `reported`, or `unverified`. The case requires at least source-reported random assignment. Unverified assignment blocks causal interpretation and decision.
6. Missing timing or follow-up evidence is a named limitation, not a reason to delete non-returning users.

SRM tests intended allocation, not exact equality of group sizes. See [Microsoft Research](https://www.microsoft.com/en-us/research/articles/diagnosing-sample-ratio-mismatch-in-a-b-testing/). The 0.001 threshold is our choice, not Microsoft's exact documented threshold.

## 6. Primary calculation

For assigned n and retained x:

```text
pA = xA / nA
pB = xB / nB
delta = pB - pA
delta_pp = 100 * delta
relative_change_percent = 100 * delta / pA  (if pA > 0)
```

- Arm intervals: Wilson, `proportion_confint(..., method='wilson', alpha=0.05)`.
- Difference interval: `confint_proportions_2indep(xB,nB,xA,nA,method='newcomb',compare='diff',alpha=0.05)`; select method explicitly.
- Primary p-value: pooled two-proportion z-test, counts/denominators B then A, two-sided.
- If any observed success/failure cell is <5, use two-sided Fisher exact on `[[xB,nB-xB],[xA,nA-xA]]`; record fallback.
- Constant outcomes across both arms: p=1, delta=0, finite Wilson/Newcombe intervals. Do not infer a precise zero from no variation.
- pA=0: relative change null with reason; absolute effect remains available.
- Z-test and Newcombe interval can differ near alpha because they use different approximations. Report both; apply the decision rules below.

References: [z-test](https://www.statsmodels.org/stable/generated/statsmodels.stats.proportion.proportions_ztest.html), [difference interval](https://www.statsmodels.org/stable/generated/statsmodels.stats.proportion.confint_proportions_2indep.html), [Fisher exact](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.fisher_exact.html).

## 7. Decision rules

Let L/U be primary interval bounds and d_min=0.005. Use unrounded values and apply in order:

| Order | Condition | Status | Meaning |
|---|---|---|---|
| 1 | Required quality fails, SRM fails, assignment unverified, or primary unavailable | `blocked` | Resolve integrity/evidence issue first |
| 2 | L>d_min and primary p<0.05 | `supported` | Evidence supports improvement exceeding assumed practical threshold |
| 3 | U<d_min | `not_supported` | Evidence does not support a sufficiently large improvement |
| 4 | Other valid cases | `inconclusive` | Uncertainty includes threshold or methods disagree |

- Within not-supported, U<0 flags evidence of harm; otherwise explain small effect or uncertain sign.
- L=d_min or U=d_min is inconclusive. p=0.05 fails the supported criterion.
- Not-supported is not proof of equivalence or exactly no effect.
- Source-reported assignment, assumed allocation, or unknown maturity requires a provisional evidence qualifier. Quality is `pass` only when assignment, allocation, and maturity evidence are verified; otherwise a valid source-reported case is `provisional`. Required failures remain `fail`.
- Supported means support within this case and assumptions. Real rollout still requires absent guardrails and experiment metadata checks.

## 8. Secondary and sensitivity work

1. Day-1 retention: rates, effect, interval, two-sided p-value, clearly secondary.
2. Engagement: full-data count, mean, median, zero fraction, p95, p99, maximum by arm.
3. Full-data Welch mean-rounds test is exploratory. Constant identical outcomes get p=1; non-estimable cases remain unavailable with reason.
4. Holm-correct day-1 and full-data engagement p-values as a fixed two-test exploratory family. An unavailable test contributes p=1 to correction but remains displayed as unavailable. Primary test is a separately designated single endpoint.
5. Outlier sensitivity: winsorise at pooled p99, describe cap, affected counts, and changed mean difference. It is descriptive and never changes primary denominators.
6. Primary bootstrap sensitivity: 10,000 independent within-arm user resamples, seeded percentile interval. Equivalent binomial success-count draws for binary outcomes avoid huge arrays. This is uncertainty estimation, not a posterior probability of improvement.
7. Do not identify causal segments using post-treatment rounds or hunt for unplanned subgroup winners.

These are Should requirements; disclose any omitted analysis. They cannot replace the primary endpoint.

## 9. Prospective power planning

1. Require 0<p0<1, absolute MDE d>0, p0+d<1, valid alpha/power/allocation.
2. Cohen's h: `abs(proportion_effectsize(p0+d,p0))`.
3. Solve with `NormalIndPower.solve_power(effect_size=h,nobs1=None,alpha=0.05,power=0.80,ratio=nB/nA,alternative='two-sided')`.
4. For qB, ratio=qB/(1-qB). Round nA up, then ratio*nA up for nB; check achieved approximate power after rounding.
5. Export all assumed-MDE scenarios with per-arm and total counts. No computed sample-size result is claimed yet.
6. This plans detection against zero. It does not promise 80% probability that the lower interval exceeds the rollout threshold; that assurance calculation is future work.
7. Do not report observed post-hoc power from measured effects. For available sample size, assess detectable effects under stated baseline assumptions.
8. Duration, if eligible new users/day is supplied: ceiling(total sample/traffic) recruitment days plus full seven-day follow-up for the final cohort. Otherwise duration is unavailable.

Reference: [statsmodels power solver](https://www.statsmodels.org/stable/generated/statsmodels.stats.power.NormalIndPower.solve_power.html).

## 10. Interpretation limits

- p-value is not the probability the null is true.
- A frequentist 95% interval is not a 95% probability about a fixed parameter.
- Snapshot cannot prove original logging, seasonal coverage, or complete follow-up.
- Non-significance does not prove equivalence.
- No Malaysian retention, revenue uplift, ChurnGuard campaign impact, daily-peeking, or sequential-testing claim is supported.
