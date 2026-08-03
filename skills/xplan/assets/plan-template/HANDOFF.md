# <Project or Feature> Handoff

Status date: <YYYY-MM-DD>
Status: `NAVIGATION_ONLY`
Canonical entrypoint: `PLAN.md`

This is a mutable resume checkpoint, not authority. The newest immutable Work
Order and current Git/test/browser/runtime truth win.

## Current identity

- Manager/worker: <task identities>
- Worktree/branch/HEAD/upstream: <exact identities>
- Current authority: <Work Order path, bytes, SHA-256>
- Immediate receipt: <path, bytes, SHA-256 or NONE>
- Known dirt/proof state: <exact paths and PASS/FAIL/NOT_RUN>

## Resume read

Read `PLAN.md`, one current Work Order, one dependency receipt, exact claimed
source/siblings, bounded ledger rows, and one matching guardrail subsection.

## Exact next action

<one dependency-ready action>

Durability: `<LOCAL_ONLY/COMMITTED/PUSHED with exact SHA>`
