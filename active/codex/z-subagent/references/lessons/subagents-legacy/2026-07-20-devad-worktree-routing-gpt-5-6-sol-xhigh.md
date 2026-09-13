# Subagent Lesson

| Field | Value |
| --- | --- |
| Date | 2026-07-20 |
| Lane | side-question |
| Task class | Devad helper-worktree routing pressure test |
| Repository / packet identity | `$DEVAD_ROOT\1-core-x9`; current Devad workspace skills |
| Model / effort requested | `gpt-5.6-sol` / `xhigh` |
| Model / effort attested | Unknown; the dispatch accepted the request but exposed no runtime model telemetry |
| Main-agent profile | SOL |
| Why this tier was selected | Cross-skill workspace conflict review with destructive-risk implications |
| Scope and forbidden actions | Read-only; no worktree, branch, file, Git, provider, or deployment mutation |
| First-pass result | PASS |
| Independent proof | Current skill hashes and live `git worktree list --porcelain`; no filesystem mutation observed |
| Retries / compactions | none |
| Wall time | unavailable |
| Token telemetry | unavailable |
| Approx. new-token volume | `Unknown` |
| Safety or truth errors | none material; correctly rejected a new root-level helper path |
| Ranking action | keep |

## Result

- Evidence and concise outcome: Rejected `$DEVAD_ROOT\content-agent-helper`, disabled the generic manual-worktree fallback, and required a host-created native worktree under `$DEVAD_ROOT\0-cdx-wt` with exact ownership/base binding.
- Best use case learned: Use SOL xhigh for one bounded cross-skill policy challenge when a wrong choice could create or move Git worktrees.
- Next profile to try, if any: SOL high for a comparable read-only routing check with a frozen packet.

Do not record secrets, cookies, raw provider output, or full sensitive prompts.
