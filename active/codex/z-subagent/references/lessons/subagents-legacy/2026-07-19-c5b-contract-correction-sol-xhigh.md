# Subagent Lesson

| Field | Value |
| --- | --- |
| Date | 2026-07-19 |
| Lane | main |
| Task class | Contract correction after independent review |
| Repository / packet identity | Devad Content Agent C5B supplemental executor contract; hashes `8b12f702...` and `bef27b12...` |
| Model / effort requested | SOL xhigh |
| Model / effort attested | Unknown; runtime telemetry did not attest the profile |
| Main-agent profile | SOL max |
| Why this tier was selected | Cross-cutting queue, idempotency, spend, and crash-boundary contract safety |
| Scope and forbidden actions | Edit exactly two supplemental contract files; no product code, Git mutation, runtime, provider, or external action |
| First-pass result | PASS |
| Independent proof | Pending targeted independent re-review; local JSON/internal-reference/cross-file/hash checks passed |
| Retries / compactions | One correction pass after three precise review findings |
| Wall time | Unknown |
| Token telemetry | unavailable |
| Approx. new-token volume | `Unknown` |
| Safety or truth errors | none reported; C5A remains UNBOUND and implementation remains disabled |
| Ranking action | keep |

## Result

- Evidence and concise outcome: The correction froze per-stage `ai_run` ownership/replay, immutable pre-send lineage revalidation, and safe `failed(Throwable)` exhaustion behavior. Parent hashes stayed unchanged, JSON/internal references passed, and no implementation action occurred.
- Best use case learned: SOL xhigh is appropriate for narrow contract corrections where queue redelivery and provider-spend semantics can create silent duplicate cost or false terminal state.
- Next profile to try, if any: Use an independent SOL xhigh targeted reviewer on the two exact new hashes before acceptance.

Do not record secrets, cookies, raw provider output, or full sensitive prompts.
