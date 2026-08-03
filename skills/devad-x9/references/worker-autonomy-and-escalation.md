# Worker Autonomy And Escalation

Use this before asking another task for routine permission or reporting a whole
goal blocked.

## Inside an Authority Envelope

The Worker owns the current objective/chunk, existing worktree, claimed paths
and resources, allowed actions, forbidden effects, focused proof, rollback,
stop conditions, and any named resume event.

Inside it, diagnose -> smallest correction -> focused proof -> continue.
Routine code, tests, parser/quoting fixes, fixtures, harnesses, local tools,
and reversible diagnostics stay local. The same low-risk root cause stays local
through three bounded correction cycles.

## Admission before an outbound question

Choose exactly one:

| Class | Use it when |
| --- | --- |
| `CONTINUE_LOCAL` | Safe work or known next action exists. |
| `LOCAL_FALLBACK` | One local route failed and another safe route exists. |
| `SUBAGENT_ONCE` | One difficult same-scope route failed and one helper can change the next action. |
| `THINKER_ALLOWED` | A frozen material diff, real security/architecture boundary, or two distinct failures where judgment is needed. |
| `OWNER_REQUIRED` | A true owner-only product, production, secret, destructive, spend, provider, or scope decision remains. |

Missing admission means `CONTINUE_LOCAL`. A reviewer finding is defect evidence,
not owner blockage: fix it inside claims and rerun the affected proof. A failed
external dependency pauses only that chunk as `DEPENDENCY_WAIT:<EVENT>`; keep
disjoint claimed work moving and record `NO_CLAIMED_DISJOINT_SLICE` once only
when none remains.

Matching fresh receipt -> declared resume action. Stale or duplicate receipt ->
zero-delta. Do not turn either into polling, a replacement worker, or a new
manager flow.
