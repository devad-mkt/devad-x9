# Worker Autonomy And Escalation

Use this before asking for authorization, creating a repair Work Order,
consulting THINKER/LOOPER, adding a visible task, or reporting `BLOCKED`.

## STYLE_ONLY role boundary

Thinker is decision-only: it reviews one stable material diff, a real
architecture/security boundary, or two distinct proof-bound failures; it does
not run the task queue or provide routine approvals. Looper is the single owner
of the ordered packet/lane queue: it continues dependency-ready safe work and
leads bounded repair/routing, but is not a second project manager and takes no
product-coding claims. Linker sends only exact canonical path/hash/result-
pointer signals and never chooses, transforms, approves, retries, or executes
work. A Worker implements only its claimed packet paths and returns proof. A
`Worker Loop Fix` is a narrow implementation Worker for STYLE
skill/package/install/host-integration defects, not a second Looper or manager,
and stops after its bounded result. Task creation leaves `thinking` unset.

## Action Classification

| Class | Rule | Action |
| --- | --- | --- |
| `EXECUTE_NOW` | Directly advances the current objective; stays inside the exact repository/worktree, claims, resources, STOP, and forbidden actions; local/read-only or reversible; no new external effect. | Execute immediately and continue. |
| `WORKER_LOCAL_REPAIR` | A recoverable implementation, test, tool, dependency, or environment problem inside the same authority envelope. | Record one compact checkpoint and try one bounded correction. Do not create a Work Order. |
| `SUBAGENT_ADVISORY` | One failed local approach or one difficult technical question where a separate reasoning session can change the next action. | Use at most one bounded internal subagent, then verify its answer. |
| `THINKER_REVIEW` | Two genuinely different evidence-bound approaches failed and judgment is needed, or architecture/security/contract evidence conflicts. | Ask the registered THINKER once with the compact proof packet. |
| `OWNER_ACTION` | Owner decision, contradictory requirements, destructive/irreversible action, production/deployment/provider/money/secret boundary, claim/resource expansion, or external authority not already granted. | Pause only the dependent action and request the smallest exact decision. |

A safe action does not become unsafe merely because an old plan did not list
the individual command. Authority is determined by objective, scope, effects,
claims, STOP, and explicit exclusions. Conversely, “harmless” narration never
authorizes scope expansion or an external effect.

## Authority Envelope

Before a Worker starts a chunk, the packet binds exactly:

```text
OBJECTIVE / CURRENT_CHUNK
OWNED_PATHS_AND_RESOURCES
ALLOWED_MUTATIONS
FORBIDDEN_EFFECTS
FOCUSED_PROOF_AND_ROLLBACK
AUTO_RESUME_EVENT
COLLISION_SET
```

Within that envelope, the Worker must diagnose -> smallest correction ->
focused proof -> continue. Parser, quoting, fixture, test-harness, local-tool,
and behavior-preserving claimed-path corrections are Worker-local. Keep a
same-root-cause low-risk problem local through three bounded correction cycles;
those cycles are not two distinct failed approaches. Escalate once after the
third only when the smallest next action needs new authority, cannot prove
cleanup, or exposes a real security/architecture boundary.

## Sticky Lane And Rebind

Keep the task, native worktree, branch, base, and exact claims stable until the
bounded source result is frozen. Ordinary coding, focused tests, local servers,
and browser proof proceed inside that lease. Do not reattach, rebase, copy, or
replace a valid lane merely because remote main advanced.

Set `REBIND_DUE` on remote movement, then perform one bounded semantic rebind
only at the next integration/release boundary. Rebind immediately only when
the task/worktree identity changes, a claimed shared path or runtime resource
changes, or new source/security/architecture evidence invalidates an accepted
assumption. A host that cannot attach the existing worktree is one owner/host
boundary; it is never authority to create a replacement worktree or copy a
dirty candidate. After one failed preserving move, one successor task inside
the already registered correct project may take over the existing candidate
only after it verifies `cwd`, branch, HEAD, staged state, and the compact
handoff acknowledgement. It must not create another worktree or replay bytes.

For a separable product domain, the sticky lane is also its
`DOMAIN_DELIVERY_BRANCH`. Accumulate eligible packet-bound chunks on that branch
until a meaningful domain milestone instead of performing per-chunk rebind,
rebase, PR, or review cycles. `AUTOPILOT_LOCAL` means the Worker directly starts
the next eligible local chunk and owns ordinary diagnosis, correction, and
focused proof. It does not widen the Authority Envelope or grant provider,
production, secret, deployment, merge, or shared-resource authority.

After local proof, deploy and test the exact branch/SHA as `RC_BRANCH_TEST`
without merging or rebinding first. Stage1 is the default RC target. An
unmerged production test requires separate exact owner approval for target,
branch/SHA, window, rollback, and stop conditions. Corrections stay on the same
branch and repeat RC proof there.

Only `OWNER_RC_APPROVED` plus finished product coding opens one bounded
current-main semantic rebind, frozen-range review, and integration disposition.
Before touching a path outside the domain envelope, send one
`CROSS_DOMAIN_CHANGE_NOTICE` to Looper with exact path, reason, effect, and
whether final-integration deferral is safe. Looper asks the owner only when
early claim expansion, merge, or rebind is genuinely required; otherwise the
shared hunk remains deferred and domain-local work continues.

At a real transition, record only:

```text
STATE: ACTIVE|WAITING_CAPABILITY|DEPENDENCY_WAIT|SHARED_SERIAL_WAIT|BLOCKED
CAN_CONTINUE_LOCAL: yes|no
EXACT_BLOCKER:
OWNER_ACTION:
AUTO_RESUME_EVENT:
PRE_WAIT_SWEEP: packet path; expected/observed packet SHA-256; blocked chunk/event;
  canonical authorized/inspected-with-eligibility/eligible candidate records,
  counts+SHA-256; selected exact packet-bound chunk/action or NONE;
  `LOCALIZATION_RECEIPT_PATH+SHA256` plus packet/inventory binding and outcome;
  expansion proposal path+SHA256 or NONE; optional LOCAL_CONTINUATION_RESERVE
  path+SHA256; one-time NO_AUTHORIZED_LOCAL_SLICE
```

An external receipt dependency is always
`DEPENDENCY_WAIT:<AUTO_RESUME_EVENT>`, never a terminal whole-goal `BLOCKED`
state. Before a Worker or Looper writes `CAN_CONTINUE_LOCAL:no`, it must make
one `PRE_WAIT_SWEEP` against the current packet: identify the dependency and
blocked chunk, compare expected/observed packet SHA-256 values, and compare
the complete authorized/inspected/eligible packet-bound candidate inventories.
Each `NEXT_AUTONOMOUS_CHUNKS` candidate needs an exact chunk ID,
`RECORD_SHA256`, paths/actions strictly within the envelope, receipt identities,
collision set, proof, rollback, STOP conditions, and `READY`, `COMPLETE`, or
`WAITING_RECEIPT` state. The gate derives the canonical authorized, inspected,
and eligible inventory hashes; every authorized record must have an inspected
eligibility result, and the selected action must be exactly one eligible
`READY` record. A plan heading or ordinary backlog prose is not authority. Any
eligible `READY` candidate, missing sweep, stale packet, incomplete candidate
inventory, scope-unclear candidate, or missing receipt alone is
`CONTINUE_LOCAL`; start the safe packet-bound action without asking Looper.
With zero eligible records, `BACKLOG_LOCALIZATION_REQUIRED` means perform
exactly one read-only backlog localization.
A useful but unbound local possibility becomes one local continuation record.
It starts without a Looper round only when its current `PROPOSAL_CREATED`
localization receipt proves it is inside the packet-bound
`LOCAL_CONTINUATION_RESERVE`: same objective/worktree, exclusive paths/actions,
focused proof/rollback, no shared resource, and no semantic or external effect.
Anything outside that reserve remains `CLAIM_EXPANSION_PROPOSAL` and waits for a
`CLAIM_EXPANSION_RECEIPT`. Shared/resource, semantic, security, or external-
effect expansion remains a Thinker/owner boundary. Only with no eligible
candidate and no pending localization/continuation route, write
`NO_AUTHORIZED_LOCAL_SLICE` once with the
exact resume event. A blocked dependency pauses only its dependent claim;
every disjoint authorized claim continues. Report an unchanged wait once, then
resume only on the named event. Do not add recurring wakeups, polling,
Controller state, or Work Orders to manage normal worker lanes.

The local `z-loop-style/scripts/style_autonomy_gate.py --wait-case` is the
compact admission check for this record. It rejects early waits to
`CONTINUE_LOCAL`; it does not create tasks, grant new claims, or intercept a
host task that has already been terminally ended.
On Windows PowerShell, pipe the JSON to `--case-stdin` instead of passing it
as an inline native argument, so quote loss cannot create a false local failure.
When it returns `DEPENDENCY_WAIT` with `should_subscribe=true`, send one exact
event handoff to the receipt producer. The producer returns one sanitized
terminal receipt directly to the named consumer and Linker; do not poll or send
the wait again.

A missing default Python alias or shell hash helper is a local tooling failure:
use the installed bundled interpreter or apply the same exact fields manually
with an available read-only hash tool. Record `LOCAL_FALLBACK` and continue;
do not clean the environment, install dependencies, or wait for Looper.

## Outcome-bound delivery budget

For one shared capability, bind one outcome packet before external execution:
finish predicate, complete local preflight, focused proof, cleanup/rollback,
and terminal branches. `PRE_WAIT_SWEEP` is one local/silent check immediately
before a true wait; it is never a separate routed result, review, or task.

Batch same-root parser, transport, harness, package-path, and receipt-format
corrections. Review only stable material bytes or a changed hard boundary. An
execution failure allows one read-only discriminator, followed by exactly one
final corrected batch/execution or one `HARD_BOUNDARY`. Do not create a child
packet, review an intermediate status, or rename the same retry.

A Worker may be `ACTIVE` only when its packet has a `READY` chunk or a
`LOCAL_CONTINUATION_RESERVE`; use `style_autonomy_gate.py --dispatch-case`
before starting it. Otherwise use `EVENT_ONLY` with one exact receipt and do
not keep the Worker alive for polling, narration, or unbound backlog discovery.
The reserve may allow one same-worktree branch rollover only after the prior
candidate is frozen and product bytes are clean; it never permits a new
worktree, rebase, merge, or deployment. Routing,
reservation, hashes, and status updates are not delivery progress.

This budget never relaxes secret, shared-resource, destructive, production,
spend, security, architecture, or owner boundaries.

## Canonical lane queue

Looper keeps the one durable ordered checklist with at most one active
shared-capability executor per non-overlapping canonical `COLLISION_SET`, not
one global unblock. A set contains canonical resource-identity keys and any
nonempty intersection conflicts. A waiting owner or capability item does not
stop disjoint dependency-ready items or a Worker-owned lane-local helper. For a
shared action, the Worker sends one `CAPABILITY_CLAIM` with packet pointer,
canonical keys, and exact action; the Looper atomically records packet/hash,
 action, keys, and bounded expiry before returning `CLAIM_FREE`, or returns
 `CLAIM_BUSY` on intersection. Release occurs only after a sanitized terminal
 receipt. Expiry alone never releases keys: one bounded reconciliation must
 first prove the executor stopped and cleanup/residue gates passed. New worker
 reports update their existing lane;
they do not
create competing plans, duplicate lanes, or a status-poll loop. A security
incident may preempt the active item. Otherwise, finish each durable receipt
and select every independent ready item immediately.

## Pre-Question Admission Gate

Run this gate before sending any message that asks another task, manager,
THINKER, or owner for permission, a decision, review, rescue, or next step.
Do not use another chat as a substitute for making a routine Worker decision.

1. Re-read the current task/Work Order, exact claims, STOP, exclusions, current
   Git/runtime identity, and newest durable correction.
2. Classify the proposed next action using the table above.
3. Search current source, focused tests, accepted decisions, and the execution
   sitemap for an existing answer. Do not search full chat history by default.
4. Apply the smallest current-repository-compatible reversible decision.
5. If the first route fails, try one structurally different safe local route
   or one bounded subagent when that can change the next action.
   Keep a same-root-cause low-risk correction local through three bounded
   cycles; it does not become a distinct-route escalation merely because the
   command or fixture changed.
6. Ask externally only when the result is `THINKER_REVIEW` or `OWNER_ACTION`.

The gate returns exactly one outcome:

| Outcome | Meaning |
| --- | --- |
| `CONTINUE_LOCAL` | Execute the safe action now. No outbound question. |
| `LOCAL_FALLBACK` | Try one materially different safe route and continue. |
| `SUBAGENT_ONCE` | Ask one bounded advisory helper, verify it, then continue. |
| `THINKER_ALLOWED` | A stable material diff, two distinct failed approaches, or a real architecture/security/contract conflict requires one review. |
| `OWNER_REQUIRED` | Only the owner can decide or authorize the exact remaining boundary. |

The following never pass this gate by themselves:

- the individual command was not listed in the plan;
- a tool alias, test command, fixture, or preferred route failed once;
- a reviewer has not approved harmless diagnosis or ordinary coding;
- the Worker wants reassurance about a reversible implementation choice;
- another task has more history or a stronger model;
- a command, test, review, or delegated task is still running;
- the next authorized dependency-ready action is already known.

If an outbound question is allowed, send one compact admission record:

```text
QUESTION_ADMISSION:
classification: THINKER_REVIEW | OWNER_ACTION
current_authority: <task/work-order/path+hash>
decision_needed: <one sentence>
local_evidence: <canonical path+hash>
distinct_failed_routes: <0|2 with receipt IDs>
why_worker_cannot_decide: <exact boundary>
safe_work_continuing: <action|NONE>
```

Missing or incomplete admission means `CONTINUE_LOCAL`, not `BLOCKED`.

For an outbound-question decision, use the packaged, stateless
`z-loop-style/scripts/style_autonomy_gate.py` with the same nine admission
fields, including `judgment_needed` and `same_root_cause_cycles`. It makes only
the five classifications above; malformed input returns
`CONTINUE_LOCAL`. It is not a Controller, scheduler, reminder, or host message
interceptor. The Worker still owns applying the result before it sends a chat
message.

## Work Order Granularity

Use one Work Order for one independently accepted outcome. Keep recoverable
substeps inside its attempt ledger or `WORKER_CHECKPOINT.json`.

Do not create separate Work Orders for:

- Composer/PHAR discovery already inside an environment-ready objective;
- process-local extensions or ordinary stderr classification;
- PID/process completion checks;
- a retry using the same objective, claims, resources, and STOP;
- a repeated review or context resend.

A new Work Order is justified only when objective, independently accepted
outcome, claimed files/resources, STOP contract, or owner/external authority
materially changes. When an equivalent active order exists, reuse it and record
`ACTIVE_WORK_ORDER_REUSED`.

## Bounded Expert Help

The separately installed `subagents` skill owns profile and dispatch mechanics.
Do not copy its model table or replace its rules here.

Default to no helper. When one is justified, the Worker owns the helper and
does not need Looper approval when the helper is local/read-only/reversible,
inside the Worker's existing worktree and claims, and outside every active
shared `COLLISION_SET`. A helper for a shared credential, resource, provider,
production, deployment, merge, security, architecture, destructive, spend, or
owner-only action is never lane-local. It may gather bounded evidence but
cannot replace required Thinker/owner disposition; use one `CAPABILITY_CLAIM`
or the existing hard-boundary route instead.

When one is justified:

1. use one active subagent per Worker at a time and no child nesting; distinct
   collision-free Workers may use their own helpers concurrently;
2. prefer `fork_turns="none"` and pass no full history;
3. send the exact goal, repository/worktree/base, named files, current
   evidence/failure, one question, acceptance test, forbidden actions, and a
   compact result schema;
4. include `TOKEN_MODE: LOW`;
5. use the lowest safe callable profile; a serious verified debugging question
   may use Sol high, while environment or permission failures stay route
   corrections;
6. keep the helper advisory and within the parent task's authority;
7. have the Worker verify decisive claims and own all edits, tests, release
   gates, and final proof.

If the subagent skill is unavailable, use one genuinely different bounded
local approach. Do not create a visible replacement Worker merely to obtain a
stronger answer.

## Proof-Bound Escalation

Each failed approach needs a unique canonical receipt binding:

- Work Order/task and action class;
- approach ID and SHA-256;
- hypothesis and exact attempted route;
- relevant source/tool hashes;
- result/failure code;
- evidence path and SHA-256;
- progress delta;
- next materially different approach.

The same route, prompt, command, evidence, or failure repeated with no progress
does not increment the count. After two distinct failed approaches, a Worker
may ask one registered THINKER only when judgment is needed. A THINKER request
for a routine safe action returns
`ROUTINE_DECISION_WORKER_LOCAL`.

Deduplicate consultation and review by stable identity:

`work_order_id + action_class + review_class + question/evidence hash + staged-tree hash`

An identical request returns the prior durable verdict and consumes no new
model review.

## Review Is Quality Control, Not Coding Permission

One stable frozen-diff review is valid when repository policy requires it or
the changed bytes cross a real Controller, architecture, or security boundary.
The Worker does not ask whether it may continue routine coding before that
point.

A review `BLOCK` containing concrete file/line findings is defect evidence, not
an owner blocker. The Worker fixes the findings inside its existing claims,
reruns only affected gates, and requests one review of the new staged tree.
Unchanged bytes reuse the prior verdict. Do not create a new Work Order,
architecture consultation, or owner question for the correction cycle.

If two materially different corrections still cannot satisfy the same
boundary, record their approach receipts and use the normal `THINKER_REVIEW`
or `OWNER_ACTION` classification. Continue every disjoint authorized action.

## Compact Transfer

Use the existing owner-context bundle, source-backed `CONTEXT_CAPSULE.json`,
Feature Packet, Work Order, and project Brain/docs sitemap. Do not create a
second memory or authority system.

Every lower-cost model or new task receives a self-contained, hash-bound
execution sitemap with direct links to:

- owner goal and active corrections;
- repository/worktree/base and current state;
- exact scope, claims, resources, and dependencies;
- actionable implementation sequence;
- acceptance tests and release/security gates;
- forbidden actions and STOP;
- evidence/result locations;
- exact next action.

Chat or callback messages contain only stable IDs, canonical path, SHA-256, and
one requested action. The receiver rereads the durable packet. Send deltas for
new corrections; never resend full history, skills, plans, diffs, or accepted
proof. A failed chat/callback route is a soft transport defect: preserve the
canonical receipt pointer, do not call product work blocked, and do not create
a replacement manager or duplicate worker lane.

## Enforcement Status

This reference is immediate Worker/manager behavior. The Style checker makes
the five-way admission deterministic locally, but host-level interception of
arbitrary Codex messages remains unavailable. Do not claim it proves distinct
approaches, deduplicates reviews, rejects micro-Work-Orders, or changes an
already-running task without an explicit steering message.
