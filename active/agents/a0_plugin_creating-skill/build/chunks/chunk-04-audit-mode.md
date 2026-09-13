# Chunk 04 — Add Mode C: AUDIT to the skill (post-build audit pass)

Serial. Depends on chunk-03 (router + README + BUILD-REPORT) being finished.

## Goal

Fold the lessons of the real post-build contract audit of the a0-google-suite-v2 plugins into the creating skill itself, so any model running this skill audits an existing plugin instead of declaring it healthy on gates alone.

## Files to write

1. `SKILL.md`
   - Add a third row to the mode table: `"Audit/review/verify/fix" an existing plugin, or "report what's wrong / what to fix" — no new feature build | **C: AUDIT**`.
   - Add `## Mode C: AUDIT (an existing plugin — report only by default)` with `### Phase 6: Audit` and `### Phase 7: Report + optional fix plan`; update A-phase/EXECUTE-phase references where a completed build now points to Mode C.
   - Add `ref/audit-checklist.md` to the Reference material block and add audit lessons to Common mistakes.
2. `AGENTS.md` — add audit checklist to Ownership, add a contract bullet ("never declare a built plugin healthy without the audit consult").
3. `README.md` — "What it does" gains an AUDIT bullet; Quick start gains `2c. AUDIT`; Folder map gains `ref/audit-checklist.md`; Design notes notes the checklist is drawn from real defects.
4. `ref/audit-checklist.md` (NEW) — 8 sections distilled from the real audit: hooks/side-effects + uninstall parity, rename/stale refs, imports, frontend Store Gate + notifications, manifest, gates, counts vs claim, output.
5. `templates/audit-report.md` (NEW) — AUDIT-REPORT skeleton with per-item table + real commands + fix plan.
6. `examples/audit-excerpt.md` (NEW) — short real excerpt: contract-audit fixes table from a0-google-suite(in table, not the "(...)"), and a call-out for the checklist itself.

## Acceptance
- `grep -c '^## Mode C' SKILL.md` = 1; `grep -c '^### Phase 6' SKILL.md` = 1; `grep -c '^### Phase 7' SKILL.md` = 1.
- `Test-Path ref\audit-checklist.md`, `Test-Path templates\audit-report.md`, `Test-Path examples\audit-excerpt.md` all True.
- No `"two modes"` or `"5 phases"` remains in SKILL/README/AGENTS/router.
- BUILD-REPORT.md updated with a chunk-04 row and new amounts.

## DO NOT
- Do not touch `ref/a0-plugin-contract.md` or the six existing plan templates, or the execute-waves example.