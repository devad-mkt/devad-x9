# Subagent Lesson

| Field | Value |
| --- | --- |
| Date | 2026-07-19 |
| Lane | main |
| Task class | Autopilot/UI/API/MCP contract correction |
| Repository / packet identity | Devad Content Agent Autopilot packet; accepted base 4a06bb09 |
| Model / effort requested | gpt-5.6-sol / xhigh |
| Model / effort attested | gpt-5.6-sol / xhigh by dispatch configuration; runtime token telemetry unavailable |
| Main-agent profile | Sol manager |
| Why this tier was selected | Live spend, credits, lifecycle, scheduler concurrency, settings, tenancy, and adapter parity span multiple authorities. |
| Scope and forbidden actions | Two exact contract files; no product code, Git, provider, database, browser, Sheet, or deploy. |
| First-pass result | PASS |
| Independent proof | Dual parser, source consistency, states/reasons/settings/persistence catalogs, UTF-8, secret and scoped-status checks reported green; fresh review still required. |
| Retries / compactions | One correction pass after independent REVISE. |
| Wall time | Unknown |
| Token telemetry | unavailable |
| Approx. new-token volume | Unknown |
| Safety or truth errors | none |
| Ranking action | keep |

## Result

- Evidence and concise outcome: Added fail-closed dependency bytes, dedicated spend scope and credit reservation, literal one-row contract, composite tenant persistence, generation lease, per-generation item hash, non-mutating entitlement reads, consistent lifecycle projections, and closed settings/timezone validation.
- Best use case learned: Freeze money and concurrency authority in machine-readable contracts before UI or scheduler code begins.
- Next profile to try, if any: Fresh xhigh independent acceptance review.
