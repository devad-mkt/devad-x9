# Subagent Lesson

| Field | Value |
| --- | --- |
| Date | 2026-07-18 |
| Task class | Exact extraction, file inventory, route/source map |
| Repository / packet identity | `$CODEX_HOME\memories` Phase 2 workspace diff |
| Model / effort requested | gpt-5.6-sol / medium |
| Model / effort attested | Unavailable; task was interrupted before returning a packet |
| Main-agent profile | GPT-5.6 Codex |
| Why this tier was selected | Read-only evidence map independent of handbook edits |
| Scope and forbidden actions | Inspect diff/raw/rollout evidence only; no edits |
| First-pass result | UNKNOWN |
| Independent proof | Main-agent reference audit completed separately: all added rollouts were represented and all handbook references resolved |
| Retries / compactions | One follow-up request, then interruption after no response |
| Wall time | Under 1 minute |
| Token telemetry | unavailable |
| Approx. new-token volume | `Unknown` |
| Safety or truth errors | none observed; no result was adopted |
| Ranking action | keep experimental; no telemetry or result quality to evaluate |

## Result

- Evidence and concise outcome: The delegated read-only audit did not return before the bounded consolidation completed; its claims were not used.
- Best use case learned: Use a tighter stop bound for memory-diff source maps when the main agent can deterministically audit references.
- Next profile to try, if any: SOL medium with a smaller, explicitly enumerated file packet.
