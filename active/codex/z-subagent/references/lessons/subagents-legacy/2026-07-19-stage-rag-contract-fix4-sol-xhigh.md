# Subagent Lesson

| Field | Value |
| --- | --- |
| Date | 2026-07-19 |
| Lane | main |
| Task class | narrow stage/RAG contract collision fix |
| Repository / packet identity | Devad Content Agent stage/RAG packet; accepted base 4a06bb09 |
| Model / effort requested | gpt-5.6-sol / xhigh |
| Model / effort attested | gpt-5.6-sol / xhigh by dispatch configuration; runtime token telemetry unavailable |
| Main-agent profile | Sol manager |
| Why this tier was selected | Named unique-index collision recovery and vector-memory scope isolation are subtle persistence concerns. |
| Scope and forbidden actions | Same three contract files only; no product code or external mutations. |
| First-pass result | PASS |
| Independent proof | Multi-parser validation and a named registry covering 46 failure sources, eight paths, and 11 unique/index vectors reported green; re-review pending. |
| Retries / compactions | One narrow fix wave. |
| Wall time | Unknown |
| Token telemetry | unavailable |
| Approx. new-token volume | Unknown |
| Safety or truth errors | none |
| Ranking action | keep |

## Result

- Evidence and concise outcome: Added a separate terminal-receipt authority that cannot re-hit stage-receipt uniques and made content/retrieval uniqueness snapshot-aware while preserving DiskANN.
- Best use case learned: Model database collision recovery as a distinct durable authority when the primary ledger itself may be the failed constraint.
- Next profile to try, if any: Same reviewer for exact narrow re-review.
