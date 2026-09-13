# Subagent Lesson

| Field | Value |
| --- | --- |
| Date | 2026-07-19 |
| Lane | main |
| Task class | Bounded staged-review correction implementation |
| Repository / packet identity | `$DEVAD_ROOT\1-core-x9`; C5A revision 2, 36 staged paths |
| Model / effort requested | SOL xhigh |
| Model / effort attested | Unknown; runtime telemetry did not attest the profile |
| Main-agent profile | SOL max |
| Why this tier was selected | Migration rollback, tenant FKs, secret serialization, typed SQLSTATE and append-only bypasses |
| Scope and forbidden actions | Six exact findings only; preserve contracts/W1B; no commit, push, runtime, provider, or deploy |
| First-pass result | PASS |
| Independent proof | Corrected staged rereview pending |
| Retries / compactions | One bounded correction cycle with explicit RED/GREEN vectors |
| Wall time | Unknown |
| Token telemetry | unavailable |
| Approx. new-token volume | `Unknown` |
| Safety or truth errors | none reported; external PostgreSQL and full repo correctly remain UNKNOWN |
| Ranking action | keep |

## Result

- Evidence and concise outcome: All six findings received explicit tests and fixes. Focused tests passed 516 assertions, AI-wide tests 3,628 assertions, and final security pre-commit passed all 36 staged paths.
- Best use case learned: Returning precise file/line blockers to the same sole writer preserves context and produces fast, bounded correction without expanding the branch.
- Next profile to try, if any: Independent SOL xhigh rereview of revision 2 before C1 approval.

Do not record secrets, cookies, raw provider output, or full sensitive prompts.
