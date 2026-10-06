# 02. Product Requirements Document

| Field | Value |
|---|---|
| Product | ExperimentGuard |
| Version | Specification v1.0 |
| Owner | ZeeqRyz, solo project |
| Status | Fully implemented and verified (T01–T13 completed) |
| Updated | 6 October 2026 |

| Delivery | Local Python CLI, notebook, tables/figures, Markdown report |
| Estimate | 30-45 focused hours; assumed 10 hours/week |

## 1. Summary

ExperimentGuard accepts one two-variant retention experiment CSV. It validates data, checks allocation, estimates treatment effects and uncertainty, applies explicit decision rules, and produces an auditable manager report. A separate prospective planner calculates required sample sizes from assumed baseline rates and minimum detectable effects.

The Cookie Cats case demonstrates retrospective analysis. It does not run a real test or measure a telco campaign.

## 2. User workflow

1. Analyst records source provenance and experiment settings.
2. Analyst checks schema, user uniqueness, assignment counts, and evidence limitations.
3. Analyst freezes the protocol before local arm outcome comparisons.
4. Analyst runs primary inference and prospective planning.
5. Manager reads the effect, uncertainty, decision, and next action.
6. Analyst reproduces outputs through the notebook and CLI.

## 3. User stories

| ID | Story | Priority |
|---|---|---|
| US1 | Analyst detects broken data before trusting effects. | Must |
| US2 | Manager sees effect size and interval to judge practical benefit. | Must |
| US3 | Manager receives an explicit decision with reasons. | Must |
| US4 | Analyst plans the sample size for another test. | Must |
| US5 | Engineer reuses tested logic across notebook and CLI. | Must |
| US6 | Reviewer traces findings to source, protocol, and execution evidence. | Must |
| US7 | Analyst investigates secondary retention and unusual engagement. | Should |

## 4. Functional requirements

| ID | Requirement | Acceptance criteria | Priority |
|---|---|---|---|
| FR01 | Ingest and validate CSV | Five required columns checked; duplicate IDs, missing outcomes, invalid values, empty arms rejected with specific messages. | Must |
| FR02 | Track provenance | URL/version/date/hash/terms and assignment evidence recorded; unknown fields explicitly marked. | Must |
| FR03 | Check allocation | Exact two-sided binomial SRM against configured allocation; failure blocks decision; assumed allocation labelled. | Must |
| FR04 | Estimate primary effect | Day-7 counts/rates, B-minus-A pp effect, relative change, 95% Newcombe interval, two-sided p-value exported. | Must |
| FR05 | Apply decision rules | Deterministic supported/not-supported/inconclusive/blocked result with reasons and evidence qualifier. | Must |
| FR06 | Plan sample size | Baseline/MDE/alpha/power/allocation inputs yield rounded-up per-arm and total sample requirements. | Must |
| FR07 | Reproduce runs | CLI exports analytical JSON, tables, memo, metadata, data/protocol hashes, and versions. | Must |
| FR08 | Execute notebook | Fresh kernel imports shared package logic and matches CLI results. | Must |
| FR09 | Communicate decision | One-to-two-page memo gives question, quality, result, practical meaning, limits, next action. | Must |
| FR10 | Diagnose day-1 retention | Secondary effect and corrected p-value follow frozen exploratory family. | Should |
| FR11 | Diagnose engagement | Full-data summaries and planned outlier sensitivity preserve primary denominators. | Should |
| FR12 | Design future ChurnGuard experiment | Separate design states randomisation, required data, costs, and outcomes without campaign claims. | Should |

## 5. Scope

### Included

- One user-level independent experiment with two arms.
- Binary primary retention endpoint and prospective power planning.
- Fixed protocol, package, CLI, notebook, report, tests, and CI definition.
- Clearly labelled synthetic fixtures for software verification.

### Future work

- Live assignment/logging, real campaign delivery, scheduling, or customer messaging.
- Web dashboard, API, Docker, cloud deployment, and MLflow.
- Predictive models, uplift models, CUPED, Bayesian/sequential/multivariate tests.
- Revenue inference, causal subgroup analysis, and pooling experiments.

The workbook's generic engineer checklist does not require adding infrastructure to this notebook/report project.

## 6. Non-functional requirements

| ID | Requirement | Verification |
|---|---|---|
| NFR01 | Windows-friendly CPU-only execution | Clean local setup and documented PowerShell commands |
| NFR02 | Reproducible seeded sensitivity | Same analytical result excluding timestamps/run ID |
| NFR03 | Reliable numerical calculations | Hand arithmetic, independent library references, edge cases |
| NFR04 | Clear failure handling | Nonzero exit and specific diagnostics for invalid inputs |
| NFR05 | Maintainable shared logic | Typed package functions, lint, notebook imports |
| NFR06 | Portable outputs | UTF-8 JSON/CSV/Markdown and PNG figures |
| NFR07 | Reasonable CPU/memory use | Target <60 s and <1 GB for 100,000 rows, measured with actual hardware |
| NFR08 | Defensible claims | No invented metrics or real-business-impact claims |

NFR07 is an unmeasured target. Environment installation and notebook startup are excluded from that benchmark.

## 7. Acceptance examples

1. Duplicate user fails before inference.
2. Valid primary interval entirely above practical threshold and p<0.05 yields supported.
3. Interval crossing practical threshold remains inconclusive even with p<0.05.
4. Failed SRM yields blocked.
5. Zero control retention yields null relative effect with a reason, never infinity.
6. Identical source/configuration reproduces counts, estimates, intervals, decision.

## 8. Assumptions and limits

- Source file, licence, randomisation, allocation, and outcome definitions require verification.
- The public snapshot cannot establish original logging or complete follow-up.
- The 0.5 pp threshold is a portfolio assumption, not an original company requirement.
- Retrospective local protocol freezing is not prospective preregistration.
- Project 2's observational churn data are not a treatment/control experiment.

## 9. Definition of done

All Must requirements and required tasks pass [validation](07_VALIDATION_AND_RELEASE.md). Notebook/report regenerate from source and frozen settings. Progress log records actual checks. A negative, inconclusive, or blocked finding is reported honestly; positive uplift is not required.
