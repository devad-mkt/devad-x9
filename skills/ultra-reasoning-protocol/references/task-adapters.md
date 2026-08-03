# Task Adapters

Use only the rows relevant to the current task.

| Domain | Add to the universal loop |
|---|---|
| Research and factual analysis | Prefer current primary sources; check dates, definitions, and source independence; cite claims near their evidence; label synthesis as inference. |
| Planning and decisions | Generate 2–3 viable options; compare dependencies, opportunity cost, reversibility, failure modes, and decision deadlines. |
| Coding and debugging | Reproduce first; rank hypotheses; write a failing regression test before a behavioral fix; inspect logs and boundaries; run focused then broad verification. |
| Creative and product design | Diverge before converging; vary concept, structure, and tone; evaluate against audience, constraints, distinctiveness, usability, and taste. |
| Writing and communication | Define audience and desired action; separate facts from persuasion; check structure, ambiguity, unsupported claims, and unnecessary detail. |
| Mathematics and data | Define variables and units; derive rather than guess; test boundary cases; perform an independent calculation or sanity check. |
| UI, browser, and desktop | Inspect current visible state; use accessibility, DOM, console, network, or screenshot evidence as appropriate; keep actions reversible. |
| Security, stateful systems, and operations | Map identity, authorization, state transitions, concurrency, stop bounds, durability, and recovery. Treat missing required artifacts and inaccessible providers as failures. Validate manifests as exact unique sets, compare authoritative state rather than versions alone, and prove rollback by restoring and validating the complete original recovery set. |
| Independent reviewer or xhigh task | Send the objective, raw artifacts, invariants, known unknowns, required negative probes, forbidden actions, and scoring rubric. Do not leak the intended answer. Require ranked findings, minimal reproducers, evidence, uncertainty, and a bounded verdict. |

## Reviewer Rubric

Score each candidate from 0–2 on: requirement coverage, factual correctness, counterexample resistance, evidence quality, safety, reversibility, efficiency, and clarity. A zero in correctness, safety, or evidence blocks `PASS` regardless of total score.

## Stateful Lessons

- An exhausted limit cannot be reopened by resetting telemetry.
- A raised migration error does not prove restoration.
- Matching generation or version does not prove matching content.
- A recovery manifest must not authorize an arbitrary subset.
- A missing active action or state artifact is not a healthy absence.
