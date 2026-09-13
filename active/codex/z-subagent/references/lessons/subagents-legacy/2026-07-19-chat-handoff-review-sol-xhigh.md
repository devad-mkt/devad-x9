# Subagent Lesson

| Field | Value |
| --- | --- |
| Date | 2026-07-19 |
| Lane | main |
| Task class | Read-only architecture and execution-handoff review |
| Repository / packet identity | core-x9 planning packet, chat-full-migration-1 |
| Model / effort requested | gpt-5.6-sol / xhigh |
| Model / effort attested | unavailable |
| Main-agent profile | GPT-5.6 Sol, owner-requested ultra reasoning |
| Why this tier was selected | The handoff combined Git authority, tenant RLS, cross-lane claims, proof sequencing, and deployment boundaries; subtle wording could grant unsafe authority. |
| Scope and forbidden actions | One Markdown handoff only; no edits, clean-project inspection, product code, Git mutation, providers, database, GitHub, or Dokploy. |
| First-pass result | FAIL |
| Independent proof | Reviewer returned seven bounded revisions, then two edge-case revisions; final follow-up returned PASS after exact corrections. Deterministic required-section, marker, hash, and diff checks also passed. |
| Retries / compactions | Two bounded follow-up review turns; no scope expansion. |
| Wall time | Approximately 6 minutes |
| Token telemetry | unavailable |
| Approx. new-token volume | `Unknown` |
| Safety or truth errors | Initial draft blurred pre-deploy C2 versus live proof, used non-exact overlap exclusions, implied name reservation, lacked explicit Controller Work Order authority, overstated mutable behavior and future Playwright truth, used unsafe worktree retirement wording, and omitted explicit DB-object claim gating. |
| Ranking action | keep |

## Result

- Evidence and concise outcome: The reviewer materially improved the handoff without touching product state; the corrected artifact passed the final independent check.
- Best use case learned: Use Sol xhigh for bounded pre-execution reviews where authority, evidence timing, resource ownership, and database security intersect.
- Next profile to try, if any: Sol high for a simpler follow-up diff; keep xhigh for new cross-lane handoffs or security-sensitive execution contracts.

Do not record secrets, cookies, raw provider output, or full sensitive prompts.
