# X9 Loop V7.3 Lite State

`PROJECT_PROFILE.json` binds every action and inbox event to this project.
`SNAPSHOT.json` is the canonical V3 recovery root; every referenced immutable
shard is required. The root stays below 8 KB and each shard stays within its
64 KB cap.

`loop.db` is the fixed disposable working cache. During V7-to-Lite migration,
the exact source database/WAL/SHM set remains preserved only as rollback input.
`runtime/ACTION.json` is generated, stays below 4 KB, and is the only action
surface LINKER reads.

Controller is the sole selector and writer of immutable `WORK_ORDER.json`.
LINKER transports exact hashed action bytes and records acknowledgement; it
never selects, combines, edits, reviews, or schedules work. WORKER reads its
Work Order, Program summary, and selected Feature Packets. THINKER is called
only for a predeclared high-risk judgment.

Owner input remains immutable, content-addressed local sensitive state under
`.devad/manager/owner-packets/`. Project Git ignores raw packets and
attachments. Tracked state stores only hashes and local paths. Back up raw
content only through an owner-approved private backup flow.

`WORKER_CHECKPOINT.json` is local, disposable, non-authoritative, tamper
checked, and expires with its Work Order. WORKER and THINKER results are
immutable, event-scoped files under `.devad/workers/<actor>/`; call receipts
record real usage or exactly `Unknown` plus prompt-prefix and tool-schema
hashes.

Migration builds V3 state side-by-side as `.next` artifacts, validates the
complete candidate, records a durable journal, and only then atomically
replaces fixed paths. Preserve the returned recovery identity until temporary
install, replay, doctor, and exact `rollback-v7` proof pass.

Use `loopctl.py doctor` before activation. `APPROVED_JOBS.json` is empty by
default. Scheduled-job drift is a typed activation gate, not automatic
authority for LINKER and not a blanket routine-dispatch rule. Doctor never
mutates schedules or exposes raw commands.

Use `loopctl.py rebuild` when the cache is missing or corrupt. Do not parse
`STATUS.md`, `HANDOFFS.md`, historical `manager/loop/` files, Obsidian, or chat
history as current authority.
