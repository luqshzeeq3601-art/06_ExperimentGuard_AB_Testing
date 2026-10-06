# 00. Start Here

## 1. Identity and state

- Product: ExperimentGuard, Project 6.
- Purpose: trustworthy two-variant retention analysis and future sample-size planning.
- State: implementation, local execution, and verification complete (T01–T13).
- First implementation task: T01 in [todo.md](../tasks/todo.md) (completed).


## 2. Reading order

1. [Problem and objectives](01_PROBLEM_AND_OBJECTIVES.md).
2. [PRD](02_PRD.md).
3. [Experiment protocol](03_EXPERIMENT_PROTOCOL.md).
4. [Data specification](04_DATA_SPEC.md).
5. [Technical design](05_TECHNICAL_DESIGN.md).
6. [Stack and commands](06_TECH_STACK_AND_COMMANDS.md).
7. [Validation](07_VALIDATION_AND_RELEASE.md).
8. [Project plan](../tasks/plan.md) and [task checklist](../tasks/todo.md).

For later sessions, read progress/decisions and only the selected task's relevant specifications. Resume completed work instead of restarting it.

## 3. Documentation authority

| Question | Authority |
|---|---|
| What belongs in v1? | `02_PRD.md` |
| How are inference and decisions calculated? | `03_EXPERIMENT_PROTOCOL.md` |
| What input is valid? | `04_DATA_SPEC.md` |
| Which modules and output schema? | `05_TECHNICAL_DESIGN.md` |
| Which tools and commands? | `06_TECH_STACK_AND_COMMANDS.md` |
| What proves completion? | `07_VALIDATION_AND_RELEASE.md` |
| What is next? | `tasks/todo.md` |
| What changed and why? | Progress and decisions logs |

Maintain one task checklist. The plan references task IDs without duplicating status.

## 4. Default assumptions

1. Solo CPU-only portfolio project on Windows.
2. Cookie Cats dataset is verified and acquired (`data/raw/cookie_cats.csv`, SHA-256 `5ab54d76...`, 90,189 rows).
3. Seven-day retention is the only primary endpoint.

4. The study is retrospective. A local protocol freeze is not prospective preregistration of the original experiment.
5. Baseline 20%, meaningful uplift 0.5 percentage points, and 10 hours/week are illustrative assumptions, not user-confirmed business facts.
6. ChurnGuard integration is future design work, not a live campaign.

## 5. First execution session

1. T01: establish package, venv, compatible lock, and import smoke test.
2. T02: acquire the CSV, record provenance/hash, and inspect schema/counts without calculating outcome differences.
3. T03: implement validation and allocation checks; freeze configuration and record unknown metadata.
4. Begin outcome analysis only after quality requirements pass. Document any source change before adapting the contract.

## 6. Stop condition

All Must requirements and required implementation tasks are verified. Outputs regenerate from the source/configuration; report explains uncertainty and limitations without invented business impact. Negative and inconclusive outcomes are valid deliverables.
