# Subagent Lesson

| Field | Value |
| --- | --- |
| Date | 2026-07-19 |
| Lane | production-support |
| Task class | narrow Stage/RAG contract correction |
| Repository / packet identity | Devad Content Agent stage/RAG packet 7f667a51/9be1d576/c59f8885 |
| Model / effort requested | gpt-5.6-sol / xhigh |
| Model / effort attested | inherited Sol worker; runtime token telemetry unavailable |
| Main-agent profile | Sol manager |
| Why this tier was selected | Terminal crash replay and database-versus-application invariant boundaries are high-risk persistence design. |
| Scope and forbidden actions | Three exact contract files only; no product, Git, provider, database, browser, Sheet, or external mutation. |
| First-pass result | PASS |
| Independent proof | JSON parsed in PowerShell, Node, and PHP; classification, uniqueness, replay, atomicity, hygiene, and stable-hash checks passed. |
| Retries / compactions | Follow-up after independent REVISE. |
| Wall time | Unknown |
| Token telemetry | unavailable |
| Approx. new-token volume | Unknown |
| Safety or truth errors | none |
| Ranking action | keep |

## Result

- Evidence and concise outcome: Added exact post-commit replay acknowledgement, separated feasible database checks from application canonical-hash enforcement, and classified the omitted item-status CHECK.
- Best use case learned: Reuse a prior contract fixer for tight corrections when the reviewer provides exact counterexamples and named invariants.
- Next profile to try, if any: Independent Sol xhigh final reviewer before implementation.
