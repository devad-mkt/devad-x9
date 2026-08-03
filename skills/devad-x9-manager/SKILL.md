---
name: devad-x9-manager
description: Compatibility name for older Devad X9 manager prompts. Redirects normal coordination to x9-loop-style without creating a second manager or V7 Controller flow.
---

# Devad X9 Manager Compatibility

This historical name is a temporary v6-style redirect. Immediately load and
follow `$x9-loop-style`; keep the requested role and prompt meaning, but use
one self-contained packet, exact Git evidence, durable receipts, and direct
signal-only handoffs.

Do not run a second manager flow, Controller Work Order, ACTION transport,
recovery route, role registry, or periodic monitor from this shim.

Report once in durable state:
`COMPAT_REDIRECT:devad-x9-manager:x9-loop-style`.

The old `.devad/manager/loop/` and V7 runtime files are historical/canary
evidence only. Removing this compatibility skill needs a later explicit owner
decision.
