# CHAT manager lessons

## Host-bound worker recovery

- Do not tell an owner to "reattach a task" until the manager has asked the
  coordinator for one supported self-repair or owner-visible route and received
  a concrete answer.
- Treat a worker's inaccessible Git metadata as `HOST_DEPENDENCY_PAUSED`, not
  a product defect. Preserve the exact worktree, index, and bytes.
- Never bypass a same-task boundary by committing from another task, changing
  ACLs, recreating a worktree, exporting/importing a patch, or retrying a
  denied Git metadata write.
- If no user-visible repair exists, say so plainly. Give the owner a compact
  support request containing the exact task, worktree, GitDir, and preserved
  index state; do not imply that a novice can safely fix it in Git.
- The overall goal can be marked blocked only after the coordinator confirms
  every accepted lane has a genuine external boundary. Resume immediately when
  the owner or host restores the dependency.
