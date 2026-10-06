# ExperimentGuard: A/B Experiment Decision Memo

**Experiment ID:** `cookie_cats_gate_placement`  
**Run ID:** `benchmark_run`  
**Date (UTC):** `2026-10-06T02:29:14.234905+00:00`  
**Evidence Qualification:** `PROVISIONAL`  

---

## 1. Executive Summary & Decision

### Decision Status: **[NOT SUPPORTED - ROLLOUT NOT RECOMMENDED]**

> Evidence does not support rollout: 95% CI upper bound (-0.0031) is strictly below 0.0, indicating evidence consistent with a negative impact / retention decrease (harm).

| Metric | Control (`gate_30`) | Treatment (`gate_40`) | Difference (B - A) | 95% Confidence Interval | p-value | Practical Threshold | Decision |
|---|---|---|---|---|---|---|---|
| **7-Day Retention (`retention_7`)** | 19.02% (N=44,700) | 18.20% (N=45,489) | **-0.82 pp** | [-1.33 pp, -0.31 pp] | `0.0016` | +0.50 pp | `not_supported` |

### Key Business Implications:
- Moving the first progression gate from level 30 to level 40 **reduced 7-day retention** by approximately 0.82 percentage points (from 19.02% down to 18.20%).
- The 95% confidence interval is strictly below zero, providing evidence consistent with a 7-day retention decrease (provisional evidence grade based on retrospective snapshot).
- **Recommendation:** Keep the initial progression gate at **Level 30**. Do not deploy gate 40.

---

## 2. Data Integrity & Sample Ratio Mismatch (SRM)

- **Data Integrity Status:** `PROVISIONAL`
- **Observed Allocation:** Control=44,700 (49.56%), Treatment=45,489 (50.44%)
- **SRM Diagnostic (Two-Sided Binomial vs Expected 0.50):** p-value = `0.008692` (Threshold α = `0.001`)
- **SRM Conclusion:** `PASS` (p = 0.008692 passes the pre-specified α_SRM = 0.001 threshold under assumed 50:50 allocation; note that at a standard α = 0.01 threshold, p = 0.0087 would be borderline).

---

## 3. Secondary & Exploratory Metrics

### 3.1 Early Retention (`retention_1`)
- **Control Rate:** 44.82% | **Treatment Rate:** 44.23%
- **Effect (B - A):** -0.59 pp (95% CI: [-1.24 pp, +0.06 pp])
- **Raw p-value:** `0.0744` | **Holm-Adjusted p-value:** `0.1488`

### 3.2 Game Engagement (`sum_gamerounds`)
- **Control (`gate_30`):** Mean = 52.46 rounds (Median = 17, P99 = 493, Max = 49854)
- **Treatment (`gate_40`):** Mean = 51.30 rounds (Median = 16, P99 = 492, Max = 2640)
- **Welch's t-test p-value:** `0.3759` | **Holm-Adjusted:** `0.3759`

### 3.3 Outlier & Bootstrap Sensitivity
- **Engagement Outlier Sensitivity (Winsorized at pooled P99 = 493 rounds):**
  - Capped Control Mean: 49.14 rounds | Capped Treatment Mean: 48.85 rounds
  - Capped Mean Difference: -0.28 rounds
- **Bootstrap Percentile CI (10,000 resamples, seed=42):** [-1.34 pp, -0.31 pp] (Agrees with Newcombe analytical CI)

---

## 4. Prospective Sample Size Planning

Required sample sizes for future two-variant retention experiments (assumed baseline rate = 20%, target power = 80%, α = 0.05):

| Scenario | Target MDE (pp) | Required per Arm (n) | Total Sample (N) | Achieved Power |
|---|---|---|---|---|
| `mde_0.25pp` | 0.25 pp | 403,738 | 807,476 | 80.00% |
| `mde_0.50pp` | 0.50 pp | 101,400 | 202,800 | 80.00% |
| `mde_1.00pp` | 1.00 pp | 25,580 | 51,160 | 80.00% |

> **Power Planning Insight:** Detecting a 0.50 pp MDE with 80% power requires ~101,400 users per arm (N = 202,800 total). The actual Cookie Cats test observed ~45,000 users per arm, indicating the original test was underpowered to detect a small 0.50 pp effect against zero; however, the observed larger effect (-0.82 pp) was sufficiently large to achieve statistical significance in the available sample.

---

## 5. Unresolved Limitations & Risk Disclosures

1. **Retrospective Snapshot:** Local analysis protocol was frozen prior to outcome evaluation, but this is retrospective analysis of a public dataset, not prospective preregistration of the original live test.
2. **Missing Timestamps:** Registration dates and cohort cutoffs are absent in the public dataset; full 7-day maturity for late-arriving cohorts is assumed.
3. **Missing Business Guardrails:** In-app revenue, player monetization, and server latency data are not present in this dataset. Production rollout decisions require full monetization guardrails.
4. **Illustrative Threshold:** The +0.50 pp minimum meaningful effect and 20% planning baseline are illustrative engineering assumptions, not executive-confirmed business constants.