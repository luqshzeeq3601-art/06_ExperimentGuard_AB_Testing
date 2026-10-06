# Project 6: ExperimentGuard

**A/B Experiment Analysis and Power Planning Package**  
Status: **Fully Implemented and Verified**  
Verified on: 6 October 2026 (Asia/Kuala_Lumpur).

---

## 1. Executive Summary & Results at a Glance

ExperimentGuard is a reproducible experimentation engine that performs strict data validation, Sample Ratio Mismatch (SRM) diagnostics, binary effect estimation with Newcombe intervals, deterministic decision rules, secondary exploratory family adjustments (Holm-Bonferroni), sensitivity analyses, and prospective power planning.

### Case Question
**Does moving the Cookie Cats first progression gate from Level 30 to Level 40 increase 7-day player retention?**

### Key Results Summary Table

| Metric | Control (`gate_30`) | Treatment (`gate_40`) | Difference (B - A) | 95% Confidence Interval | p-value | Practical Threshold | Decision |
|---|---|---|---|---|---|---|---|
| **7-Day Retention (`retention_7`)** | 19.02% (N=44,700) | 18.20% (N=45,489) | **-0.82 pp** | [-1.33 pp, -0.31 pp] | `0.0016` | +0.50 pp | **`NOT_SUPPORTED`** |
| **1-Day Retention (`retention_1`)** | 44.82% (N=44,700) | 44.23% (N=45,489) | **-0.59 pp** | [-1.24 pp, +0.06 pp] | `0.0744` (Holm `0.1488`) | N/A | Exploratory |
| **Rounds Played (`sum_gamerounds`)** | 52.46 (std=256.7) | 51.30 (std=103.3) | **-1.16 rounds** | [-3.73, +1.41] (Welch calc) | `0.3759` (Holm `0.3759`) | N/A | Exploratory |

### Decision & Business Recommendation
- **Decision:** `NOT_SUPPORTED` (Evidence of Harm). The 95% CI upper bound is strictly below zero ($-0.31\text{ pp}$), confirming a statistically significant negative impact on player retention.
- **Recommendation:** Retain the first progression gate at **Level 30**. Do not deploy Gate 40.
- **Visual Artifacts:** Generated figures are stored in [`reports/cookie-cats-v1/figures/`](reports/cookie-cats-v1/figures/):
  - [Retention Rates by Arm (`retention_rates.png`)](reports/cookie-cats-v1/figures/retention_rates.png)
  - [Treatment Effect vs Threshold (`retention_effect.png`)](reports/cookie-cats-v1/figures/retention_effect.png)
  - [Prospective Power Curve (`power_sensitivity.png`)](reports/cookie-cats-v1/figures/power_sensitivity.png)
- **Executive Memo:** Read the full 2-page decision report at [`reports/cookie-cats-v1/decision_report.md`](reports/cookie-cats-v1/decision_report.md).
- **Reproducibility Run:** An independent benchmark run is archived at [`reports/benchmark_run/`](reports/benchmark_run/), confirming analytically identical results except run ID and timestamp.

---

## 2. Architecture & Modules

```
06_ExperimentGuard_AB_Testing/
  configs/experiment.yaml              # Frozen protocol settings (SHA-256: d9bc1e9b...)
  data/
    source_manifest.json               # Dataset provenance, terms, and metadata
    raw/cookie_cats.csv                # Immutable 90,189-row dataset (SHA-256: 5ab54d76...)
  src/experimentguard/
    config.py                          # Typed configuration schema and range validation
    data.py                            # Strict schema ingestion and validation (ITT retention)
    integrity.py                       # SRM exact binomial test and evidence grading
    effects.py                         # Binary proportions, Wilson CIs, Newcombe CIs, tests
    power.py                           # Prospective sample size solver (NormalIndPower)
    decision.py                        # Deterministic 4-status protocol decision rules
    report.py                          # Report bundle export, figure generation, Markdown memo
    cli.py                             # validate, analyze, and plan CLI entry points
  notebooks/
    01_cookie_cats_analysis.ipynb      # Executed end-to-end analytical notebook
  reports/cookie-cats-v1/              # Production analytical bundle
    quality.json                       # Validation and SRM report
    analysis.json                      # Full structured analytical results
    summary.csv                        # Formatted summary table
    power_plan.csv                     # Prospective MDE sample size table
    decision_report.md                 # 2-page executive decision memo
    run_metadata.json                  # Runtime, memory, hashes, and platform info
    figures/
      retention_rates.png              # Arm retention rates with Wilson CIs
      retention_effect.png             # Treatment effect vs practical threshold
      power_sensitivity.png            # Prospective power planning curve
  tests/                               # 42 unit and integration tests (100% passing)
  .github/workflows/ci.yml             # Automated CI pipeline definition
```

---

## 3. Setup and Execution

### 3.1 Environment Setup
```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.lock.txt
.\.venv\Scripts\python.exe -m pip install --no-deps -e .
```

### 3.2 CLI Commands
```powershell
# 1. Validate dataset schema and check Sample Ratio Mismatch (SRM)
.\.venv\Scripts\python.exe -m experimentguard validate --data data/raw/cookie_cats.csv --manifest data/source_manifest.json --config configs/experiment.yaml --out reports/quality-check

# 2. Run full A/B analysis, decision memo, and figure generation
.\.venv\Scripts\python.exe -m experimentguard analyze --data data/raw/cookie_cats.csv --manifest data/source_manifest.json --config configs/experiment.yaml --out reports/cookie-cats-v1

# 3. Calculate prospective power and sample size requirements
.\.venv\Scripts\python.exe -m experimentguard plan --config configs/experiment.yaml --out reports/power-v1
```

### 3.3 Test Suite & Quality Verification
```powershell
# Run full pytest suite (42 tests)
.\.venv\Scripts\python.exe -m pytest tests -q

# Run ruff lint and formatting verification
.\.venv\Scripts\python.exe -m ruff check src tests
.\.venv\Scripts\python.exe -m ruff format --check src tests

# Execute notebook from a fresh kernel
.\.venv\Scripts\python.exe -m nbconvert --to notebook --execute notebooks/01_cookie_cats_analysis.ipynb --ExecutePreprocessor.kernel_name=experimentguard --output executed_cookie_cats --output-dir reports/notebook
```

---

## 4. Verification Evidence & Benchmarks

| Requirement | Target | Verified Result | Evidence Path |
|---|---|---|---|
| **Data Validation & SRM** | Strict ITT, $\alpha_{\text{SRM}}=0.001$ | $N=90,189$, Zero-rounds=3,994 retained in the analysis (intention-to-treat), SRM $p=0.008692 \ge 0.001$ (`PASS`) | `reports/cookie-cats-v1/quality.json` |
| **Statistical Inference** | Wilson & Newcombe CIs, 2-prop z-test | Gate 30: 19.02%, Gate 40: 18.20%, Diff: -0.82 pp, 95% CI [-1.33, -0.31], $p=0.0016$ | `reports/cookie-cats-v1/analysis.json` |
| **Decision Rule** | $d_{\text{min}} = +0.50\text{ pp}$ | Status: `not_supported`, Harm: `True` | `reports/cookie-cats-v1/decision_report.md` |
| **Secondary & Exploratory** | Holm-Bonferroni correction | Day-1 effect: -0.59 pp (Holm $p=0.1488$), Engagement: 52.46 vs 51.30 rounds (Holm $p=0.3759$) | `reports/cookie-cats-v1/analysis.json` |
| **Sensitivity** | P99 Winsorization & 10k Bootstrap | P99 Capped diff: -0.28 rounds; Bootstrap CI: [-1.34 pp, -0.31 pp] | `reports/cookie-cats-v1/analysis.json` |
| **Prospective Power** | 80% Power at $\alpha=0.05$ | 0.25 pp $\rightarrow N=807,476$; 0.50 pp $\rightarrow N=202,800$; 1.00 pp $\rightarrow N=51,160$ | `reports/cookie-cats-v1/power_plan.csv` |
| **Performance Benchmark** | $<60\text{ s}$, $<1\text{ GB}$ on 100k rows | **7.70 seconds**, **28.08 MB peak memory** (AMD64, Python 3.11.9) | `reports/cookie-cats-v1/run_metadata.json` |
| **Test Coverage** | 100% test pass rate | 42 unit & integration tests passing | `tests/` |

---

## 5. Limitations & Disclosures

1. **Retrospective Snapshot:** Local analysis protocol was frozen prior to outcome evaluation, but this is retrospective analysis of a public dataset, not prospective preregistration of the original live experiment.
2. **Missing Timestamps:** Registration dates and cohort cutoffs are absent in the public dataset; full 7-day maturity for late-arriving cohorts is assumed.
3. **Missing Business Guardrails:** In-app revenue, player monetization, and server latency data are not present in this dataset. Production rollout decisions require full monetization guardrails.
4. **Illustrative Threshold:** The +0.50 pp minimum meaningful effect and 20% planning baseline are illustrative engineering assumptions.
