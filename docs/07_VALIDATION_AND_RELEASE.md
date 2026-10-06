# 07. Validation and Release

## 1. Principle

Verify calculations and decisions independently. Checking that files exist, comparing a function to itself, or reproducing a published Cookie Cats answer does not prove correctness.

## 2. Statistical verification matrix

| Check | Fixture / expected behaviour |
|---|---|
| Arithmetic | A=200/1000, B=250/1000: rates .20/.25; effect .05=5 pp; relative change 25% |
| Direction | Swapping arms negates effect and reverses interval bounds |
| Equal rates | Effect zero, non-significant comparison |
| Allocation | Compare counts against configured fraction, not necessarily 50:50 |
| SRM failure | Extreme imbalance blocks decision |
| Interval | Explicit Newcombe reference agrees; B-minus-A orientation correct |
| Small cells | Fisher fallback recorded and reference checked |
| Constant outcomes | Both all-zero/all-one: p=1, finite intervals, no false precision |
| Zero control | Relative effect null with reason; absolute effect valid |
| Supported | L>.005 and p<.05 yields supported |
| Practical uncertainty | Significant effect crossing .005 remains inconclusive |
| Boundaries | L/U=.005 inconclusive; p=.05 cannot support |
| Not supported | U<.005, with U<0 separately flagged as harm |
| Power | Smaller MDE needs larger sample; rounded counts meet target approximate power |
| Allocation-aware power | Per-arm ratio follows allocation within rounding |
| Bootstrap | Seed reproducible; sensitivity cannot alter primary decision |
| Secondary family | Holm correction remains fixed when one test unavailable |

Tolerances: exact counts/statuses; 1e-12 rate arithmetic; 1e-8 analytical reference values; 1e-6 power solutions. Monte Carlo interval comparisons require a declared tolerance, not exact analytical agreement.

## 3. Input and engineering checks

- Reject duplicates, cross-arm duplicates, missing fields/outcomes, empty arms, unknown variants, fractional counts, NaN/infinity, negative rounds.
- Accept zero rounds and day-1 false/day-7 true.
- Parse false string tokens correctly.
- Reject invalid baseline/MDE/alpha/power/allocation and evidence contradictions.
- Invalid input cannot leave a stale success report.
- CLI and notebook use shared functions and matching result fields.
- Identical source/configuration/version/seed reproduces analytical content excluding run ID/timestamps.
- Notebook executes from a fresh kernel and resolves paths correctly.

## 4. Report inspection

1. Independently aggregate counts and reconcile denominators/rates.
2. Check primary metric, B-minus-A sign, interval, p-value, threshold, decision.
3. 20% to 20.5% means 0.5 percentage points and 2.5% relative, not 0.5% relative.
4. Secondary metrics cannot replace the primary conclusion.
5. Inspect figures at normal zoom for labels, units, intervals, zero reference, practical threshold.
6. Place retrospective status, assumed thresholds, metadata gaps, and absent guardrails near the decision.
7. Measure runtime/memory with hardware recorded; do not claim the target as measured performance.

## 5. Release acceptance

- All Must requirements and required tasks have actual evidence.
- Source manifest/hash complete; unknown experiment metadata visibly labelled.
- Lint, tests, synthetic CLI, real CLI, and fresh notebook pass, or a genuine integrity-blocked result is explained honestly.
- Report and notebook regenerate without hand-edited result values.
- README describes measured results and limitations.
- Include source, tests, protocol, acquisition instructions, labelled fixtures, permitted aggregate results.
- Exclude environments, caches, credentials, and raw data with unverified redistribution rights.
- Publishing/pushing is a separate user-requested action; local delivery can be complete without it.

## 6. Defensible portfolio claim

Use after execution: "Analysed a public retention experiment using integrity checks, effect intervals, hypothesis tests, and sample-size planning."

Add numerical findings only after verification. Do not claim increased retention, saved RM, an AirAsia experiment, or a proven telco campaign from this educational snapshot.
