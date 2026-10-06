# 08. Decisions Log

## 1. Decisions on 6 October 2026

| ID | Decision | Reason / revisit condition |
|---|---|---|
| D001 | Prepare Project 6 now | Explicit request despite Project 3 being next numerically |
| D002 | Name ExperimentGuard; folder `06_ExperimentGuard_AB_Testing` | Clear purpose and portfolio convention |
| D003 | Projects 1/2 complete per user | Newer than workbook; no independent completion audit |
| D004 | Cookie Cats candidate dataset | Suitable two-arm retention case; revisit if inaccessible/unsuitable |
| D005 | Local package, CLI, notebook, report | Fits workbook scope and solo estimate |
| D006 | Primary day-7 retention, B-minus-A, two-sided .05 | One explicit decision endpoint |
| D007 | Explicit Newcombe difference interval | Avoid changing library defaults |
| D008 | Practical .5 pp; planning baseline 20% | Portfolio assumptions until business values supplied |
| D009 | SRM .001; allocation initially assumed 50:50 | Conservative diagnostic; verify source metadata |
| D010 | Retrospective local freeze | Not original prospective preregistration |
| D011 | No IBM churn-data A/B reinterpretation | No randomised offer assignment/outcomes |
| D012 | Workbook read-only | User requested inspection and new documents |
| D013 | Source/terms/file verification at T02 | Kaggle body unavailable to text browser |
| D014 | Later start request executes defaults | Continuity from Markdown, with material blockers surfaced |
| D015 | Freeze protocol v1.0 and config hash | Frozen at T03 prior to outcome comparison: SHA-256 `d9bc1e9b684eb7238015db2ba4ecb6d55cba9313f1cdbba05f1527101be4e512`; primary endpoint retention_7; alpha 0.05; d_min 0.005; srm_alpha 0.001 |

## 2. Checks and tasks completed (T01–T13)

- **Completed at T01–T03**:
  - Python 3.11.9 environment, locked dependencies (`requirements.lock.txt`).
  - Dataset acquired and verified (`data/raw/cookie_cats.csv`, SHA-256 `5ab54d761fbddcd50de7b88e4eaf7837cba4569474f50c043a4d17ee342c46bd`, 90,189 rows).
  - Protocol frozen in `configs/experiment.yaml` (SHA-256 `d9bc1e9b684eb7238015db2ba4ecb6d55cba9313f1cdbba05f1527101be4e512`).
  - Strict data validation and SRM diagnostic passing (`p=0.008692 >= 0.001`).
- **Completed at T04–T06**:
  - Binary effect estimation (Wilson CIs, Newcombe difference CI, z-test, Fisher exact fallback).
  - Pure deterministic 4-status decision rules with harm detection and provisional evidence qualification.
  - Primary vertical slice export and synthetic validation.
- **Completed at T07–T09**:
  - Prospective power planning across MDE scenarios (0.25, 0.50, 1.00 pp).
  - Secondary Day-1 retention, engagement analysis, Holm-Bonferroni correction, P99 winsorization, and 10k bootstrap sensitivity.
  - Decision memo and diagnostic figures generation.
- **Completed at T10–T13**:
  - CLI `validate`, `analyze`, and `plan` subcommands.
  - Executed reproducible notebook (`01_cookie_cats_analysis.ipynb`) on fresh kernel.
  - CI workflow (`.github/workflows/ci.yml`) and measured performance benchmark (7.70 s, 28 MB peak memory).
  - Documentation, checklist, and final evidence review.
- **Pending**: None. All tasks and Must/Should acceptance criteria verified.


## 3. New decision format

Record ID, date, triggering evidence, decision/rationale, affected documents/tasks, and verification impact. Method changes after outcome inspection must be logged as deviations without silently replacing the original analysis.


## 6 October 2026: remediation evidence decision

Preserve the original models and evaluation records. Repairs address packaging, evidence generation or display without retuning against viewed outcomes. Benchmark receipts now separate fresh-process CLI time, inner timing and sampled process-tree RSS. Public case: 2.5736s/193.555MiB. Constructed balanced synthetic 100k workload: 2.6014s/195.602MiB, exit 0. No experimental inference is drawn from synthetic capacity data. Original protocol/data/negative findings preserved.
