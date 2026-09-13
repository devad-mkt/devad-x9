# Subagent Lesson

| Field | Value |
| --- | --- |
| Date | 2026-07-19 |
| Lane | side-question |
| Task class | independent Autopilot/UI/API/MCP contract review |
| Repository / packet identity | Devad Content Agent Autopilot contract; accepted code base 4a06bb09 |
| Model / effort requested | gpt-5.6-sol / xhigh |
| Model / effort attested | gpt-5.6-sol / xhigh by dispatch configuration; runtime token telemetry unavailable |
| Main-agent profile | Sol manager |
| Why this tier was selected | Lifecycle, live spend, credit, scheduler concurrency, tenancy, settings, and adapter parity are cross-cutting. |
| Scope and forbidden actions | Two exact contracts plus read-only accepted code and dependency hashes; no edits or external mutations. |
| First-pass result | FAIL |
| Independent proof | Rebound from historical contract checkout to clean exact integration SHA 4a06bb09; nine literal feasibility gaps returned. |
| Retries / compactions | One source-authority path correction. |
| Wall time | Unknown |
| Token telemetry | unavailable |
| Approx. new-token volume | Unknown |
| Safety or truth errors | none |
| Ranking action | keep |

## Result

- Evidence and concise outcome: Found incomplete destination byte binding, unsafe reuse of read-only credit scope, underspecified one-row spend, scalar tenant FKs, no generation-wide lease, missing generation idempotency material, mutating entitlement reads, state/reason drift, and incomplete settings/timezone validation.
- Best use case learned: Xhigh review against exact accepted code catches contract assumptions that internal JSON consistency checks cannot.
- Next profile to try, if any: Keep xhigh for the post-correction acceptance pass.
