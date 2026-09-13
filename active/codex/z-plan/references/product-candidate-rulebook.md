# Product-Candidate Rulebook

Use this when building or repairing a long-running plan where agents are
stopping for tool routes, proof transport, reviews, or capability packaging
instead of delivering product behavior.

## Plan invariant

The plan exists to ship a working candidate. It is not a proof factory.

Each lane must carry:

```text
USER_VISIBLE_OUTCOME:
CURRENT_PRODUCT_SLICE:
OWNED_PATHS:
FOCUSED_PROOF:
PRIMARY_ROUTE:
CHEAPEST_STRUCTURAL_FALLBACK:
DISJOINT_LOCAL_CONTINUATION:
TRUE_OWNER_BOUNDARY:
STOP_AFTER:
```

If `CURRENT_PRODUCT_SLICE` is absent, the lane is event-only and should not
consume worker turns.

## Forbidden plan shapes

- More than one active plan/router for the same feature.
- New packet family after a route failure unless the product contract changed.
- Review of unchanged material bytes.
- Rebinding or merging during domain-local branch work before RC approval.
- Treating a missing preferred tool as a whole-goal blocker.
- Turning disposable test proof into sealed RC proof, or sealed RC proof into a
  blocker for local source behavior.
- Asking Thinker/Looper to approve routine harness, parser, browser, quoting,
  source, or focused-test fixes.

## Required split

Track proof rows independently:

| Row | Blocks |
|---|---|
| Source/test behavior | Product code readiness only |
| Browser/UI proof | Visible acceptance row only |
| Disposable runtime proof | Behavior confidence only |
| Deploy/readback | RC deployment row only |
| Provider/publication/spend | Live external row only |
| Sealed transport/capability | Reusable/RC transport row only |

No row may block another row unless the current slice explicitly depends on it.

## Loop breaker

After two process-only turns, the plan must force:

```text
DELIVERY_RESET:
  smallest product action:
  focused proof:
  process work deferred:
```

After one failed route plus one discriminator, the next update must be one of:

- product source/test action;
- split focused proof;
- structurally different direct route;
- exact true owner/operator boundary.

## Examples

- CHAT PG: sealed gateway missing blocks sealed RC only. Disposable PG behavior
  proof remains valid when owner authorized it.
- Content: runtime topology tool failure does not block UI/backend persistence
  repair, source deploy/readback, or task-shape validation.
- Image: local browser failure blocks only visual proof; Node/PHP/source proof
  continues until the visual row is active.
