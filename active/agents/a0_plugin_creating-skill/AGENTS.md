# a0_plugin_creating — DOX

## Purpose

- Own the end-to-end workflow for creating, extending, or auditing Agent Zero plugins: research, plan, chunk, execute, verify, audit.
- Make the workflow runnable by weak/cheap models in a fresh chat: every phase has runnable gates, no skipped steps.
- Keep all A0 plugin conventions (manifest, imports, layout, Store Gate, notifications) accurate — mirror `ref/a0-plugin-contract.md`.

## Ownership

- `SKILL.md` owns trigger metadata, the three-mode decision, phase steps, gates, and the common-mistakes checklist.
- `ref/a0-plugin-contract.md` owns the A0 plugin contract (single source of truth for conventions).
- `ref/audit-checklist.md` owns the audit review pass (Mode C runbook).
- `templates/` owns reusable plan/chunk skeletons AND the audit-report skeleton.
- `examples/` owns short real excerpts that demonstrate the workflow.

## Local Contracts

- The workflow must ALWAYS include an explicit Plan step (restate intended files/paths before creating them) and a Verify/Dry-Run step (syntax, YAML, tests) before reporting completion.
- Plan-before-write and dry-run-before-done are mandatory, never optional skips — skipping verification is the primary source of plugin errors.
- A *built* plugin is never declared healthy without a Mode-A audit pass (install/uninstall parity, filenames, imports, frontend notifications). Gates prove code runs; the audit proves contract compliance.
- Never introduce content that contradicts `ref/a0-plugin-contract.md`; if it changes, update both the contract and the matching SKILL.md sections.

## Work Guidance

- Keep every chunk ≤ ~250 lines; each chunk has Goal / Files-to-write / Acceptance / DO-NOT.
- Serial chunks first (scaffold, auth core); parallel waves only with disjoint files.
- Update the templates when the plan/chunk/audit format evolves, and re-verify `examples/` excerpts still match the workflow.