# Subagent Lesson

| Field | Value |
| --- | --- |
| Date | 2026-07-19 |
| Lane | main |
| Task class | Long-lived implementation helper branch setup |
| Repository / packet identity | `$DEVAD_ROOT\1-core-x9`; Devad Content Agent C5A |
| Model / effort requested | SOL xhigh |
| Model / effort attested | Unknown; runtime telemetry did not attest the profile |
| Main-agent profile | SOL max |
| Why this tier was selected | Multi-file Laravel persistence work with schema and security implications |
| Scope and forbidden actions | Exact branch/base gate; no reset, clean, merge, deploy, provider call, or production mutation |
| First-pass result | FAIL |
| Independent proof | Thread readback showed a credential/approval-state stall; manager stop returned a clean checkout without product mutation |
| Retries / compactions | One compaction; the stalled route was split, then stopped and rerouted |
| Wall time | About 8 minutes 37 seconds for the stopped implementation turn |
| Token telemetry | unavailable |
| Approx. new-token volume | `Unknown` |
| Safety or truth errors | No product corruption; the visible thread became idle after an explicit bounded stop |
| Ranking action | keep |

## Result

- Evidence and concise outcome: The long-lived Codex task reached an approval-state/credential-helper stall during branch setup. The manager stopped it before overlapping edits and assigned the same bounded C5A scope to one internal sole-writer subagent. The replacement created the authorized branch and progressed normally.
- Best use case learned: A long-lived task is useful for durable context, but it should not share a checkout with an active internal writer. If its safe branch gate stalls on UI approval, park it and transfer sole-writer ownership explicitly.
- Next profile to try, if any: Keep SOL xhigh for C5A; change the execution route, not the reasoning tier.

Do not record secrets, cookies, raw provider output, or full sensitive prompts.
