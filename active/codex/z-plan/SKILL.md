---
name: z-plan
description: Create or reorganize a durable read-by-need delivery package with one canonical PLAN.md and only the short Work Order, handoff, validation, decision, review-packet, reference, guardrail, or receipt files the project actually needs. Use for migrations, long-running delivery programs, noisy plan folders, multi-worker projects, external-model reviews, deadline prioritization, or any task where agents repeatedly read too much, use stale status, stop for routine questions, or lose authority boundaries.
---

# zPlan

Create one compact entrypoint that makes a large project easier to resume,
execute, and verify without copying all source material into context.

For repeated false blockers or over-engineered proof routes, apply
`references/product-candidate-rulebook.md`. A plan must bias toward a working
candidate and focused proof before reusable infrastructure, sealed transport,
or review machinery.

## Execution cutoff

xPlan organizes already-needed delivery; it must never become a prerequisite
for obvious local execution. If current authority, paths, invariants, and proof
are known, use the existing plan and act. Do not create or revise a Work Order,
handoff, manifest, decision, review packet, capability package, or successor
plan merely because a tool route failed. One failed route permits one concise
diagnosis and one structurally different direct attempt. After that, either
perform the material action, continue another authorized chunk, or record one
true external event. Planning/routing/status is not progress.

Never encode a preferred browser, SSH transport, listener, database instance,
or wrapper as the goal invariant. Bind the safety and acceptance properties;
choose the shortest disposable test route that preserves them. Existing lane
waits remain resumable and do not authorize ending the host goal.

Every long-running lane must include a concrete product next-action ladder:
primary route, cheapest structurally different fallback, disjoint local
continuation, and true owner boundary. If the lane cannot name a product action,
it is `EVENT_ONLY`, not a worker that should keep reporting.

## False Blocker Guard for PLANs and Work Orders

A plan must not let workers report `BLOCKED`, `WAITING`, `FROZEN`,
`HARD_BOUNDARY`, `RESUME_ON`, or `OWNER_REQUIRED` from a preferred route
failure alone. Any such packet must include:

- `GOAL_OUTCOME`
- `EVIDENCE_TARGET`
- `FAILED_ROUTE`
- `WHY_ROUTE_FAILURE_APPLIES_TO_ALL_ALLOWED_ROUTES`
- `CHEAPEST_WORKAROUND_TESTED`
- `ACTION_NOW`
- `NEXT_MATERIAL_ACTION_OR_TRUE_OWNER_BOUNDARY`
- `CONSTRAINT_CLASS:HARD|SOFT|ASSUMED`

If any field is missing, the manager response is
`REJECT_FALSE_BLOCKER:CONTINUE_LOCAL` plus one direct next action. Each worker
lane must include a next-action ladder: primary route, cheapest structurally
different fallback, local source/test continuation, and true owner boundary.
Timeouts require phase split or focused repair; browser/tool failures block
only the proof row that depends on that tool.

Use `assets/plan-template/compact/README.md` for the default compact big-plan
pack. It is a flat folder: copy `PLAN.md` and `CANONICAL-CHECKLIST.md` first,
then add only a one-purpose `WORK-ORDER.md`, `HANDOFF.md`, `DECISION.md`, or
`RUN-RECEIPT.md` if the delivery actually needs it. The older nested templates
remain compatibility assets; do not copy them for new plans.

## 1. Lock current truth

Before writing:

1. Resolve the repository root and exact owner-named destination.
2. Record current branch, HEAD, upstream, status, and relevant remote/runtime
   identity when they matter.
3. Identify the newest accepted authority, Work Order, receipt, and live
   evidence.
4. Mark stale narration as stale. Do not merge conflicting status prose.
5. Preserve dirty/user-owned files and avoid unrelated edits.

An explicit user destination overrides another documentation convention.
Otherwise use the project's established plan/feature folder.

## 2. Inventory without broad reading

List first; read second.

- Read the current receipt and current plan headings before historical plans.
- Search exact feature IDs, paths, statuses, and keywords with `rg`.
- Read only relevant workbook tabs/ranges or exported pages.
- Hash external answers and verify decisive claims against current source,
  installed versions, runtime evidence, or primary documentation.
- Never make raw model answers mandatory startup context.

Classify every source:

| Class | Rule |
|---|---|
| Mandatory | Read for every task; keep this list very short |
| Signal-routed | Read only when the current slice matches |
| Historical | Use only for provenance or conflict resolution |
| Forbidden | Secrets, databases, dirty reference state, or explicitly denied material |

## 3. Build one canonical PLAN.md

The main plan must contain:

1. purpose, bounded scope, date, current identity, and honest status;
2. authority/truth order;
3. minimum mandatory read;
4. a signal-to-file/range router;
5. bounded workbook/ledger routing;
6. current checkpoint with `PASS`, `FAIL`, `NOT_RUN`, `UNKNOWN`, or blocker;
7. dependency-ordered priorities that do not silently delete scope;
8. one-slice implementation and verification loop;
9. long-run worker lanes and continuation rules;
10. owner-attention decisions with recommended defaults;
11. completion, stop, rollback, and recovery rules;
12. a compact map of supporting files.

For long-running recovery programmes, the plan header must also carry
`ACTIVE_PROGRAM_PHASE`, `ACTIVE_SLICE_ID`, `ACTIVE_SLICE_STATE`,
`ADVANCE_GATE`, and `OWNER_SELECTED_BASELINE`. A generic continuation, helper
callback, or proposed next row resumes the active slice; it cannot change these
fields or advance the queue. Only owner acceptance or explicit owner-approved
defer may open the next slice.

Reference canonical large documents by exact path, section, hash, or ID.
Do not duplicate them. State which source wins when status conflicts.

### Per-chunk delivery sequence

For each material feature, route one lightweight sequence:

`matching evidence -> current-source ownership map -> bounded chunk contract
or sub-plan -> PRE_CODE SHA/preimage rebind -> hash-bound Work Order -> code ->
focused proof -> one frozen-diff review -> delivery`.

The chunk contract contains only implementation-changing decisions: outcome,
owners to reuse, exact gap, inputs/outputs, authorization, persistence/effects,
errors/recovery, accessibility, paths/tests, and exclusions. Reuse a frozen
contract after an identity rebind; never repeat the contract cycle for
unchanged semantics.

Include a maintainability check before adopting predecessor/reference code.
Reuse behavior and owner seams, but reject needless abstractions or complexity.
Name shared platform owners once in the plan so later chunks cannot recreate
them. In Devad, the notification owner chain includes Laravel Notifications,
Reverb, WebPush/service-worker delivery, the ledger, and suppression/throttling.

### Layered page and channel ledger

Do not assign one status to an entire page or channel when only one layer is
gated. The canonical checklist must split pages as:

`shell -> read model/local draft -> persistence -> asynchronous/external effect
-> browser parity -> runtime/live proof`.

Split channels as:

`settings/read -> credential/connect -> callback/signature -> inbound ->
outbound -> receipt/retry -> live/canary`.

Every row names its evidence denominator, current owner, exact paths, local
proof, later gate, primary route, structurally different fallback, and one next
action. A missing provider, PostgreSQL, browser, or deployment input may change
only the rows that consume it. It must not hide a safe shell or local draft
behind a blanket `DEFER` status.

When the owner declares local-first delivery, place all independent
`BUILD_NOW` and `SAFE_SHELL_NOW` rows before PG/provider/deploy/live rows. The
plan must show the count of unfinished local rows, and remote proof cannot be
the active next action while that count is nonzero unless the owner explicitly
reorders it.

Count only actions a worker can actually execute as unfinished local rows.
Keep source/test-complete browser rows that require real PostgreSQL tenancy,
HTTPS publication, or another hard invariant visible as
`BROWSER_PENDING_<INVARIANT>`, but do not let them keep the executable-local
count nonzero and do not authorize a fake bypass to close them. This preserves
the missing acceptance tier without trapping the plan behind work that is no
longer local.

## 4. Route workbooks by need

Do not tell workers to read the whole workbook.

For each slice, name only:

- one overview/status range;
- one feature/page/chunk row;
- exact control, setting, journey, gap, and traceability IDs;
- acceptance/release rows only when closing the slice.

Use a live connector for current writes/readback. Treat offline exports as
read-only snapshots. Require exact preimage, bounded write, and exact readback.

## 5. Route external advice safely

For each recommendation, record:

| Verdict | Meaning |
|---|---|
| `VERIFIED_ROUTE` | Current source or primary evidence supports it and a slice needs it |
| `DEFER_GUARD` | Useful later, but not justified now |
| `REJECT_STALE` | Current source already fixed or superseded it |
| `REJECT_UNSUPPORTED` | Primary/current evidence does not support it |
| `OWNER_DECISION` | Technically possible but changes scope, runtime, cost, or risk |

Verify counts directly. Reject false precision and model consensus without
evidence. A recommendation never grants code, database, provider, or deploy
authority.

## 6. Keep helpers running without widening authority

Use a durable, hash-bound mission file rather than a chat-only todo list.
Default mission size is 90-240 minutes. A coding mission normally owns 5-15
exclusive files; an evidence/browser mission closes one complete denominator
segment rather than one row, page, or locator. One done token closes the whole
outcome, not one file, command, test, review, receipt, or commit.

Give each helper:

- one long-run lane goal;
- desired user outcome and explicit non-outcomes;
- exact task, worktree, branch/base, authority, and dependency receipts;
- an ordered internal phase queue through focused proof and stable closeout;
- exact write ownership;
- explicit `EXCLUSIVE`, `SHARED_SERIAL_ONLY`, `READ_ONLY`, and `FORBIDDEN`
  paths/resources;
- routine decision rights inside exact claims;
- one structurally different safe fallback per likely blocked dependency;
- hard-stop conditions;
- one stable review after bytes stabilize;
- C1/C2, normal push/readback, remote equality, and clean proof only when
  authorized;
- one compact DONE/BLOCKED wake packet and proposed next dependency gap.

Workers continue through already-authorized queue items. If one item is
blocked, they record it once and move to a non-overlapping safe item. They ask
the accountable manager for routine questions and stop only for owner
decisions, missing write authority, shared collisions, security ambiguity,
secrets, destructive/live actions, or invalidated architecture.

A worker blocker packet is valid only when it carries:
`GOAL_OUTCOME`, `EVIDENCE_TARGET`, `FAILED_ROUTE`,
`WHY_ROUTE_FAILURE_APPLIES_TO_ALL_ALLOWED_ROUTES`,
`CHEAPEST_WORKAROUND_TESTED`, `ACTION_NOW`, and
`NEXT_MATERIAL_ACTION_OR_TRUE_OWNER_BOUNDARY`, plus `HARD`, `SOFT`, or
`ASSUMED`. Otherwise the plan must classify it as
`REJECT_FALSE_BLOCKER:CONTINUE_LOCAL` and choose the next direct action. Every
long mission must include an ordered next-action ladder and one fallback per
likely preferred-tool failure, so a browser, test runner, PG transport, or
review-route failure cannot stop the full lane.

Use checkpoints only for new facts, stable diffs, receipts, or blockers. Do not
send unchanged heartbeats.

Immediately before `DONE` or a genuine hard `BLOCKED`, the worker wakes the
accountable manager with lane, state, exact token/blocker, branch/HEAD, receipt
path/hash/bytes, and one proposed next gap. The callback grants no next
authority. If messaging is unavailable, the final answer carries the same
packet.

The manager verifies hashes, paths, privacy/prohibited actions, tests/review,
C1/C2 separation, branch/base, remote equality, and clean state, then issues
the next dependency-ready hash-bound Work Order immediately. A periodic
snapshot may catch a missed callback, but it is a dispatch deadline and never
a worker stop point or a substitute for the mission file.

For recovery writes, the Work Order and receipt also bind absolute target root,
read-only reference roots, resolved write paths, preimage hashes, target
containment, reference post-hashes, and wrong-root rollback. If any write lands
outside the target root or output is truncated, repair the exact preimages and
verify them before issuing or accepting another Work Order.

For divergent-history or predecessor-adoption work, the manager also verifies
the integration-tip semantic result: bind decisive accepted paths or
predicates before integration, inspect the resulting blobs, rerun the focused
regression after integration, and refresh downstream Work Orders to that exact
tip. Merge ancestry alone is not acceptance.

Do not dispatch one-command prompts, replace a long mission with repeated
micro-prompts, accept early return after one phase, repeat aliases of a failed
route, assign filler research, or escalate routine choices to the owner.

## 7. Keep supporting files small

Create a supporting file only when it prevents the main plan from becoming
noisy:

- `CANONICAL-CHECKLIST.md`: concise dependency-ordered delivery ledger;
- `HANDOFF.md`: mutable restart checkpoint; never authority;
- `WORK-ORDER.md`: immutable, hash-bound execution authority;
- `DECISION.md`: accepted/open decisions with exact provenance;
- `RUN-RECEIPT.md`: immutable implementation or proof receipt.

For a complex program, `PLAN.md` plus `CANONICAL-CHECKLIST.md` are the normal
pair. Do not copy every optional template. A Work Order template grants no
authority until instantiated, frozen, and hash-accepted. Keep handoffs
explicitly subordinate to current Git/runtime and receipts. The compact pack has
one short `README.md` because it is the requested copy/use guide; do not add a
project README, changelog, duplicate plan, broad evidence dump, or copied
workbook by default.

## 8. Validate

Before finishing:

1. Resolve every routed local path.
2. Verify hashes/counts/status claims used for decisions.
3. Check encoding, final newline, and Markdown structure.
4. Confirm only intended documentation/template files changed.
5. State whether files are untracked, staged, committed, and pushed.
6. Report skipped runtime/browser/connector checks as skipped, not passed.

Return the main plan path, supporting files, the most important owner decision,
and one next action.

## Provenance (consolidated 2026-09-12)

Canonical body: `z-plan` (2026-08-15 14:12:40, 20 files, sha256 `4c1599d5530f606d`).

Former names now disabled: `AGENTS/xplan`, `CODEX/xplan`, `NINELLC/xplan`.

Unique content from disabled copies is preserved under `references/preserved/` and is NOT authoritative; this body wins on any conflict.
