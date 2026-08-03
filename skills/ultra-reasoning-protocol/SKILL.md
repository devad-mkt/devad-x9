---
name: ultra-reasoning-protocol
description: Use when a task is complex, ambiguous, novel, high-stakes, multi-step, slow, looping, repeatedly error-prone, prematurely blocked by one failed route, or process is growing faster than useful delivery.
---

# Ultra Reasoning Protocol

## Core Principle

Match reasoning effort to difficulty, uncertainty, stakes, and reversibility. Improve process without pretending to change model weights or compute. Ultra behavior means wider route search, sharper constraint separation, current evidence, and deliberate convergence, not verbosity or exposed chain-of-thought.

## Select Depth

- **Quick:** Clear, low-stakes, reversible task. Use one evidence pass and a direct answer.
- **Deep:** Ambiguous, novel, multi-step, or dependent task. Compare alternatives and verify key assumptions.
- **Critical:** High-stakes, irreversible, security-sensitive, stateful, or repeatedly failed task. Add independent challenge, failure injection, and explicit rollback proof.

Escalate one level only when evidence conflicts, a material premise is `UNKNOWN`,
or a failed approach exposes a new changed-risk boundary. A bad command, missing
host extension, test-fixture defect, unavailable preferred tool, or other route
failure does not escalate the whole task; correct or replace that route at the
current depth. More tokens are not automatically better; stop when the success
predicate is proven or a bound is reached.

Select depth independently for each bounded slice and decision. A Critical
program may contain Quick documentation, hash, or workbook work and Deep
ordinary implementation; parent risk does not automatically propagate to every
substep.

## Delivery-First Override

Deeper reasoning must produce fewer, better actions. Internal exploration,
possible risks, framework categories, and reviewer ideas are hypotheses; they
do not become tasks, documents, gates, or blockers without an accepted
requirement or demonstrated material risk.

- Default to direct execution when the owner, touched flow, acceptance check,
  and rollback boundary are already known. Do not turn an implementation
  request into an audit program.
- Keep one active product slice, one canonical plan or checkpoint, focused
  checks while editing, and one broad milestone gate. A new artifact, helper,
  or review must replace existing work or answer a decision-changing question.
- Treat nonblocking findings as backlog. They do not delay the requested result
  unless they violate its acceptance predicate or a hard safety boundary.
- Separate reversible setup and parallel preparation from production
  certification. Do not make a low-risk project, branch, fixture, or local
  workflow wait for unrelated deployment proof when its base and limitations
  can be stated safely.
- Hash immutable executable inputs and accepted outputs, not mutable checkboxes,
  progress narration, or every bookkeeping update. A status edit does not
  invalidate unchanged code or reviews.
- Use one canonical checkpoint for a meaningful transition. Do not synchronize
  the same event into several plans, manifests, topics, and receipts unless an
  external contract explicitly requires each one.
- Treat session summaries, topic indexes, progress ledgers, and generated
  reports as disposable navigation unless explicitly designated authoritative.
  Link to current authority; do not keep several narrative mirrors in sync.
- Before starting a full-program audit, percentage reconstruction, historical
  baseline replay, or multi-chunk review, require a decision it can change.
  Otherwise inspect only the current delivery slice and its direct dependencies.
- Keep the owner at product, risk, spend, and irreversible milestone decisions.
  Do not insert owner approval between every already-bounded implementation or
  review chunk when the acceptance contract has not changed.
- If two consecutive completed cycles produce only plans, packets, hashes,
  reviews, or status updates while the product objective could advance, run a
  `DELIVERY_RESET`: restate the user-visible finish line, name the single real
  blocker, choose the smallest direct action and proof, and defer everything
  that cannot change the next go/no-go decision.
- A stronger model noticing more edge cases must rank and discard them. Reasoning
  completeness is not workflow scope.

## Critical-Path Control

- Freeze scope after framing. Add work only for an explicit requirement, a reproducible failure, or an unresolved critical risk.
- Route mechanical work to deterministic tools and Quick depth. Reserve Deep or Critical depth for ambiguous, irreversible, security, and go/no-go gates.
- Batch related changes. Run focused checks while iterating and broad verification at declared milestones.
- Challenge a stable candidate once. Treat an accepted review as reusable when it is bound to the exact artifact hash, rubric, and evidence. Repeat only when those bytes or evidence change, or when a new blocker-relevant falsifiable probe is declared; an unresolved blocker alone does not justify rereading identical bytes.
- Freeze contract, receipt, and evidence-format versions once a stable candidate
  is ready for its first runtime proof. Create another version only for changed
  behavior, changed authority, a failed acceptance probe, or a required
  compatibility repair; narration churn is not a new version.
- Separate static maintainability signals from runtime capacity. File count and
  LOC may trigger inspection, but throughput requires a bound workload,
  completion definition, concurrency, measurement window, provider mode,
  retries/timeouts, and resource ceilings.
- Reuse a compact invariant checklist with source hashes instead of rereading unchanged instructions. Checkpoint before handoff or context compaction.
- Diagnose before steering: inspect live activity, checkpoints, process or test state, and evidence changes. Distinguish slow from stalled; a bounded running gate or newly demonstrated regression is progress, while repeated unchanged cycles are a stall.
- Treat skill edits as guidance for agents that load them, not retroactive runtime control. They do not alter an in-progress turn, queued call, cached context, or another thread; steer active work explicitly.
- Separate implementation, attestation, deployment, and pilot at stable phase boundaries when atomicity does not require one run. Resume from a compact checkpoint in fresh context when accumulation becomes costly.
- State enforcement limits: a skill cannot select or attest a model tier, impose runtime deadlines, cancel work, or make external gates pass.

## Long-Run Continuity

For work spanning multiple phases, turns, context compactions, waits, or subtasks, read [long-run-continuity.md](references/long-run-continuity.md).

- Keep one root objective, one acceptance predicate, and one active main slice. Preserve later work in a deferred list without allowing it onto the current critical path.
- Treat current source and runtime evidence as authority. Chat memory and prior narration are orientation only until rebound to current facts.
- Update one compact durable checkpoint after meaningful proof, failure, handoff, subtask completion, or before context compaction; do not rewrite it after every command.
- A subtask result is not accepted automatically. Verify decisive claims, absorb accepted facts into the main checkpoint, then close, supersede, or explicitly retain the subtask.
- Continue non-conflicting main work while a nonblocking subtask runs. Only the main agent may declare the root acceptance predicate complete.

## Risk-Scaled Pre-Plan And Pre-Code Context Gate

Before creating or accepting a Work Order, finalizing an implementation plan
for execution, or editing behavior, map only the context that can change the
solution. Quick work normally needs the definition, relevant caller, and
focused test; keep that evidence internal unless a durable handoff is required.
Deep or Critical work may use the fields below, but record only applicable
fields as `VERIFIED:<evidence>`, `NOT_APPLICABLE:<reason>`, or `UNKNOWN`.

- `EXISTING_FEATURE`: Does this feature or equivalent behavior already exist?
- `UI_SETTINGS`: Which UI settings, feature flags, or configuration controls it?
- `SERVER_AUTHORITY`: Which server-side component owns the canonical policy or value?
- `PLAN_ENTITLEMENT`: Which plan, entitlement, quota, or permission gates it?
- `REFERENCE_REUSE`: Is there a reference application or existing implementation to reuse?
- `PERSISTENCE_CONSUMPTION`: Where is the value persisted, transformed, and consumed at runtime?
- `INTEGRATED_HISTORY`: Which accepted predecessor, merge, or branch introduced related ownership, and is it present at the current Git identity?
- `TEST_PROOF`: Which tests and browser or runtime proof cover the complete path?
- `GAP`: Which exact accepted behavior remains unmet after reuse?
- `CHANGE_MODE`: Is this `REUSE`, `EXTEND`, `NEW`, or `REPLACE_AUTHORIZED`?

`NEW` requires source-backed absence in the touched scope;
`REPLACE_AUTHORIZED` requires an explicit owner decision. For user-facing
behavior, prove both the visible UI/settings path and the
request-to-service-to-persistence-to-runtime path. DOM alone does not prove
server ownership; source alone does not prove the current visible contract.

When current authority already exists, reuse it or document evidence that it cannot satisfy the requirement. Do not replace it with duplicated hard-coded policy merely to make a local path pass. A material `UNKNOWN` blocks only the action that depends on it; continue safe independent work. Revalidate cited evidence after relevant changes. Use targeted search, accepted integration history, framework-native inspection, and reusable source hashes; do not create a separate context packet or full-repository reread by default. Sheets, handoffs, memory, and code graphs may locate candidates but remain advisory until rebound to current source or runtime evidence.

## Constraint-Preserving Ingenuity

A failed method is `ROUTE_BLOCKED`, not proof that the objective is blocked.
Creativity changes the route, never the authority boundary. Preserve user rules,
roles, ownership, claims, security, privacy, spend, mutation, deployment, and
proof gates.

- Classify constraints as `HARD`, `SOFT`, or `ASSUMED`. Obey hard constraints,
  optimize soft constraints, and challenge assumptions with current evidence.
- Before `BLOCKED` or `SOFT_BLOCKED`, state the objective, invariant, failed
  route, actual cause, and whether the failure applies to one route or every
  allowed route.
- For a nontrivial blocker, generate a route portfolio from distinct mechanisms:
  direct repair, alternate tool or interface, alternate evidence path, reversible
  temporary bridge, and independent progress that does not depend on the blocker.
  Renaming the same retry is not a new route.
- Inspect local source, tool inventory, help, logs, durable state, and available
  interfaces. When browsing is allowed and current external facts could change
  the decision, search current primary sources before declaring `Unknown` or
  blocked. Respect an explicit no-web rule.
- Attempt the two cheapest safe independent routes, including one structurally
  different route, unless a stop bound, cost limit, or hard constraint forbids it.
- While a durable fix is long-running, continue one safe non-dependent slice or
  use a bounded temporary bridge. Keep the durable fix and continuity route as
  separate tracks; neither may impersonate final completion.
- A temporary bridge must be reversible, isolated, time-bounded, observable,
  and explicit about owner, expiry, rollback, cleanup, and switch-back trigger.
  It must not weaken authorization, validation, durability, privacy, or proof.
- Declare the objective hard-blocked only when required authority, secret, or
  owner choice is missing; all allowed independent routes are disproved; a hard
  stop bound is reached; or every remaining route violates an invariant.
  A soft blocker must still produce one safe next action or useful parallel slice.

## Critical Evidence Receipt

For Critical work, use one compact receipt and include only fields affected by
the current slice. Reuse repository evidence and mark the rest
`NOT_APPLICABLE`; do not create a receipt per command, retry, or micro-edit.
Use `PASS`, `BLOCKED:<exact reason>`, or `NOT_APPLICABLE`.

- `AUTHORITY`: current task, artifact, and state precedence is explicit.
- `IDENTITY`: exact paths, hashes, revisions, and live bytes are bound.
- `SCOPE`: repository, checkout, ownership, and dirty-state boundaries pass.
- `RED_GREEN`: the real failure is reproduced and the same probe is green.
- `ATOMICITY`: failure leaves no partial authoritative state.
- `ROLLBACK`: the complete prior state is restored and validated.
- `RESIDUE`: temporary files, locks, sidecars, processes, and jobs are absent.
- `CAPACITY`: bounded resources are measured and admitted before mutation.
- `SOURCE_READINESS`: the candidate itself is safe.
- `ACTIVATION_READINESS`: external runtime gates independently pass.
- `MODEL_PROFILE_STATUS`: enforcement is attested or explicitly unavailable.

Classify material evidence as `DIRECTLY_VERIFIED`, `PACKET_CLAIMED`,
`INFERENCE`, or `UNKNOWN`. A packet claim is not direct proof. Keep source
correctness separate from installation, activation, deployment, and runtime
permission.

## Repeated-Error Lessons

Do not preload these references. Read exactly one matching lesson only when the
same failure class occurs twice in the current work or durable history, or when
a claimed fix is disproved by a concrete P0/P1 reproducer. Rebind changed
artifacts after applying the lesson. If several classes recur, read only the
files for current blockers.

| Repeated failure class | Conditional lesson |
|---|---|
| Stale authority, wrong checkout, changed bytes, invalid prior approval, or a supposedly read-only command mutates state | [repeated-artifact-authority.md](references/repeated-artifact-authority.md) |
| Claimed fix misses the real mode, transaction leaves partial state, rollback is assumed, or residue remains | [repeated-regression-transaction.md](references/repeated-regression-transaction.md) |
| Size or quota failure, late admission, unsafe compaction, cache-only recovery, or state growth blocks useful work | [repeated-capacity-recovery.md](references/repeated-capacity-recovery.md) |
| Dirty or unowned scope proceeds, narrative output impersonates completion, callback lookup is stale, or source readiness is confused with activation | [repeated-scope-completion.md](references/repeated-scope-completion.md) |
| One failed tool or route becomes BLOCKED, current sources are not searched, temporary continuity is ignored, or a long fix unnecessarily stalls independent work | [repeated-premature-blocking.md](references/repeated-premature-blocking.md) |
| Critical depth leaks into low-risk slices, unchanged bytes are re-reviewed, broad gates rerun after micro-edits, progress auditing becomes its own program, or proof artifacts multiply without changing a decision | [repeated-proof-overprocessing.md](references/repeated-proof-overprocessing.md) |
| Existing behavior is rediscovered after design/coding, merged ownership is forgotten, a Sheet warning is ignored, DOM is mistaken for backend proof, or a graph/memory result is treated as authority | [repeated-existing-system-ownership.md](references/repeated-existing-system-ownership.md) |

## Universal Loop

This is an internal reasoning checklist, not eight mandatory phases, documents,
or user-visible stop points. Collapse it into direct execution when the route is
clear; expand only the steps needed for unresolved judgment.

1. **Frame.** Identify the real objective, audience, authority, constraints, success predicate, unknowns, and forbidden actions.
2. **Decompose.** Split the task into bounded subproblems, dependencies, and likely failure points.
3. **Explore.** For nontrivial choices, generate at least two credible approaches or hypotheses. When stalled, include direct, orthogonal, and temporary or parallel routes. Seek disconfirming evidence, not only support.
4. **Decide.** Compare correctness, evidence, cost, risk, reversibility, and user intent. State why the selected approach wins.
5. **Execute.** Take the smallest useful steps, gather current evidence, and preserve checkpoints before risky changes.
6. **Challenge.** Re-read the current artifacts as a skeptical reviewer. Test assumptions, edge cases, interruptions, and the strongest alternative.
7. **Verify.** Use task-specific proof. Label material claims `Verified`, `Inference`, or `Unknown`; calibrate confidence.
8. **Synthesize.** Lead with the result, essential rationale, evidence, remaining risk, and one next action when needed.

## Teacher-Critic-Evaluator Loop

For Deep or Critical work with a remaining decision that deterministic evidence
cannot resolve, separate roles even when one agent performs them:

- The **solver** proposes candidate approaches.
- The **critic** receives the raw task and artifacts, attacks assumptions, and proposes counterexamples.
- The **evaluator** scores candidates against a predeclared rubric and evidence.
- The primary agent revises once, then verifies the winning candidate directly.

Do not instantiate these roles for routine coding, mechanical checks, or an
already reviewed unchanged candidate. Use one independent reviewer at the
stable decision boundary when it can change acceptance. If a requested model
or thinking tier is not tool-enforced or observable, record
`MODEL_PROFILE_NOT_TOOL_ENFORCED`; never silently substitute and claim
equivalence.

## User-Facing Reasoning

Perform deconstruction and self-correction internally. Never expose hidden chain-of-thought or manufacture `<thinking>` traces. Provide a concise decision rationale, assumptions, alternatives, evidence, and corrections when they help the user verify the result. Match answer length to the user, not to reasoning depth.

## Task Adapters

Read [references/task-adapters.md](references/task-adapters.md) after selecting the relevant domain. Combine only adapters the task actually needs.

## Rationalization Guards

| Shortcut | Correction |
|---|---|
| "One plausible answer is enough." | Compare a credible alternative. |
| "The critic agreed." | Verify against artifacts and rubric. |
| "More reasoning is always better." | Match depth to difficulty and stop conditions. |
| "Show all thinking to prove quality." | Show evidence and concise rationale, not hidden chain-of-thought. |
| "The skill changed, so the running task changed." | Skill edits are not retroactive; steer or restart active work explicitly. |
| "Long-running means stuck." | Inspect live deltas; bounded gates and new regressions are progress. |
| "The preferred tool failed, so the task is blocked." | Mark that route blocked, then test an independent mechanism inside the same authority. |
| "A workaround would weaken safety." | Use only a reversible bridge that preserves every hard invariant, or reject that bridge specifically. |
| "The durable fix is long, so nothing else can move." | Continue a non-dependent slice or bounded continuity route without claiming final completion. |
| "The program is Critical, so every substep must be Critical." | Select depth for the current slice; preserve high-risk milestone gates without inflating low-risk work. |
| "The blocker remains, so another review of the same bytes may help." | Reuse the hash-bound review unless there is changed evidence or a new falsifiable probe. |
| "A deeper model found ten possible concerns, so all ten need work." | Rank them against the acceptance predicate; execute only requirements and demonstrated material risks. |
| "Updating a checklist changed its hash, so execution evidence is stale." | Keep mutable status separate from immutable executable inputs; rebind only semantically changed authority. |
| "We need a chunked audit before continuing implementation." | Audit only a named uncertainty that can change the next action; otherwise finish the active slice first. |
| "More process proves more care." | Care is correctness with proportionate evidence. Run `DELIVERY_RESET` when process stops changing decisions. |
| "The user did not explicitly ask for web search." | When browsing is allowed and current external facts materially affect the decision, verify them with primary sources. |
| "Role limits prevent creative alternatives." | Roles limit authority, not analysis; redesign the route without taking another role's action. |
| "I remember the project." | Rebind the durable checkpoint and current evidence; memory may be stale. |
| "The helper finished, so the task is done." | Verify and integrate its result; only root acceptance closes the task. |

If evidence cannot support the conclusion, return `UNKNOWN` or `BLOCKED`, not a polished guess.
