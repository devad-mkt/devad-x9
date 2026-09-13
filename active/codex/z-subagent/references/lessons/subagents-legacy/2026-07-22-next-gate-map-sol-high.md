# Subagent Lesson

| Field | Value |
| --- | --- |
| Date | 2026-07-22 |
| Lane | side-question |
| Task class | next delivery-gate mapping |
| Repository / packet identity | `D:\\CDx9\\0-cdx-wt\\wfi\\4-core-ai-r0` at `5fa202f802d455655c16534601ddefcdb21d7b39` |
| Model / effort requested | GPT-5.6 SOL / high |
| Model / effort attested | unavailable |
| Main-agent profile | unavailable |
| Why this tier was selected | The map had to distinguish completed code from browser, PostgreSQL, n8n, destination, and release proof without inventing another implementation slice. |
| Scope and forbidden actions | Read current plan/source/tests only; no edits, external calls, browser actions, providers, n8n, Sheets, PostgreSQL, workers, schedulers, or deployment. |
| First-pass result | PASS |
| Independent proof | Main agent executed the proposed current-head lifecycle check: Pause generation 4, close the tab, reopen in a fresh isolated browser context, confirm Paused generation 4, Resume, reload, and confirm Active generation 4 with zero provider calls, publish attempts, or work items. |
| Retries / compactions | none observed |
| Wall time | unavailable |
| Token telemetry | unavailable |
| Approx. new-token volume | Unknown |
| Safety or truth errors | none |
| Ranking action | keep |

## Result

- Evidence and concise outcome: The helper found the one remaining provider-disabled local acceptance item: lifecycle state persistence across browser closure. It correctly classified all later material gates as external.
- Best use case learned: Use SOL high for a bounded next-gate decision when the main agent needs to avoid both premature stopping and speculative code.
- Next profile to try, if any: Terra high for a smaller single-surface next-proof map; retain SOL high when several external gates must be separated safely.

