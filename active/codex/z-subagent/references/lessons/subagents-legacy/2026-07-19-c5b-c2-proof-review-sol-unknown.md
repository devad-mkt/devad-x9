# Subagent Lesson

| Field | Value |
| --- | --- |
| Date | 2026-07-19 |
| Lane | side-question |
| Task class | Hash-bound C2 proof review |
| Repository / packet identity | Devad Content Agent C5B proof branch at C1 91952c5e7d29b5a3e47ca3a9a248f39695d9500d |
| Model / effort requested | inherited reviewer |
| Model / effort attested | unavailable |
| Main-agent profile | SOL, owner-requested max with risk-calibrated depth |
| Why this tier was selected | One narrow independent truth check before committing durable proof |
| Scope and forbidden actions | Four staged proof files only; no edits, network, database, provider, merge, or deploy |
| First-pass result | FAIL |
| Independent proof | Reviewer found one P2 staged-versus-committed wording mismatch; exact one-line correction then PASS |
| Retries / compactions | one focused correction round |
| Wall time | unavailable |
| Token telemetry | unavailable |
| Approx. new-token volume | `Unknown` |
| Safety or truth errors | none; one documentation-state precision issue caught before commit |
| Ranking action | keep |

## Result

- Evidence and concise outcome: The reviewer verified C1 parent/tree/path-manifest and file hashes, caught one inaccurate `C2 absent` phrase while four C2 files were staged, and passed the exact corrected bytes with no broader re-review.
- Best use case learned: Reuse one reviewer for a small changed diff and ask it to check only the prior finding plus hash-bound claims.
- Next profile to try, if any: A lower-cost high-accuracy reviewer may be sufficient for proof-only four-file packets once model telemetry is available.

Do not record secrets, cookies, raw provider output, or full sensitive prompts.
