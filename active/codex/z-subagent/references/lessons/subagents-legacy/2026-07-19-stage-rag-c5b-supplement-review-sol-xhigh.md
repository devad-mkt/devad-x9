# Subagent Lesson

| Field | Value |
| --- | --- |
| Date | 2026-07-19 |
| Lane | side-question |
| Task class | C5B supplemental contract review |
| Repository / packet identity | Devad Content Agent C5B ee949fad/5bdfef99 |
| Model / effort requested | inherited Sol / inherited effort |
| Model / effort attested | runtime token telemetry unavailable |
| Main-agent profile | Sol manager |
| Why this tier was selected | Stage-run ownership, last-moment spend lineage, and queue-exhaustion races are production safety boundaries. |
| Scope and forbidden actions | Read-only exact C5B supplement, accepted parents, and Laravel queue source. |
| First-pass result | FAIL |
| Independent proof | Found missing per-stage ai_run replay ownership, incomplete locked spend preconditions, and unsafe duplicate-job exhaustion semantics. |
| Retries / compactions | One independent pass. |
| Wall time | Unknown |
| Token telemetry | unavailable |
| Approx. new-token volume | Unknown |
| Safety or truth errors | none |
| Ranking action | keep |

## Result

- Evidence and concise outcome: Outbox/UUID/lease/no-resend logic was sound, but three literal gaps could still break receipt lineage or falsely terminalize duplicate jobs.
- Best use case learned: Queue contracts need per-code `failed(Throwable)` behavior and explicit stage-run creation/replay before receipt finalization.
- Next profile to try, if any: Same C5B author for three exact fixes, then targeted independent review.
