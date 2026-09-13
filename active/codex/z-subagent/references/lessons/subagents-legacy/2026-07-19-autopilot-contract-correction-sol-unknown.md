# Subagent Lesson

| Field | Value |
| --- | --- |
| Date | 2026-07-19 |
| Lane | side-question |
| Task class | bounded implementation-contract correction |
| Repository / packet identity | Devad Content Agent Autopilot/UI/API/MCP contract at base 4a06bb09 |
| Model / effort requested | Sol contract author; exact effort unavailable in current telemetry |
| Model / effort attested | Unknown |
| Main-agent profile | Sol manager |
| Why this tier was selected | Lifecycle CAS, scheduler, settings, workspace-key, UI, and dependency gates span several trust boundaries. |
| Scope and forbidden actions | Two exact contract files only; no product code, Git staging, browser, provider, database, or deployment action. |
| First-pass result | PASS |
| Independent proof | Two strict JSON parsers, semantic assertions, hash readback, UTF-8, secret, whitespace, and scoped-diff checks passed. |
| Retries / compactions | One design approval followed by one bounded correction pass. |
| Wall time | Unknown |
| Token telemetry | unavailable |
| Approx. new-token volume | Unknown |
| Safety or truth errors | none |
| Ranking action | keep |

## Result

- Evidence and concise outcome: Produced corrected Markdown and machine-readable runtime contracts with split dependency gates, repeated-generation CAS, preview/end invariants, exhaustive setting classification, and adapter parity.
- Best use case learned: A bounded contract author is effective when the manager freezes contested lifecycle decisions before edits.
- Next profile to try, if any: Use a fresh skeptical reviewer at the same or higher tier before implementation.
