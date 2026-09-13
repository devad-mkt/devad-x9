---
name: z-ship
description: v2 canonical skill for executing accepted coding plans in product-candidate-first slices without false blockers, process loops, or over-engineered proof routes.
---

# zShip

This is the canonical `smooth-coding` skill. If another installed
`smooth-coding` copy exists, it is a compatibility shim and must route here:
`$AGENTS_HOME\skills\z-ship\SKILL.md`.

Start from the accepted plan and current Git truth. Implement the smallest
owned slice, run its focused proof, and continue to the next authorized slice.
Keep unrelated work moving when a dependency blocks one chunk; do not ask for
routine approval or create review loops. Escalate only genuine security,
architecture, destructive, secret, spend, production, or owner boundaries.

## Product-candidate-first contract

Default output is working product behavior. Security, tenancy, migrations,
provider spend, production activation, secrets, destructive actions, and
rollback remain hard gates, but they gate only the action that depends on them.
They do not justify stopping source work, local tests, disposable test proof, or
other packet-authorized slices.

Use this order:

1. Identify the user-visible outcome and the current owned slice.
2. Reuse existing source, route, test, browser, or runtime seams before building
   new infrastructure.
3. Implement the smallest vertical behavior change.
4. Run the focused proof that can fail that behavior.
5. Continue the next authorized slice or record one real owner boundary.

### Reuse-first single-pass budget

Before the first behavioral edit, trace the existing vertical once:

`visible UI -> route/request -> authorization -> service -> persistence ->
effect/adapter -> focused test`.

Compare that chain with the task-authorized history/reference evidence and
record `REUSE`, `EXTEND`, `NEW`, or `REPLACE_AUTHORIZED`. `NEW` requires a
targeted absence result. Stop discovery when the owner, reusable seams, and
concrete gap are known; do not turn discovery into recurring evidence rounds.

For one channel or feature row:

- run one bounded evidence pass and reuse it until relevant source/reference
  bytes or the acceptance predicate materially change;
- group related safe changes into one maintainable vertical, run focused gates
  during editing, then use at most one stable-byte independent review;
- do not request another review for unchanged bytes, deterministic PASS/FAIL,
  formatting-only changes, checklist edits, or narration/hash churn;
- prefer existing POST, CHAT, Laravel, route, persistence, queue and test owners;
  every new production file, table, job, abstraction or polling loop must be
  required by the product contract, not by proof convenience;
- for settings on every channel, including manual-key channels, inspect the
  existing product-admin provider surface and its workspace Add/Connect surface
  before adding another settings owner; when POST has no matching provider,
  record that targeted absence but still compare/reuse its shared shell,
  validation, secret-redaction and role-gate patterns;
  reuse their components, registry, validation, encrypted-secret, redaction,
  role-gate and focused-test owners when semantics match, and record why an
  existing seam cannot be extended before choosing `NEW`;
- keep queries bounded/index-aligned, avoid synchronous provider loops and
  repeated polling, and do not add CPU/RAM/DB infrastructure before measured
  need; maintainability and low steady-state resource use are acceptance
  predicates, not cleanup promises.

When exact reference parity matters and authenticated access is authorized,
the evidence pass must inspect the reference screen in a real browser. Capture
visible controls plus tabs, menus, modals, collapsed sections, conditionally
rendered or hidden DOM, disabled actions, defaults, validation/error states,
and the request/effect each reachable control triggers. Distinguish
`VISIBLE`, `RENDERED_HIDDEN`, `CONDITIONAL_NOT_RENDERED`, `DISABLED`, and
`ABSENT`. Redact secrets. A screenshot or visible-text list alone is not a
complete settings inventory.

Use at most one active bounded helper for mechanical history/DOM inventory or
one independent high-risk review. Give it a compact task-local packet, forbid
nested delegation, wait once, and do not redo its exact work. Deterministic
tests and source inspection stay local; subagents must reduce total work, not
multiply review turns.

When the request includes restoration, previous work, exact parity, missing
features, or suspected regression, read
`references/lessons/08-historical-retention-before-reconstruction.md` before
selecting the implementation base. Current HEAD, a newer path, or a unified
theme is not automatic replacement authority. Freeze the owner-selected
historical baseline and current-new-work protections before editing.

An unfinished owner-selected recovery slice is a focus lock. A generic
`continue`, Thinker/Looper callback, new queue suggestion, or unrelated proof
request resumes that same slice; it cannot advance the plan until the canonical
active-slice row records owner acceptance or an explicit owner-approved defer.
Before any recovery write, bind the absolute target root, read-only reference
roots, exact target paths, and preimage hashes. If a patch resolves outside the
target root, touches a reference worktree, or has truncated/ambiguous output,
stop, restore the exact preimages, verify their hashes, and only then resume.

Do not perfect the baseline before a product candidate exists. Do not create a
gateway, listener, package, manifest, review packet, new plan, helper, or
wrapper unless the product contract itself requires that artifact or no
disposable/direct route can preserve the hard invariant.

### Evidence-cache and implementation-budget gate

Reuse an accepted evidence, test, browser, or review receipt while its bound
root, source/reference bytes, denominator, and acceptance criteria remain
unchanged. Reopen it only for a material delta, failed gate, contradiction, or
owner-changed acceptance, and record that trigger once. Never spend another
round or worker merely reconfirming an unchanged claim.

Extend existing owners, components, routes, and tests before adding files or
abstractions. Choose the smallest maintainable vertical with bounded indexed
work. Reject duplicate helpers, stores, dependencies, persistent proof
infrastructure, polling, or designs that add avoidable files, database work,
CPU, or RAM without changing acceptance.

For adopted settings, evidence must include a settled authenticated browser
DOM inventory of visible plus hidden, collapsed, tabbed, modal, disabled, and
conditionally absent controls. Map each reachable control to its source,
persistence, and effect owner or `UNKNOWN`; a screenshot or visible note alone
cannot close the settings denominator.

A shared admin/provider screen is a reuse and authority seam, not automatic
product parity. Reuse it to avoid duplicate work, but never expose super-admin
controls in a workspace, translate publication success into CHAT messaging
success, or call a channel complete without its own Connect, General,
persistence and effect claim matrix.

Classification is not implementation. Do not label a required channel feature
`EXTERNAL_GATED` merely because its provider proof is external when local
normalizers, storage, adapters, workers, routes, UI, or fake-backed contracts
are still missing. Reconcile reusable current/history/admin owners first, then
finish the smallest local vertical before requesting live-provider proof.

### Local-first completion and effect decomposition

When the owner asks to finish local product work before PostgreSQL, providers,
deployment, or live proof, that ordering is binding. Before entering a remote
proof lane, sweep the canonical checklist for every independent `BUILD_NOW` or
`SAFE_SHELL_NOW` row and finish those rows through source, focused tests,
types/format/build, and available local browser proof.

Never gate a whole page because one control has an unavailable effect. Split
each surface into:

`visible shell -> safe read model/local draft -> persistence -> external effect
-> browser/PG/provider/live proof`.

An unavailable credential, callback, storage, worker, provider, PostgreSQL, or
deployment owner gates only its dependent layer. Build an honest disabled,
unconfigured, unavailable, or explicitly non-persistent state when current
source and the reference denominator make that state truthful. Do not present
the shell as proof that the gated effect works.

### Hourly channel/feature delivery cutoff

For an evidence-backed channel or major feature, use one grouped mission with
hourly decision deadlines instead of one mission per checklist row:

1. Hour 1: finish the single evidence/ownership pass and freeze the semantic
   union, protected surfaces, exact gap and file budget.
2. Hour 2: deliver the primary user path and real persistence first. For
   channel settings this means Connect/account isolation and authorized
   General settings save/reload, not notes or browser-memory drafts.
3. Hour 3: group remaining RC1-essential local behavior into the fewest
   existing owners. Keep provider-only and optional behavior separate.
4. Hour 4: run one focused proof set, affected format/types, available browser
   proof and at most one stable-byte review.

Count active delivery time only; do not count owner sleep or external queue
waits. At each boundary, apply Ponytail's ladder: remove speculative scope and
extend an existing owner before adding code. Missing a deadline is
`TIMEBOX_MISS`, not permission for silent overtime, a fresh evidence worker,
another review, or a completion claim. Immediately choose the shortest honest
path: smaller reuse/extension, explicit defer of optional/provider-only work,
or one owner-approved extension naming the unresolved must-have. Never weaken
validation, tenancy, security or accessibility to meet the cutoff.

Every bounded helper packet must include the active execution-card path,
current active-hour checkpoint, exact remaining outcome, forbidden later rows,
and `NO_AUTOMATIC_TIME_EXTENSION`. A helper receipt that omits these fields or
returns after one C-row is incomplete and cannot advance the channel.

A coding mission owns the complete local vertical across frontend, backend/read
model, SQLite/fakes, focused tests, types/format/build, and available local
browser evidence. Returning after research, one file, or one green test while
another owned local substep remains is an incomplete mission, not a checkpoint.

Count unfinished **executable local product rows** separately from lower-tier
browser evidence that genuinely consumes PostgreSQL, HTTPS/publication, or
another hard product invariant. When source and focused tests pass but an
honest browser route reaches that invariant, record
`SOURCE_TEST_PROVED_BROWSER_PENDING_<INVARIANT>`, preserve the proof row, and
continue. Do not add a SQLite tenancy bypass, fake HTTPS publication route, or
test-only product authority merely to turn the browser cell green.

## Action-before-architecture cutoff

Once the owned slice, hard invariants, and focused proof are known, the next
meaningful event must be a source edit, executable command, or acceptance
proof. Allow at most one short diagnosis after a failure. Do not respond by
building a wrapper, installer, gateway, manifest, review packet, renamed plan,
or reusable capability when a disposable test-only command or existing native
tool can prove the requirement. A test harness is code only when the product
needs it or it will be reused by an accepted contract; otherwise keep it an
ignored one-shot command and delete it after proof.

If two consecutive turns produce only explanation, planning, routing, hashes,
or review requests, stop that route immediately and execute the cheapest safe
alternative. A preferred proof mechanism is never an invariant. Preserve the
security property, then change the transport or test method. Do not mark the
host goal blocked for a lane wait; continue another authorized slice or leave
one resumable event without ending the goal.

If the next proposed action is another packet/review/manifest/routing artifact,
reject it unless it changes a product go/no-go decision.

Run `DELIVERY_RESET` when process has displaced delivery:

```text
USER_VISIBLE_OUTCOME:
CURRENT_OWNED_SLICE:
CHEAPEST_SAFE_ACTION_NOW:
FOCUSED_PROOF:
DEFERRED_PROCESS_WORK:
```

## False Blocker Guard

Before emitting `BLOCKED`, `WAITING`, `FROZEN`, `HARD_BOUNDARY`, `RESUME_ON`,
or `OWNER_REQUIRED`, prove:

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

If any field is missing, continue locally. Routine parser, quoting, harness,
browser, local test, and source issues are worker-owned repairs, not Looper or
Thinker questions. A missing preferred transport blocks only that evidence row;
split the proof or switch mechanism before escalating.

The fields are invalid if `ACTION_NOW` is passive. `ACTION_NOW` must name the
actor and concrete next operation: source edit, command, focused proof, cleanup,
receipt creation, or owner/operator action. Passive values such as `retain
claim`, `preserve packet`, `wait`, `none`, `unchanged`, or `do not allocate`
are false blockers.

True hard boundaries are limited to secret or raw credential/config/log
exposure, production/provider/spend action not already authorized, destructive
or irreversible data/action without rollback, unresolved shared collision on
the exact resource keys, or missing owner/operator authority that no allowed
local route can substitute.

## Goal status firewall

Do not mark the whole platform goal `blocked` merely because one proof row is
waiting on an external executor, browser bridge, deploy surface, provider
gate, or runtime admission.

If the exact missing owner/operator capability is known and has been routed,
the correct state is row-scoped:

```text
PARTIAL:<proof-row>
EVENT_ONLY:<missing-receipt>
ACTION_NOW:<owner/operator capability already named>
```

Return a normal final/update with the row-scoped dependency and stop touching
that row until the receipt arrives. Do **not** call the active goal blocked, do
not phrase it as whole-lane stopped, and do not wake the worker again for
status. Mark a platform goal blocked only when the entire requested objective
has no executable local row, no routed owner/operator action, and no known
resume predicate.

If no local row remains but an exact external cleanup, receipt, or
owner/operator capability is known, return a resumable event instead of a host
goal block:

```text
SOURCE_COMPLETE/EXTERNAL_ONLY
PARTIAL:<exact proof-or-cleanup-row>
EVENT_ONLY:<exact missing event>
ACTION_NOW:<named actor performs exact next operation>
RESUME_AFTER:<exact receipt predicate and next local command>
```

Do not call `update_goal(blocked)` or use equivalent host terminal status for a
row-scoped dependency with a known resume predicate. Any owner continuation,
test-only exception, or newly named external action invalidates an older
blocked classification immediately.

If the host UI/API has already marked a task goal `blocked` and exposes no
unblock operation to the worker, do not spend turns trying to repair host state.
Emit the normal resumable receipt above, then route the concrete
owner/operator action through the manager. The host label is display state; the
delivery program resumes from the receipt, not from another status report.

## Outcome split

Keep proof labels narrow:

- source proof is not browser proof;
- browser proof is not provider/publication proof;
- disposable test proof is not sealed RC proof;
- deploy/readback proof is not runtime-effect proof;
- transport proof is not product behavior proof.

A missing proof continues as `PARTIAL:<row>`, not a worker-wide stop. Continue
any source/test/browser/runtime row that is still inside the packet envelope.

## Runtime and tool fallback ladder

Use the shortest allowed mechanism that proves the same invariant:

1. direct source/test fix;
2. native framework command or focused test;
3. existing browser/session/API route already authorized;
4. disposable isolated test-only route with explicit label;
5. one structurally different transport or evidence path;
6. true owner/operator boundary.

Timeout means split the proof or fix the focused failing phase. Browser reset
means `BROWSER_TOOL_ONLY` unless the current row is specifically visible UI
acceptance. A failed SSH/Tailnet/Dokploy route blocks that route, not local
product work or a disposable behavior proof. Never rerun the unchanged failing
route.

## Worker response contract

A normal worker update should be:

```text
PRODUCT_PROGRESS:
CHANGED_PRODUCT_BEHAVIOR:
FOCUSED_PROOF:
NEXT_PRODUCT_ACTION:
SIDE_QUESTS_REJECTED:
TRUE_BOUNDARY_ONLY_IF_ANY:
```

Do not lead with `HARD_BOUNDARY`, `RESUME_ON`, or package hashes. If a boundary
is real, include the False Blocker Guard fields and one minimal owner/operator
action. If there is no boundary, start the next product action.

## Lessons

Read lessons only when their trigger is present:

- repeated process/review/checkpoint inflation:
  `references/lessons/01-workflow-final-check-overprocessing.md`
- routine delivery using too much coordination:
  `references/lessons/02-gate-ordering-and-quiet-autopilot.md`
- existing capability was missed:
  `references/lessons/03-existing-capability-discovered-too-late.md`
- delegation is multiplying work:
  `references/lessons/04-subagent-context-and-coordination-multiplication.md`
- GPT/Codex is building proof infrastructure instead of the product:
  `references/lessons/05-product-candidate-first-anti-overengineering.md`
- goal text is letting a worker stop on one missing proof route:
  `references/lessons/06-product-candidate-goal-template.md`
- Stage1 acceptance mixes source readiness, browser entry, runtime topology, and
  provider/spend gates:
  `references/lessons/07-stage1-content-acceptance-proof-split.md`
- an accepted historical surface was replaced, omitted, or reconstructed from
  screenshots/current HEAD instead of exact source:
  `references/lessons/08-historical-retention-before-reconstruction.md`

Preserve existing edits, use the declared rollback, and return one concise
result with changed paths, tests, and the next action. The complete portable
skill body is preserved in `references/portable-full-skill.md`.

## Provenance (consolidated 2026-09-12)

Canonical body: `z-ship` (2026-08-15 14:12:40, 15 files, sha256 `a682132f6bd86953`).

Former names now disabled: `AGENTS/smooth-coding`, `CODEX/smooth-coding`, `NINELLC/smooth-coding`.

Unique content from disabled copies is preserved under `references/preserved/` and is NOT authoritative; this body wins on any conflict.
