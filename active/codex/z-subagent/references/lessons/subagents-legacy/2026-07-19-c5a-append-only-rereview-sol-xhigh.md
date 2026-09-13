# Subagent Lesson

| Field | Value |
| --- | --- |
| Date | 2026-07-19 |
| Lane | main |
| Task class | Laravel append-only bypass rereview |
| Repository / packet identity | C5A revision 2, `AiBlogTerminalReceiptBuilder` |
| Model / effort requested | SOL xhigh |
| Model / effort attested | Unknown |
| Main-agent profile | SOL max |
| Why this tier was selected | Framework mutation escape hatches can corrupt append-only authority silently |
| Scope and forbidden actions | Exact corrected staged bytes; no edits, Git mutation, external runtime, or provider calls |
| First-pass result | FAIL |
| Independent proof | Laravel 13.20 source exposes additional unblocked mutation methods beyond ordinary update/delete |
| Retries / compactions | Second staged review cycle |
| Wall time | Unknown |
| Token telemetry | unavailable |
| Approx. new-token volume | `Unknown` |
| Safety or truth errors | none; C1 approval remained withheld |
| Ranking action | keep |

## Result

- Evidence and concise outcome: Ordinary, quiet and bulk update/delete were blocked, but conflict-update, counter mutation, forced removal, timestamp touch, forwarded conditional-update and whole-table-clear methods remained reachable.
- Best use case learned: Append-only review must inventory the framework's complete write API, not only model events and the two obvious builder methods.
- Next profile to try, if any: One narrow implementer correction and final source-based rereview.

Do not record secrets, cookies, raw provider output, or full sensitive prompts.
