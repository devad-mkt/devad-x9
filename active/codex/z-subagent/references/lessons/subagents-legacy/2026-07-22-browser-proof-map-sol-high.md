# Subagent Lesson

| Field | Value |
| --- | --- |
| Date | 2026-07-22 |
| Lane | side-question |
| Task class | browser-proof source mapping |
| Repository / packet identity | `D:\\CDx9\\0-cdx-wt\\wfi\\4-core-ai-r0` at `5fa202f802d455655c16534601ddefcdb21d7b39` |
| Model / effort requested | GPT-5.6 SOL / high |
| Model / effort attested | unavailable |
| Main-agent profile | unavailable |
| Why this tier was selected | The proof crossed UI state, lifecycle transitions, queue behavior, and provider-spend safety, while the helper remained read-only. |
| Scope and forbidden actions | Map the existing `needs_review -> end -> fresh start` seam and exact proof steps; no edits, UI actions, provider calls, queue worker, scheduler, or external writes. |
| First-pass result | PASS |
| Independent proof | Main agent executed the mapped path only on the disposable SQLite fixture and confirmed generation 3 `source_fetch_failed -> needs_review -> complete`, generation 4 `active`, zero provider calls, zero publish attempts, zero work items, localhost-only requests, and no console errors. |
| Retries / compactions | none observed |
| Wall time | unavailable |
| Token telemetry | unavailable |
| Approx. new-token volume | Unknown |
| Safety or truth errors | The helper's final database snapshot preceded the main agent's controlled fixture transition, but it clearly labeled it as a snapshot and supplied the correct next steps. |
| Ranking action | keep |

## Result

- Evidence and concise outcome: The helper found the existing `AiBlogAutomationSourceMaterializer::markFailed` seam and the exact HTTP test, avoiding new code or a duplicate test-only lifecycle path.
- Best use case learned: Use SOL high for bounded cross-layer source mapping when the main agent can independently execute the mutation and browser proof.
- Next profile to try, if any: Terra high for a similarly narrow single-module map; retain SOL high when lifecycle, queue, and security boundaries intersect.

