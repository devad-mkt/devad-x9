# V6-style Operating Reference

## Packet and receipt

Keep one packet per bounded outcome. It names the exact repository, worktree,
base SHA, source evidence, claimed paths, exclusions, acceptance tests,
security/release gates, rollback, STOP conditions, and next owner. A result
records the same identity plus changed paths, commands/proof references,
remaining risk, rollback, and an exact next action.

Use Git and the packet/receipt as durable truth. A message carries only task
ID plus canonical path/hash. The receiver rereads the file; it does not rely
on remembered chat context.

## Progress without a Controller

- One blocked dependency pauses only that lane. Select a disjoint safe local
  action immediately when the packet already authorizes it.
- Thinker is decision-only: one stable material-diff review, a real
  architecture/security boundary, or two distinct proof-bound failures. It
  neither runs the queue nor supplies routine approvals.
- Looper is the single owner of the ordered packet/lane queue. It continues
  dependency-ready safe work and leads bounded repair/routing, without becoming
  a second project manager or taking product-coding claims.
- Linker sends only exact canonical path/hash/result-pointer signals; it never
  chooses, transforms, approves, retries, or executes work. Workers implement
  only their claimed packet paths and return proof.
- A `Worker Loop Fix` is a narrow STYLE skill/package/install/host-integration
  implementation Worker, not a Looper or manager; it stops after its bounded
  result. Task creation leaves `thinking` unset.
- A result is acknowledged once by rereading the durable receipt. Duplicate
  signals are zero-delta. If a signal is lost, resend the same pointer once;
  do not create a new manager, work order, or polling loop.

## Sticky lane and task recovery

Keep a task, its native worktree, branch, base, and exclusive paths stable
until the bounded candidate is frozen. Remote-main movement alone is
`REBIND_DUE`, not a reason to stop local work, rebase, copy bytes, or replace a
valid candidate. Rebind at integration/release, a changed shared claim or
resource, a changed task/worktree identity, or new evidence that invalidates an
accepted assumption.

For a wrong task attachment, use this ladder once: continue in the correct
existing worktree if the same task can reach it; otherwise try one host move
that preserves it; otherwise create one successor task in the already
registered correct project. The successor rereads the compact packet and proves
`cwd`, branch, HEAD, staged state, and candidate acknowledgement before the old
task is marked superseded. Never create a replacement worktree, copy dirty
bytes, or retry attachment routes.

Looper keeps one durable ordered checklist. A waiting dependency pauses only
its lane; select the next dependency-ready item, and resume the waiting one on
its named receipt. A new message updates its existing lane instead of creating
another plan or queue. Only a security incident may preempt the active item.

## Question admission

Before any external question, select exactly one:

| Class | Use it when |
| --- | --- |
| `CONTINUE_LOCAL` | Safe work, evidence gathering, coding, tests, or known next action is available. |
| `LOCAL_FALLBACK` | One preferred local route failed and a safe alternative exists. |
| `SUBAGENT_ONCE` | One difficult same-scope technical route failed; use one bounded helper. |
| `THINKER_ALLOWED` | Stable material diff, real architecture/security boundary, or two distinct proof-bound failures. |
| `OWNER_REQUIRED` | Owner-only product/scope/production, secret, destructive, or spend decision. |

Missing or incomplete admission is `CONTINUE_LOCAL`, never `BLOCKED`. A
reviewer `BLOCK` with concrete findings is Worker defect evidence: fix inside
claims, rerun affected proof, and review the changed tree once.

## Quarantined Controller trial

`x9-loop-code` is an experimental Controller trial for a fresh disposable
project. `devad-x9-loop` is only its compatibility name. Neither is a fallback
for ordinary work. A later classifier may expose
`STYLE_FALLBACK_AVAILABLE` only when no V7 ACTION is active and a host routing
failure is proven. It cannot bypass security, receipt, claim, provider,
deployment, destructive, or production boundaries.
