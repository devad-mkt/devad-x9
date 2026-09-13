# Deploy Bridge Sentinel

This checkout is deploy-only. Do not implement feature, debug, docs, or
recovery work here.

Use this source folder for new X9 work:

```text
$DEVAD_ROOT\core-aio\core-x9
```

Allowed actions in this checkout:

- inspect state
- export a diff
- verify deploy or health
- apply a previously committed X9 commit into a clean v105 bridge

If this checkout is dirty, classify it as `ORPHAN_PATCH`: export/report the
diff, port relevant changes to `$DEVAD_ROOT\core-aio\core-x9`, or discard it.
