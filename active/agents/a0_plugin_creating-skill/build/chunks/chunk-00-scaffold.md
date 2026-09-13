# chunk-00 — Scaffold + A0 contract reference

**Wave 0. Serial. BLOCKS everything else.**

## Goal
Create the skeleton of the `a0_plugin_creating` skill so every later chunk has a stable home. Also pin the A0 plugin contract as a single-reference `ref/a0-plugin-contract.md`.

## Files to write (inside `$DEVAD_TOOLS_ROOT\10-Other\0a-plugins\a0_plugin_creating-skill\`)

### 1. `SKILL.md`
Frontmatter + all Phase headers + one-line stub under each phase. Exact frontmatter:

```yaml
---
name: a0_plugin_creating
description: Create or extend Agent Zero plugins end-to-end (research -> plan -> chunk -> execute -> verify), or execute an existing chunked plugin plan. Use when asked to build/plan/plan-out/create/extend an A0 plugin, or to execute a plugin plan from chunk specs.
---
```

Headers (must exist, in this order):
```
# a0_plugin_creating
## Two modes (detect from the request)
## Mode A: PLAN (a new plugin from a raw request)
### Phase 1: Search / Research
### Phase 2: Plan (write plan files)
### Phase 3: Chunk (write chunk specs)
## Mode B: EXECUTE (an existing chunked plan)
### Phase 4: Execute chunks
### Phase 5: Verify + BUILD-REPORT
## Reference material (paths)
## Common mistakes checklist
```

Each `### Phase` gets 2-4 placeholder sentences (to be filled in chunk-01/02) plus `<!-- do: ... -->` markers listing exactly what belongs there.

### 2. `AGENTS.md`
~35 lines DOX. Purpose, Ownership, Local Contracts, Work Guidance, Keep-in-sync rules. Model it on the deepwiki `a0-create-plugin/AGENTS.md` + `plugins/AGENTS.md` excerpts (Local Contracts must state: plan-before-write + dry-run-before-done).

### 3. `ref/a0-plugin-contract.md`
The A0 plugin CONTRACT. Source = cleaned-up synthesis of `D:\0a-plugins\a0_google_suite_plus\task-3.txt` lines 7-139 (deepwiki ref) + `plugins/AGENTS.md` excerpt already quoted there.

Structure exactly:
```
# Agent Zero plugin contract (reference)
## Manifest (plugin.yaml)
## Directory layout
## Import conventions
## Settings & scoping
## Frontend: Store Gate + notifications
## hooks.py vs execute.py
## Extension layouts
## Common mistakes (table)
## Dry-run / self-check commands
```
Content must be concrete and checkable — YAML name regex, `usr/plugins/` path, import rule `usr.plugins.<name>...`, no `sys.path` hacks, Store Gate wrapper, `toastFrontendError/Success`, hook names `install|pre_update|uninstall`, execute.py guard, dry-run commands. ~120-180 lines.

## Acceptance
```powershell
cd $DEVAD_TOOLS_ROOT\10-Other\0a-plugins\a0_plugin_creating-skill
Test-Path SKILL.md, AGENTS.md, ref\a0-plugin-contract.md
(Select-String -Path SKILL.md -Pattern '^## ').Count # >= 9
(Get-Content ref\a0-plugin-contract.md).Count # >= 100
(Get-Content AGENTS.md).Count # >= 30
```

## DO NOT
- Do not write any Phase body content yet (only stubs/placeholders).
- Do not write templates/ or examples/ files.
- Do not add content from outside `a0_google_suite_plus\task-3.txt` and `a0_google_suite_plus` assets — the contract ref must stay self-contained.