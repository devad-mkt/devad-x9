# Subagent Lesson

| Field | Value |
| --- | --- |
| Date | 2026-07-19 |
| Lane | main |
| Task class | Independent targeted contract re-review |
| Repository / packet identity | Devad Content Agent C5B supplement `8b12f702...` / `bef27b12...` |
| Model / effort requested | SOL xhigh |
| Model / effort attested | Unknown; runtime telemetry did not attest the profile |
| Main-agent profile | SOL max |
| Why this tier was selected | Provider-spend lineage and queue exhaustion are high-cost correctness boundaries |
| Scope and forbidden actions | Read only two exact contract files; no edits, Git, tests, runtime, or external calls |
| First-pass result | FAIL |
| Independent proof | Exact hashes matched and 64 internal references resolved; one lineage omission remained |
| Retries / compactions | Targeted re-review after one correction pass |
| Wall time | Unknown |
| Token telemetry | unavailable |
| Approx. new-token volume | `Unknown` |
| Safety or truth errors | No mutation; review correctly kept implementation disabled |
| Ranking action | keep |

## Result

- Evidence and concise outcome: The reviewer closed per-stage run ownership and exhaustion behavior but found that spend gates rechecked only the memory-scope hash, not its independent type/key, and did not explicitly recheck the root run's same-workspace tool/non-stage/non-provider shape.
- Best use case learned: Independent rereview remains valuable even after mechanically complete cross-file validation because hash equality alone does not prove all immutable lineage dimensions are rebound at the spend boundary.
- Next profile to try, if any: Reuse SOL xhigh for one exact correction and final targeted pass.

Do not record secrets, cookies, raw provider output, or full sensitive prompts.
