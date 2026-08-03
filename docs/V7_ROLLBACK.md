# X9 Loop V7 Rollback

Rollback is byte-preserving and does not depend on model memory.

## Before Activation

- Capture a fresh live installation backup.
- Hash and preserve `loop.db`, `loop.db-wal`, `loop.db-shm`, and `SNAPSHOT.json`.
- Record the V6 source snapshot hash, generation, installed source hashes, and
  router pointer.
- Keep V2 construction in `.next` files until complete validation passes.

## Immediate Triggers

Rollback on migration mismatch, unresolved context, cache drift, unauthorized
recurring job, packet-cap violation, security failure, reviewed C1 identity
mismatch, remote-SHA mismatch, activation timeout, pilot invariant failure, or
unexpected source-byte change.

## Restore

1. Stop activation without creating a fourth commit.
2. Restore the complete V6 installation and the exact recovery set:
   `loop.db`, `loop.db-wal`, `loop.db-shm`, and `SNAPSHOT.json`.
3. Restore the V6 router pointer and rebuild only from the last V6 snapshot and
   identity-checked receipts.
4. Run V6 doctor, record the rollback acknowledgement, and send one
   `ROLLBACK_TO_V6:<sha>` event to the same Linx task.
5. Preserve V7 packets, evidence, worktrees, and local work.
