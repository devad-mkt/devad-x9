---
name: z-loop-code
description: Use only for an owner-approved, disposable fresh-project trial of the X9 V7 Controller code. Never use for normal, existing, production, or recovery work; use $z-loop-style there instead.
---

# zLoopCode

## Hard boundary

`$z-loop-style` is the stable default for all normal and existing projects.
This skill exposes the retained V7 Controller code only for a fresh,
disposable, owner-approved test project. It is experimental and not
production-ready.

Do not use it to repair, migrate, reactivate, or take over an existing
project. Do not import a project's old Controller state. Do not use it when a
safe Style packet can continue the work.

## Trial admission

Before any Controller initialization, prove all of the following:

- the project is newly created or disposable, has no production data, and has
  a clean, current Git base;
- the owner explicitly selected this trial and supplied a rollback/delete
  owner-action route outside Codex;
- one Looper owns the trial and one bounded canary is defined;
- provider, deployment, credential, money, and destructive actions are out of
  scope unless separately owner-approved.

If any item is absent, record `STYLE_FALLBACK_AVAILABLE` and use
`$z-loop-style`; do not call `loopctl`.

## Event-driven canary

Use one admitted Codex app native task-delivery for ACTION and RESULT_READY
signals. Do not use `codex exec resume` for an existing desktop task: the live
canary proved immediate interruption twice. Do not add a heartbeat, scheduler,
polling loop, mailbox service, or second manager.

Controller ACTION is the only pending delivery. Thinker, helpers, and Workers
write durable evidence but do not send parallel direct task messages. Looper
takes one current task snapshot: `active` returns `HOLD_ACTIVE` with no prompt;
`idle` or `notLoaded` permits one compact host-native signal. Duplicate
event/task/artifact identities, commentary, status, PASS acknowledgements, and
unchanged blockers are zero-delta.
Before a Worker finalizes any non-success result, require the shared Style
pre-stop admission; routine or same-root repair remains local, and a valid
packet-bound wait pauses only its dependent phase.

One transport failure permits one bounded Looper correction. A repeated
same-root transport failure ends the canary and returns to Style. Read
[the trial reference](references/fresh-project-trial.md) before starting.

## Evidence and exit

Keep a self-contained packet and exact Git/proof receipt. Run cheap checks,
focused tests, one stable-diff Thinker review, and the bounded canary. A failed
Controller route is evidence for the trial; it is never a reason to block
unrelated Style work. Return to `$z-loop-style` for all continuing project
work.

## Preserved capabilities (merged 2026-09-12)

Unique content recovered from archived variants. The canonical body above
wins where they overlap; these sections are the non-overlapping remainder.

### From `CODEX__x9-loop-code`

# X9 Loop Code - Trial Only
Do not invoke this skill, its Controller, or its packet machinery to solve a
Worker stall, missing test runtime, browser failure, database proof, transport
failure, or capability repair in an existing project. Those use direct local
execution and `$x9-loop-style`. A process-only cycle is not a reason to start a
canary or create a Controller action.
If normal product work is losing time to over-engineered proof infrastructure,
apply `$smooth-coding` v2 and `$x9-loop-style` product-candidate-first rules.
Do not use V7 code to make false blockers look more rigorous.
If a normal project message contains `BLOCKED`, `WAITING`, `FROZEN`,
`HARD_BOUNDARY`, `RESUME_ON`, or `OWNER_REQUIRED`, do not route it here. Apply
the Style False Blocker Guard first and return
`REJECT_FALSE_BLOCKER:CONTINUE_LOCAL` unless a true secret, production/provider,
spend, destructive, collision, or owner-only boundary is proven.

### From `NINELLC__x9-loop-code`

## One-hour external Looper check
An owner may enable an external host wake at most once per hour for this
disposable trial. It is not a Loop scheduler or poller. Each wake reads the
current receipt, runs `doctor`, and checks the one current action. It may fix
local source/test defects inside its claimed trial paths, or emit one compact
incident. It must never auto-retry a provider/deploy action, create or mutate
resources, handle secrets, override task models, bypass a failed gate, or
mutate Controller state outside its explicit action.
Stop the wake after the canary PASS/FAIL result or a repeated deterministic
failure. Read [the trial reference](references/fresh-project-trial.md) before
starting or monitoring a trial.


## Provenance (consolidated 2026-09-12)

Canonical body: `z-loop-code` (2026-08-13 00:38:44, 3 files, sha256 `61f97af0edcb759e`).

Former names now disabled: `CODEX/x9-loop-code`, `NINELLC/x9-loop-code`.

Unique content from disabled copies is preserved under `references/preserved/` and is NOT authoritative; this body wins on any conflict.
