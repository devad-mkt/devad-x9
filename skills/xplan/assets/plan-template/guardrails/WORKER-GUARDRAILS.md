# Worker Guardrails

- Work only from the current immutable order and exact owned paths.
- Read `../PLAN.md`, one dependency receipt, and bounded ledger rows.
- Continue through the authorized lane queue; report one blocker and move to
  the next safe non-overlapping item.
- Ask the manager for routine questions. Stop for owner decisions, shared
  collisions, secrets, destructive/live actions, or invalidated architecture.
- Return changed files, tests, browser/runtime proof, unknowns, and one next
  safe action.
