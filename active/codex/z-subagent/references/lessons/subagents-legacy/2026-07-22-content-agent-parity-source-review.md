# Subagent Lesson

| Field | Value |
| --- | --- |
| Date | 2026-07-22 |
| Lane | side-question |
| Task class | Existing-source map and stable-diff review |
| Repository / packet identity | `integration/ai-workflow-r0-20260721@41f64c4a` |
| Model / effort requested | inherited |
| Model / effort attested | Unknown |
| Main-agent profile | Smooth Coding implementer |
| Why this tier was selected | Narrow read-only mapping and one independent changed-risk review |
| Scope and forbidden actions | Parity CLI/comparator/validator only; no edits, providers, deploy, or production actions |
| First-pass result | PASS |
| Independent proof | Main agent reproduced the missing/type-coercion failures, fixed them, and passed 684 focused assertions |
| Retries / compactions | One bounded correction review |
| Wall time | Unknown |
| Token telemetry | unavailable |
| Approx. new-token volume | `Unknown` |
| Safety or truth errors | none |
| Ranking action | keep |

## Result

- Evidence and concise outcome: the mapper found the existing validator bypass and unsafe default; the reviewer then caught malformed boolean coercion and raw error-path output before C1. The corrected five-file diff received PASS.
- Best use case learned: use one read-only source mapper before editing and reuse that same agent once for the stable changed-risk review.
- Next profile to try, if any: same bounded profile.
