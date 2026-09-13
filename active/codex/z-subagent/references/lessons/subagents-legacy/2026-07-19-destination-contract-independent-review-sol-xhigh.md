# Subagent Lesson

| Field | Value |
| --- | --- |
| Date | 2026-07-19 |
| Lane | side-question |
| Task class | independent destination-contract review |
| Repository / packet identity | Devad Content Agent destination contract; accepted code base 4a06bb09 |
| Model / effort requested | gpt-5.6-sol / xhigh |
| Model / effort attested | gpt-5.6-sol / xhigh by dispatch configuration; runtime token telemetry unavailable |
| Main-agent profile | Sol manager |
| Why this tier was selected | Provider replay, append-only authority, lineage, quota, tenancy, SSRF, and credential boundaries are high-risk. |
| Scope and forbidden actions | Two exact destination contract files plus read-only accepted schema; no edits, Git mutation, provider, database, browser, Sheet, or deploy. |
| First-pass result | FAIL |
| Independent proof | Exact accepted checkout 4a06bb09 and fixed contract bytes were inspected; ranked literal schema/state contradictions were returned. |
| Retries / compactions | One path-authority correction from historical repo to accepted integration checkout. |
| Wall time | Unknown |
| Token telemetry | unavailable |
| Approx. new-token volume | Unknown |
| Safety or truth errors | none; reviewer also caught a manager-supplied 63-character expected hash typo |
| Ranking action | keep |

## Result

- Evidence and concise outcome: Found under-bound accepted-output lineage, unfrozen column constraints, forkable receipt authority, incomplete execution/quota semantics, circular publication projection, infeasible account-version/secret snapshot rules, unsafe real-503 retry semantics, target-schema drift, and declarative-only asset immutability.
- Best use case learned: Use xhigh independent review before any external-mutation adapter implementation; it prevented unsafe automatic replay and ambiguous quota accounting.
- Next profile to try, if any: Keep xhigh for the exact post-correction acceptance pass.
