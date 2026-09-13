# Subagent Lesson

| Field | Value |
| --- | --- |
| Date | 2026-07-21 |
| Lane | side-question |
| Task class | stable changed-boundary review |
| Repository / packet identity | `worker/content-agent-provider-outcomes-r0-20260721` from `7052e408` |
| Model / effort requested | inherited default |
| Model / effort attested | unavailable |
| Main-agent profile | Codex primary agent |
| Why this tier was selected | Independent read-only verification of a provider retry and receipt boundary. |
| Scope and forbidden actions | Changed provider-outcome files only; no edits, provider calls, secrets, or architecture expansion. |
| First-pass result | PASS |
| Independent proof | Focused provider-disabled suite passed 869 assertions; main agent also checked syntax, formatting, and diff integrity. |
| Retries / compactions | none |
| Wall time | unavailable |
| Token telemetry | unavailable |
| Approx. new-token volume | `Unknown` |
| Safety or truth errors | none |
| Ranking action | keep |

## Result

- Evidence and concise outcome: Confirmed marker authority, workspace revalidation, ambiguous no-resend behavior, terminal-state protection, and preserved non-Content-Agent retry behavior.
- Best use case learned: One final stable-diff review after TDD and before repository security gates.
- Next profile to try, if any: Keep the inherited/default reviewer for similarly bounded diffs.
