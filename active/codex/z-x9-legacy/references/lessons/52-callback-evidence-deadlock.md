# Lesson 52 — Callback evidence must not deadlock result consumption

Status: fixed in the next V7.3 Lite hotfix after `81056bd9889671faafd6a705318f34359096c1d8`.

## Trigger

Brain Worker `019f8716-0bba-72c0-a989-4b42e260a1da` released a valid result for task
`task-13b2f544-1c16-4eb5-8f24-c741713e7104`. Its receipt, proofs, C1, attestation-only
C2, and remote readback passed, but Controller returned `RESULT_GIT_INVALID` while the
approved OMP Worker `019f870b-eec0-7331-a494-1d642d127b44` waited for the claims.

## Violated invariants

- Canonical callback evidence must survive without becoming unauthorized worktree dirt.
- A consumed terminal task must release its claims without manual evidence deletion.
- Preserved evidence from `COMPLETE` and `SUPERSEDED` tasks must be reusable only after
  its full receipt, event, worktree, and Git identity is revalidated.
- A failed transaction must remain zero-delta.

## Root cause

The active-result allowlist recognized the Worker `INBOX_EVENT.json`, receipt, and proofs
but not the adjacent canonical `RESULT_READY.json`. Its historical outbox validator also
recognized only `COMPLETE`, excluding a valid consumed callback retained by a
`SUPERSEDED` task. Both files were therefore misclassified as product dirt.

## Correction

Validate and admit at most one adjacent `RESULT_READY.json` only when it is canonical,
untracked, non-reparse, deterministic, and exactly bound to the already validated
requester, profile, event, result, task, Work Order, dispatch, packet, and Worker. Admit
historical consumed outboxes for `COMPLETE` or `SUPERSEDED` only when the Work Order has
the same terminal state and the dispatch is `COMPLETE`. All other dirt remains rejected.

## Regression and rollback

Focused tests cover exact acceptance, wrong-requester zero delta, unrelated sibling
rejection, and restart/reuse with a superseded consumed outbox. The real repair consumed
the Brain result as `FEATURE_DONE`; replay returned `ALREADY_CONSUMED` with identical
database, snapshot, ACTION, and signal hashes. Rollback reverts only the Controller,
tests, lesson, and generated manifest while preserving every runtime evidence byte.

Token telemetry: Unknown.

Host-enforcement status: `MODEL_PROFILE_NOT_TOOL_ENFORCED`; no model or thinking override
was used.
