# Style G Operating Contract

Style G keeps one accountable Worker moving inside a compact authority
envelope. It adds no database, queue, scheduler, monitor, or background
callback service.

## Packet

```text
LANE_ID:
TASK_ID:
ROLE:
REPO / WORKTREE / BRANCH / BASE_SHA / HEAD_SHA:
EXCLUSIVE_PATHS:
SHARED_RESOURCES:
ALLOWED_ACTIONS:
FORBIDDEN_EFFECTS:
ACCEPTANCE_PROOF:
ROLLBACK:
STOP_CONDITIONS:
CANDIDATE_STATE: PRESERVED_CANDIDATE | INTEGRATED | LIVE_PROVED
NEXT_LOCAL: <one action>
```

If an external input is unavailable, replace only `NEXT_LOCAL` for that chunk:

```text
DEPENDENCY_WAIT:<EVENT>
MISSING_RECEIPT_OR_CAPABILITY:
PRODUCER:
RESUME_ON: <receipt type + SHA-256 + expiry + exact action>
NO_CLAIMED_DISJOINT_SLICE: <once, only if true>
```

## Routine repair

Routine coding, diagnostics, formatting, focused tests, fixtures, parser
fixes, command corrections, and temporary reversible probes are already
authorized when they remain in the envelope. They do not require Thinker or
Looper permission. After one route fails, choose one different safe local
route; stay local through three same-root low-risk cycles.

Two different failures allow a Thinker review only when judgment is actually
needed. A Thinker `BLOCK` with file/line findings is defect evidence: fix it,
rerun the affected proof, and review the changed tree once. It is not owner
blockage.

## Direct receipt flow

```text
Worker result or helper terminal receipt
  -> durable file path + SHA-256
  -> Looper verifies the named subscriber
  -> one pointer to that Worker
  -> Worker rereads receipt and runs its predeclared action
```

Duplicate pointers and stale receipts are zero-delta. Never turn a lost pointer
into a new task, a broad dependency board, polling, or a controller runtime.

## Capability preflight

Before a new external capability epoch, prove only the needed capability:
worktree identity, runtime/extensions, secret-safe transport, private network,
rollback/backup, or browser/build support. Reuse that proof for the epoch;
never preflight every product chunk.

## Status language

Use `ACTIVE`, `NEXT_LOCAL`, `DEPENDENCY_WAIT:<EVENT>`,
`SHARED_SERIAL_WAIT`, or `HARD_BOUNDARY`. Do not call a whole worker blocked
for a soft local failure or a dependency that pauses only one chunk.
