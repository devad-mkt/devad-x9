# Subagent Lesson

| Field | Value |
| --- | --- |
| Date | 2026-07-19 |
| Lane | side-question |
| Task class | independent destination contract re-review |
| Repository / packet identity | Devad Content Agent destination packet bd89df54/a1753998 |
| Model / effort requested | gpt-5.6-sol / xhigh |
| Model / effort attested | gpt-5.6-sol / xhigh by dispatch configuration; runtime token telemetry unavailable |
| Main-agent profile | Sol manager |
| Why this tier was selected | Remote mutation ambiguity, quota settlement, and closed receipt schemas are high-risk contract work. |
| Scope and forbidden actions | Read-only exact packet; no product, Git, provider, database, browser, Sheet, or deploy mutation. |
| First-pass result | FAIL |
| Independent proof | Found actual-503 replay contradiction, false-success representability, incomplete asset schema, quota-period gaps, missing no-side-effect path, lease contradiction, receipt-idempotency gap, and stale typed DDL. |
| Retries / compactions | Independent re-review after prior correction. |
| Wall time | Unknown |
| Token telemetry | unavailable |
| Approx. new-token volume | Unknown |
| Safety or truth errors | none |
| Ranking action | keep |

## Result

- Evidence and concise outcome: The contract remained fail-closed at the dependency gate, but its local receipt, success, quota, and schema invariants were not yet acceptance-ready.
- Best use case learned: For remote destinations, model every actual HTTP response as potentially sent and make success/quota settlement impossible without authoritative proof.
- Next profile to try, if any: Same tier for a narrow hash-bound final review.
