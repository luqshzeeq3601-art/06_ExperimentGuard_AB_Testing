# ExperimentGuard Agent Instructions

## 1. Communication

- Explain directly and briefly, using numbered sections and bullet points.
- Distinguish plans, verified results, assumptions, and unresolved issues.

## 2. Mandatory starting context

1. Read `docs/00_START_HERE.md`.
2. Read `docs/09_PROGRESS_LOG.md` and `docs/08_DECISIONS_LOG.md`.
3. Select the first unfinished task in `tasks/todo.md`.
4. Read the specifications linked by that task before editing code.

Current human instructions take priority. The PRD owns scope, the protocol owns statistical rules, and the data/technical specifications own implementation contracts. Resolve contradictions in those files before dependent implementation.

## 3. Engineering rules

- Work within this project folder unless the user requests otherwise.
- Reusable logic belongs in `src/experimentguard/`; the notebook imports it.
- Verify calculations and decision rules with independent synthetic fixtures.
- Preserve raw data and reject invalid required fields. Do not silently filter users.
- Retain all supplied assigned users, including zero-round users.
- Do not change metrics, exclusions, test direction, or thresholds to obtain preferred findings.
- Use treatment minus control; distinguish percentage points from relative percent.
- V1 is a local analysis package, CLI, notebook, and report. Do not add a predictive model or serving platform.
- Do not claim real campaign impact, Malaysian data, or saved revenue from this case.
- Local dependency setup, analysis, tests, and CI preparation are within the execution plan. Record compatible pinned versions at setup.

## 4. Session completion

- Verify the task before checking it off.
- Record commands, outcomes, limitations, and next task in `docs/09_PROGRESS_LOG.md`.
- Record material scope/method changes in `docs/08_DECISIONS_LOG.md` before implementing them.
- A later instruction to start this project authorises execution of the documented plan. Raise only material unresolved choices that the defaults cannot resolve.
