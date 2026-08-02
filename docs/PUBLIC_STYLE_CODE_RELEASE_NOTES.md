# Public Style + Code Release Notes

## What is safe to use

`x9-loop-style` is the stable default for normal and existing projects. It
uses self-contained packets, source-backed context, documentation, durable
receipts, and direct handoffs without starting a Controller.

## What remains a trial

`x9-loop-code` retains the Controller source for an owner-approved, fresh
disposable-project canary only. It is experimental and is not a production
workflow, migration route, or recovery mechanism for existing projects.

## Public validation status

- Style/package/project-docs regression set: PASS (46 tests).
- Generated registry and source-manifest validator: PASS.
- Secret scan: PASS (no high-confidence matches).
- One full test discovery run exceeded its ten-minute bound without a failure
  diagnostic. It is recorded as `FULL_SUITE_TIMEOUT`, not a passing claim.

No live Codex installation, provider call, deployment, Controller activation,
or project runtime state was exercised for this public source update.
