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
- Looper owns the compact lane ledger and next-action routing. Thinker is not
  a routine approval service.
- Linker transports only an exact signal. Workers own implementation and proof.
- A result is acknowledged once by rereading the durable receipt. Duplicate
  signals are zero-delta. If a signal is lost, resend the same pointer once;
  do not create a new manager, work order, or polling loop.

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
