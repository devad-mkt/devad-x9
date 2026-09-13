# Subagent Lesson

| Field | Value |
| --- | --- |
| Date | 2026-07-20 |
| Lane | main |
| Task class | Exact staged-diff correctness and evidence review |
| Repository / packet identity | `$DEVAD_ROOT/content-agent-rephrase-c5c2`, C5C2 exact 13-file C1 stage at base `a1b0b3e31ad341b2f160292deaca05d888db83cd` |
| Model / effort requested | `gpt-5.6-sol` / xhigh |
| Model / effort attested | `gpt-5.6-sol` / xhigh |
| Main-agent profile | SOL max manager with bounded independent review |
| Why this tier was selected | Spend/replay and receipt-lineage code required a high-confidence independent pass while the main agent ran deterministic gates. |
| Scope and forbidden actions | Read-only staged bytes; no edits, Git mutation, providers, network, database, merge, or deployment |
| First-pass result | FAIL |
| Independent proof | Reproduced inert proof INI, enumerated 266 tests, reran provider-disabled suite, PHP syntax, Composer, diff check, and exact staged security hook |
| Retries / compactions | One narrow re-review after evidence-only correction; no product-code retry |
| Wall time | Partial telemetry; several bounded waits, under one task turn plus one re-review |
| Token telemetry | unavailable |
| Approx. new-token volume | `Unknown` |
| Safety or truth errors | Caught an unusable checkout proof INI and stale staged-evidence wording; no product defect found |
| Ranking action | keep |

## Result

- Evidence and concise outcome: First pass returned `REVISE_BEFORE_C1`; the manager repaired only the two evidence files, refreshed the authorization, reran all gates, and the same reviewer returned `PASS` with `BLOCKS_C1: no`.
- Best use case learned: SOL xhigh is valuable for exact pre-commit review of spend-critical code plus proof packets, especially when told to inspect evidence accuracy as well as product behavior.
- Next profile to try, if any: Keep SOL xhigh for spend/security/tenancy gates; use SOL high for ordinary evidence-only rechecks when no behavior byte changes.

Do not record secrets, cookies, raw provider output, or full sensitive prompts.
