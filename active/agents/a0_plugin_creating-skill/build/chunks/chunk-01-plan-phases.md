# chunk-01 — SKILL.md Phase 1-3 (Mode A: PLAN)

**Wave 1. Serial. Depends on chunk-00.**

## Goal
Fill SKILL.md's Mode A (PLAN) with the 3 research/plan/chunk phases. Every phase: what-to-do checklist, template pointer, example pointer, GATE.

## Files to edit (inside `...\a0_plugin_creating-skill\SKILL.md`)

Replace the Phase 1/2/3 stubs with full content. Contract:

### Phase 1: Search / Research — What-to-do
1. Read identity: is the target an existing plugin (find its source) or greenfield?
2. Read `ref/a0-plugin-contract.md` fully (1st pass; must know manifest/import/store-gate rules before writing anything).
3. Enumerate the target's current shape: services / tools / skills / config keys / auth method / WebUI tabs. For a greenfield plugin: enumerate exactly which services/tools/skills the user wants.
4. Identify the SINGLE biggest bottleneck or gap (e.g. "one global token.json → no multi-account").
5. Document A0 native affordances that make the task cheap (scoped config, `_oauth` precedent, sub-agents, toggles).
6. Capture external-API facts that change the plan (scopes, rate limits, auth caves like unverified-app 7-day refresh) in a research note.
GATE: a research note with: current-shape bullet list, gap list, A0-facts, external-facts.

Example pointer: `examples/research-excerpt.md`. Template: `templates/plan-01-research.md`.

### Phase 2: Plan — What-to-do
- Write, in order, using the `templates/plan-*.md` files:
  1. `00-README.md` (index + approved decisions + constraints)
  2. `01-research-summary.md` (from Phase 1 note)
  3. `02-decisions-winners.md` (option tables with win %; REQUIRES user approval)
  4. `03-target-architecture.md` (file tree, data model, function signatures, imports)
  5. `04-test-strategy.md` (dry-run/mock plan)
- Place them in a `plan_search-files/` folder NEXT TO the skill-specific build work.
- STOP for approval after `02-decisions-winners.md` before writing the architecture.
GATE: 5 files in `plan_search-files/`, decisions approved by user.

### Phase 3: Chunk — What-to-do
- Break `03-target-architecture.md` into **chunks** (each ≤ ~250 lines) with:
  - Wave label + dependencies
  - Goal
  - `Files to write` — exact paths, full signatures, key behavior (not full file bodies)
  - `Acceptance` — runnable commands + expected output
  - `DO NOT` — forbidden scope
- Ordering: serial chunks first (scaffold, auth core), then PARALLEL wave of independent chunks (each touches disjoint files).
- Emit a builder SKILL.md (like `examples/subagent-prompt.md`) that fixes paths, waves, sub-agent protocol, hard rules, final checklist.
- Place chunks in `<build root>\skills\<builder-name>\chunks\`.
GATE: chunks exist; each has the 5 sections; waves are dependency-true; parallel waves touch disjoint files.

Template pointer: `templates/chunk-template.md`. Example: `examples/chunk-excerpt.md`, `examples/wave-structure.md`.

## Acceptance

```powershell
Select-String -Path SKILL.md -Pattern '^### Phase [123]'   # 3 hits
Select-String -Path SKILL.md -Pattern 'templates/plan-|examples/' | Measure-Object   # >= 6
```

## DO NOT
- Do not write Phase 4/5 bodies yet.
- Do not write `templates/` or `examples/` (references by path only).
- Don't duplicate contract rules here — point at `ref/a0-plugin-contract.md`.