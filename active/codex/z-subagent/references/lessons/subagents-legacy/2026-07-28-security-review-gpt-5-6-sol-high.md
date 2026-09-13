# Subagent Lesson

| Field | Value |
| --- | --- |
| Date | 2026-07-28 |
| Lane | side-question |
| Task class | Critical security, tenancy, money, and idempotency diff review |
| Repository / packet identity | core-x9 c50cafb3 accepted-delivery claim bridge |
| Model / effort requested | gpt-5.6-sol / high |
| Model / effort attested | unavailable |
| Main-agent profile | gpt-5.6-sol |
| Why this tier was selected | Provider spend, tenant isolation, migration, and crash-retry correctness required a critical reviewer; Spark was excluded as final authority. |
| Scope and forbidden actions | Thirteen named source, migration, test, and security files; read-only; no providers, deployment, secrets, edits, or child agents. |
| First-pass result | FAIL - useful but incomplete; the bounded follow-up found two additional P1 issues |
| Independent proof | Main agent reproduced all six source findings and added focused regression tests before accepting the corrections. |
| Retries / compactions | one focused follow-up / none |
| Wall time | unavailable |
| Token telemetry | unavailable |
| Approx. new-token volume | Unknown |
| Safety or truth errors | none |
| Ranking action | keep |

## Result

- Evidence and concise outcome: The first pass returned four actionable issues:
  spend authority was not revalidated under lock, media used text pricing,
  caption provider identity came from mutable settings, and media rows could
  commit before claim confirmation. The follow-up caught two more: the final
  dispatch point needed another authority lock, and empty frozen media models
  could select a mutable fallback. All six were source-verifiable and changed
  the implementation.
- Best use case learned: Sol high produces strong actionable findings for a
  frozen critical backend diff, but one correction-focused follow-up is still
  valuable when concurrency, money, and tenant boundaries interact.
- Next profile to try, if any: Use Spark xhigh only as a non-authoritative
  shadow challenger on a future comparable frozen packet; keep Sol high as the
  accepted critical verdict until at least five comparable runs exist.
