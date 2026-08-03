# Supporting Skill Merge

The v5 source starts from the clean remote v3 package, then compares the live
installed copies. No supporting skill is overwritten blindly.

| Skill | Chosen base | Retained additions |
| --- | --- | --- |
| codex-x9-backup | v3 package | five-suite/package manifest and benchmark checks plus all live backup policy |
| codex-token-budget | v3 package | telemetry schema caution, model benchmark mode, compact routing files, all live diagnostics |
| devad-memory | v3 package | memory is historical, ROUTER is active truth, all live extraction guidance |

Exact pre-v5 live folders are in archives/pre-v5-2026-07-13/live-skills.
The package copies are the intentional union because the remote v3 versions are
strict supersets of the current live entrypoints for these clauses.

Validated adaptation:
- restore-codex-x9-backup.ps1 had an invalid foreach pipeline in DryRun.
  V5 stores the foreach output in rootPlan before formatting. The pre-v5 archive
  remains byte-exact and unchanged.
