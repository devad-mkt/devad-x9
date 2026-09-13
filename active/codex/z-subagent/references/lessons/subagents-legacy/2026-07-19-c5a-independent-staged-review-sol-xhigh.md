# Subagent Lesson

| Field | Value |
| --- | --- |
| Date | 2026-07-19 |
| Lane | main |
| Task class | Independent spec/code/security staged review |
| Repository / packet identity | `$DEVAD_ROOT\1-core-x9`; C5A 36-path staged diff at `4a06bb09...` |
| Model / effort requested | SOL xhigh |
| Model / effort attested | Unknown; runtime telemetry did not attest the profile |
| Main-agent profile | SOL max |
| Why this tier was selected | High-risk persistence authority, replay, tenant isolation, and secrets boundaries |
| Scope and forbidden actions | Exact staged bytes and accepted contracts; no edits, Git mutation, provider/runtime/deploy action |
| First-pass result | FAIL |
| Independent proof | Six concrete blockers with exact file/line evidence; contract and W1B hashes independently matched |
| Retries / compactions | One review pass plus nested DB review |
| Wall time | Unknown |
| Token telemetry | unavailable |
| Approx. new-token volume | `Unknown` |
| Safety or truth errors | none; C1 approval was correctly withheld |
| Ranking action | keep |

## Result

- Evidence and concise outcome: In addition to the DB findings, the reviewer found SQLSTATE mapping could be bypassed by name-only terminalization and event-only append-only enforcement could be bypassed by quiet or bulk model writes.
- Best use case learned: Independent staged review should inspect negative/bypass paths, not only the intended repository call and green tests.
- Next profile to try, if any: Same SOL xhigh tier for a narrow rereview after the six bounded corrections.

Do not record secrets, cookies, raw provider output, or full sensitive prompts.
