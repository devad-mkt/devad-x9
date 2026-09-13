# Repeated Capacity And Recovery Failures

Read this only after bounded state, context, storage, quota, or concurrency
limits repeatedly reject valid work, or after compaction weakens recovery.

## Required Response

1. Measure canonical byte or resource contribution by section before changing
   limits. Test current state, expected growth, and the declared concurrency.
2. Reserve worst-case headroom before mutation. Admission failure must occur
   before authoritative rows, files, actions, or external work are created.
3. Prefer compact active state plus immutable content-addressed history over a
   larger constant when growth is structural.
4. Bind every externalized shard by schema, generation, canonical path, count,
   byte size, and hash from one atomic root.
5. Write and validate immutable shards before atomically replacing the root.
   Retain the previous generation until the new state and rollback are proven.
6. Rebuild without disposable caches from the root, shards, immutable receipts,
   and authoritative source state. Fail on missing, extra, duplicate, oversized,
   path-escaping, malformed, or hash-mismatched material.
7. Archive only terminal, unreferenced records. Never delete source history,
   worktrees, failed-attempt evidence, or the last known-good recovery set.

## Proof Matrix

Cover current state, at least 2x state, target concurrency, boundary-size input,
corruption, interruption, rebuild, exact rollback, and prior-version
compatibility. Report capacity as a measured contract, not an estimate.
