# Subagent Lesson

| Field | Value |
| --- | --- |
| Date | 2026-07-19 |
| Lane | main |
| Task class | Nested Laravel/database staged-diff review |
| Repository / packet identity | `$DEVAD_ROOT\1-core-x9`; C5A 36-path staged diff at `4a06bb09...` |
| Model / effort requested | Inherited SOL xhigh reviewer profile |
| Model / effort attested | Unknown; runtime telemetry did not attest the profile |
| Main-agent profile | SOL max |
| Why this tier was selected | Migration rollback, encrypted serialization, physical PostgreSQL types, and composite tenant FKs |
| Scope and forbidden actions | Read-only staged review; no edits, Git mutation, external runtime, or provider calls |
| First-pass result | FAIL |
| Independent proof | Exact file/line findings were confirmed and adopted into the correction packet |
| Retries / compactions | One nested review pass |
| Wall time | Unknown |
| Token telemetry | unavailable |
| Approx. new-token volume | `Unknown` |
| Safety or truth errors | none; reviewer did not mutate state |
| Ranking action | keep |

## Result

- Evidence and concise outcome: The reviewer found incomplete rollback preflight, plaintext serialization risk for an encrypted idempotency key, an impossible PostgreSQL SQLSTATE expectation, and missing negative composite-FK execution proof.
- Best use case learned: A focused database reviewer adds value even after large green assertion counts because test configuration can hide FK behavior and physical types can fail before named CHECK constraints.
- Next profile to try, if any: Reuse SOL xhigh for the corrected staged bytes.

Do not record secrets, cookies, raw provider output, or full sensitive prompts.
