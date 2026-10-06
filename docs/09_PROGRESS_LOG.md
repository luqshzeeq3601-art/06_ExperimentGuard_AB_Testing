# 09. Progress Log

## 1. Planning session: 6 October 2026

### Completed

- Inspected all six workbook sheets using read-only XLSX XML extraction.
- Confirmed `Project Tracker!A9:F9`: Project 6 A/B analysis, hypothesis testing, intervals, power, notebook/report.
- Confirmed Project 3 is next numerically; prepared Project 6 as explicitly requested.
- Recorded user-reported completion of Projects 1/2 without re-auditing results.
- Reviewed Project 2's numbered planning structure for continuity.
- Checked official statistical APIs and Microsoft SRM guidance.
- Identified Kaggle candidate source and obsolete DataCamp redirect.
- Created PRD, protocol, data/technical specifications, execution plan, tasks, and logs.
- Verified 16 Markdown files, 59 local links, balanced code fences, T01-T13 order, per-task acceptance/verification fields, and at most five listed implementation files per task.
- Rechecked workbook SHA-256 against the inspection value; unchanged.
- Reconciled task effort with milestone totals: 24-37 h plus buffer, rounded to 30-45 h.

### Limits

- No dataset downloaded, dependencies installed, production code written, or experiment analysed.
- Kaggle file/terms/version and original metadata remain unverified.
- Workbook remains unchanged and still stores `Not started` statuses.
- Parent Ai-ML folder is not a Git repository; none initialised here.

### Next action

Planning complete. Handed off for full execution.

## 2. Execution session: 6 October 2026 (Completed T01 - T13)

### Completed Tasks & Verification Evidence

1. **T01 Bootstrap package & environment:**
   - Set up Python 3.11.9 virtual environment (`.venv`), installed dependencies, froze `requirements.lock.txt`.
   - Verified editable install of `experimentguard` package and import smoke tests for SciPy 1.17.1, statsmodels 0.15.0, pandas 3.0.6, numpy 2.4.6, matplotlib 3.11.2.

2. **T02 Acquire & record dataset:**
   - Acquired authentic 90,189-record `cookie_cats.csv` (`data/raw/cookie_cats.csv`).
   - Verified SHA-256: `5ab54d761fbddcd50de7b88e4eaf7837cba4569474f50c043a4d17ee342c46bd`.
   - Created `data/source_manifest.json` and updated `docs/10_SOURCES.md` with verified row count, arm counts (44,700 control vs 45,489 treatment), zero-rounds count (3,994), and limitations.

3. **T03 Validate & freeze protocol:**
   - Created `configs/experiment.yaml` (SHA-256: `d9bc1e9b684eb7238015db2ba4ecb6d55cba9313f1cdbba05f1527101be4e512`).
   - Implemented `src/experimentguard/config.py`, `src/experimentguard/data.py`, `src/experimentguard/integrity.py`.
   - Recorded protocol freeze in `docs/08_DECISIONS_LOG.md` (D015).
   - Verified via `tests/test_integrity.py` and real data check (`SRM p=0.008692 >= 0.001`, `PASS`).

4. **T04 Implement binary effects:**
   - Implemented `calculate_binary_effect` and `calculate_retention_effect` in `src/experimentguard/effects.py` with Wilson arm CIs, Newcombe difference CIs, two-sided pooled z-test, and Fisher exact small-cell fallback.
   - Verified via `tests/test_effects.py` against reference fixtures in `tests/fixtures/binary_counts.json`.

5. **T05 Implement decision rules:**
   - Implemented pure deterministic decision logic in `src/experimentguard/decision.py` with four-status hierarchy (`blocked`, `supported`, `not_supported`, `inconclusive`), boundary checks, harm detection, and evidence qualifications.
   - Verified via `tests/test_decision.py`.

6. **T06 Deliver primary vertical slice:**
   - Implemented pipeline execution and export in `src/experimentguard/report.py`.
   - Created synthetic fixtures `valid_experiment.csv` and `invalid_experiment.csv`.
   - Verified via `tests/test_primary_flow.py`.

7. **T07 Implement prospective power planning:**
   - Implemented `src/experimentguard/power.py` using `NormalIndPower` with Cohen's h, integer rounding, achieved power calculation, and multi-scenario tables.
   - Verified via `tests/test_power.py`.

8. **T08 Add secondary and sensitivity analysis:**
   - Added Day-1 retention analysis, engagement summaries (`sum_gamerounds`), Welch's t-test, Holm-Bonferroni exploratory family correction, P99 winsorization outlier sensitivity, and 10,000-replicate binomial bootstrap sensitivity to `src/experimentguard/effects.py`.
   - Verified via `tests/test_secondary.py`.

9. **T09 Render memo and figures:**
   - Implemented figure generation (`retention_rates.png`, `retention_effect.png`, `power_sensitivity.png`) and Markdown decision memo generation in `src/experimentguard/report.py`.
   - Verified via `tests/test_report.py`.

10. **T10 Expose CLI:**
    - Implemented `validate`, `analyze`, and `plan` subcommands in `src/experimentguard/cli.py` and entrypoint in `src/experimentguard/__main__.py`.
    - Verified via `tests/test_cli.py` and executed against real data producing `reports/cookie-cats-v1/` and `reports/power-v1/`.

11. **T11 Create executed notebook:**
    - Created `notebooks/01_cookie_cats_analysis.ipynb` importing package functions and executed it from a fresh `experimentguard` kernel via `nbconvert` to `reports/notebook/executed_cookie_cats.ipynb`.
    - Verified via `tests/test_notebook_contract.py`.

12. **T12 Prepare CI and benchmark:**
    - Created `.github/workflows/ci.yml` and `tests/test_smoke.py`.
    - Verified ruff linting (`ruff check`) and formatting (`ruff format --check`).
    - Measured benchmark on real 90,189 rows: **7.70 s runtime**, **28.08 MB peak memory**.

13. **T13 Final evidence review:**
    - Reconciled all findings, updated `README.md`, `docs/08_DECISIONS_LOG.md`, `docs/09_PROGRESS_LOG.md`, `docs/10_SOURCES.md`, and `tasks/todo.md`.

### Summary of Measured Analytical Results

- **Dataset SHA-256:** `5ab54d761fbddcd50de7b88e4eaf7837cba4569474f50c043a4d17ee342c46bd`
- **Config SHA-256:** `d9bc1e9b684eb7238015db2ba4ecb6d55cba9313f1cdbba05f1527101be4e512`
- **Control (`gate_30`):** N = 44,700, 7-Day Retention = 19.0201% (8,502 users), 95% Wilson CI [18.66%, 19.39%]
- **Treatment (`gate_40`):** N = 45,489, 7-Day Retention = 18.2000% (8,279 users), 95% Wilson CI [17.85%, 18.56%]
- **Treatment Effect (B - A):** -0.8201 percentage points (relative change: -4.31%)
- **95% Newcombe Confidence Interval:** [-1.3340 pp, -0.3063 pp]
- **Two-Sided Pooled z-test:** $z = -3.1644$, $p = 0.001554$
- **Decision Status:** `NOT_SUPPORTED` with evidence of harm (CI upper bound $< 0.0$).
- **Sample Ratio Mismatch:** Binomial test $p = 0.008692 \ge 0.001$ (`PASS`).
- **Quality Status:** `PROVISIONAL` (reported assignment, assumed allocation, unknown maturity).
- **Secondary Day-1 Effect:** -0.5898 pp, raw $p = 0.0744$, Holm-adjusted $p = 0.1488$.
- **Engagement Welch Test:** raw $p = 0.3759$, Holm-adjusted $p = 0.3759$.
- **Test Suite Status:** 42 passed, 0 failed.

## 3. Remediation & Polish session: 6 October 2026

### Completed Fixes & Verification

1. **Stale Documentation Status Rectification:**
   - Synchronized `docs/00_START_HERE.md`, `docs/02_PRD.md`, and `docs/08_DECISIONS_LOG.md` to reflect completed and verified T01–T13 status.
2. **Decision Memo Phrasing & Statistical Nuance:**
   - Calibrated wording in `src/experimentguard/report.py` to state evidence is "consistent with a 7-day retention decrease (provisional evidence grade)".
   - Added context on SRM $\alpha = 0.01$ borderline status ($p = 0.0087$) alongside the pre-specified $\alpha = 0.001$ threshold.
   - Added prospective power planning insight comparing required sample size ($101,400$ per arm for $0.5\text{ pp}$) with actual test sample size ($\approx 45,000$ per arm).
3. **Notebook & Codebase Lint Remediation:**
   - Removed unused imports in `notebooks/01_cookie_cats_analysis.ipynb`.
   - Executed full codebase formatting and linting: `ruff check .` (0 errors) and `ruff format --check .` (0 reformats needed across all 40 project files).
   - Re-executed notebook to `reports/notebook/executed_cookie_cats.ipynb`.
4. **README Enhancements:**
   - Added "Results at a Glance" summary table with clickable figure links and executive memo references.
   - Clarified the verification role of `reports/benchmark_run/` for independent reproducibility check.
5. **Final Test Suite & Cleanliness Run:**
   - `pytest tests -v` $\rightarrow$ 42 passed in 1.48s.
   - `ruff check .` $\rightarrow$ All checks passed.
   - `ruff format --check .` $\rightarrow$ 40 files already formatted.


