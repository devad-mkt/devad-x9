---
name: loop-subagents
description: Run a lean evidence-to-implementation team loop for one product slice at a time using a source-bound evidence worker, an implementation worker, an independent acceptance reviewer, and a parent integrator. Use for UI, workflow, migration, parity, or feature work that needs high fidelity without speculative breadth, repeated status loops, or X9 coordination overhead.
---

# Loop Subagents

Deliver one bounded feature or page through evidence, implementation, adversarial review, repair, and direct proof.

## Core loop

1. Choose one channel, settings page, workflow, or feature with exact owned paths and a visible completion predicate. Never batch unrelated features.
2. Dispatch the strongest admitted evidence role with no product writes. Require authoritative source identity, reference behavior, UI and DOM states, hidden and conditional behavior, current owner, exact delta, privacy scan, and UNKNOWN or effect-gated boundaries.
3. Recompute evidence hashes and spot-check the highest-risk claims. Reject stale authority, missing states, or unsupported completeness before coding.
4. Give the implementation worker only the accepted evidence and exact owned paths. Require reuse of existing components, working local interactions, honest disabled external effects, focused tests, and no invented provider, storage, or runtime contract.
5. Use a different admitted role for read-only acceptance review when possible. Require `PASS` or concrete `REQUEST_CHANGES`; do not reward activity or documentation volume.
6. Send concrete failures back to the same implementer. Permit one bounded correction at a time. Rerun focused proof without creating a new plan or packet.
7. Inspect the final diff, run deterministic focused checks, and exercise the real local browser flow at required viewports. Keep SOURCE, TEST, BROWSER, PROVIDER, DEPLOYED, and LIVE verdicts separate.
8. Freeze the accepted slice and select the next item. Do not let evidence run more than one ready slice ahead of implementation.

## Dispatch rules

- Use `fork_turns="none"` and include complete task-local context, paths, constraints, proof, and callback.
- Honor the runtime's actual model and role inventory. State when Luna or Terra is unavailable; never silently claim a named model.
- Use three roles only: evidence, implementation, reviewer. The parent owns integration and final truth.
- Forbid child agents unless the user explicitly expands the loop.
- Assign exclusive write paths. Keep evidence and review roles read-only.
- Reuse long-lived agents for the same role and domain through follow-up tasks.

## Acceptance rubric

Check every applicable item:

- evidence coverage and current source authority;
- exact workflow and information architecture;
- visible, hidden, loading, empty, error, disabled, selected, modal, and permission states;
- observable behavior for every enabled control;
- visible reasons for unavailable effects;
- responsive density, keyboard flow, labels, focus, announcements, and overflow;
- tenant isolation, authorization, secret absence, and lifecycle-status honesty;
- reuse of existing components and avoidance of one-file growth;
- behavior proof rather than source-string assertions alone;
- no provider, persistence, deployment, or live claim without direct proof.

## Stop and reset rules

- After two process-only turns, execute the smallest safe edit, test, or browser action.
- Treat a failed preferred tool or route as blocking only that proof route. Try the cheapest structurally different allowed route.
- Stop the slice only for a genuine product authority, destructive, secret, spend, production, or cross-owner boundary.
- Cap review and repair at three evidence-backed cycles. Then shrink the slice or identify one concrete contract contradiction.
- Never mark the wider goal blocked because one slice or external proof tier is pending.

## Callback contracts

```text
EVIDENCE_READY | authority | artifacts+hashes | coverage | UNKNOWN/effect gates | privacy/stale scan
CODE_READY | changed paths | behavior changed | focused proof | intentionally unimplemented effects
PASS | REQUEST_CHANGES | exact issue+location | observable acceptance predicate | tiered verdict
ACCEPTED_SLICE | source SHA/worktree | SOURCE/TEST/BROWSER/PROVIDER tiers | next slice
```

## Keep it lean

Use X9 only for real branch, collision, or cross-worker ownership coordination. Do not create controller ledgers, recurring status packets, another plan family, or loop telemetry for ordinary feature delivery. Treat the code, focused tests, browser proof, and concise callbacks as the ledger.
