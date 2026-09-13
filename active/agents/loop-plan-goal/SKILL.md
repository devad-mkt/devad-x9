---
name: loop-plan-goal
description: Protect long-running recovery and delivery goals from focus drift, wrong-root edits, feature loss, duplicate planning, and unsupported completion claims. Use when work spans many turns, branches, agents, historical implementations, evidence packs, or a recovery plan followed by a main plan.
---

# Loop Plan Goal

Maintain one durable, read-by-need program package and one active product slice. Preserve accepted old and new behavior before changing either.

## Start Here

1. Read the program `INDEX.md` only.
2. Follow its routes to the active slice, canonical checklist, and at most one relevant domain file.
3. Truth-lock the exact repository root, branch, HEAD, upstream, dirty paths, and owned-file preimages.
4. Reconstruct the accepted denominator before editing an existing surface.
5. Execute one bounded slice through implementation, independent review, and proportionate proof.

Do not repeatedly reread every plan, rule, skill, or evidence file. Record which inputs were loaded in the slice receipt.

## Skill Routing

- Use `$z-plan` only to create or materially reorganize the durable package.
- Use `$z-subagent` for a complex fail-closed slice needing strict independent admission and review, and for a lean evidence-to-implementation team on one clearly bounded slice. Both modes now live in one skill; pick the mode, never run two competing managers for the same slice.
- Use `$z-memory` only for a bounded historical-evidence query. Memory is evidence, never source authority.
- Use domain skills only after the active slice and owned files are fixed.

## Round and delegation economy

Treat accepted evidence and review receipts as durable cache entries keyed to
their target root, relevant source/reference bytes, denominator, and acceptance
criteria. Reuse them until one key materially changes; do not redispatch
evidence or review merely to reconfirm an unchanged claim.

Default to parent execution. When independent help is useful, run at most one
cheapest-adequate bounded subagent at a time with exact scope and receipt
fields. Reuse that agent for follow-up; do not fan out, retry-spawn, or permit
helper-to-helper delegation. The parent verifies the receipt before it changes
the active slice or completion state.

## Focus Lock

- The canonical checklist is the queue authority.
- A new user, thinker, or looper message becomes a side task unless the owner explicitly accepts it as `SUPERSEDES`, `BLOCKS`, or `PROMOTES_TO_MAIN`.
- Generic messages such as `continue the main plan` cannot skip an active recovery slice or accepted user review gate.
- After at most two planning-only turns, start a safe product/proof action or name the exact external receipt required.
- A route 200, blank page, zero-row fixture, source string, screenshot without interaction, or subagent `PASS` cannot close a feature-rich surface.

## Goal Clarity Contract

Keep one stable generic goal for the whole program. Do not rewrite, resend, or
specialize that goal after normal rounds merely because the active slice or its
proof state changed. The goal owns durable scope, sequence, invariants,
completion rules and deferred scope; the checkpoint and canonical checklist own
changing progress, current slice, receipts, blockers and next action. Update the
goal only when the owner explicitly changes one of its durable fields.

Present the master goal once when the owner creates or explicitly restarts the
long-running loop, or when the owner directly asks to see it. At every ordinary
round boundary, return only the checkpoint delta, proof matrix, remaining gate
and one next action. Never generate a replacement goal, versioned goal, channel-
specific goal, or new paste prompt merely because a C-row, channel, feature,
worker or proof round changed. Never ask the owner to restart the loop to apply
normal progress; the durable checkpoint is the resume authority.

Never use the current slice as shorthand for the whole program goal. Every
long-running goal and checkpoint must separately state:

`PROGRAM_SCOPE | SERIAL_QUEUE | CURRENT_SLICE | PER_VERTICAL_STEPS |
ADVANCE_GATE | AFTER_CURRENT_PHASE | DEFERRED_SCOPE`

For “channel by channel and feature by feature” work, list the complete channel
queue and one fixed feature checklist applied inside every channel. Say plainly
that the current channel is only one queue item, not the complete release. A
later channel cannot start early, but it must remain visible in the program
scope so serial execution is not mistaken for permanent exclusion.

## Completion Claim Matrix

Require every plan row, worker receipt, review, and parent acceptance to separate applicable axes:

`SOURCE | TEST | BROWSER | PERSISTENCE | PROVIDER_EFFECT | DEPLOY | PRODUCTION | OWNER_ACCEPTANCE`

Use `NOT_STARTED`, `PARTIAL`, `PASS`, `FAIL`, `UNKNOWN`, `NOT_REQUIRED`, `EXTERNAL_GATED`, or `DEFERRED_PRESERVE` per axis. Reject bare `done`, `complete`, `working`, `ready`, `restored`, `adopted`, or `PASS`.

A screenshot, route 200, browser-memory draft, disabled control, fake, test, or subagent verdict proves only its named axis. `DEPLOYED` does not mean `PRODUCTION_PROVED`. A feature is complete only when its active checklist row names every required axis and each required axis passes. Defer preserves the accepted baseline; it does not remove or complete it.

`EXTERNAL_GATED` is valid only when the remaining behavior genuinely requires
external authority or an unavailable external runtime. Evidence classification,
a missing adapter, an unwired worker, an empty route stub, or unimplemented
local source is local work, not an external gate. The parent must override a
reviewer `PASS_EXIT` that closes a required product row by merely cataloguing it.

For settings and integrations, enforce these translations in every parent and subagent packet:

- `reference note` means documentation/evidence only, never a product control;
- `rendered field` means UI only until a named authorized save/reload owner passes persistence proof;
- `connected account` means only the proved compatible account/OAuth seam, never CHAT callback, inbound, outbound, receipt, retry, revoke, deploy, or production proof;
- `disabled action` means unavailable/unknown effect, never implemented behavior;
- `manual user-owned credentials` means the customer owns the provider app/integration and supplies credentials; it removes Devad-managed OAuth/install/discovery/provisioning only, never the required secure persistence, authorization, provider adapters, lifecycle, or proof;
- `channel complete` requires its declared Connect and General settings axes to pass one provider vertical at a time.

For a mixed provider queue, the durable plan must name exactly which channels
belong to each connection class. A worker may not infer a class from another
product, add a provider to a class, or translate `manual` into `UI-only` or
`backend not required`. Pass the exact class and channel list to every evidence,
implementation, review, test, and browser packet.

If work stops mid-vertical, the checkpoint must list exact changed files, the last verified source state, every unrun gate, and the single restart action. The next agent must resume that vertical before selecting another feature unless a newer owner message explicitly supersedes it.

Put the required axes in every subagent admission packet. Require the receipt and reviewer verdict to return the matrix. The parent must reject any broader claim or silently missing axis.

## Resume and Message-Flood Gate

Run this gate after interruption, compaction, long waits, tool failure, several queued messages, or any phrase such as `continue`, `resume`, or `from the interrupted point`:

1. Read the one durable checkpoint, not the chat transcript as authority.
2. Revalidate root, branch, HEAD, dirty paths, active process, and latest proof.
3. Build an intent delta from every message received since the checkpoint. Classify each as `SAME_SLICE`, `CORRECTION`, `SIDE_TASK`, `SUPERSEDES`, or `CONFLICT`.
4. Compare the proposed next action with `ROOT_OBJECTIVE`, `ACCEPTANCE`, `CURRENT_SLICE`, `DEFERRED_NOT_LOST`, and `ONE_NEXT_ACTION`.
5. Continue the recorded next action only when current evidence and the newest owner correction still support it. Otherwise update the checkpoint first.

Never say `continuing from the interrupted point` without naming the rebound current slice and next material action internally. Never let a queued thinker/looper continuation message override a newer owner correction. Use `solve-before-stopping` only for route recovery; use `ultra-reasoning-protocol` at Deep depth when intent or authority conflicts remain.

The checkpoint fields are:

`ROOT_OBJECTIVE | ACCEPTANCE | AUTHORITY_AND_SOURCE | CURRENT_SLICE | ACCEPTED_FACTS_AND_PROOF | IN_FLIGHT_SUBTASKS | BLOCKERS_AND_UNKNOWNS | DEFERRED_NOT_LOST | ONE_NEXT_ACTION`

## Serial Comparison And Protected-Surface Gate

“One channel/feature at a time” applies to the entire team, not only the implementer. While one vertical is active, do not dispatch evidence, memory, implementation, review, test, or browser packets for later verticals. A broad catalog index may name later rows but must not inspect or decide them.

Before the active vertical changes source, compare current target owners with every task-authorized historical candidate and select one documented semantic union. Continue the best existing owners; never restart from zero merely because an older commit is inconvenient to locate. Record exact SHAs/paths, conflicts, rejected candidates, and a `DO_NOT_REBUILD` list. `UNKNOWN` history is a gate, not evidence that no implementation exists.

When the owner protects a shared page, shell, modal architecture, or sibling feature, freeze it as a retention baseline. The active vertical may edit only its dedicated component and the smallest required shared binding. Any shared-surface change requires an explicit necessity tied to the active vertical plus regression proof for every protected interaction it touches.

Only after the active vertical reaches an explicit accept, external-gate, defer, or supersede decision may the parent admit the next vertical. Subagent availability, idle time, or a generic continuation message never authorizes speculative work on later rows.

### Single-pass vertical budget

Each admitted channel/feature gets one current-source/history/reference pass,
one parent semantic-union decision, one grouped implementation pass, focused
proof while bytes move, and at most one independent stable-byte review. Reopen
evidence or review only for a material source/reference/predicate change or a
confirmed P1/P2. Checklist narration, hashes, formatting and unchanged proof
do not start a new round.

Before `NEW`, the active receipt must map the existing UI, route/request,
authorization, service, persistence, effect/adapter and tests and must state why
none can be extended. Prefer the fewest compatible existing owners and files.
Reject speculative abstractions, duplicate account/settings stores, unbounded
queries, polling loops, and background infrastructure without a measured
product need. The accepted vertical must remain easy to maintain and bounded
in DB, CPU and RAM use.

When an authenticated reference UI is part of the denominator, its evidence
card must include a redacted browser DOM/action inventory: visible controls,
tabs/menus/modals, collapsed regions, hidden or conditional nodes, disabled
states, defaults/errors, and observed request/effect ownership. Label each item
`VISIBLE`, `RENDERED_HIDDEN`, `CONDITIONAL_NOT_RENDERED`, `DISABLED`, or
`ABSENT`; visible screenshots alone are incomplete.

Use no more than one active bounded helper for the vertical. Mechanical history
or DOM collection may use the cheapest admitted runtime; architecture,
security, semantic-union selection and acceptance remain with the parent. Do
not run evidence, implementation and review agents concurrently against the
same files.

Provider/feature folders may be created ahead of time only as stable queue
destinations. Mark every non-active folder `QUEUED_NOT_ADMITTED`. Folder
existence, a placeholder README, or an old report never authorizes reading its
history, dispatching an agent, changing source, or claiming progress. The
active folder alone may move through `EVIDENCE_SEARCH_RUNNING ->
EVIDENCE_ACCEPTED -> SEMANTIC_UNION_SELECTED -> CURRENT_CANDIDATE ->
LOCAL_ACCEPTED/DEFERRED_PRESERVE`.

For each admitted channel, its single evidence pass must inspect the existing
product-admin provider/settings surface and workspace Add/Connect surface,
including reusable shell/components, validation, encrypted-secret handling,
redaction, authorization and focused tests. This applies to OAuth and
manual-key channels alike. Cache the comparison until a material byte or
acceptance change; do not redispatch it or create a parallel CHAT settings
owner merely because the POST surface has different publication semantics.

### Hourly deadline and anti-micro-round gate

After the active channel/feature evidence pass is accepted, create exactly one
execution card in its existing evidence folder. Bind active-hour checkpoints:
Hour 1 semantic union, Hour 2 primary persisted user path, Hour 3 remaining
local must-haves, Hour 4 focused proof/browser/one review. C-rows and edge
cases are acceptance predicates inside that mission, not separate workers,
plans, review packets or goal turns.

The checkpoint records cumulative **active delivery time** only. Waiting for
the owner, provider, deployment or browser admission does not consume it;
narration, hashes, repeated evidence and unchanged review never count as
progress. At every hour boundary run the Ponytail reuse ladder and delete or
defer speculative work before adding another owner/file.

On `TIMEBOX_MISS`, do not silently continue, weaken the denominator, call the
slice complete, or admit the next vertical. The parent must choose one recorded
disposition: `REUSE_SMALLER_OWNER`, `DEFER_OPTIONAL_EXTERNAL` with exact resume
predicate, or `OWNER_EXTENSION` naming the unresolved RC1 must-have and new
cutoff. A generic looper/thinker continuation cannot grant the extension.

Pass the execution-card path, active-hour checkpoint, remaining outcome and
`NO_AUTOMATIC_TIME_EXTENSION` to every evidence, implementation, test, browser
and review helper. A helper may close the grouped mission or return one exact
defect; it may not invent another C-row packet, later-channel task or deadline.

## Historical Retention Gate

Before changing an existing page, feature, channel, backend contract, or security owner, create or update a retention ledger with accepted current behavior, accepted historical authority, newly approved behavior, missing and unsafe rows, the chosen semantic union, rejected alternatives, and required fixture/browser journeys.

Do not replace the current owner with a fresh approximation when an accepted implementation exists. Adopt the smallest verified semantic union into the current owner set.

## Admission Gate

No worker may edit until its packet contains every field in `references/contracts.md`. Reject admission on an ambiguous root, dirty collision without preimage hashes, unavailable claimed role/runtime, missing denominator, report-only authority, or overlapping ownership.

## Team Contract

- Evidence worker: read-only; finds sources, contradictions, denominators, and fixtures.
- Implementer: owns exact files and implements the accepted slice only.
- Reviewer: independently recomputes the highest-risk claims and may return `REQUEST_CHANGES`.
- Parent: owns decisions, resolves disagreements, verifies receipts, and never forwards a subagent verdict blindly.

Agents must challenge unsupported assumptions without redoing another role's entire job. Log/inventory workers cannot be the sole authority for product, security, or completion decisions.

## Side-Task Intake

Record `id | source | request | relation | certainty | authority | decision | owner | revisit_after`.

Allowed decisions: `DO_NOW`, `SIDE_TASK`, `PROMOTE_TO_MAIN`, `SUPERSEDES`, `DUPLICATE`, `REJECT`, `EXTERNAL_GATED`.

Finish or explicitly transition the active slice before promoting unrelated work.

## Receipt and Acceptance

Require the receipt and reviewer fields in `references/contracts.md`. Parent acceptance separately classifies source, focused tests, browser/runtime, external effects, retention reconciliation, and dirty-worktree recovery.

Use `CODE_READY`, `PARTIAL`, `REQUEST_CHANGES`, or `BLOCKED` only with the claim matrix. Never use bare `Done`; completion requires every user-required axis, not just code or tests.

## Template

Copy the mandatory `INDEX.md`, `CANONICAL-CHECKLIST.md`, `TERMS-AND-COMPLETION-STATES.md`, and recovery ledger from `assets/program-template/`; add only needed domain files. Keep one canonical checklist and load domain files on demand.
