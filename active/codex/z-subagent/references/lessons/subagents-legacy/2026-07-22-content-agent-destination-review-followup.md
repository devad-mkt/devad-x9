# Subagent Lesson

| Field | Value |
| --- | --- |
| Date | 2026-07-22 |
| Lane | code review |
| Task class | focused destination transport correction review |
| Model / effort requested | inherited |
| Model / effort attested | unavailable |
| Scope | Read-only stable-diff review; no broad audit or external calls. |
| First-pass result | REVISE, then PASS |
| Independent proof | Main agent added RED/GREEN tests, removed receipt recovery from the reversed lock order, and reran 249 focused plus 6,422 POST assertions. |
| Safety or truth errors | none observed |
| Ranking action | keep |

## Result

- Evidence and concise outcome: The helper caught a rollback and lock-order problem that ordinary happy-path tests missed, then confirmed the fail-closed post-lock recovery correction.
- Best use case learned: Reuse the same reviewer for one correction follow-up; it preserves finding context and avoids a duplicate audit.

