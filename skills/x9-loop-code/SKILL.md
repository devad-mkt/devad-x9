---
name: x9-loop-code
description: Use only for an owner-approved, disposable fresh-project trial of the bundled legacy X9 controller code. Never use it for normal, existing, production, or recovery work; use x9-loop-style there instead.
---

# X9 Loop Code — Trial Only

`x9-loop-style` is the stable default for normal and existing projects. This
skill exposes the public package's bundled legacy controller code only for one
fresh, disposable, owner-approved experiment. It is experimental and not
production-ready.

Before a trial, prove a clean current base, no production data, a bounded
canary, and an owner-run rollback/delete route. Keep provider, deployment,
credential, money, and destructive actions out of scope unless separately
authorized.

If any admission item is absent, record `STYLE_FALLBACK_AVAILABLE` and return
to `x9-loop-style`; do not initialize the controller.

An owner may request one external read-only Looper check at most once an hour
for a disposable trial. It reads the current canary evidence and may correct
local claimed source/test defects. It is not a scheduler, retry loop, provider
runner, or production control path. Stop it at the canary's PASS/FAIL result or
a repeated deterministic failure.

Never use a trial to repair, migrate, reactivate, or take over an existing
project. A failed route is evidence for the trial and cannot block unrelated
Style work.
