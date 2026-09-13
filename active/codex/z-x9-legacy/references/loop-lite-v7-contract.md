# X9 Loop Lite V7 Contract

V7 patches V6 at `5f55e75caead79306c0bffdd2c14443039b25a19`.
`loopctl.py` remains the only Controller and state engine.

## Authority Flow

1. Verify packet bytes, Git identity, import coverage, doctor, and context.
2. The Controller is the sole writer of immutable `WORK_ORDER.json`.
3. Linx reads only `ACTION.json`, transports it unchanged, records the exact
   acknowledgement, and stops. Linx never selects, combines, edits, or reviews work.
4. Worker reads the Work Order, program summary, and selected feature packets.
5. Deterministic acceptance runs before any conditional Thinx judgment.
6. V7 predeclares one staged-diff Thinx review before C1 because migration and
   security boundaries change. Any staged-byte change invalidates the review.
7. C1 is the unchanged reviewed source commit. C2 is attestation-only.

C1 review occurs only after deterministic gates pass. A deterministic
`activation_allowed=false` is final `NO_GO` evidence and never calls Thinx.

## Thread Messages, Owner Input, And Long Runs

Plain Codex task/thread messages are signals, not executable authority. The
owner may send normal text, Markdown, files, links, screenshots, plans, or
requested actions to any role; do not reject owner input merely because it is
noncanonical. Preserve exact text and attachment or link identity and hashes as
non-executable owner context. Linx may forward owner input unchanged, but Linx
cannot label it captured or selected. Controller alone turns owner context into
a Work Order.

A plain message cannot execute or impersonate ACTION.json, WORK_ORDER.json, or
WORKER_RESULT. Missing canonical schema, registered identity, path, or SHA-256
returns `NONCANONICAL_THREAD_MESSAGE` with zero Controller or delivery state
changes.

A durable primary goal/program is executed as finite Controller-selected CHUNK
Work Orders. Each has a per-chunk success predicate, per-chunk STOP contract,
per-chunk checkpoint, per-chunk dependencies, and per-chunk claims. There is no
time-based loop and no pre-reservation.

An owner-approved external Codex heartbeat monitor may run outside the Loop
runtime only. It targets the Controller task, appears in APPROVED_JOBS.json
before ACTIVE with stable job ID, command hash, and schedule hash, and performs
one bounded Controller pass per wake. It must not poll or blindly wake Linx.

## Canonical Bytes And Caps

- Paths are repository-relative Unicode NFC with forward slashes. Reject
  absolute paths, `..`, case-fold collisions, symlink escapes, and reparse escapes.
- Resource identity uses one case-folded Controller key for persistence, conflict
  checks, and Work Order comparison. Immutable Work Order bytes retain the
  owner/source spelling; a different canonical resource still fails closed.
- JSON uses sorted keys, compact separators, UTF-8, no floats/non-finite values,
  and exactly one trailing LF. JSONL is one canonical object plus LF per line.
- Caps: program 16 KB; feature 32 KB; Work Order 16 KB; local checkpoint
  16 KB; coverage summary 16 KB; coverage shard 64 KB; ACTION 4 KB; snapshot 8 KB.
- Full inventory is mechanical and outside model context.

## STOP And Cache

Each Work Order includes success predicate, maximum attempts, wall seconds,
model calls, and tokens (`null` when unavailable). Before every call: check
success, all hard bounds, then prompt-prefix and tool-schema hashes.
No model call occurs after exhaustion. Hard bounds override the proof-bound
challenge. Unknown token telemetry is recorded exactly as `Unknown`.

Every call receipt records call ID, action class, attempt, compaction generation,
pre/post prompt-prefix and tool-schema SHA-256 values, stability, drift reason,
and token usage. Intentional changes start a recorded action class. Unexplained
drift emits `CACHE_PREFIX_CHANGED` before another call.

## Jobs And Events

The project monitor mode is `DISABLED` by default. Core Loop is event/callback
driven and scheduler-independent on Windows, Linux, and macOS:
`CORE_LOOP_READY` covers Controller/state/ACTION/receipts only. Provider absence,
unavailability, other-project jobs, and unrelated OS jobs never block it.

`EXTERNAL_WAKE_READY` is evaluated only when the project explicitly selects
`EXTERNAL` and binds its exact project profile plus approved provider, job ID,
command hash, and schedule hash. Exact current-project findings preserve
`NEW_JOB`, `COMMAND_DRIFT`, and `SCHEDULE_DRIFT`; unknown project binding also
blocks only this wake gate. Doctor inventories supported jobs without exposing
raw commands and reports `OTHER_PROJECT_JOB` or `UNRELATED_OS_JOB` as
nonblocking. It never auto-approves, creates, runs, edits, cancels, or rounds
schedules.

- Deterministic success -> `FEATURE_DONE`.
- `HARD_EXTERNAL`, conflicting owner requirements, exhausted STOP, or unresolved
  cache drift -> `OWNER_DECISION_REQUIRED`.
- A new autonomy-bound Work Order requires two distinct canonical approach
  receipts before `HARD_BLOCKER_AFTER_2_PROOFS` and one silent Thinx review.
  Legacy immutable orders retain their historical three-proof interpretation.
- Controller THINKER admission classifies an explicit canonical question record
  as `CONTINUE_LOCAL`, `LOCAL_FALLBACK`, `SUBAGENT_ONCE`, `THINKER_ALLOWED`, or
  `OWNER_REQUIRED`. Missing or malformed records continue locally without a
  Controller mutation; this command cannot intercept arbitrary host messages.
- Soft failure -> local disposable checkpoint only.
- Claim/resource conflict -> pause only the affected Controller task.
- `recover-pre-dispatch-worker-result-contract-drift` is a typed, one-order
  recovery, not compatibility: it admits only an exact immutable Work Order
  hash whose current verification fails solely at `worker_result_contract`,
  while the persisted ACTION is `NOOP`, task/order/dispatch are
  `REGISTERED`/`CREATED`/one `PREPARED`, and no delivery, event, inbox, or call
  evidence exists. It validates then consumes only that dispatch's canonical
  bound `SEND_WORK_ORDER` outbox action, records its hash in the recovery
  receipt, and publishes the receipt within the lifecycle transaction with
  rollback cleanup. It releases only that terminal task's active
  claims/resources. Any other drift, packet mismatch, pending/malformed outbox,
  or evidence rejects with zero Controller delta; immutable packet bytes are
  never rewritten. If snapshot publication fails after the SQLite commit,
  `rebuild` may republish only the immediately prior prepared snapshot when its
  task/order/dispatch/outbox bytes exactly match that committed receipt and
  gate; retry then reports `ALREADY_RECOVERED`.

## Migration And Explicit Bans

Build the SQLite V2 database and an `x9-loop-lite-snapshot-v3` bundle as
side-by-side candidate state. Compact active task, order, and dispatch summaries
remain in the at-most-8-KB V3 root. Exact variable active claims and resources
live in content-addressed `active-lifecycle-v1` shards of at most 64 KB together
with task, order, dispatch, delivery, event, gate, metric, pending outbox/ACTION,
program, and call-reservation detail. Root hashes and compact summaries bind
every exact row. Legacy V3 roots with inline active detail or
claims/resources-only shards remain
readable unchanged at their generation and upgrade only on a new generation.
Their historical active-outbox omission remains unchanged at the old generation;
upgrade reconstructs each missing PREPARED action even when terminal outbox rows
exist, then binds the exact pending ACTION bytes in active-lifecycle shards. The
root and immutable shard set are the complete V7 recovery truth;
every referenced shard and the bound prior-generation root must be preserved.
Missing, tampered, or misclassified detail fails closed; root-only recovery is
insufficient. Preserve the complete V6 database, WAL,
SHM, snapshot, and hashes. Validate before atomic replacement; any failure
restores the entire V6 recovery set. Rollback moves the whole V7 snapshot
namespace into failed-attempt evidence before restoring V6 so a retry starts
with no conflicting active-generation shard. Active missing worktrees are
fatal. `core-legacy` can be `HISTORICAL_MISSING` only with zero active ownership
proofs and an exact owner-decision hash.

No polling or heartbeat exists inside the Loop runtime; no interval rounding, cache warming, cron loop, autonomous
sentinel, second Controller, EventStore, scheduler, duplicate runtime, Orca,
Windows UI automation, Dokploy, product deployment, or fourth commit is allowed.
