# Subagent Lesson

| Field | Value |
| --- | --- |
| Date | 2026-07-28 |
| Lane | main |
| Task class | Critical Laravel/PostgreSQL tenancy implementation and independent review |
| Repository / packet identity | CHAT channel-storage tenancy correction; base `64ecc8d6ee5a2d2f8219ce1fcc9c97cdc53ddf6e`; C1 `03ab705695f2a59685991ac3d0c6d64c1d4859ff`; C2 `e96c1f624d975098576f0ff52f27c3b0e733532b` |
| Model / effort requested | Sol high implementer; Sol xhigh independent reviewer |
| Model / effort attested | `gpt-5.6-sol` high and `gpt-5.6-sol` xhigh |
| Main-agent profile | Root delivery manager |
| Why this tier was selected | The slice changed forced RLS, SECURITY DEFINER functions, composite tenant constraints, transaction-local context, and irreversible rollback |
| Scope and forbidden actions | Seven exact paths; no PostgreSQL runtime, role mutation, provider, queue, Reverb, deployment, integration, or eighth path |
| First-pass result | Sol-high source and focused tests passed, but Sol-xhigh review found three High proof or boundary defects |
| Independent proof | Final Sol-xhigh frozen-diff review passed after corrections; C1/C2 security gates and remote readback passed |
| Retries / compactions | Three bounded correction passes, each on the same seven-path authority |
| Wall time | Unavailable |
| Token telemetry | Unavailable |
| Approx. new-token volume | Unknown |
| Safety or truth errors | First pass allowed weak PHP scalar coercion and under-specified permanent PostgreSQL proof; no runtime or production mutation occurred |
| Ranking action | keep |

## Result

- Evidence and concise outcome: Sol high produced a coherent seven-path implementation, but the independent Sol xhigh review found a tenant-selection coercion bug, incomplete exact policy and least-privilege assertions, missing negative/race/cleanup proof, and one fixture-bookkeeping defect. The same implementer corrected them, and the final reviewer returned PASS.
- Best use case learned: Use Sol high for serious bounded implementation. Use Sol xhigh as the accepted independent reviewer when tenancy, RLS, privileged functions, irreversible migrations, or production-security boundaries change. Do not use Spark as the final reviewer for this class.
- Next profile to try, if any: Keep Spark or Luna trials for immutable low-risk extraction and routine analysis only. Compare them on the same hidden-fact packet before changing any default.

Actionable task packets materially improved both profiles: exact paths,
preimages, risk invariants, required assertions, forbidden actions, success
predicate, stop conditions, and compact output made every correction auditable.
Unknown token telemetry means this run proves quality routing, not cost
superiority.
