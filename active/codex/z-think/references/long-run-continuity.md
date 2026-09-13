# Long-Run Continuity

Load this reference only when work spans multiple phases, turns, context compactions, waits, or subtasks. It preserves continuity without creating another manager, datastore, or narration loop.

## Durable Checkpoint

Keep one compact checkpoint with these fields:

```text
ROOT_OBJECTIVE:
ACCEPTANCE:
AUTHORITY_AND_SOURCE:
CURRENT_SLICE:
ACCEPTED_FACTS_AND_PROOF:
IN_FLIGHT_SUBTASKS:
BLOCKERS_AND_UNKNOWNS:
DEFERRED_NOT_LOST:
ONE_NEXT_ACTION:
```

Use exact paths, revisions, proof identities, and statuses only where they affect resumption. Reference durable evidence instead of embedding full logs or histories.

## Update Points

Update the checkpoint after:

- meaningful proof or a disproved claim;
- a material failure or route change;
- accepting, rejecting, or superseding a subtask result;
- a handoff, long wait, or context compaction;
- changing the current slice or its one next action.

Do not update it after every command, restate unchanged history, or use it as a second project-management system.

## Resume

1. Read the latest checkpoint and its cited evidence.
2. Cheaply revalidate drift-prone facts: repository/worktree, revision, dirty state, active process, runtime status, and latest proof.
3. Mark stale claims explicitly; do not silently preserve or discard them.
4. Continue from `ONE_NEXT_ACTION` unless current evidence invalidates it.
5. Preserve the root objective and deferred work; do not restart planning from chat history.

## Subtask Reintegration

Each subtask remains bounded by its objective, authority, scope, and output contract. Use `$z-subagent` for dispatch and routing details.

- Treat completion as a claim until decisive evidence is verified.
- Do not let a subtask redefine the root objective, branch, authority, scope, or finish line.
- Record accepted evidence and its effect on the current slice.
- Record rejected or stale output as superseded evidence when it matters to later diagnosis.
- Close or supersede completed subtasks so old work cannot impersonate current activity.
- Keep the main slice moving when `BLOCKS_MAIN: no`; pause only the dependency when `BLOCKS_MAIN: yes`.

Only the main agent evaluates the root acceptance predicate and declares completion.
