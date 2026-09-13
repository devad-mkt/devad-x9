# Subagent Lesson

| Field | Value |
| --- | --- |
| Date | 2026-07-20 |
| Lane | side-question |
| Task class | read-only R0 security and focused-gate review |
| Repository / packet identity | D:\\CDx9\\0-cdx-wt\\f22d\\1-core-x9; R0 preparation 2564bb18ca3947003a73d0b93466b505ac699d5570353f999e99274b64ab6caf |
| Model / effort requested | gpt-5.6-sol / high |
| Model / effort attested | requested through the collaboration tool; runtime telemetry unavailable |
| Main-agent profile | Unknown |
| Why this tier was selected | Security-sensitive PowerShell range validation and cross-language focused-gate selection |
| Scope and forbidden actions | Read-only review; no edits, Git/ref/index mutation, or broad test run |
| First-pass result | PASS |
| Independent proof | Parser/lint/diff checks plus a bounded invalid-tree range probe |
| Retries / compactions | 0 / 0 |
| Wall time | Unknown |
| Token telemetry | unavailable |
| Approx. new-token volume | Unknown |
| Safety or truth errors | none; found one pre-C1 endpoint-type validation defect |
| Ranking action | keep |

## Result

- Evidence and concise outcome: Three manual code/security resolutions matched their recipes; the pre-push hook incorrectly accepted arbitrary tree OIDs as an outgoing range.
- Best use case learned: Sol High is effective for focused security review with a minimal reproducer while implementation continues elsewhere.
- Next profile to try, if any: SOL medium for deterministic parser/lint reruns after the fix.

