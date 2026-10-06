# 04. Data Specification

## 1. Candidate source

- [Kaggle: Mobile Games A/B Testing](https://www.kaggle.com/datasets/yufengsui/mobile-games-ab-testing).
- Intended file: `data/raw/cookie_cats.csv`.
- Status: page identified; CSV not downloaded; schema/terms/version/hash not verified.
- Text browser resolved the page title but not its body. Do not infer current licence or exact row count.
- Legacy DataCamp project 184 redirects to soccer project 1611. It is not the current Cookie Cats acquisition path.

## 2. Acquisition at T02

1. Check source description, publisher, files, version, and terms.
2. Download through the source website or an already configured official Kaggle tool. Keep credentials outside the project.
3. Preserve original bytes; extract the selected CSV to the intended path.
4. Record manifest, SHA-256, header/types, row/arm counts.
5. Seek source evidence of random assignment, intended fraction, outcome definitions, and completeness.
6. Freeze protocol at T03 before comparing arm outcomes.

If unavailable, record failure and proposed replacement source. Synthetic fixtures can test software but cannot substitute for real case-study evidence or satisfy real-analysis completion.

## 3. Planned schema to confirm

| Column | Representation | Validation | Use |
|---|---|---|---|
| `userid` | Integer-like ID | Positive exact integer, non-null, globally unique | User unit |
| `version` | String | Exactly `gate_30`/`gate_40`; both arms present | Assignment |
| `sum_gamerounds` | Integer | Finite integer >=0; no arbitrary upper exclusion | Engagement |
| `retention_1` | Boolean/token | Strict True/False or 1/0, no missing | Secondary |
| `retention_7` | Boolean/token | Strict True/False or 1/0, no missing | Primary |

Allow outer whitespace and case-insensitive true/false tokens. Reject ambiguous yes/unknown/blank/2, fractional values, and float-like IDs. Never parse `bool('False')`. Record extra columns without using them in inference; missing required columns fail. Actual row count is recorded after acquisition, not copied from another project.

## 4. Quality rules

- Duplicate ID within/across arms fails; never keep an arbitrary first row.
- Missing or invalid required outcomes fail; never impute false.
- Empty dataset/arm, unknown arm, fractional/negative/non-finite rounds fail.
- Zero rounds and day-1 false/day-7 true are valid.
- Extreme engagement is retained in raw data and primary denominators; investigate with prescribed sensitivity.
- Passed validation/SRM does not prove original randomisation or follow-up.

Quality output states input/retained rows, issues, missingness, duplicates, arm counts, SRM method/value/status, blockers, and limitations. Required-field failure gives nonzero exit and no actionable decision.

## 5. Manifest contract

Create `data/source_manifest.json` during acquisition with:

- Dataset ID, source URL, publisher, dataset version.
- Download timestamp, relative raw path, SHA-256, row count, columns.
- Licence/terms evidence and redistribution status.
- Assignment evidence: verified/reported/unverified with source explanation.
- Expected allocation evidence: verified fraction or assumed fraction with reason.
- Retention definition, rounds observation window, maturity evidence.
- Named unresolved limitations.

Unknown fields remain null/unknown with explanatory reasons. Do not populate fake metadata to make a manifest look complete.

## 6. Data organisation and release

- `data/raw/`: immutable source; default excluded from public Git until rights verified.
- `data/processed/`: deterministic typed normalisation; no eligible user removed.
- `tests/fixtures/`: small hand-designed synthetic data, labelled synthetic.
- `reports/`: aggregate evidence, hashes, run metadata; no user identifiers in manager memo.
- Release acquisition instructions and synthetic fixtures by default. Review any raw redistribution using actual source terms.

## 7. Unsupported fields

Reliable timestamps, geography, revenue, costs, pre-treatment covariates, and assignment logs have not been established. V1 cannot verify temporal balance, Malaysian applicability, revenue uplift, CUPED, or real ChurnGuard campaign effectiveness.
