# chunk-03 — router sub-skill + README + BUILD-REPORT + final verification

**Wave 3. Serial (small). Depends on chunk-02.**

## Goal
Add a router sub-skill (dispatch to builder / reviewer / contributor paths), write the human-facing README.md, and produce BUILD-REPORT.md. Close the loop with final gates.

## Files to write (inside `...\a0_plugin_creating-skill\`)

### 1. `router.md` (or `skills/a0-plugin-router/SKILL.md`)
Cheap-model dispatch: given a plugin request, decide which narrower skill to load:
- `a0_plugin_creating` — plan or execute chunked plugin work
- `a0-plugin-review` — review an existing plugin's layout/manifest/security (pointer only; not part of this deliverable)
- `a0-plugin-contribute` — fold external top-level plugins into a plugin suite (pointer only)
Rules: ≤ ~40 lines, table of signals → skill; absolute paths to the other skills; bold note: this router cannot plan — it only dispatches.

### 2. `README.md`
Human-intent summary: what the skill does, two modes, quickstart (2 commands), folder map, contract pointer, acknowledgements (that the chunk+sub-agent methodology is distilled from the a0-google-suite-v2 build), planned extensions. No verbatim google internals.

### 3. `BUILD-REPORT.md`
As in the google-suite report: file inventory by chunk (00-03), gate outputs pasted verbatim (compile/yaml/pytest/simulate as applicable to this skill), counts (phases, templates, examples, ref docs), known limitations.

## Acceptance — final
```powershell
Get-ChildItem -Recurse -File | Measure-Object   # list count
Select-String -Path README.md -Pattern 'quick start' -Quiet
Test-Path router.md  # or skills\a0-plugin-router\SKILL.md
(Get-Content BUILD-REPORT.md).Count -ge 30
```
Also verify every relative path the skill points to (`templates/`, `examples/`, `ref/`) actually exists (open + eyeball).

## DO NOT
- Do not create implementation stubs for review/contribute skills — router only *points* at them with absolute paths.
- Do not regress SKILL.md structure.