# Subagent Lesson

| Field | Value |
| --- | --- |
| Date | 2026-07-19 |
| Lane | main |
| Task class | Multi-file Laravel/PostgreSQL persistence implementation |
| Repository / packet identity | `$DEVAD_ROOT\1-core-x9`; C5A staged at base `4a06bb09...` |
| Model / effort requested | SOL xhigh |
| Model / effort attested | Unknown; runtime telemetry did not attest the profile |
| Main-agent profile | SOL max |
| Why this tier was selected | Additive schema, immutable lineage, replay, and tenant-safety work across 36 paths |
| Scope and forbidden actions | C5A only; no C5B/C5C/UI/destinations/provider/runtime/deploy; no commit before manager review |
| First-pass result | PASS |
| Independent proof | Independent staged spec/code/security review is pending |
| Retries / compactions | Several bounded RED/GREEN cycles; one full-suite run stopped after 3m45s and recorded UNKNOWN |
| Wall time | Unknown |
| Token telemetry | unavailable |
| Approx. new-token volume | `Unknown` |
| Safety or truth errors | none reported; no external state or commit/push mutation |
| Ranking action | keep |

## Result

- Evidence and concise outcome: The helper staged exactly 36 paths with no unstaged/untracked bytes. Focused persistence tests passed 718 assertions; the broader AI Feature/Unit set passed 3,530 assertions; Pint, PHP lint, Composer validation/audit, diff check, and security pre-commit passed. Full repository and real PostgreSQL/pgvectorscale proof remain honestly UNKNOWN.
- Best use case learned: A bounded sole-writer SOL xhigh helper can safely carry a large persistence slice when contracts, forbidden surfaces, commit authority, and proof labels are frozen up front.
- Next profile to try, if any: Keep SOL xhigh for implementation; require an independent SOL xhigh staged review before C1/C2 approval.

Do not record secrets, cookies, raw provider output, or full sensitive prompts.
