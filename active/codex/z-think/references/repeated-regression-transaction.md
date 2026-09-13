# Repeated Regression And Transaction Failures

Read this only after a fix repeatedly misses the real failure, a transaction
leaves partial state, rollback is claimed without proof, or residue returns.

## Required Response

1. Preserve the smallest reproducer that demonstrates the actual mode,
   environment, data shape, and boundary condition.
2. Run the same probe red before the fix and green after it. A nearby unit test
   that does not exercise the failing mode is not closure.
3. Bind the regression to the exact candidate bytes. Separate packet-reported
   tests from tests directly recomputed in the review.
4. Inject failure at each authoritative write boundary. Verify no partial task,
   row, file, action, dispatch, or external side effect survives.
5. Restore the complete original set and compare exact identities, integrity,
   and behavior. A raised rollback function or matching version is insufficient.
6. Scan for temporary files, locks, journals, WAL/SHM sidecars, processes,
   scheduled jobs, and hidden dirty state after success and failure.

## Stable Review Rule

After a candidate is identity-bound, block only on a demonstrated P0/P1 defect
with an exact contract violation or minimal reproducer. Do not expand scope with
speculative redesign. A repaired candidate gets one delta review against the
last bound candidate plus all affected invariants.

## Receipt

Record `REPRODUCER`, `RED`, `GREEN`, `ATOMICITY`, `ROLLBACK`, and `RESIDUE`.
Any missing required field blocks closure.
