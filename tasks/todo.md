# ExperimentGuard Execution Checklist

All implementation tasks T01 through T13 are completed and verified.

## 1. Trusted input

- [x] **T01 Bootstrap package/environment** (Completed 6 Oct 2026)
  - Read: [technical design](../docs/05_TECHNICAL_DESIGN.md), [stack](../docs/06_TECH_STACK_AND_COMMANDS.md).
  - Files: `pyproject.toml`, `requirements.in`, `requirements.lock.txt`, `src/experimentguard/__init__.py`, `.gitignore`.
  - Acceptance: compatible venv/lock; editable src package imports; cache/raw-data exclusions recorded.
  - Verify: Fresh lock install; package/SciPy 1.17.1/statsmodels 0.15.0 import smoke test passed.

- [x] **T02 Acquire and record dataset** (Completed 6 Oct 2026)
  - Read: [data](../docs/04_DATA_SPEC.md), [sources](../docs/10_SOURCES.md).
  - Files: `data/raw/cookie_cats.csv`, `data/source_manifest.json`, `docs/10_SOURCES.md`.
  - Acceptance: 90,189 unique users; SHA-256 `5ab54d761fbddcd50de7b88e4eaf7837cba4569474f50c043a4d17ee342c46bd`; reported assignment and assumed allocation recorded.
  - Verify: Get-FileHash agrees with manifest; independent CSV header/row/arm inspection passed.

- [x] **T03 Validate and freeze protocol** (Completed 6 Oct 2026)
  - Read: [protocol](../docs/03_EXPERIMENT_PROTOCOL.md), [data](../docs/04_DATA_SPEC.md).
  - Files: `configs/experiment.yaml`, `src/experimentguard/config.py`, `src/experimentguard/data.py`, `src/experimentguard/integrity.py`, `tests/test_integrity.py`.
  - Acceptance: Strict schema, failure cases, exact allocation diagnostic, config/manifest agreement.
  - Verify: `pytest tests/test_integrity.py -q` passed; real-data SRM binomial test $p=0.008692 \ge 0.001$ (`PASS`). Protocol frozen at SHA-256 `d9bc1e9b...` (D015).

**M1 checkpoint:** Verified and passed.

## 2. Primary decision

- [x] **T04 Implement binary effects** (Completed 6 Oct 2026)
  - Read: [protocol](../docs/03_EXPERIMENT_PROTOCOL.md), [verification matrix](../docs/07_VALIDATION_AND_RELEASE.md).
  - Files: `src/experimentguard/effects.py`, `tests/test_effects.py`, `tests/fixtures/binary_counts.json`.
  - Acceptance: Counts/rates, Wilson/Newcombe intervals, two-sided test, small/constant-count handling.
  - Verify: `pytest tests/test_effects.py -q` passed; reference fixtures in `binary_counts.json` reconciled.

- [x] **T05 Implement decision rules** (Completed 6 Oct 2026)
  - Read: [protocol](../docs/03_EXPERIMENT_PROTOCOL.md), [PRD](../docs/02_PRD.md).
  - Files: `src/experimentguard/decision.py`, `tests/test_decision.py`.
  - Acceptance: Ordered four-status rules (`blocked`, `supported`, `not_supported`, `inconclusive`), reasons, harm detection, provisional qualifier.
  - Verify: `pytest tests/test_decision.py -q` passed across all boundary conditions.

- [x] **T06 Deliver primary vertical slice** (Completed 6 Oct 2026)
  - Read: [output contract](../docs/05_TECHNICAL_DESIGN.md), [validation](../docs/07_VALIDATION_AND_RELEASE.md).
  - Files: `src/experimentguard/report.py`, `tests/test_primary_flow.py`, `tests/fixtures/valid_experiment.csv`, `tests/fixtures/invalid_experiment.csv`.
  - Acceptance: read -> validate -> integrity -> effect -> decision -> JSON export; invalid input exports diagnostics without actionable result.
  - Verify: `pytest tests/test_primary_flow.py -q` passed.

**M2 checkpoint:** Verified and passed.

## 3. Planning and report

- [x] **T07 Implement power planning** (Completed 6 Oct 2026)
  - Read: [protocol](../docs/03_EXPERIMENT_PROTOCOL.md), [output contract](../docs/05_TECHNICAL_DESIGN.md).
  - Files: `src/experimentguard/power.py`, `tests/test_power.py`, `src/experimentguard/report.py`.
  - Acceptance: MDE scenarios (0.25, 0.50, 1.00 pp), rounded arm/total sizes, allocation-aware solver, achieved power validation.
  - Verify: `pytest tests/test_power.py -q` passed.

- [x] **T08 Add secondary/sensitivity analysis** (Completed 6 Oct 2026)
  - Read: [protocol](../docs/03_EXPERIMENT_PROTOCOL.md).
  - Files: `src/experimentguard/effects.py`, `tests/test_secondary.py`, `src/experimentguard/report.py`.
  - Acceptance: Day-1 retention, engagement summary/Welch t-test, fixed Holm family correction, pooled-P99 outlier sensitivity, 10k-replicate seeded binary bootstrap.
  - Verify: `pytest tests/test_secondary.py -q` passed; primary decision unchanged.

- [x] **T09 Render memo and figures** (Completed 6 Oct 2026)
  - Read: [PRD](../docs/02_PRD.md), [report review](../docs/07_VALIDATION_AND_RELEASE.md).
  - Files: `src/experimentguard/report.py`, `tests/test_report.py`.
  - Acceptance: JSON/CSV exports, three readable figures (`retention_rates.png`, `retention_effect.png`, `power_sensitivity.png`), Markdown memo (`decision_report.md`).
  - Verify: `pytest tests/test_report.py -q` passed; visual inspection of memo and figures confirmed.

**M3 checkpoint:** Verified and passed.

## 4. Reproducibility and evidence

- [x] **T10 Expose CLI** (Completed 6 Oct 2026)
  - Read: [commands](../docs/06_TECH_STACK_AND_COMMANDS.md), [exit/output rules](../docs/05_TECHNICAL_DESIGN.md).
  - Files: `src/experimentguard/cli.py`, `src/experimentguard/__main__.py`, `tests/test_cli.py`.
  - Acceptance: `validate`, `analyze`, `plan` subcommands; documented exits (0 for valid completion, 2 for blocked/invalid, 1 for error); export bundles.
  - Verify: `pytest tests/test_cli.py -q` passed; verified on real data generating `reports/cookie-cats-v1/` and `reports/power-v1/`.

- [x] **T11 Create executed notebook** (Completed 6 Oct 2026)
  - Read: [commands](../docs/06_TECH_STACK_AND_COMMANDS.md), [validation](../docs/07_VALIDATION_AND_RELEASE.md).
  - Files: `notebooks/01_cookie_cats_analysis.ipynb`, `tests/test_notebook_contract.py`.
  - Acceptance: Complete narrative importing package-owned logic; fresh kernel execution.
  - Verify: `nbconvert` executed to `reports/notebook/executed_cookie_cats.ipynb`; `pytest tests/test_notebook_contract.py -q` passed.

- [x] **T12 Prepare CI and benchmark** (Completed 6 Oct 2026)
  - Read: [CI scope](../docs/06_TECH_STACK_AND_COMMANDS.md), [release](../docs/07_VALIDATION_AND_RELEASE.md).
  - Files: `.github/workflows/ci.yml`, `tests/test_smoke.py`, `README.md`.
  - Acceptance: Credential-free synthetic CI definition; ruff clean; measured benchmark recorded.
  - Verify: `ruff check` and `ruff format --check` passed; benchmark measured **7.70 s runtime**, **28.08 MB peak memory**.

- [x] **T13 Final evidence review** (Completed 6 Oct 2026)
  - Read: [release](../docs/07_VALIDATION_AND_RELEASE.md), [extension](../docs/11_CHURNGUARD_EXTENSION.md).
  - Files: `README.md`, `docs/10_SOURCES.md`, `docs/09_PROGRESS_LOG.md`, `docs/08_DECISIONS_LOG.md`.
  - Acceptance: Measured results replace plans; Must requirements trace to evidence; limitations disclosed.
  - Verify: Full pytest suite (42 tests) passed, CLI and notebook reproduce matching figures and tables.

**M4 checkpoint:** Verified and passed.

## 5. Portfolio polish & live demonstration

- [x] **Post-M4 Portfolio Polish & Streamlit Dashboard** (Completed 6 Oct 2026)
  - Files: `LICENSE`, `app.py`, `app/streamlit_app.py`, `.streamlit/config.toml`, `requirements-app.txt`, `README.md`.
  - Acceptance: MIT license, GitHub repo description/topics configured, multi-tab interactive Streamlit dashboard (Case Study, Power Simulator, Live CSV Evaluator), `test_validate_dataframe` verified (43/43 tests passing).

