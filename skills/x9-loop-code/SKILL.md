---
name: x9-loop-code
description: Use only for an owner-approved, disposable fresh-project trial of the X9 V7 Controller code. Never use for normal, existing, production, or recovery work; use x9-loop-style there instead.
---

# X9 Loop Code - Trial Only

## Hard boundary

`$x9-loop-style` is the stable default for all normal and existing projects.
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
`$x9-loop-style`; do not call `loopctl`.

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

## Evidence and exit

Keep a self-contained packet and exact Git/proof receipt. Run cheap checks,
focused tests, one stable-diff Thinker review, and the bounded canary. A failed
Controller route is evidence for the trial; it is never a reason to block
unrelated Style work. Return to `$x9-loop-style` for all continuing project
work.
