# Subagent Lesson

| Field | Value |
| --- | --- |
| Date | 2026-07-19 |
| Lane | side-question |
| Task class | final Autopilot contract acceptance review |
| Repository / packet identity | Devad Content Agent Autopilot 39a53c15/7515bb1c on integration 4a06bb09 |
| Model / effort requested | gpt-5.6-sol / xhigh |
| Model / effort attested | gpt-5.6-sol / xhigh by dispatch configuration; runtime token telemetry unavailable |
| Main-agent profile | Sol manager |
| Why this tier was selected | Strict read-only claims require checking middleware, sessions, cache, feature flags, throttling, and auth side effects. |
| Scope and forbidden actions | Read-only exact Autopilot packet and integration source. |
| First-pass result | FAIL |
| Independent proof | Found unavoidable writes in current web/API middleware and database-backed session/cache paths that were missing from zero-delta tests. |
| Retries / compactions | Final pass after ten-finding correction. |
| Wall time | Unknown |
| Token telemetry | unavailable |
| Approx. new-token volume | Unknown |
| Safety or truth errors | none |
| Ranking action | keep |

## Result

- Evidence and concise outcome: All earlier blockers closed, but strict zero-write reads still needed a dedicated non-recording middleware/limiter contract and wider zero-delta tests.
- Best use case learned: Read-only API claims must account for framework transport bookkeeping, not only domain tables.
- Next profile to try, if any: Narrow fixer then independent targeted review.
