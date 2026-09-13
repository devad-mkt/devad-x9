# Subagent Lesson

| Field | Value |
| --- | --- |
| Date | 2026-07-19 |
| Lane | main |
| Task class | Final independent staged acceptance review |
| Repository / packet identity | C5A revision 3, 37 staged paths at `4a06bb09...` |
| Model / effort requested | SOL xhigh |
| Model / effort attested | Unknown |
| Main-agent profile | SOL max |
| Why this tier was selected | Final source, test-truth and append-only authority gate before Git mutation |
| Scope and forbidden actions | Read-only exact staged bytes; no edits, Git mutation, external runtime, or provider calls |
| First-pass result | PASS |
| Independent proof | Laravel 13.20 source routing plus 21 zero-mutation datasets and exact Git/hash/security readback |
| Retries / compactions | Third staged review after two bounded correction cycles |
| Wall time | Unknown |
| Token telemetry | unavailable |
| Approx. new-token volume | `Unknown` |
| Safety or truth errors | none; UNKNOWN runtime labels preserved |
| Ranking action | keep |

## Result

- Evidence and concise outcome: All named Eloquent and model-derived base-query mutation paths reach the guard. Tests prove exception, byte stability, count stability, read, and exact replay for every dataset. Exact 37-path Git state and security pre-commit passed.
- Best use case learned: High-risk staged changes benefit from repeated independent review when each cycle is strictly limited to the remaining blocker.
- Next profile to try, if any: No further review before bounded C1/C2; perform commit readback and post-push review next.

Do not record secrets, cookies, raw provider output, or full sensitive prompts.
