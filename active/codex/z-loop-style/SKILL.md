---
name: z-loop-style
description: Use as the default lightweight Devad X9 coordination style for normal project work. It keeps V6-style self-contained packets, exact Git evidence, direct result handoffs, and autonomous Workers without starting the V7 Controller, Work Orders, ACTION transport, recovery, or recurring monitors.
---

# zLoopStyle

## Default

Use `STYLE_ONLY` unless the owner explicitly selects a separately proven V7
canary. Read `$z-x9` first, then
[the operating reference](references/v6-style-operating.md). This skill is
the normal route for Thinker, Looper, Linker, and Worker project coordination.

Do **not** run `loopctl`, activate a Controller, create a Work Order, dispatch
an ACTION, register a role, recover V7 state, or start a recurring monitor.
The retained `$z-x9-legacy` compatibility name redirects to this skill.
`$z-loop-code` is the separately named, quarantined Controller trial; it is
not the default operating authority.

## One bounded work packet

Before implementation, create or reread one compact durable packet containing:

- a compact identity: `lane_id`, task, role, repository, existing worktree,
  branch, base, head, and `PRESERVED_CANDIDATE`, `INTEGRATED`, or
  `LIVE_PROVED` candidate state;
- exact exclusive paths, shared resources, allowed mutations, forbidden
  effects/external-effect ceiling, focused proof, rollback, collision set, and
  STOP conditions;
- either `NEXT_LOCAL` or `DEPENDENCY_WAIT:<EVENT>`. A dependency declaration
  names the missing receipt/capability owner, blocked chunk, `RESUME_ON` receipt
  type/hash, expiry/staleness rule, and exact next action. Its packet may bind
  `NEXT_AUTONOMOUS_CHUNKS`, where every canonical candidate record carries
   `CHUNK_ID`, `RECORD_SHA256`, exact paths and allowed action as strict subsets
   of this envelope, required receipt identities, collision set, focused proof,
   rollback, STOP conditions, and `READY`, `COMPLETE`, or `WAITING_RECEIPT`
   state. `LOCAL_CONTINUATION_RESERVE` may bind an exclusive path/action domain,
   focused proof, rollback, effect ceiling, and an optional same-worktree branch
   rollover after the prior candidate is frozen and product bytes are clean. An
   `ACTIVE` lane must have a `READY` chunk or that reserve; otherwise it is
   `EVENT_ONLY` and is not kept open waiting. A plan heading or ordinary backlog
   sentence is never execution authority. Before either a Worker or
  Looper declares that no local route remains, bind one `PRE_WAIT_SWEEP` to the
  current packet path plus expected/observed packet SHA-256 values, and
  canonical authorized, inspected-with-eligibility, and eligible candidate
  records/counts/SHA-256 values; selected exact chunk/action or `NONE`; named
  dependency event and blocked chunk; and a read-only
  `LOCALIZATION_RECEIPT_PATH+SHA256` bound to the current packet and authorized
  inventory, with outcome
  `NOT_RUN`, `NONE_FOUND`, or `PROPOSAL_CREATED`;
- current source evidence, acceptance tests, security/release gates, rollback,
  and STOP conditions;
- the next safe action and the task that owns it.

Existing Git, source, tests, and durable receipts are truth. Chat is a
signal-only pointer to a packet or result; do not resend history. Verify a
capability before planning replacement work. A missing owner relation blocks
only that affected task.

## Optional context, memory, and docs

Style can use the existing source-backed Project Intelligence contract at
[project-intelligence-v1.md](references/project-intelligence-v1.md),
`$z-memory`, and `$z-docs`. Before planning and before the first
behavioral edit, re-read the capsule’s source spans at the current Git SHA.
Memory, chats, graphs, Sheets, and RAG only help locate candidates; none can
authorize a task.

After an accepted Style result, generate the compact feature sitemap and docs
from the bound `x9-loop-style-result-v1` receipt described in
[style-result-receipt.md](references/style-result-receipt.md). The generated
docs and profile-local memory are derived context, never a Controller,
dispatch, claim, or routing authority.

## Roles

| Role | V6-style responsibility |
| --- | --- |
| Thinker | Decision-only: review one stable material diff, a real architecture/security boundary, or two distinct proof-bound failures. It does not own routine approvals or the queue. |
| Looper | The single owner of the ordered packet/lane queue: continue dependency-ready safe work and lead bounded repair/routing. It does not merely report, become a second project manager, or take product-coding claims. |
| Shared-capability helper | One execution-only packet **per active, non-overlapping canonical `COLLISION_SET`**, not one global helper. A set contains canonical resource-identity keys; any nonempty intersection conflicts. The Looper atomically records a bounded reservation before dispatch. It cannot select work, manage Workers, take product-code claims, decide priority, create a second queue, or run V7. It returns one sanitized terminal receipt directly to the Looper and named subscriber. |
| Lane-local helper | A Worker may own one bounded `$z-subagent` helper when its scope is inside that Worker's existing worktree and claims, local/read-only/reversible, and outside every shared collision set. It needs no Looper approval and cannot use shared credentials/resources, provider/production/deploy actions, Git integration, security/architecture, destructive/spend, or owner-only decisions, or child nesting. It may gather evidence but cannot replace Thinker/owner disposition. The Worker verifies its result and remains accountable. |
| Linker | Send only exact canonical path/hash/result-pointer signals. It never chooses, transforms, approves, retries, or executes work. |
| Worker | Implement only its claimed packet paths, return focused proof, and record the bounded result. A `Worker Loop Fix` is a narrow Worker for STYLE skill/package/install/host-integration defects; it is not a second Looper or manager and stops after its bounded result. |

Use short task titles: `Thinker`, `Looper`, `Linker`, or `Worker` plus a one-
or two-word suffix; `Worker Loop Fix` is a valid narrow Worker title. Creation
defaults never overwrite an existing task's model or reasoning; every follow-up
omits both. Task creation leaves `thinking` unset. If an explicit setting is
needed, use only a host-advertised model/reasoning pair.

## Domain delivery branches

For each separable domain, keep one `DOMAIN_DELIVERY_BRANCH` in one existing
native worktree. Accumulate packet-bound chunks there; do **not** create a
branch, rebind, rebase, PR, or review per chunk. Remote-main movement is only
`REBIND_DUE`; local work continues.

`AUTOPILOT_LOCAL` selects the next eligible chunk, repairs ordinary owned
failures, proves it, and continues without Looper permission. It is not a
background wake and grants no wider path, runtime, provider, production,
merge, deploy, or secret authority.

After local proof, deploy and test the exact domain branch and commit SHA as
`RC_BRANCH_TEST`; do not merge or rebind first. Stage1 is the default RC target.
An unmerged-branch test on production requires separate exact owner approval
for target, branch/SHA, window, rollback, and stop conditions. Fix RC findings
on the same domain branch and redeploy that branch.

Only `OWNER_RC_APPROVED` plus finished product coding opens integration. Then
perform one bounded current-main semantic rebind, one frozen-range review, and
one integration PR or merge disposition. Only actual
shared-path intersections serialize: the named integration owner applies those
shared hunks once after the contributing domain candidates are frozen.

Before touching a path outside the domain envelope, the Worker sends one
`CROSS_DOMAIN_CHANGE_NOTICE` to the Looper with the exact path, reason, effect,
and whether it can wait until final integration. The Looper asks the owner only
when the case genuinely requires early claim expansion, merge, or rebind;
otherwise it records the deferred shared hunk and the Worker continues its own
domain. No early integration is inferred from a notice.

## Autonomous flow

1. Check repository, base, local changes, claimed paths, and the packet.
2. Classify a question as `CONTINUE_LOCAL`, `LOCAL_FALLBACK`,
   `SUBAGENT_ONCE`, `THINKER_ALLOWED`, or `OWNER_REQUIRED`.
   Before sending an outbound permission, decision, review, rescue, or
   next-step question, use the small local checker in
   `scripts/style_autonomy_gate.py` or apply its exact fields. A malformed or
   missing admission returns `CONTINUE_LOCAL`; one failed tool, fixture, alias,
   command, or preferred route returns a local fallback, never `BLOCKED`.
3. Implement and run cheap/focused proof first. Inside the Authority Envelope,
   the Worker must diagnose -> make the smallest owned correction -> run
   focused proof -> continue; it does not seek Looper permission for a parser,
   harness, fixture, quoting, local-tool, or bounded implementation repair.
   A single real external receipt dependency is
   `DEPENDENCY_WAIT:<AUTO_RESUME_EVENT>`, not a whole-task `BLOCKED` result.
   It pauses only that lane; immediately continue any disjoint safe work. The
   pre-wait sweep must inspect every packet-bound `NEXT_AUTONOMOUS_CHUNKS`
   candidate, not merely the current active chunk. The gate derives the three
   inventory hashes from canonical records, verifies every authorized record
   was inspected, and requires the selected action to match one eligible
   `READY` record. That chunk starts immediately with its recorded action,
   without Looper approval. If no
   eligible authorized chunk exists, the gate returns
   `BACKLOG_LOCALIZATION_REQUIRED`: perform one read-only backlog localization.
   A useful but unbound possibility becomes one compact local continuation
   record. It may start immediately only when its current
   `PROPOSAL_CREATED` localization receipt proves it is inside the packet-bound
   `LOCAL_CONTINUATION_RESERVE`, same objective/worktree, exclusive paths/actions
   and effect ceiling, with focused proof/rollback and no shared, semantic, or
   external effect. `style_autonomy_gate.py --wait-case` then returns
   `LOCAL_CONTINUATION_READY`; no Looper round is needed. A proposal outside
   that reserve remains `CLAIM_EXPANSION_PROPOSAL` and waits only for
   `CLAIM_EXPANSION_RECEIPT`. Shared-resource, semantic, security, or
   external-effect expansion remains a Thinker/owner boundary. Only after no
   eligible chunk and no pending localization/continuation route may the Worker record
   `NO_AUTHORIZED_LOCAL_SLICE` once and wait for the exact dependency event.
   Run `scripts/style_autonomy_gate.py --wait-case` immediately before that
   wait. A missing, incomplete, stale-packet, candidate-inventory mismatch,
   scope-unclear, or eligible-local-action sweep is `CONTINUE_LOCAL`, never
   permission to wait. A missing receipt alone also remains `CONTINUE_LOCAL`:
   it first needs this valid sweep. A Looper must
   not send `CAN_CONTINUE_LOCAL:no` from an old plan or a single finished local
   check; it must point to the current packet and valid `PRE_WAIT_SWEEP`.
   From Windows PowerShell, pipe the JSON to `--case-stdin` rather than
   passing an inline native argument; its schema chooses the same stateless
   classifier without quote loss.
   When that gate returns `DEPENDENCY_WAIT` / `should_subscribe=true`, send one
   exact event handoff to the declared receipt producer: event, consumer task,
   receipt predicate, expiry, and pre-bound resume action. Do it once; the
   producer sends its terminal receipt directly to the consumer and Linker.
   This is point-to-point transport, not a board, poll, or approval request.
   A matching eligible packet-bound candidate starts immediately without Looper
   approval. This does not let a Worker promote ordinary backlog prose into a
   claim or widen its envelope.
   If the default Python alias or shell hash helper fails, this is
   `LOCAL_FALLBACK`, not a wait: use the installed bundled interpreter when it
   is available, or apply the identical fields manually with the available
   read-only hash tool and record the fallback. Never clean an environment,
   install a package, or ask Looper merely to run this local classifier.
   The gate does not invent work, widen claims, bypass a real external boundary,
   or host-intercept a terminal Codex task state; if a host goal has already
   been ended, the user or task host must reopen that same task.
   Before declaring that no local route exists, a Worker may use one
   lane-local helper under `$z-subagent` to answer one decision-changing,
   isolated technical question. It must not create a competing helper for an
   already-claimed shared resource. For a shared external action, send one
   compact `CAPABILITY_CLAIM` containing the packet pointer, canonical resource
   keys, and exact action. The Looper rejects a nonempty intersection as
   `CLAIM_BUSY`; otherwise its one check-and-record atomically reserves the
   keys with packet/hash, action, and bounded expiry before returning
   `CLAIM_FREE`. Release occurs only after a sanitized terminal receipt. Expiry
   alone never releases keys: one bounded reconciliation must first prove the
   executor stopped and cleanup/residue gates passed. This is collision control,
   not an approval review. A free,
   already-authorized set may proceed without waiting behind an unrelated
   helper.
   A matching fresh `RESUME_ON` receipt resumes the predeclared action without
   another approval. A stale, mismatched, expired, or duplicate receipt is
   `ZERO_DELTA`, not a new packet, retry, or escalation. The stateless receipt
   classifier in `scripts/style_autonomy_gate.py --receipt-case` is a small
   guard for this decision; it stores nothing and cannot wake a task.
   Keep the current task, worktree, branch, and exclusive paths as a sticky
   lane while its bounded result is in progress. Remote-main movement alone is
   `REBIND_DUE`, not a reason to stop, reattach, rebase, copy, or replace the
   Worker. Rebind only at an integration/release boundary or on an actual
   identity, shared-claim, resource, or assumption change.
   If the host attaches the task to the wrong worktree, first keep the task if
   its correct existing worktree is writable. Otherwise try one host-supported
   move that preserves that worktree. If that is unavailable, create one
   same-project successor task, give it the compact packet, and verify its
   `cwd`, branch, HEAD, staged state, and candidate acknowledgement before
   marking the old task superseded. Never create a replacement worktree, copy
   dirty bytes, or retry attachment routes.
4. A same-root-cause low-risk correction remains Worker-local through three
   bounded correction cycles; it is not two distinct failed routes. Request
   one Thinker review only for a stable material diff, a real
   architecture/security boundary, or two distinct proof-bound failed routes
   where judgment is actually needed.
5. Write a compact durable result with base, changed paths, tests/security,
   remaining risk, rollback, and next owner. Send one `RESULT_READY` signal.

Routine local/read-only/reversible inspection, coding, tests, formatting,
commits, push/readback, and dependency-ready next actions are already
authorized inside the packet. Never call a lane `BLOCKED` because a reviewer
has not approved routine work. After one difficult same-scope failure, use at
most one bounded lane-local helper according to `$z-subagent`; do not create
an escalation loop or make the Looper a helper-approval desk.

Looper keeps one durable ordered checklist, not competing chat todos or a
status-poll loop. It uses canonical resource-key `COLLISION_SET`s to serialize
only a nonempty intersection; it must atomically reserve a shared set before
dispatch and must not serialize unrelated lanes behind a single helper. It
records one `AUTO_RESUME_EVENT` per unavailable dependency
and, after verification, sends one direct message only: `EVENT + receipt
path/hash + exact resume action + stop conditions`. Routing a message is not
progress. When one item waits, continue every dependency-ready item whose
collision set is independent; resume the waiting lane only on its named
receipt. Run capability-first preflight once per new external capability epoch
(worktree/writer, runtime, secret transport, private network, rollback/backup,
or browser/build support), never once per product chunk. A security incident
may preempt the checklist. Otherwise, a worker message updates its existing
lane and never creates a duplicate lane. A failed callback or chat route is a
soft transport defect: preserve the receipt pointer and retry neither product
work nor a new manager lane.

The checker is a decision aid, not a background service or host interceptor.
It deliberately has no `BLOCKED` result, no state file, no reminder feature,
and no task creation. A true external boundary pauses only its dependent lane;
the Looper immediately selects the next packet item already safe to execute.

## Outcome-bound delivery

Treat one shared capability packet as one outcome, never as a stream of
micro-packets, status reviews, or renamed retries. Before its external action,
bind the finish predicate, all local preflight checks, focused proof,
cleanup/rollback, and terminal branches in that packet.

- Run `PRE_WAIT_SWEEP` locally/silently before a true wait; it is never a
  routed result, review, task, or reason to pause a ready action.
- Batch same-root corrections; after one failed execution use one discriminator
  then one final batch or `HARD_BOUNDARY`, never child packets or renamed retries.
- Long-running packets need real continuation chunks where possible; otherwise
  use a terminal dependency, never a polling or invented-work loop.
- `EVENT_ONLY`/`SOURCE_COMPLETE` is terminal local state. Do not wake an idle
  Worker to restate it: only a new hash-bound `READY` mission or matching
  `RESUME_ON` may arrive. Keep one capability owner; after `OWNER_REQUIRED`,
  route the minimum owner action once and stop relaying.
- Routing, a reservation, a hash, or a status update is not delivery progress.
  Only a focused product proof, an accepted material result, or a terminal
  authority boundary changes the lane.

This is guidance for loaded tasks, not host interception. Apply it directly to
an already-running task; a later skill installation cannot retroactively stop
an in-progress packet chain.

## Safety and fallback

Apply `DISPOSABLE_TEST_TRANSPORT` only as defined in the operating reference;
it never weakens product/data invariants or proves transport/deploy/live gates.

Never use style mode to bypass a live controller action, identity/receipt
mismatch, claim conflict, security gate, provider/deploy boundary, destructive
action, or production decision. Those remain fail-closed or owner-bound.

If there is no active V7 action and the host cannot route a task or worktree,
record `STYLE_FALLBACK_AVAILABLE` and continue only through this packet flow.
Do not automatically switch on test or code failures; fix those locally first.
The host cannot enforce arbitrary Codex messages, task models, or task wakes;
record that limitation honestly.

## Completion labels

Use exact labels only when proven: `STYLE_APPLIED`,
`SKILLS_VERIFIED_EXISTING`, `SKILLS_INSTALLED`,
`LOOP_PROFILE_INITIALIZED`, and `LOOP_ACTIVATED`. `VERIFY_ONLY` is never an
installation claim.

## Preserved capabilities (merged 2026-09-12)

Unique content recovered from archived variants. The canonical body above
wins where they overlap; these sections are the non-overlapping remainder.

### From `CODEX__x9-loop-style`

```text
GOAL_OUTCOME:
EVIDENCE_TARGET:
FAILED_ROUTE:
WHY_ROUTE_FAILURE_APPLIES_TO_ALL_ALLOWED_ROUTES:
CHEAPEST_WORKAROUND_TESTED:
ACTION_NOW:
NEXT_MATERIAL_ACTION_OR_TRUE_OWNER_BOUNDARY:
CONSTRAINT_CLASS: HARD|SOFT|ASSUMED
```


## Provenance (consolidated 2026-09-12)

Canonical body: `z-loop-style` (2026-08-15 14:12:40, 6 files, sha256 `648bfb64656e448c`).

Former names now disabled: `CODEX/x9-loop-style`, `NINELLC/x9-loop-style`.

Unique content from disabled copies is preserved under `references/preserved/` and is NOT authoritative; this body wins on any conflict.
