# Stage1 Content acceptance proof split

Use this lesson when a Content/AI acceptance task mixes source correctness,
browser entry, task shape, runtime topology, provider spend, and publication
proof into one blocker.

## Rule

Content acceptance must be split by proof row:

- `SOURCE_ONLY`: React/Laravel code, controller/repository behavior, schedule
  math, row persistence, field-bound errors, labels, and tests.
- `LOCAL_BROWSER_PROVED`: browser can render controls, preserve task state,
  and show no console errors.
- `TASK_SHAPE_READY`: target task has valid dates, expected row count,
  selected targets, enabled buttons, and no warnings.
- `RUNTIME_EFFECTS_ADMITTED`: exact deployed SHA, rollback preimage, effective
  web/provider/publication gates, worker topology, and cleanup are admitted by
  a non-rendering capability.
- `LIVE_PROVED`: one visible authorized Run/Publish or Autopilot action
  produced durable row/provider receipts under spend/retry/media limits.

Missing `RUNTIME_EFFECTS_ADMITTED` does not justify more source rewrites after
`SOURCE_ONLY`, `LOCAL_BROWSER_PROVED`, and `TASK_SHAPE_READY` pass. Missing or
flaky browser-native date input does not justify provider execution; use the
existing same-origin task update route when task-configuration writes are
already authorized.

Do not mark the whole Content goal blocked when `RUNTIME_EFFECTS_ADMITTED` is
the only missing row and the exact runtime executor capability has been named.
The correct state is:

```text
PARTIAL:RUNTIME_EFFECTS_ADMITTED
EVENT_ONLY:STAGE1_CONTENT_RUNTIME_EFFECTS_ADMITTED
ACTION_NOW:shared runtime-capability owner provides the sanitized receipt
```

Then leave Content dormant without source rewrites, provider clicks, or status
wakes until that receipt exists.

## Required response to a tool failure

If a browser, Tailnet, Dokploy, topology-probe, or marker runner fails:

1. classify which proof row failed;
2. prove whether the source/task/browser rows can still advance;
3. switch to the cheapest structurally different allowed mechanism once;
4. if still unavailable, emit a complete False Blocker Guard packet for that
   proof row only;
5. do not wake the product worker again until the missing receipt exists.

## Concrete regression from Task26

Task26 reached a valid shape:

- start date and end date present;
- five planned slots;
- no schedule warning;
- Run full preview, Run and publish now, and Run Autopilot visible/enabled;
- spreadsheet idle;
- console errors zero;
- no provider/spend effect.

That is `TASK_SHAPE_READY`, not `LIVE_PROVED`. The next real gate is
`STAGE1_CONTENT_RUNTIME_EFFECTS_ADMITTED`. Until that receipt exists, the
worker should not run provider actions, but it also should not rewrite source
or report the whole program stopped.
