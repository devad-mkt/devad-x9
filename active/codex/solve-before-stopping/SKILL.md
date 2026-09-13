---
name: solve-before-stopping
description: Diagnose and recover stalled work before declaring it blocked, paused, frozen, waiting, or unable to continue. Use when a Worker or Looper hits a failed tool, browser bridge, test harness, Git/worktree issue, unavailable callback, external dependency, resource problem, repeated retry/review loop, or any situation where one failed route may be mistaken for failure of the whole goal. Also use before asking a Looper, Thinker, or owner for rescue or permission.
---

# Solve Before Stopping

Keep the objective moving without weakening real safety boundaries. Treat a
failed method as a route failure until evidence proves the objective itself
cannot proceed.

This skill embeds the smallest useful parts of deep reasoning, Ponytail,
Smooth Coding, evidence-to-implementation, and xPlan. Do not load those full
skills merely to apply this workflow unless the task independently requires
them.

## Non-negotiable rule

Before writing or saying `BLOCKED`, `PAUSED`, `FROZEN`, `WAITING`, `CANNOT
CONTINUE`, or asking another role what to do, complete the recovery pass below.
Do not turn the pass into a report, new task, approval round, or planning loop.

Never bypass an actual secret, security, destructive, production, spend,
provider, claim, collision, or owner-authority boundary. Change the route,
never the authority.

## False Blocker Guard

A message that contains `BLOCKED`, `WAITING`, `FROZEN`, `HARD_BOUNDARY`,
`RESUME_ON`, or `OWNER_REQUIRED` is invalid unless it includes all fields below:

```text
GOAL_OUTCOME:
EVIDENCE_TARGET:
FAILED_ROUTE:
WHY_ROUTE_FAILURE_APPLIES_TO_ALL_ALLOWED_ROUTES:
CHEAPEST_WORKAROUND_TESTED:
ACTION_NOW:
NEXT_MATERIAL_ACTION_OR_TRUE_OWNER_BOUNDARY:
```

The sender must also classify the issue as `HARD`, `SOFT`, or `ASSUMED`. If
any field is missing, or if the failure is a routine harness, parser, quoting,
browser, local test, preferred transport, or local source issue, the receiver
must reply `REJECT_FALSE_BLOCKER:CONTINUE_LOCAL` and name the next direct
action. A conclusion-first blocker is not evidence.

`ACTION_NOW` must be executable. Passive text such as `retain claim`,
`preserve packet`, `wait`, `hold open`, `unchanged`, `none`, or `do not
allocate` is not a valid action. Name the actor and the concrete source edit,
command, cleanup, proof, receipt, or owner/operator operation that moves the
row. If the only remaining action is external and already named, return
`EVENT_ONLY`/`SOURCE_COMPLETE` with that actor and receipt instead of blocking
the host goal.

Outcome rows stay separate: product behavior proof is not transport proof;
disposable test proof is not sealed RC proof; browser proof is not source
proof; deployment/readback proof is not provider/publication proof. Missing one
row blocks only that row.

## Delivery success gate

A recovery succeeds only when it produces material goal progress or proves
that the authorized local objective is materially complete. Progress means an
owned source/test/doc change, focused proof, authorized runtime/RC action, or
completed external unblock. Local completion requires exact authoritative-plan
coverage, current branch/result identity, focused proof, and an external-only
remainder. A classification, packet, hash, routing message, candidate
preservation, or cleaner explanation alone is not success.

Do not end the turn immediately after filling the output contract. Execute the
safe `ACTION_NOW`, then report its evidence. When coordinating Workers, observe
for the requested bounded window and classify each lane as `MOVING`,
`TERMINAL_LOCAL_COMPLETE`, `HARD_BOUNDARY`, or `DRIFTED`. Count `MOVING` only
after concrete work starts or completes. Accept `TERMINAL_LOCAL_COMPLETE` only
with the completion proof above, and do not wake it merely to look active. If
an unfinished lane returns only a classification, the recovery failed; correct
the route instead of declaring the skill successful.

## Recovery pass

### 1. Rebind the real objective

State internally:

```text
OBJECTIVE:
SUCCESS_PREDICATE:
CURRENT_PROGRESS:
FAILED_ROUTE:
OBSERVED_CAUSE:
HARD_INVARIANTS:
CURRENT_AUTHORITY:
```

Use current Git, source, tests, runtime, and exact receipts. Old chat/status
text is orientation only. Preserve completed work and do not restart the plan.

### 2. Classify the stop correctly

| Class | Meaning | Required behavior |
| --- | --- | --- |
| `CONTINUE_LOCAL` | A safe in-scope reversible action exists. | Execute it now. |
| `ROUTE_BLOCKED` | One tool, command, browser, fixture, or interface failed. | Repair it or use a different mechanism. |
| `DEPENDENCY_WAIT:<EVENT>` | One exact external receipt is missing. | Pause only that chunk; continue authorized local work. |
| `EVENT_ONLY:<EVENT>` | The authorized current scope is already complete and only a named external or owner event can open more work. | Preserve the completed result once; do not claim activity, rerun green proof, or invent a chunk. |
| `SECURITY_STOP` | A credential/data exposure or trust-boundary violation occurred. | Contain that epoch/resource; continue disjoint work. |
| `HARD_BOUNDARY` | The next action needs new owner authority, secret-safe capability, destructive action, production/spend approval, or collision resolution. | Ask once for the smallest authority and bind `RESUME_ON`. |
| `OBJECTIVE_BLOCKED` | Every allowed route and independent slice is disproved. | Stop the objective with direct evidence. |

Do not use `BLOCKED` as a synonym for slow, inconvenient, unreviewed, or
missing a preferred tool.

Never map `DEPENDENCY_WAIT`, `EVENT_ONLY`, or `TERMINAL_LOCAL_COMPLETE` to the
host goal status `blocked`. Those labels describe one lane or local scope, not
an impasse for the durable program. Keep the goal resumable while its named
capability owner is active. If the owner says continue or widens test
authority, discard the old blocked classification before doing any other
work; do not wait for three more repetitions of stale evidence.

If a host tool or lifecycle asks whether to mark the goal `blocked` after a
row-scoped dependency, answer with the resumable receipt instead. A denied
exact cleanup, browser bridge, Tailnet command, Docker operation, or other
execution surface blocks that operation only. It becomes
`SOURCE_COMPLETE/EXTERNAL_ONLY` when current local scope is proven complete and
the exact cleanup/receipt owner is known. Do not call `update_goal(blocked)` or
its equivalent unless the whole requested objective lacks any known resume
predicate.

### 3. Separate constraints

- `HARD`: authority, security, privacy, claims, collisions, destructive or
  production effects, spend, rollback, and required proof.
- `SOFT`: a preferred tool, workflow convention, convenience, or evidence
  format replaceable without changing the outcome.
- `ASSUMED`: inherited narration or an unverified belief. Test it cheaply.

A safety rule protects an invariant; it does not require the failed route.

Bind capability packets to outcome invariants, not a preferred transport,
listener, package, or receipt shape. If SSH stdin, Taildrop, a browser bridge,
or a custom gateway fails, keep the exact security/data/cleanup invariants and
select the shortest structurally different mechanism. Do not promote a
production-grade reusable gateway into a prerequisite for an owner-authorized
disposable test proof.

Classify the evidence target before inheriting a security mechanism. A product
behavior proof, transport-security proof, and live-acceptance proof are not the
same outcome. When the owner explicitly authorizes a disposable test-only
transport, preserve product and data invariants but do not require a reusable
production-grade gateway merely to run the test. Bound the exception to
non-production isolated state, transient non-output secrets, exact source and
command, expiry, cleanup, and residue proof. Mark the result test-only; it
cannot satisfy transport-security, deploy, or live-acceptance gates.

### 4. Build the smallest route portfolio

Stop at the first route that holds:

1. **Reuse:** freshly admit existing code, worktree, branch, resource, session,
   helper, or receipt.
2. **Direct repair:** fix the root cause at the real owner.
3. **Local fallback:** use a bundled runtime, native tool, alternate command,
   browser/interface, or deterministic local proof.
4. **Equivalent evidence:** prove the same predicate through another safe
   observable path.
5. **Reversible bridge:** isolated, time-bounded, observable, rollback-bound,
   and no weaker than every hard invariant.
6. **Parallel progress:** execute an authorized local chunk independent of the
   failed route.

Prefer the simplest route that proves the outcome. Do not create a new
resource, worktree, branch, database, packet, helper, or abstraction when an
admitted existing one works.

Attempt up to two cheap safe mechanisms, including one structurally different
route. Same-root local quoting, parser, fixture, or harness corrections may
continue for at most three bounded cycles. Cosmetic retries are one route.

Decompose an apparently missing capability before escalating it. Test the
cheapest independent layers—installed client/runtime, loadable extension,
transport/listener, admitted server endpoint, authentication, and required
state—and escalate only the first unproven layer. Never request an entire new
stack when the existing client or service already satisfies part of the gate.

### 5. Protect local continuation

Before a wait, inspect the current authority for a concrete eligible chunk
with exact paths/actions, focused proof, rollback, collision state, and stop
conditions. Start it directly when authorized.

A frozen or completed candidate is not necessarily the end of a long domain
goal. Re-read the current authoritative plan and owner instructions once. If
unfinished domain-local work remains inside the same worktree, branch, effect
ceiling, and exclusive domain, select the smallest next chunk and execute it.
Do not require a new claim merely because the previous candidate was frozen.
Escalate only a real cross-domain/shared-path or external-effect expansion.

When the owner has already authorized RC testing of the exact domain branch,
do not manufacture a merge prerequisite. Test that branch/SHA on the approved
RC target with its existing rollback and stop conditions; reserve merging for
the owner's declared integration boundary.

Do not invent filler work. If no authorized local chunk exists, report
`EVENT_ONLY` once with a named `RESUME_ON` event. Event-only is not a failed
product goal. It is also not `CONTINUE_LOCAL`: preserving, retaining, waiting,
or restating an already-frozen candidate is not an executable local action.
Use `EVENT_ONLY` only after the current authoritative plan, owner-granted domain
scope, approved RC route, and one structurally different safe fallback contain
no executable action. A single finished candidate or failed preferred tool is
insufficient.

When `EVENT_ONLY` includes exact completed-plan coverage and proof, classify the
lane `TERMINAL_LOCAL_COMPLETE`. Deliver its single external resume event and
leave it idle. Repeatedly steering a completed lane wastes tokens and pressures
the Worker to invent unsafe or duplicate work.

`TERMINAL_LOCAL_COMPLETE` ends only the Worker's local slice, not an unfinished
program objective. Before idling, transfer the external remainder once to its
already-authorized capability owner. Prefer reuse of a freshly admitted shared
test service with isolated logical state over another resource epoch. Keep the
product Worker idle while the capability lane actively produces the matching
resume receipt; wake the Worker only with that receipt.

Remote-main movement alone does not stop work in a valid sticky domain
worktree. Rebind, review, and merge at the declared RC/integration boundary,
not between ordinary local chunks.

### 6. Escalate to the correct role once

| Recipient | Use only for |
| --- | --- |
| Worker | Routine in-scope diagnosis, correction, tests, tooling, fixtures, and fallbacks. |
| Looper | A real shared-resource collision, capability executor, or direct receipt delivery. |
| Thinker | A stable material diff, architecture/security contradiction, or two genuinely different proof-bound failures requiring judgment. |
| Owner | New authority, production/provider/spend, secret injection, destructive action, irreversible choice, or product decision. |

```text
ESCALATION_CLASS:
CURRENT_AUTHORITY:
DECISION_NEEDED:
FAILED_DISTINCT_ROUTES:
WHY_LOCAL_DECISION_IS_INVALID:
SAFE_WORK_CONTINUING:
RESUME_ON:
```

Missing fields mean continue locally. Do not resend unchanged waits or ask
several roles the same routine question.

## Outcome-bound budget

For one blocker allow one diagnosis, one batch of same-root corrections, one
focused proof, one stable review only if material bytes or a hard boundary
changed, and one execution. After failure allow one read-only discriminator,
then one final corrected execution or one hard boundary.

Routing, hashes, reservations, status messages, and packet renames are not
progress. After two process-only cycles run `DELIVERY_RESET`: restate the
finish line, take one direct action, keep one focused proof, and defer anything
that cannot change the next decision.

If an unfinished lane produces no material progress within the bounded
observation window, run one `RECOVERY_FAILED` correction: identify which
assumed prerequisite or overly narrow scope caused the idle result, apply the
smallest already-authorized alternative, and steer again. Do not apply this to
a proven `TERMINAL_LOCAL_COMPLETE` lane, and do not count compliant output
formatting as a pass.

## Autopilot depth contract

When a goal is resumed or its local authority is widened, discard stale
`blocked`, `paused`, or `event-only` state and classify from the new owner input
plus current source. A prior status is evidence, not authority.

For an unfinished local lane, do this without asking for detailed steering:

1. Trace the authoritative plan and the real source/test owner once.
2. Rank unfinished authorized slices by goal value and decisive risk; choose the
   highest-value coherent vertical, not the easiest status, docs, or rerun task.
   Before choosing a safer adjacent slice, compare it with one finish-line
   vertical. If the finish-line slice cannot proceed, prove the exact missing
   source owner, capability, or authority; never invent that architecture.
3. Bound exploration: after the slice and owner are identified, the next
   meaningful action must be a file change, focused proof, or authorized runtime
   action. More narration or repeated source mapping is drift.
4. Diagnose ordinary command, safety-hook, type, lint, fixture, and harness
   failures locally. Preserve the invariant and switch mechanism; do not ask the
   coordinator to debug routine execution.
5. Continue until the vertical has focused proof or reaches a genuine hard
   boundary. Do not stop at implementation intent, a partial diff, or the first
   failing command.

Reason deeply at decision points, not by producing more process. The quality
signal is a correct source owner, minimal coherent behavior, skeptical boundary
checking, self-repair, and decisive proof—not the number of plans, skills,
messages, or retries.

Judge continuation at the program level: every unfinished objective must have
exactly one active owner—product Worker for local delivery, or Looper/helper for
a real shared capability. A locally complete Worker plus an active capability
owner is healthy continuation; a locally complete Worker with an unrouted
external remainder is an orchestration failure.

## Output contract

```text
CLASS: CONTINUE_LOCAL | ROUTE_BLOCKED | DEPENDENCY_WAIT:<EVENT> |
  EVENT_ONLY:<EVENT> | SECURITY_STOP | HARD_BOUNDARY | OBJECTIVE_BLOCKED
ROOT_CAUSE:
ACTION_NOW:
PARALLEL_LOCAL:
ESCALATE_TO: NONE | LOOPER | THINKER | OWNER
RESUME_ON:
STOP_BOUND:
PROOF:
```

`ACTION_NOW` must be executable, not “wait”, “monitor”, “review again”, or
“ask what is next.” `PARALLEL_LOCAL` is a concrete authorized chunk or
`NONE_AFTER_CURRENT_SCOPE_CHECK`. The sole exception is
`EVENT_ONLY:<EVENT>`, where `ACTION_NOW` must be
`NONE_CURRENT_SCOPE_COMPLETE`; the completed result and exact `RESUME_ON`
event are the proof. Never use `CONTINUE_LOCAL` for that condition.

When the host cannot unblock a previously marked task, treat the label as UI
state. Do not spend turns trying to repair the label. Send the exact
row-scoped receipt to the manager/capability owner once and resume only when
the matching receipt or a new authorized local chunk arrives.

## Learning from solved blockers

Read [the blocker lessons](references/lessons/LESSONS.md) only when a current
failure matches a listed class or has recurred. Use
[the lesson template](references/lessons/TEMPLATE.md) after a blocker is
actually solved.

Update an existing lesson instead of adding a duplicate. Add a lesson only
when evidence proves the root cause, winning route, preserved boundary, and
regression check. Never promote speculation or a merely attempted route.

An implicitly triggered product Worker must not edit the installed skill while
delivering product work. It returns one `LESSON_CANDIDATE`. When the owner
explicitly asks to improve this skill, apply verified candidates to the lesson
ledger and promote a repeated rule into this core file only when it prevents
the class without widening authority.

## Rationalization guards

- Preferred tool failed -> use another safe mechanism.
- Plan omitted the command -> judge authority from scope, effects, invariants,
  and stop conditions.
- Main advanced -> mark rebind due and keep domain work moving.
- Review is pending -> continue disjoint work; reuse unchanged reviews.
- Browser failed -> visual proof is partial; source/tests may continue.
- Resource is old -> freshly admit the service, never stale credentials,
  logical state, or quarantined epochs.
- More process feels safer -> keep hard gates and delete ceremony that cannot
  change the decision.
- No local chunk exists -> prove it against current authority, then use one
  event-only resume predicate without claiming whole-goal failure.

## Provenance (consolidated 2026-09-12)

Canonical body: `CODEX/solve-before-stopping` (2026-08-12 01:53:47, 4 files, 18289 bytes) - newest and largest.

Former names now disabled: `NINELLC/solve-before-stopping` (14569 bytes, 291 lines, a strict subset).
