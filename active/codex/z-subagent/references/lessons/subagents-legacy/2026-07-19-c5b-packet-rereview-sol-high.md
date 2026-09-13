# Subagent Lesson

| Field | Value |
| --- | --- |
| Date | 2026-07-19 |
| Lane | side-question |
| Task class | corrected owner-packet re-review |
| Repository / packet identity | `$DEVAD_ROOT/content-agent-c5b-postgres-proof`, owner packet ending `04dc572d`, request ending `61f91773`, source `d547d3bf9d28604825871adf9ae13732bb4d1560` |
| Model / effort requested | SOL high |
| Model / effort attested | request accepted; runtime telemetry not exposed |
| Main-agent profile | unavailable |
| Why this tier was selected | Stateful database/destructive owner packet required a focused independent security check. |
| Scope and forbidden actions | Read-only packet review; no edits, staging, Git mutation, database, network, Dokploy, provider, runtime, or destructive action. |
| First-pass result | FAIL |
| Independent proof | Root independently reproduced the first two packet risks and verified final hash binding/scans. |
| Retries / compactions | 1 focused fix/re-review turn |
| Wall time | unavailable |
| Token telemetry | unavailable |
| Approx. new-token volume | `Unknown` |
| Safety or truth errors | none; first pass found retained HMAC-key P1, final pass clean |
| Ranking action | keep |

## Result

- Evidence and concise outcome: Initial re-review found one retained HMAC-key P1. After disposal and key-array zeroing, final result was P0/P1/P2 all zero and `MAY_STAGE_C1: YES`.
- Best use case learned: Reuse the same reviewer for one narrowly changed security packet instead of creating another review panel.
- Next profile to try, if any: Keep SOL high for executable destructive/runtime packets; use medium only for hash-only follow-ups with no secret lifecycle change.

