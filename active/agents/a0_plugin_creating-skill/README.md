# a0_plugin_creating — Agent Zero plugin creation skill

Plan, build, and **audit** Agent Zero plugins without needing an expensive model. `a0_plugin_creating` packages the exact workflow that produced the **a0-google-suite-v2** multi-account plugin build *and* the post-build contract audit that fixed it: research → plan → chunk → execute → verify → audit.

Use it in a fresh chat, with any cheap model, and it will reproduce the same structured, verifiable build.

## What it does

- **CREATE (PLAN) mode** (fresh request): searches, writes a 5-file plan (`plan_search-files/`), gets your approval on the decisions, then writes dependency-ordered **chunk specs** plus a builder SKILL.md.
- **EXECUTE mode** (existing plan): follows the chunk specs in waves — serial foundation waves, then parallel waves via sub-agents — running each chunk's acceptance commands until green, then writes a `BUILD-REPORT.md`.
- **AUDIT mode** (existing plugin): checks install/uninstall parity, stale filenames, imports, frontend notifications, manifest, and gates (see `ref/audit-checklist.md`), then writes `AUDIT-REPORT.md` + an optional fix plan.

Everything runs dry: mocked external APIs, no real network, tests + a simulation harness.

## Quick start

```
1. Load SKILL.md (or skills/a0-plugin-router/SKILL.md for dispatch).
2a. CREATE (PLAN): describe the plugin -> it produces plan_search-files\ + chunks\.
2b. EXECUTE: "execute chunks 00..N in waves" -> it reads builder SKILL.md and runs.
2c. AUDIT: "audit this plugin" -> it runs the checklist and emits AUDIT-REPORT.md (+ fixes if you say "fix").
```

## Folder map

| Path | What |
| --- | --- |
| `SKILL.md` | The skill: three modes, 7 phases, gates |
| `AGENTS.md` | DOX: local contracts + sync rules |
| `ref/a0-plugin-contract.md` | A0 plugin contract (manifest, imports, Store Gate, hooks, layout, check commands) |
| `ref/audit-checklist.md` | Post-build audit runbook (install/uninstall parity, naming, imports, frontend, gates) |
| `templates/` | Plan, chunk, and audit-report skeletons |
| `examples/` | Real (short) excerpts: research bottleneck, chunk spec, wave chart, sub-agent prompt, audit fixes |
| `skills/a0-plugin-router/SKILL.md` | Cheap-model entry-point dispatcher |
| `build/chunks/` | The chunk specs used to build this very deliverable |

## Design notes

- Chunks are ≤ ~250 lines, each with Goal / Wave / Files-to-write / Acceptance / DO-NOT, so a weak model stays on rails.
- Gates are runnable commands (py_compile, YAML parse, pytest, simulation) with pasted output in the report.
- The methodology (plan-before-write, dry-run-before-done, sub-agent waves for parallel work) is distilled from the a0-google-suite-v2 build and documented with real excerpts.
- The audit checklist is NOT hypothetical — every item maps to a real defect it caught in the a0-google-suite-v2 post-build review.

## Planned extensions

- A decision-record template that scores options with win-rates like the google-suite `02-decisions-winners.md`.
- (Audit of existing plugins is already in-skill as AUDIT mode; `a0-review-plugin` could later add cross-plugin consistency checks if needed.)