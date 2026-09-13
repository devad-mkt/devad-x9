# Subagent Lesson

| Field | Value |
| --- | --- |
| Date | 2026-07-22 |
| Lane | side-question |
| Task class | repository gate diagnosis |
| Repository / packet identity | Devad Workflow integration at `bb0709ad` |
| Model / effort requested | GPT-5.6 SOL / high |
| Model / effort attested | unavailable |
| Main-agent profile | primary implementation agent |
| Why this tier was selected | A cross-cutting pre-push failure needed separation of product failure from tooling baseline behavior. |
| Scope and forbidden actions | Read-only; no edits, installs, tests, Git mutation, providers, database, deployment, browser, or Sheets. |
| First-pass result | PASS |
| Independent proof | Main agent confirmed the exact-range path computation, global formatter call, changed-file formatter PASS, types/build PASS, and full AI suite PASS. |
| Retries / compactions | none reported |
| Wall time | unmeasured |
| Token telemetry | unavailable |
| Approx. new-token volume | `Unknown` |
| Safety or truth errors | none observed |
| Ranking action | keep |

## Result

- Evidence and concise outcome: Identified an existing pre-push tooling defect: an exact changed-file range triggers a repo-wide Prettier baseline with unrelated failures. Recommended a touched-file formatter ratchet while preserving global types/build/tests.
- Best use case learned: Use a bounded read-only helper to distinguish a real product regression from an over-broad repository gate before changing or bypassing either.
- Next profile to try, if any: Keep SOL high for bounded security-tooling diagnosis.
