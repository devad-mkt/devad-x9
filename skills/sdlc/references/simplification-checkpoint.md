# Simplification Checkpoint

Use this only after a stable dependency-setting slice has a concrete
maintainability concern: duplicated policy, repeated validation, unnecessary
indirection, mixed ownership, oversized review surface, or repeated fixtures.
Line count is an inspection signal, not proof of a defect and not a reduction
quota.
When reporting LOC, name the counting rule such as physical or nonblank lines;
do not compare figures produced by different rules as if one disproves the
other.

## Timing

If refactoring would change the bytes whose runtime behavior still needs proof,
finish that proof and integration first. Run the checkpoint before downstream
work hardens the interface. Do not delay an independent base token, release, or
lane unless the concern is itself a correctness or safety blocker.

If the requirement is throughput or resource use, define a benchmark contract
before changing structure: workload mix, completion boundary, concurrency,
measurement window, provider mode/limits, retry and timeout accounting, and
CPU/RAM/DB ceilings. Measure the stable bytes first, then rerun the same
benchmark after any accepted simplification.

## Bounded Audit

Bind the exact base, diff, files, tests, and accepted behavior. Run one read-only
simplification review against named candidates. `$ponytail-review` can provide
the deletion lens, but its findings are proposals: it explicitly excludes
correctness and security, so normal ownership and safety review remain
authoritative.

Before thinning or retiring an existing owner, close its caller map: source and
runtime entry points, routes/commands/jobs/events, flags/configuration,
persistence readers and writers, compatibility consumers, and covering tests.
Any material caller left `UNKNOWN` forces `DEFER`.

Classify each candidate:

- `REMOVE`: redundant behavior with exact preservation proof.
- `CONSOLIDATE`: duplicated policy or helper with one canonical owner.
- `SPLIT`: demonstrated mixed ownership separated along cohesive boundaries,
  with preserved interfaces and a net reduction in review/coordination
  complexity; moving the same code into more files does not qualify.
- `KEEP_SAFETY`: complexity required for isolation, durability, replay,
  idempotency, spend, rollback, or evidence.
- `DEFER`: plausible improvement without a safe bounded proof now.

## Change Contract

Use one behavior-neutral commit at a time. Predeclare forbidden semantic deltas,
including applicable schema, API, status, SQL, receipt, spend, replay, tenancy,
authorization, and rollback behavior. Run focused tests after each change and
the required broad provider-off, security, or integration suite at the end.
Inspect the exact diff and use one independent review of changed bytes.

Revert a candidate when behavior changes, proof weakens, or the abstraction is
not clearly smaller. If no candidate survives, record `LEAN_ENOUGH`; a review
does not owe a line reduction.
