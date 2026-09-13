---
name: a0_plugin_creating-skill
description: Create, extend, or audit Agent Zero plugins (research -> plan -> chunk -> execute -> verify -> audit), or execute/fix an existing chunked plugin plan. Use when asked to create/plan/execute/build/extend/index/review/audit/verify/fix an A0 plugin, or to run chunks from a plan, or to check an existing plugin against the contract.
---

# a0_plugin_creating

Create, extend, or audit Agent Zero plugins; the audit also catches fixes that a raw build misses. The methodology here is distilled from a real multi-account plugin build (a0-google-suite-v2) *and the post-build audit that fixed it*; see `examples/` for short real excerpts and `ref/a0-plugin-contract.md` for the A0 plugin contract.

## Three modes (detect from the request)

| Signal | Mode |
|---|---|
| "Create/extend/plan a plugin"; no plan folder exists for it | **A: PLAN** |
| Request names existing chunk files + a builder SKILL.md, or a plan folder already exists for the plugin | **B: EXECUTE** |
| "Audit/review/verify/fix" an existing plugin, or "report what's wrong / what to fix" — no new feature build | **C: AUDIT** |

Decision rule: if the request names a plugin and `plan_search-files/` (or chunk files) already exist, default to EXECUTE. If the request is about the *health* of an existing plugin (manifest, layout, imports, hooks, frontend, cleanup) with no build intent, default to AUDIT. Ask one clarifying question only when genuinely ambiguous.

## Mode A: PLAN (a new plugin from a raw request)

### Phase 1: Search / Research

Do research before writing any file. Steps:

1. Read `ref/a0-plugin-contract.md` once, in full — know the manifest/import/Store-Gate/hooks rules before planning anything.
2. Enumerate the target's **current shape** (existing plugin): services, tools, skills, config keys, auth method, WebUI tabs. For a greenfield plugin, enumerate the **requested** services/tools/skills instead.
3. Identify the **single biggest bottleneck or gap** (e.g. "one global token.json blocks multi-account"). Name one — this drives the whole plan.
4. Capture **A0 affordances** that make the task cheap: scoped config (`per_project_config`/`per_agent_config`), sub-agent waves, toggles, existing `_oauth`/store precedents.
5. Capture **external-API facts** that change the plan: scopes needed, free-tier rate limits, auth caves (e.g. unverified-app 7-day refresh, developer-token approval).

Write the result as a research note using `templates/plan-01-research.md`. See `examples/research-excerpt.md` for a real excerpt (bottleneck identification + options table).

**GATE:** note has current-shape bullets, gap list, A0-facts, external-facts.

### Phase 2: Plan (write plan files)

Write, in this order, into a `plan_search-files/` folder next to the build root:

| # | File | Content | Template |
|---|------|---------|----------|
| 1 | `00-README.md` | index, goal, approved decisions, constraints | `templates/plan-00-README.md` |
| 2 | `01-research-summary.md` | distilled Phase 1 note | `templates/plan-01-research.md` |
| 3 | `02-decisions-winners.md` | options table, pros/cons/win rates, winner call | `templates/plan-02-decisions.md` |
| 4 | `03-target-architecture.md` | file tree, data model, function signatures, imports | `templates/plan-03-architecture.md` |
| 5 | `04-test-strategy.md` | mock/dry-run test plan, zero real network | `templates/plan-04-tests.md` |

**STOP after file 3** and get user approval of the winner before writing the architecture. File names must match the `plan_search-files/` contract exactly so EXECUTE mode can find them.

**GATE:** 5 files exist; decisions approved by the user.

### Phase 3: Chunk (write chunk specs)

Break the architecture into build chunks, each in its own file with exactly these 5 sections:

1. **Goal** — one paragraph of intent.
2. **Wave label + dependencies** — serial or parallel; what it blocks on.
3. **Files to write** — exact paths, full function signatures, precise behavior. Specs, not full file bodies.
4. **Acceptance** — runnable commands with expected output (syntax gate, test file, YAML parse, simulation).
5. **DO NOT** — forbidden scope (keeps a weak sub-agent on rails).

Rules:

- Serial chunks come first: scaffold, auth/core, shared plumbing.
- Parallel waves only contain chunks whose `Files to write` lists are disjoint.
- After the last chunk, emit a **builder SKILL.md** (see `examples/subagent-prompt.md`) that fixes: plan root, chunks root, build root, wave list, per-chunk workflow, hard rules, final checklist. Store chunks under `<build root>/skills/<builder-name>/chunks/`.
- Then hand the whole thing to EXECUTE mode — optionally a separate sub-agent.

**GATE:** every chunk has the 5 sections; waves are dependency-true; parallel waves list disjoint files; builder SKILL.md exists.

## Mode B: EXECUTE (an existing chunked plan)

### Phase 4: Execute chunks

1. Read the builder SKILL.md fully — it fixes paths, waves, hard rules, final checklist.
2. Execute chunks in wave order (serial waves one at a time; parallel waves = one sub-agent per chunk).
3. Per chunk: read the chunk file fully → write **only** the listed files at the exact paths → run the acceptance commands → if a command fails, fix and re-run (max 3 attempts) → paste real output.
4. Sub-agent protocol for a parallel wave: spawn one subordinate per chunk with `examples/subagent-prompt.md` (read chunk + architecture, write only listed files, run acceptance, report PASS/FAIL). Collect all reports before starting the next wave; if any FAIL, fix that chunk yourself.
5. Never redesign scope: if a chunk is impossible as written, stop and report to the user rather than improvising.

**GATE:** every chunk's acceptance command exits 0 before moving past its wave.

### Phase 5: Verify + BUILD-REPORT

Run every gate on the finished build:

1. Syntax: `python -m py_compile` on all new/modified `.py` files.
2. Manifest: `python -c "import yaml; yaml.safe_load(open('<build>/<plugin>/plugin.yaml'))"`.
3. Tests: `python -m pytest <build>/<plugin>/tests -q` (mock/dry-run only).
4. Simulation: `python <build>/<plugin>/tests/simulate_e2e.py` (prints ALL PASS, exit 0) if the plan has one.
5. Counts: tools, services, skills, helpers — compare to the plan's architecture; if they differ, document it rather than hiding it.
6. Re-open `ref/a0-plugin-contract.md` for any dry-run self-checks (import grep, Store Gate, hooks names).

Then write `BUILD-REPORT.md` at the build root: file-by-chunk inventory table, every gate's pasted real output, counts, known limitations.

**GATE:** BUILD-REPORT exists; all gates green; actual counts match the plan (discrepancies documented).

## Mode C: AUDIT (an existing plugin — report only by default)

Run this on any existing plugin whose health you must confirm, or to find what a build missed. Cheap, dry, read-only first; you only write the report (and a fix-plan) unless the user explicitly asks to apply fixes.

### Phase 6: Audit

Read `ref/audit-checklist.md` fully, then inspect the plugin against each item. The checklist covers things build gates miss — the audit of the a0-google-suite build surfaced all of these:

1. **Side effects outlive the plugin** — does `hooks.py` `install()` copy skills or mirror files outside the plugin dir? Does `uninstall()` remove EVERYTHING `install()` created (skill list drift)? This is the top fix-source found in the real audit.
2. **Stale filenames/greps** — `initialize.py` vs the contract's `execute.py`; grep for old names in `helpers/gremlins`, `install.sh`, regression tests, READMEs, error strings.
3. **Cross-plugin imports** — `from plugins.<name>` in a usr plugin (contract wants `usr.plugins.<name>`), `sys.path` in production code (tests may use it — note that difference).
4. **Frontend contract** — Store Gate on every store-using component, no `alpine:init` inside HTML, separate `.js` store modules via `/js/AlpineStore.js`, inline error/success `<div>` blocks replaced by `toastFrontendError/Success/Info` (this is what the real audit had to fix in both config pages).
5. **Manifest + configs** — `plugin.yaml` parses; `name` regex; `settings_sections` matches `webui/config.html` presence; `default_config.yaml` parses; no `always_enabled: true` on custom plugins.
6. **Folder-name routing** — YAML `name` matches folder name; folder uses no hyphens; WebUI store JS derives plugin name from `import.meta.url`, not hardcoded; Python code derives from `Path(__file__).parent.parent.name`, not hardcoded; API handler docstrings match actual folder name.
7. **Gate re-run** — `py_compile`, pytest (offline), YAML parse, simulation harness exit 0.
8. **Counts vs contract** — services/tools/skills/helpers vs what the README/contract claims (drift detection).

**GATE:** every checklist item has a PASS/FAIL/WARN with evidence (line numbers / command output).

### Phase 7: Report + optional fix plan

Write `AUDIT-REPORT.md` next to the plugin: per-item table, the real commands you ran, and a **fix plan** (`priority | file | change | risk`) derived from the FALL items. If the user asked for fixes ("fix them"), apply them chunk-style (see `templates/chunk-template.md`): each fix = one tight change at exact path, re-run the affected gate, report output. Fix upsert-order smallest/cleanest first (e.g. filenames rename, then import, then frontend).

**GATE:** AUDIT-REPORT exists; every fix is applied + its gate re-run; unapplied fixes listed as "recommended".

## Reference material (paths)

- Contract: `ref/a0-plugin-contract.md` (read once in PLAN; re-open in EXECUTE Phase 5 and AUDIT Phase 6)
- Audit checklist: `ref/audit-checklist.md` (run in AUDIT mode)
- Templates: `templates/plan-00-README.md` .. `templates/chunk-template.md`, `templates/audit-report.md`
- Examples: `examples/research-excerpt.md`, `examples/chunk-excerpt.md`, `examples/wave-structure.md`, `examples/subagent-prompt.md`, `examples/audit-excerpt.md`
- Router: `skills/a0-plugin-router/SKILL.md` (for dispatcher-style requests)

## Common mistakes checklist

- Skips the plan step and starts writing files (biggest source of errors)
- Writes when a chunk says "acceptance" — acceptance commands MUST be run
- Redesigns scope mid-build instead of failing the chunk
- Declares done before compile/YAML/tests all pass
- Declares a built plugin "healthy" without an audit pass (real plug audits found: uninstall skill drift, stale `initialize.py` names, cross-plugin imports, inline frontend errors, **folder-name mismatch causing 404s**)
- Mirrors test-only `sys.path` patterns into production code
- `hooks.py install()` creates files that `uninstall()` doesn't remove
- Forgets the manifest `name` regex / wrong directory root — see `ref/a0-plugin-contract.md`
- Hardcodes plugin name in `get_config()` / API URLs / store JS — A0 uses the folder name, not the YAML name; derive dynamically