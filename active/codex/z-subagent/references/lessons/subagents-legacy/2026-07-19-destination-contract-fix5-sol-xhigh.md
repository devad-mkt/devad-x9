# Subagent Lesson

| Field | Value |
| --- | --- |
| Date | 2026-07-19 |
| Lane | production-support |
| Task class | destination contract correction |
| Repository / packet identity | Devad Content Agent destination 33c08807/8d4715be |
| Model / effort requested | gpt-5.6-sol / xhigh |
| Model / effort attested | gpt-5.6-sol / xhigh by dispatch configuration; runtime token telemetry unavailable |
| Main-agent profile | Sol manager |
| Why this tier was selected | Remote mutation, receipts, quota periods, and authoritative success are high-risk state-machine work. |
| Scope and forbidden actions | Two exact contract files only; no product, Git, provider, database, browser, Sheet, or deploy mutation. |
| First-pass result | PASS |
| Independent proof | JSON parsing, closed adapter union, closed asset schema, typed destination DDL, 18-row quota matrix, transition parity, and uniqueness checks passed. |
| Retries / compactions | Corrected filename handoff once; no content retry. |
| Wall time | Unknown |
| Token telemetry | unavailable |
| Approx. new-token volume | Unknown |
| Safety or truth errors | Initial manager filename mismatch was caught at the hash gate; no mutation occurred before correction. |
| Ranking action | keep |

## Result

- Evidence and concise outcome: Closed false-success, actual-HTTP replay, asset typing, quota terminal/period, lease expiry, reconciliation idempotency, and typed DDL gaps while keeping provider/runtime proof UNKNOWN.
- Best use case learned: Immutable hashes let a worker reject a bad filename safely and resume on the exact matching artifact.
- Next profile to try, if any: Independent Sol xhigh final reviewer.
