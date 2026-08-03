---
name: smooth-coding
description: Use before and during Worker or Looper implementation of an accepted software plan, especially when delivery risks slowing through over-planning, excessive reviews, artifact growth, broad risk propagation, scope inflation, or premature blocked claims.
---

# Smooth Coding

## Purpose

Finish the full accepted plan as quickly as its real dependencies allow while
preserving correctness, security, and rollback. Slices control execution order;
they do not reduce the owner's scope or silently convert the plan into MVP/V2.

## Role Boundary

- This is the default implementation skill for `WORKER` and `LOOPER` roles.
- Workers and Loopers do not invoke `$ultra-reasoning-protocol` or `$sdlc`.
  Those skills are for `THINKER` judgment. If the owner explicitly mentions
  their concepts to a Worker or Looper, apply only the smallest relevant Lite
  idea inside this workflow; do not start their full process.
- Use Ponytail's minimum-solution ladder while coding. It is a reflex, not a
  separate audit, agent, report, or approval cycle. If `@ponytail` is explicitly
  invoked, obey it without weakening the safeguards below.
- This skill does not grant product, spend, provider, deployment, destructive,
  or owner authority that the current role does not already have.
- Do not rewrite this installed skill from inside the product-delivery loop.
  A Worker or Looper may record a candidate lesson, but skill maintenance is a
  separate owner-requested or THINKER-owned action. When updating this skill,
  read [Maintaining Smooth Coding](references/skill-maintenance.md) first.

## Safeguards That Stay

Never simplify away tenancy, trust-boundary validation, security, migrations,
provider-spend controls, idempotency, durable receipts, data-loss prevention,
production activation gates, rollback, accessibility basics, or exact source
proof. Apply extra rigor only to the slice currently changing one of these
boundaries; risk does not spread to the whole plan.

## Classify The Current Slice

Classify changed risk, not project prestige or total plan size:

| Tier | Current slice |
|---|---|
| `LITE` | Documentation, copy, hashes, small reversible edits, and routine bookkeeping |
| `MEDIUM` | Ordinary application code, multi-file behavior, and noncritical refactoring |
| `HIGH` | The slice currently changes tenancy, security, a stateful migration, provider spend, production activation, rollback, or exact release/source authority |

`HIGH` preserves the named boundary proof; it does not invoke Ultra/SDLC for an
implementer or make adjacent work High.

## Start Once

1. Bind the accepted plan or contract, current Git SHA, write scope, finish
   line, and first dependency-ready slice.
2. Complete the Reuse-First Gate below. Read the real implementation flow,
   direct callers, existing helpers, and focused tests. Do not reread the whole
   repository by default.
3. Reuse the accepted plan. Do not create another plan, packet, percentage
   audit, or architecture review unless it changes the next coding decision.
4. State the current slice in one sentence and begin a code or test action in
   the first work cycle. Planning-only cycles are not progress.

## Freeze Each Chunk Before Code

For a material feature whose behavior or ownership is not already frozen, run
one compact sequence:

`current source/tests + matching evidence -> PRE_PLAN ownership map -> bounded
chunk contract -> PRE_CODE preimage rebind -> code and proof`.

The chunk contract records only decisions that change implementation: user
outcome, existing owners to reuse, exact gap, inputs/outputs, authorization,
persistence and side effects, errors/recovery, accessibility, claimed paths,
tests, and exclusions. Reuse an accepted contract when it already covers the
slice; do not create another plan or contract merely because a new turn began.

Never adopt reference or predecessor code blindly. Reuse its proven behavior
and owner seam, but reject unnecessary state machines, duplicate abstractions,
test-only production seams, brittle source-string proof, or code that is harder
to maintain than the smallest native implementation. Correct a small verified
defect when it shares the active paths; defer broad behavior-neutral cleanup
until it no longer risks the delivery-critical slice.

## Existing-System Gate: Reuse Before New

Run this gate before accepting or revising an implementation plan and recheck
it against the current branch immediately before the first behavioral edit.
Pure copy, hash, and attestation edits need only a direct-caller/nearby-helper
check. Before adding any service, model, controller, route, job, migration,
provider, channel catalog, queue, settings surface, or persistence path:

1. Trace the current user flow from visible UI/settings or route through the
   request, owning service, model, job/queue, persistence, runtime consumer, and
   focused tests. DOM evidence proves presentation, not backend ownership;
   source evidence alone does not prove the current user-visible contract.
2. Search the accepted source, current integration history, and every
   owner-named predecessor branch, handoff, Sheet, or app-domain contract that
   could already own the capability. A Sheet or memory item is a discovery
   lead until current source or runtime evidence rebinds it.
3. Record one compact row in the existing plan, Work Order, note, or chat:
   `EXISTING_FEATURE`, `UI_SETTINGS`, `SERVER_AUTHORITY`, `PLAN_ENTITLEMENT`,
   `REFERENCE_REUSE`, `PERSISTENCE_CONSUMPTION`, `INTEGRATED_HISTORY`,
   `TEST_PROOF`, `GAP`, and `CHANGE_MODE`.
4. Set `CHANGE_MODE` to exactly `REUSE`, `EXTEND`, `NEW`, or
   `REPLACE_AUTHORIZED`. `NEW` requires source-backed absence in the touched
   scope. `REPLACE_AUTHORIZED` requires an explicit owner decision. An unknown
   owner blocks only that dependent edit; it does not stop unrelated work.
5. When another app or domain owns the capability, integrate through its
   existing service, contract, or API. Keep that owner authoritative; do not
   clone provider lists, channel catalogs, policies, queues, tables, or UI
   settings.
6. Add behavior only for the proven `GAP`, then leave one focused test proving
   the selected reuse seam and one user-facing check when visible behavior
   changed.

Treat combined platform capabilities as one reusable owner chain. For Devad
notification work, trace and reuse Laravel Notifications, Reverb for connected
realtime, WebPush/service-worker delivery for background or closed browsers,
the notification ledger, and existing suppression/throttling before proposing
Pusher, OneSignal, another push provider, or a second throttle.

This is a short decision gate, not a repository-wide audit or new artifact.
Use `rg`, Git history, and route/service/test tracing first. Read
[existing-system-discovery.md](references/existing-system-discovery.md) only
when the slice crosses frontend/backend or app-domain ownership, or the first
targeted pass cannot name the owner and reuse seam.

## Decision-First Autopilot

1. Run the earliest decisive gate, not blindly the cheapest gate. Prefer
   low-cost deterministic prerequisites before broad tests or model review when
   they can invalidate later work: intent, source, scope, writable target,
   required tools, Git identity, links, manifest shape, syntax, and focused
   reproduction. If runtime, migration, security, compatibility, or release
   proof is the first real dependency or decision-changing risk, run that gate
   early even when it is slower or more expensive.
2. Run broad tests and independent review once on stable bytes. After a change,
   rerun only the failed gate and affected later gates.
3. Never ask a reviewer to reinterpret a deterministic failure. Fix it or stop
   at the exact external boundary.
4. While a command or delegated task is merely running, wait silently. Report
   only a state transition, genuine blocker, required owner action, or result.
5. After every successful action, immediately start the next authorized,
   dependency-ready action. `NEXT` describes work already starting; it is not a
   reason to end the turn.
6. Keep build, publication, installation, initialization, activation, and
   production verification as distinct claims. Report only the strongest state
   actually proven.

## Execute The Full Plan

- Keep one delivery-critical slice active. Group related plan chunks when they
  share the same flow and can be reviewed together.
- After a slice passes its focused proof, continue automatically to the next
  accepted dependency-ready slice. Do not wait for owner approval unless a
  requirement, spend, provider, irreversible, or production decision changed.
- A blocked dependency pauses only dependent work. Run disjoint safe slices in
  parallel when ownership and files do not overlap.
- Do not invent V1/V2 deferrals, cut features, or replace the accepted finish
  line unless the owner requests it or a genuine external dependency requires a
  decision. Record a real dependency without turning it into a scope rewrite.
- Classify newly noticed work as `REQUIRED_NOW` when it affects the current
  acceptance predicate or a hard safeguard, `ACCEPTED_LATER` when it already
  belongs to a later dependency-ready slice, or `DROP` when neither is true.
  Never silently delete accepted owner scope merely because it is not P0/P1 for
  the current slice.
- Prefer one context-retaining implementer. Add another Worker only for a
  genuinely parallel, disjoint write set that reduces wall time.
- Subagents are optional and default to none. When one is justified, follow
  `$subagents`: ordinary slices default to one active child; explicit
  long-running goal mode may use up to three pairwise-disjoint agents with one
  accountable manager, no nesting, no duplicate parent work, bounded waits,
  and compact task-local context capsules.

## Minimum-Solution Ladder

For each change, stop at the first sound option:

1. No change is needed.
2. Reuse existing behavior or a nearby helper.
3. Use the standard library or framework/native platform.
4. Use an already-installed dependency.
5. Make the smallest local change in the real owner.
6. Add an abstraction or dependency only for a demonstrated current need.

No speculative scaffolding, duplicate policy, one-implementation interface,
future-proof factory, or new service merely because the plan is large.

## Evidence Budget

- Use focused tests while coding. Run broad tests, security, migration,
  browser, and build gates once at the milestone that actually needs them.
- Use one accountable implementer and one independent review of the stable,
  materially changed diff. An accepted exact-diff review is reusable. Keep a
  distinct repository-mandated security or release gate only when it answers a
  different real boundary question; do not duplicate the same review.
- Review a correction once. Do not rereview unchanged bytes, repeat a scan
  because time passed, or create a review of a review.
- Keep one canonical checkpoint. Mutable status, checkboxes, percentages, and
  narration never invalidate immutable code, contracts, or accepted evidence.
  If an external contract requires a status snapshot, bind that immutable
  snapshot once rather than hash-binding the mutable working checklist.
- Create C1/C2 only when repository policy requires them. Do not create another
  packet, manifest, topic, memory file, or hash for the same event.
- Historical/current dual-browser proof is only for a plausible regression or
  release claim. Reuse accepted evidence for unchanged behavior.

## Evidence-Linked Checklists

Use at most one checklist when the accepted plan has several real acceptance
items and the checklist makes the next action clearer. For a simple slice,
`DONE / NEXT / BLOCKED` is enough; do not create a checklist by default.

- `[x]` means linked source, focused test, runtime, or accepted review evidence
  proves that acceptance item. An attempted command or written implementation
  without proof is not checked.
- `[ ]` means incomplete or currently unproved. It does not mean blocked.
- `BLOCKED:<external cause>` applies only to the dependent item. Name the safe
  work that can continue.
- Keep checklist rows at acceptance-item or vertical-slice granularity, not per
  command, file, test, or narration step.
- Link to canonical evidence; do not duplicate the evidence inside the plan.
- Revalidate only affected checked rows after material code or contract changes.
  Unchanged evidence remains reusable.
- Treat the checklist as mutable navigation, never proof or execution authority.
  Do not hash it, derive routine percentages from it, or maintain duplicate
  checklist plans. Update it at a milestone or handoff, not after every command.

## Blocked Is Expensive

- A failed command, tool, fixture, connector, or preferred route is
  `ROUTE_BLOCKED`, not an objective blocker. Correct it or try one structurally
  different safe route by default; do not loop on renamed retries. More route
  exploration is justified only by a distinct mechanism at a current hard-risk
  boundary.
- A material unknown blocks only the action that depends on it. Continue other
  plan work.
- A temporary route is allowed when reversible, isolated, observable,
  time-bounded, and no weaker than the hard safeguards.
- Declare the objective blocked only when required authority, secret,
  environment, or owner choice is absent and every allowed useful route is
  disproved.

## Ceremony Preflight

Before adding a document, agent, hash, scan, gate, review, audit, or deeper
reasoning step, ask:

1. Does the current slice touch a real changed-risk boundary?
2. Is there material new risk or conflicting evidence?
3. Will this action change a pending decision, or is repository policy explicit?

If all answers are no, skip it and continue implementation. If one answer is
yes, take the smallest action that resolves that exact question.

## Delivery Reset

After two completed cycles containing only plans, reports, hashes, reviews,
checkpoints, or status narration:

1. Restate the full owner finish line.
2. Name the one real current blocker and its type.
3. Select the smallest direct code/test action.
4. Keep one focused proof and one milestone gate.
5. Move nonblocking findings out of the critical path.
6. Resume implementation immediately; do not create a reset document.

## Progress Output

Report only:

- `DONE`: accepted plan items completed with concise proof.
- `NEXT`: the dependency-ready implementation action already starting.
- `BLOCKED`: only dependent items, exact reason, and alternate safe work.
- `OWNER_ACTION`: `NONE` unless a real owner decision is required.

Percentages are optional and never block coding. Stop only when the full
accepted plan is complete or all remaining items have genuine external
blockers with a restartable handoff.

## Conditional Lesson

Read [Workflow Final Check overprocessing](references/lessons/01-workflow-final-check-overprocessing.md)
only when reviews multiply, progress auditing pauses coding, the whole plan is
treated as Critical, mutable status invalidates evidence, or two process-only
cycles occur. Apply its corrections, then return to implementation.

Read [Gate ordering and quiet autopilot](references/lessons/02-gate-ordering-and-quiet-autopilot.md)
when an install/release task repeats planning or permission rounds, broad tests
run before cheap checks, unrelated host state blocks the objective, waiting is
narrated repeatedly, or a task stops while an authorized next action exists.

Read [Existing capability discovered too late](references/lessons/03-existing-capability-discovered-too-late.md)
when a requested capability may already exist, an accepted branch was merged
without rebinding ownership, UI and backend evidence disagree, or a Worker is
about to add a second service, catalog, queue, provider path, or persistence
model for behavior another domain may own.

Read [Subagent context and coordination multiplication](references/lessons/04-subagent-context-and-coordination-multiplication.md)
when more than one subagent is proposed, agent waits or follow-ups repeat, the
parent starts duplicating child work, a child receives broad task history, or
delegation produces more process than delivery.

Read [Maintaining Smooth Coding](references/skill-maintenance.md) only when the
owner asks to change this skill itself or a task proposes promoting a local
lesson into the reusable core.
