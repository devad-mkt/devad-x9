# Lesson 03: Existing Capability Discovered Too Late

## Proven Failure

A delivery plan treated publishing destinations as missing even though an
accepted Sheet and merged POST source already identified POST as the owner of
target validation, drafts, dispatch claims, quotas, usage accounting, and
provider/channel behavior. The final implementation reused POST, but ownership
was discovered after avoidable design and coding work.

## Root Causes

| Problem | Consequence | Required correction |
|---|---|---|
| Capability absence was assumed from request wording | Existing behavior was redesigned before reuse was tested | Prove `EXISTING_FEATURE` before selecting `NEW` |
| Accepted merge history was not rebound to the current branch | Prior owner work was present but mentally treated as unrelated | Inspect accepted commits, merge-base, and current call sites |
| Accepted ancestry was treated as semantic parity | A merge retained a stale blob even though the correct predecessor was reachable | Bind decisive paths or predicates before integration, then verify the integration-tip result and focused regression |
| Sheet/handoff evidence was treated as narration | A direct ownership warning did not change the plan | Rebind the claim to current source and record the reuse seam |
| DOM/frontend review was treated as complete discovery | Visible controls did not reveal jobs, services, persistence, or provider authority | Trace UI/request through backend ownership and runtime consumption |
| Backend source was treated as complete product proof | Current visible settings and behavior remained unknown | Prove the changed user-facing path when applicable |
| Tests were designed after the new structure | Passing tests could validate a duplicate architecture | Start from an existing acceptance test or a red seam regression |
| File-by-file reading replaced flow tracing | Similar AI/POST names hid the canonical owner | Trace one vertical user-to-result journey |
| Heavy graph/memory tooling was considered too early | Discovery risked becoming another project | Use `rg`, Git, framework inspection, and focused DOM first |

## Mandatory Response

Before planning and again before the first behavioral edit, record one compact
row in the existing plan or Work Order:

```text
EXISTING_FEATURE / UI_SETTINGS / SERVER_AUTHORITY / PLAN_ENTITLEMENT
REFERENCE_REUSE / PERSISTENCE_CONSUMPTION / INTEGRATED_HISTORY
TEST_PROOF / GAP / CHANGE_MODE
```

Use `VERIFIED:<evidence>`, `NOT_APPLICABLE:<reason>`, or `UNKNOWN`.
`CHANGE_MODE` is exactly `REUSE`, `EXTEND`, `NEW`, or
`REPLACE_AUTHORIZED`. `NEW` needs source-backed absence in the touched scope;
replacement needs owner authority.

## Fast Evidence Order

1. Current Git identity, accepted integration commits, and exact call sites.
2. Routes, requests, services, models, jobs, migrations, settings, flags,
   entitlements, provider adapters, and focused tests.
3. Current UI/DOM plus request behavior for changed visible functionality.
4. Owner-named Sheets, handoffs, and references, rebound to current source.
5. Framework-native inspection such as Laravel routes/schema when available.
6. Graphify only if a cross-module owner remains unresolved after the targeted
   pass. A graph remains advisory until its claim is verified in current bytes.

Stop when owner, seam, and true gap are proven. Do not create a new inventory,
percentage audit, graph, or report. Unknown ownership blocks only the dependent
edit. Do not rewrite already accepted work unless a concrete duplicate,
contradiction, or behavioral defect is demonstrated.

After a divergent merge, rerun the smallest owner-facing regression at the
integration tip before downstream work starts. Reachable commits, clean merge
status, broad CI, and deployment health do not substitute for checking the
resulting behavior. Refresh downstream bases to that verified integration SHA;
never repair drift by adopting an entire historical branch.
