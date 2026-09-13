# Subagent Lesson

| Field | Value |
| --- | --- |
| Date | 2026-07-19 |
| Lane | main |
| Task class | Laravel append-only base-builder correction |
| Repository / packet identity | C5A revision 3, 37 staged paths at `4a06bb09...` |
| Model / effort requested | SOL xhigh |
| Model / effort attested | Unknown |
| Main-agent profile | SOL max |
| Why this tier was selected | Complete framework mutation-surface hardening for terminal authority |
| Scope and forbidden actions | One guarded query builder, model wiring, bypass tests and proof docs; no commit/push/runtime external |
| First-pass result | PASS |
| Independent proof | Final revision-3 rereview pending |
| Retries / compactions | One narrow correction cycle after framework-source review |
| Wall time | Unknown |
| Token telemetry | unavailable |
| Approx. new-token volume | `Unknown` |
| Safety or truth errors | none; full repository and live PostgreSQL remain UNKNOWN |
| Ranking action | keep |

## Result

- Evidence and concise outcome: A dedicated model-specific base query builder now rejects all ten update/removal mutators. Twenty-one datasets passed 126 assertions; focused tests passed 642 assertions and the AI-wide set passed 3,754 assertions. Final security pre-commit passed 37 staged paths.
- Best use case learned: A guarded base query builder is safer than enumerating only Eloquent-level methods because model-derived base access and forwarded methods share one enforcement point.
- Next profile to try, if any: Final independent SOL xhigh source/test rereview, then C1/C2 if PASS.

Do not record secrets, cookies, raw provider output, or full sensitive prompts.
