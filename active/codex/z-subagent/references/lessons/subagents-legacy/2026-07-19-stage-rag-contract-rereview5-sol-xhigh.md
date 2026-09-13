# Subagent Lesson

| Field | Value |
| --- | --- |
| Date | 2026-07-19 |
| Lane | side-question |
| Task class | narrow stage/RAG contract re-review |
| Repository / packet identity | Devad Content Agent stage/RAG packet af3feb6e/afc5fc79/0141af46 |
| Model / effort requested | gpt-5.6-sol / xhigh |
| Model / effort attested | gpt-5.6-sol / xhigh by dispatch configuration; runtime token telemetry unavailable |
| Main-agent profile | Sol manager |
| Why this tier was selected | Crash redelivery, DB CHECK feasibility, and named constraint totality require exact persistence reasoning. |
| Scope and forbidden actions | Read-only exact packet/base; no mutations. |
| First-pass result | FAIL |
| Independent proof | Demonstrated post-commit replay counterexample, impossible PHP canonical hash in plain PostgreSQL CHECK, and one unclassified named CHECK. |
| Retries / compactions | Narrow re-review after collision fix. |
| Wall time | Unknown |
| Token telemetry | unavailable |
| Approx. new-token volume | Unknown |
| Safety or truth errors | none |
| Ranking action | keep |

## Result

- Evidence and concise outcome: The collision authority was structurally sound, but crash-after-commit replay, database/application invariant separation, and one named status constraint still required correction.
- Best use case learned: Every durable terminal transaction needs a crash-after-commit-before-ack replay case, and PHP-only hashes must never be promised as plain database CHECKs.
- Next profile to try, if any: Same reviewer for final narrow pass.
