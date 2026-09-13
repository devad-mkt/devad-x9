# Subagent Lesson

| Field | Value |
| --- | --- |
| Date | 2026-07-19 |
| Lane | side-question |
| Task class | bounded destination-receipt contract correction |
| Repository / packet identity | Devad Content Agent destination contract at base 4a06bb09 |
| Model / effort requested | Sol contract author; exact effort unavailable in current telemetry |
| Model / effort attested | Unknown |
| Main-agent profile | Sol manager |
| Why this tier was selected | Provider ambiguity, approval, quota, append-only receipts, SSRF, and tenant FKs are high-risk cross-cutting concerns. |
| Scope and forbidden actions | Two exact contract files only; no product code, provider, browser, database, Git staging, or deployment action. |
| First-pass result | PASS |
| Independent proof | Dual JSON parsing, closed-transition checks, cross-artifact invariants, secret/placeholder/whitespace scans, and scoped diff checks passed. |
| Retries / compactions | One design approval followed by one bounded correction pass. |
| Wall time | Unknown |
| Token telemetry | unavailable |
| Approx. new-token volume | Unknown |
| Safety or truth errors | none |
| Ranking action | keep |

## Result

- Evidence and concise outcome: Produced a default-off destination runtime contract with accepted-output dependency, append-only receipts, exact ambiguity handling, approval/quota ledgers, WordPress draft-only transport, and an empty social allowlist.
- Best use case learned: Freeze provider ambiguity and replay semantics in a machine contract before any adapter implementation.
- Next profile to try, if any: Use a fresh independent reviewer before accepting the contract or assigning destination code.
