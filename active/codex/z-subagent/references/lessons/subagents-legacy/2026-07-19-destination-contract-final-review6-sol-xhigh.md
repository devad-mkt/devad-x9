# Subagent Lesson

| Field | Value |
| --- | --- |
| Date | 2026-07-19 |
| Lane | side-question |
| Task class | final destination contract acceptance review |
| Repository / packet identity | Devad Content Agent destination 33c08807/8d4715be |
| Model / effort requested | gpt-5.6-sol / xhigh |
| Model / effort attested | gpt-5.6-sol / xhigh by dispatch configuration; runtime token telemetry unavailable |
| Main-agent profile | Sol manager |
| Why this tier was selected | Cross-contract accepted-output hashes, remote success proofs, reconciliation identity, period accounting, and enforcement layers are high risk. |
| Scope and forbidden actions | Read-only exact destination packet plus adjacent Stage/RAG contract. |
| First-pass result | FAIL |
| Independent proof | Found six literal blockers after prior eight findings were closed; verified prior corrections and null writer gate. |
| Retries / compactions | Final pass after destination correction. |
| Wall time | Unknown |
| Token telemetry | unavailable |
| Approx. new-token volume | Unknown |
| Safety or truth errors | none |
| Ranking action | keep |

## Result

- Evidence and concise outcome: Found accepted-output hash/receipt drift, caller-controlled false success, key-reuse bypass, stale-period accounting gap, metadata-limit mismatch, and mixed DB/application enforcement claims.
- Best use case learned: Destination contracts must be reviewed against the accepted output writer contract, not in isolation.
- Next profile to try, if any: Same narrow fixer, then independent final review.
