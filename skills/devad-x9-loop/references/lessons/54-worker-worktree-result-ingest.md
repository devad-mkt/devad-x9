# Worker Worktree Result Ingest

Bug class: a valid Worker-worktree finalizer output must have one
Controller-owned ingest path. Requiring LOOPER to manually copy the Worker
outbox event or receipt into Controller runtime staging is a Loop bug, not an
operating procedure.

The Controller may ingest a Worker result from a registered worktree only after
verifying the canonical inbox event, exact Worker outbox location, source
actor, task, Work Order, dispatch, payload path, result receipt hash, proof
hashes, and non-reparse in-worktree paths. Generic `run-once --file` remains
strictly limited to Controller-owned inbox files and must not learn to read
arbitrary absolute payload references.

Duplicate ingest of the same exact event is idempotent. Wrong worker, task,
dispatch, payload path, hash, unregistered worktree, path escape, stale state,
or active dirty conflict must reject without changing Controller lifecycle
state.
