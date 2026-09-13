# Subagent Lesson

| Field | Value |
| --- | --- |
| Date | 2026-07-19 |
| Lane | main |
| Task class | Guarded C1/C2 commit and branch-only push |
| Repository / packet identity | C5A C1 `67b9bee6...`, C2 `68a65039...` |
| Model / effort requested | SOL xhigh |
| Model / effort attested | Unknown |
| Main-agent profile | SOL max |
| Why this tier was selected | Exact commit separation, security prepush, and remote-tip integrity |
| Scope and forbidden actions | C1 accepted source, C2 proof-only, normal worker-branch push; no integration/deploy/runtime |
| First-pass result | PASS |
| Independent proof | Local/upstream/remote readback identical; exact 2-commit ancestry and 37/2 path split |
| Retries / compactions | One guarded commit/push pass after final review PASS |
| Wall time | Unknown |
| Token telemetry | unavailable |
| Approx. new-token volume | `Unknown` |
| Safety or truth errors | none; runtime UNKNOWN labels preserved |
| Ranking action | keep |

## Result

- Evidence and concise outcome: C1 and C2 were atomically pushed without force. Prepush security, Pint and Feature/Ai passed; local/tracking/remote tips matched and the worktree was clean.
- Best use case learned: Keep source and attestation commits separate, then guard the new remote branch with exact absence and ancestry checks.
- Next profile to try, if any: Main agent performs serial integration; helper can start C5B only after binding the accepted integration SHA.

Do not record secrets, cookies, raw provider output, or full sensitive prompts.
