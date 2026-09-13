# Subagent Lesson

| Field | Value |
| --- | --- |
| Date | 2026-07-19 |
| Lane | side-question |
| Task class | owner command packet security review |
| Repository / packet identity | `$DEVAD_ROOT/content-agent-c5b-postgres-proof`, pre-staging C1 packet on source `d547d3bf9d28604825871adf9ae13732bb4d1560` |
| Model / effort requested | unavailable from nested-agent telemetry |
| Model / effort attested | unavailable |
| Main-agent profile | unavailable |
| Why this tier was selected | Independent review was required before staging an owner-run destructive/runtime command packet. |
| Scope and forbidden actions | Read-only packet/harness review; no edits, staging, network, database, provider, Dokploy, or runtime action. |
| First-pass result | FAIL |
| Independent proof | Root directly read all three packet files and independently found the same two risks before receiving the reviewer result. |
| Retries / compactions | 0 retries; one fix/re-review remains |
| Wall time | unavailable |
| Token telemetry | unavailable |
| Approx. new-token volume | `Unknown` |
| Safety or truth errors | none; reviewer found two real P1 packet defects |
| Ranking action | keep |

## Result

- Evidence and concise outcome: `REVISE`, P1=2: ambient database aliases could redirect execution, and missing `try/finally` could retain secrets or route state after failure.
- Best use case learned: A bounded independent reviewer is valuable for executable owner packets even when the product diff itself is unchanged.
- Next profile to try, if any: Reuse the same review depth on the corrected bytes; do not add another reviewer if the re-review passes.

