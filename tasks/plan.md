# Implementation Plan: ExperimentGuard

## 1. Objective

Deliver reproducible two-variant retention analysis and manager decision report with integrity checks, uncertainty, and prospective power planning. [PRD](../docs/02_PRD.md) owns scope; [todo.md](todo.md) is the only task checklist.

## 2. Responsibilities

| Hat | Responsibility |
|---|---|
| Project manager | Scope, milestones, effort, risks, next task |
| Senior ML engineer | Architecture, lock, reproducibility, tests, CI |
| Experiment analyst | Provenance, methods, protocol, limits |
| Product reviewer | Practical assumptions and decision interpretation |

These are solo responsibilities, not a claimed team. No additional agent is required by this plan.

## 3. Milestones and estimate

| Milestone | Tasks | Effort | Exit evidence |
|---|---|---|---|
| M1 Trusted input | T01-T03 | 6-9 h | Environment, manifest, validator/SRM, frozen protocol |
| M2 Primary decision | T04-T06 | 6-9 h | Reference-tested inference, decision, JSON slice |
| M3 Planning/report | T07-T09 | 6-9 h | Power scenarios, report/figures, limits |
| M4 Reproducibility | T10-T13 | 6-10 h | CLI/notebook agreement, local CI, evidence review |
| Buffer | Checkpoint issues | 5-6 h | Data/environment/report fixes |

Base 24-37 h including optional T08; with 5-6 h buffer, 29-43 h, rounded to a planning budget of **30-45 h**. At assumed 10 h/week allow 3-5 weeks. No actual capacity, start date, or deadline is confirmed. Milestone quality takes precedence over calendar estimates.

## 4. Dependencies

```text
T01 -> T02 -> T03 -> T04 -> T05 -> T06
                 T03 -> T07
                 T04 -> T08 (Should work)
      T06 + T07 (+T08 if included) -> T09 -> T10 -> T11 -> T12 -> T13
```

Primary vertical slice precedes exploratory work. Power planning uses assumptions without treatment results. T08 may be skipped only with an explicit scope note.

## 5. Checkpoints

1. After T03: verify source suitability and quality; freeze assumptions before effects.
2. After T06: independently verify calculations and all decision boundaries.
3. After T09: inspect memo/figures and practical interpretation.
4. After T13: prove fresh-process reproduction before marking implemented.

Continue routine authorised work when checks pass. Clarify only material unresolved choices the documented defaults cannot handle.

## 6. Risk register

| Risk | Impact | Response |
|---|---|---|
| Source unavailable/terms unclear | Real case delayed | Verify early; fixtures only for tests |
| Unknown assignment/allocation | Weak causal evidence | Source-reported vs verified; assumed SRM label; unverified assignment blocks |
| Missing maturity timestamps | Completeness unknown | Named limit near decision, no invented timing |
| Known public results influence method | Retrospective bias | Freeze local protocol; disclose retrospective status |
| Post-treatment filtering | Biased estimate | Include zero rounds/non-returners |
| Engagement outliers | Secondary instability | Full data plus prescribed descriptive sensitivity |
| Small significant effect oversold | Wrong rollout interpretation | Practical interval decision rule |
| Notebook differs from CLI | Non-reproducible results | Shared package, fresh kernel |
| Scope expands to platform | Delayed delivery | V1 stop condition; future work list |
| Windows dependency/kernel mismatch | Setup failure | Compatible lock and kernel smoke test early |

## 7. Management rules

- Update progress after each session; decisions before dependent changes.
- Keep one implementation checklist.
- Split a task exceeding five production/test/config files before edits.
- Do not silently omit a Must requirement to meet the estimate.

## 8. Requirement traceability

| Requirements | Tasks |
|---|---|
| FR01-FR03 | T02-T03 |
| FR04-FR05 | T04-T06 |
| FR06 | T07 |
| FR07 | T09-T10 |
| FR08 | T11 |
| FR09 | T09/T13 |
| FR10-FR11 | T08, Should scope |
| FR12 | Existing future design, review T13 |
| NFR01-NFR08 | T01/T03-T13 plus final evidence audit |

## 9. Stop condition

All Must requirements, required tasks, and release checks satisfied. Explicitly disclose T08 omission. No new model/API/dashboard/cloud/campaign is added without a scope decision.
