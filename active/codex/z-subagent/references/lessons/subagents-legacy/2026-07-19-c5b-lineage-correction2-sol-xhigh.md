# Subagent Lesson

| Field | Value |
| --- | --- |
| Date | 2026-07-19 |
| Lane | main |
| Task class | Spend-boundary lineage contract correction |
| Repository / packet identity | Devad Content Agent C5B supplement `9e897c47...` / `1ef9f556...` |
| Model / effort requested | SOL xhigh |
| Model / effort attested | Unknown; runtime telemetry did not attest the profile |
| Main-agent profile | SOL max |
| Why this tier was selected | Immutable memory/root-run lineage directly controls provider-spend safety |
| Scope and forbidden actions | Edit only two contract files; no product, Git, runtime, or external action |
| First-pass result | PASS |
| Independent proof | Pending final targeted re-review |
| Retries / compactions | Second narrow correction after independent rereview |
| Wall time | Unknown |
| Token telemetry | unavailable |
| Approx. new-token volume | `Unknown` |
| Safety or truth errors | none reported; implementation remains disabled and C5A remains unbound |
| Ranking action | keep |

## Result

- Evidence and concise outcome: Both locked provider gates now independently compare memory scope type/key/hash and the exact same-workspace `content_agent_blog` root-run shape, ID, and idempotency hash. Drift tests mutate each field independently.
- Best use case learned: Treat composite lineage as separate immutable dimensions; a snapshot hash must not replace explicit type/key/root-shape checks at the final spend boundary.
- Next profile to try, if any: One final independent SOL xhigh hash-bound review.

Do not record secrets, cookies, raw provider output, or full sensitive prompts.
