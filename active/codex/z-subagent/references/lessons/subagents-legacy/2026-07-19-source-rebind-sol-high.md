# Subagent Lesson

| Field | Value |
| --- | --- |
| Date | 2026-07-19 |
| Lane | side-question |
| Task class | source-contract authority rebind |
| Repository / packet identity | `$DEVAD_ROOT/1-core-x9` at C5B C2 `d547d3bf9d28604825871adf9ae13732bb4d1560`; three historical source-resolution artifacts hash-bound in the report |
| Model / effort requested | SOL high |
| Model / effort attested | request accepted; runtime telemetry not exposed |
| Main-agent profile | unavailable |
| Why this tier was selected | Cross-file contract comparison needed judgment but no mutation or architecture decision. |
| Scope and forbidden actions | Read-only; no edits, Git mutation, database, provider, browser, network, deployment, or implementation. |
| First-pass result | PASS |
| Independent proof | Root separately verified the C5B/integration checkout tips and inspected current stage/source interfaces. |
| Retries / compactions | 0 retries |
| Wall time | unavailable |
| Token telemetry | unavailable |
| Approx. new-token volume | `Unknown` |
| Safety or truth errors | none identified |
| Ranking action | keep |

## Result

- Evidence and concise outcome: The bounded reader found stale C5B identities, preserved the non-recursive sitemap authority, and located UTM equivalence in future C6 semantic comparison rather than ingestion dedupe.
- Best use case learned: SOL high is suitable for a hash-bound, read-only rebind spanning current source and a small historical contract packet.
- Next profile to try, if any: SOL medium for a purely mechanical hash refresh; keep SOL high when contract conflicts must be adjudicated.

