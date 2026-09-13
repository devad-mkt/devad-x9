# Product-candidate goal template

Use this lesson when a long goal lets the worker stop on a missing preferred
proof route, transport, gateway, browser bridge, or runtime executor.

The goal must define the product outcome first and proof rows second. Missing
one proof row blocks only that row, not every source/test/UI/fake-provider
slice.

## Template

```text
Manage the full <FEATURE> program under <PLAN_PATH> through its completion
firewall on one exact final source SHA.

Target: deliver <RC_LABEL> as one exact local/integration branch and PR after
required source work, focused tests, semantic rebind, review, and collision
check. Deployment, provider effects, spend, and live proof remain separate
gates; the deadline never weakens security, tenancy, provider, production, or
rollback boundaries.

OPERATING RULE: product-candidate first. The worker's primary job is to finish
user-visible behavior. Missing preferred proof transport blocks only that proof
row. Continue any disjoint source, test, fake-provider, UI, browser, semantic
card, disposable proof, deploy-readback, or documentation row still inside the
current envelope.

Before any BLOCKED/WAITING/FROZEN/HARD_BOUNDARY/RESUME_ON/OWNER_REQUIRED,
include:
- GOAL_OUTCOME
- EVIDENCE_TARGET
- FAILED_ROUTE
- WHY_ROUTE_FAILURE_APPLIES_TO_ALL_ALLOWED_ROUTES
- CHEAPEST_WORKAROUND_TESTED
- ACTION_NOW
- NEXT_MATERIAL_ACTION_OR_TRUE_OWNER_BOUNDARY
- CONSTRAINT_CLASS=HARD|SOFT|ASSUMED

If any field is missing, self-reject as REJECT_FALSE_BLOCKER:CONTINUE_LOCAL
and execute the next direct action.

After two process-only turns involving wrappers, packets, manifests,
transports, cleanup classifiers, or review reshaping, run DELIVERY_RESET:
- USER_VISIBLE_OUTCOME
- CURRENT_OWNED_SLICE
- CHEAPEST_SAFE_ACTION_NOW
- FOCUSED_PROOF
- DEFERRED_PROCESS_WORK

Keep these states distinct:
PLANNED, SOURCE_ONLY, TEST_PROVED, DISPOSABLE_BEHAVIOR_PROVED,
LOCAL_BROWSER_PROVED, SEALED_RC_PROVED, DEPLOYED, STAGE1_PROVED,
LIVE_PROVED.

Active continuation ladder:
1. <smallest current source/test/UI slice>
2. <current local/browser proof if runnable>
3. <disposable behavior proof if explicitly authorized>
4. <sealed/runtime/deploy/provider proof only when its receipt exists>
5. <true owner/operator boundary only after every allowed route is exhausted>

Do not invent generic infrastructure, credentials, provider integrations,
runtime workers, storage owners, or gateway packages when their accepted owner
contract is absent.

Mark complete only when the canonical plan's completion firewall accepts every
required row against the same final source SHA.
```

## Failure pattern this prevents

- A missing sealed gateway stopped a worker even though disposable behavior
  proof and source/test work were still allowed.
- A browser-native control failure was treated as owner/user action instead of
  proving source persistence and using an already-authorized task update route.
- Runtime topology proof absence stopped deploy-readback and task-shape
  validation that were independent.

The correction is always the same: preserve the invariant, switch mechanism,
and keep working on the next material row.
