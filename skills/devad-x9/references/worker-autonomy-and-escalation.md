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
| `THINKER_REVIEW` | Two genuinely different evidence-bound approaches failed, or architecture/security/contract evidence conflicts. | Ask the registered THINKER once with the compact proof packet. |
| `OWNER_ACTION` | Owner decision, contradictory requirements, destructive/irreversible action, production/deployment/provider/money/secret boundary, claim/resource expansion, or external authority not already granted. | Pause only the dependent action and request the smallest exact decision. |

A safe action does not become unsafe merely because an old plan did not list
the individual command. Authority is determined by objective, scope, effects,
claims, STOP, and explicit exclusions. Conversely, “harmless” narration never
authorizes scope expansion or an external effect.

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

At a real transition, record only:

```text
STATE: ACTIVE|WAITING_CAPABILITY|WAITING_DEPENDENCY|SHARED_SERIAL_WAIT|BLOCKED
CAN_CONTINUE_LOCAL: yes|no
EXACT_BLOCKER:
OWNER_ACTION:
AUTO_RESUME_EVENT:
```

`BLOCKED` means no safe main-plan or accepted fallback action remains. A
blocked dependency pauses only its dependent claim; every disjoint authorized
claim continues. Report an unchanged wait once, then resume only on the named
event. Do not add recurring wakeups, polling, Controller state, or Work Orders
to manage normal worker lanes.

## Canonical lane queue

Looper keeps the one durable ordered checklist with at most one active unblock.
A waiting owner or capability item does not stop disjoint dependency-ready
items. New worker reports update their existing lane; they do not create
competing plans, duplicate lanes, or a status-poll loop. A security incident may
preempt the active item. Otherwise, finish its durable receipt and select the
next ready item immediately.

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

Default to no helper. When one is justified:

1. use one active subagent at a time and no child nesting;
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
does not increment the count. After two distinct failed approaches, ask one
registered THINKER. A THINKER request for a routine safe action returns
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
proof.

## Enforcement Status

This reference is immediate Worker/manager behavior. Until the matching Loop
Controller hotfix, record `AUTONOMY_CONTROLLER_ENFORCEMENT_PENDING`. Do not
claim that prose prevents direct task messages, proves distinct approaches,
deduplicates reviews, or rejects micro-Work-Orders.
