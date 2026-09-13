# Subagent Lesson

| Field | Value |
| --- | --- |
| Date | 2026-07-22 |
| Lane | side-question |
| Task class | release-tooling source map |
| Repository / packet identity | `D:\\CDx9\\0-cdx-wt\\wfi\\4-core-ai-r0` at `d8e466d9b76231f2b8b018a4249f55d8a51ae972` |
| Model / effort requested | GPT-5.6 SOL / medium |
| Model / effort attested | unavailable |
| Main-agent profile | unavailable |
| Why this tier was selected | Exact path, blob, and history extraction was bounded and read-only. |
| Scope and forbidden actions | Inspect the pre-push script and targeted refs only; no edits, fetch, branch changes, commits, or pushes. |
| First-pass result | PASS |
| Independent proof | Main agent confirmed the same script blob on integration and main, the global `format:check` call, and the absence of a known fix in targeted history. |
| Retries / compactions | none observed |
| Wall time | unavailable |
| Token telemetry | unavailable |
| Approx. new-token volume | Unknown |
| Safety or truth errors | none |
| Ranking action | keep |

## Result

- Evidence and concise outcome: The helper proved that the inherited pre-push formatter defect had no existing approved fix to cherry-pick.
- Best use case learned: Use SOL medium for bounded Git/path/source ownership checks before creating a new fix.
- Next profile to try, if any: none.
