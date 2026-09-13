# Subagent Lesson

| Field | Value |
| --- | --- |
| Date | 2026-07-19 |
| Lane | side-question |
| Task class | independent Autopilot contract re-review |
| Repository / packet identity | Devad Content Agent Autopilot packet 3614788c/7acbfcd6 |
| Model / effort requested | gpt-5.6-sol / xhigh |
| Model / effort attested | gpt-5.6-sol / xhigh by dispatch configuration; runtime token telemetry unavailable |
| Main-agent profile | Sol manager |
| Why this tier was selected | Lifecycle, spend authorization, generation concurrency, and read-only API guarantees require cross-layer reasoning. |
| Scope and forbidden actions | Read-only exact packet; no product, Git, provider, database, browser, Sheet, or deploy mutation. |
| First-pass result | FAIL |
| Independent proof | Found generation lease stranding, destination coupling, generation FK gaps, manual receipt mismatch, wildcard spend bypass, read-only write paths, projection escape, CLI/MCP schema gaps, principal binding gap, and cadence ambiguity. |
| Retries / compactions | Independent re-review after prior correction. |
| Wall time | Unknown |
| Token telemetry | unavailable |
| Approx. new-token volume | Unknown |
| Safety or truth errors | none |
| Ranking action | keep |

## Result

- Evidence and concise outcome: The split dependency gates were correctly fail-closed, but the local runtime contract still permitted stranded generations and authorization/read-only inconsistencies.
- Best use case learned: Wildcard API keys must not imply future spend authority, and read-only endpoints need non-recording auth plus non-mutating feature lookup.
- Next profile to try, if any: Same tier for a narrow hash-bound final review.
