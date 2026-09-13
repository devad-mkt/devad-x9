# chunk-02 — SKILL.md Phase 4-5 + templates + examples

**Wave 2. Serial for SKILL.md; then PARALLEL sub-agents for templates + examples.**

## Goal

Finish SKILL.md (Execution mode) and write all supporting templates + examples. Templates/examples are independent → spawn up to 2 sub-agents (one for templates, one for examples) after SKILL.md Phase 4-5 is stable.

## Part A — Edit `SKILL.md` (Phase 4 Execute, Phase 5 Verify)

### Phase 4: Execute chunks — What-to-do
- Read builder SKILL.md (waves + gates). Execute chunks in wave order.
- Per chunk: read chunk file *fully* -> write ONLY listed files at exact paths -> run acceptance commands -> fix (max 3 tries) -> paste real output.
- Parallel waves: spawn a sub-agent per chunk with the protocol prompt from `examples/subagent-prompt.md`.
- Rules: never redesign; never touch files outside the chunk; no real network; type hints `|`; response `Response(...)`.
- GATE: every chunk's acceptance command exits 0.

### Phase 5: Verify + BUILD-REPORT — What-to-do
- Run compile gate: `python -m py_compile helpers\*.py tools\*.py api\*.py` (per plugin).
- YAML gate: `python -c "import yaml; d=yaml.safe_load(open('plugin.yaml'))"`.
- Test gate: `python -m pytest <plugin>\tests -q`.
- Simulate gate (if a simulation harness exists): `python <plugin>\tests\simulate_e2e.py`.
- Counts: tools, skills, services, helpers (report actuals; flag plan mismatches).
- Write `BUILD-REPORT.md` with: file-by-chunk inventory table, gate outputs pasted verbatim, counts, known limitations.
- GATE: BUILD-REPORT exists; all gates green; counts match or discrepancies documented.

## Files to write — templates (sub-agent T1)

`templates/plan-00-README.md`, `plan-01-research.md`, `plan-02-decisions.md`, `plan-03-architecture.md`, `plan-04-tests.md`, `chunk-template.md`. Generic, all placeholders (`<plugin-name>`, `<plan-root>`, `<build-root>`). Match the section structure actually used in the a0-google-suite build (short templates, tight tables, shell acceptance).

## Files to write — examples (sub-agent E)

Real excerpts **≤50 lines each**, clearly attributed to the a0-google-suite-v2 project:
- `examples/research-excerpt.md` — from `plan_search-files/01-research-summary.md`: "single-account bottleneck", platform facts bullet, options table row, API facts.
- `examples/chunk-excerpt.md` — from `chunk-01-auth-core.md`: the "Files to write" + function signatures + Acceptance block.
- `examples/wave-structure.md` — from `skills/a0-gsp-builder/SKILL.md` the waves block (verbatim).
- `examples/subagent-prompt.md` — from `skills/a0-gsp-builder/SKILL.md` the subagent protocol (verbatim).

## Acceptance

```powershell
Test-Path templates\plan-00-README.md, templates\plan-01-research.md, templates\plan-02-decisions.md, templates\plan-03-architecture.md, templates\plan-04-tests.md, templates\chunk-template.md, examples\research-excerpt.md, examples\chunk-excerpt.md, examples\wave-structure.md, examples\subagent-prompt.md
Select-String -Path SKILL.md -Pattern '^### Phase [45]'  # 2 hits
```

## DO NOT
- Do not embed full google-suite files (only ≤50-line excerpts).
- Do not put absolute `D:\` paths inside templates (use `<plan-root>`/`<build-root>`).
- Templates must be generic — no `google`, `gmail`, `accounts.py` references.