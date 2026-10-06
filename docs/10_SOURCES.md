# 10. Sources and Evidence

## 1. Workbook

[Classical_ML_Portfolio_Plan_Malaysia.xlsx](../../Classical_ML_Portfolio_Plan_Malaysia.xlsx), inspected read-only on 6 October 2026.

| Range | Evidence |
|---|---|
| `Project Tracker!A9:F9` | Priority 6, A/B analysis (add-on), AirAsia example, hypothesis tests/intervals/power, notebook/short report, public A/B dataset |
| `Project Tracker!A6:F6` | Priority 3, demand forecasting/inventory optimisation; next numeric project |
| `Project Tracker!A1` | Suggested order 2 > 1 > 3 > 4-6 |
| `Project Tracker!G4:G9` | All stored statuses `Not started`, stale relative to user's update |
| `Skills Demand!A12:C12` | A/B and hypothesis testing demand score 3 |
| `Engineer Checklist!A4:A11` | Generic checklist, tailored rather than forcing infrastructure |

Workbook SHA-256: `DEA7706770BFFAF9980015F15225121AF2AF18744871109EE0412D7B3B781900`.

User statement supplies Projects 1/2 completion state. Employer demand/vacancy availability was not independently refreshed.

## 2. Dataset references

| ID | Source | Verification |
|---|---|---|
| S01 | [Kaggle: Mobile Games A/B Testing](https://www.kaggle.com/datasets/yufengsui/mobile-games-ab-testing) | Candidate acquisition page; title resolved, body/terms/CSV/version/assignment not verified; T02 owns these checks |
| S02 | [DataCamp September 2024 update](https://support.datacamp.com/hc/en-us/articles/25695050326679-DataCamp-Content-Updates-September-2024) | Official search result lists legacy project 184 replacement by 1611; live redirect observed independently |
| S03 | [Legacy DataCamp project 184](https://www.datacamp.com/projects/184) | Redirected on 6 October 2026 to soccer project `/projects/1611`; not Cookie Cats download |

Five-column contract and gate-placement case are planned assumptions to confirm against acquired source. Do not adopt other portfolios' conclusions or exact row counts.

## 3. Primary statistical references

Checked on 6 October 2026; match to installed versions at T01. Stable URLs may evolve.

| ID | Reference | Use |
|---|---|---|
| S04 | [Microsoft Research SRM diagnosis](https://www.microsoft.com/en-us/research/articles/diagnosing-sample-ratio-mismatch-in-a-b-testing/) | Intended allocation checks before decision; investigate mismatch |
| S05 | [SciPy binomtest](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.binomtest.html) | Exact configured two-arm allocation diagnostic |
| S06 | [statsmodels proportions_ztest](https://www.statsmodels.org/stable/generated/statsmodels.stats.proportion.proportions_ztest.html) | Two-sided primary test and sign orientation |
| S07 | [statsmodels independent proportion intervals](https://www.statsmodels.org/stable/generated/statsmodels.stats.proportion.confint_proportions_2indep.html) | Explicit Newcombe method, B-minus-A |
| S08 | [statsmodels proportion_effectsize](https://www.statsmodels.org/stable/generated/statsmodels.stats.proportion.proportion_effectsize.html) | Cohen's h for proportion planning |
| S09 | [statsmodels power solver](https://www.statsmodels.org/stable/generated/statsmodels.stats.power.NormalIndPower.solve_power.html) | Sample size and allocation ratio |
| S10 | [SciPy Fisher exact](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.fisher_exact.html) | Small-cell fallback |
| S11 | [statsmodels multipletests](https://www.statsmodels.org/stable/generated/statsmodels.stats.multitest.multipletests.html) | Holm exploratory correction |

SRM .001, practical .5 pp, baseline 20%, and conservative support rule are project choices, not claims copied from sources.

## 4. Verified acquisition at T02

- **Acquired file**: `data/raw/cookie_cats.csv`
- **Source repository**: [ryanschaub/Mobile-Games-A-B-Testing-with-Cookie-Cats](https://github.com/ryanschaub/Mobile-Games-A-B-Testing-with-Cookie-Cats) (mirrored from DataCamp / Tactile Entertainment)
- **SHA-256**: `5ab54d761fbddcd50de7b88e4eaf7837cba4569474f50c043a4d17ee342c46bd`
- **Total rows**: 90,189 unique users (`userid` unique across entire dataset)
- **Arms count**: `gate_30` (control): 44,700 users (49.56%), `gate_40` (treatment): 45,489 users (50.44%)
- **Zero-round users**: 3,994 users (retained per ITT protocol)
- **Assignment evidence**: Reported (source indicates random assignment at installation)
- **Expected allocation**: Assumed 50:50 (qB = 0.50)
- **Maturity evidence**: Unknown (no timestamps in public snapshot)

