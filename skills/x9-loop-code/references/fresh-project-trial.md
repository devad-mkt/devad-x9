# Fresh-Project Controller Trial

Use this only after `x9-loop-code` admission succeeds. Keep the experiment
isolated from normal work:

1. Bind fresh repository, worktree, branch, base SHA, canary goal, owned paths,
   and rollback/delete owner action.
2. Run package and focused controller tests before creating project trial state.
3. Run one bounded canary with providers, deployment, secrets, money, and
   destructive actions excluded.
4. Preserve a compact result with source SHA, tests, candidate state, and
   rollback evidence.
5. Exit to `x9-loop-style` after terminal PASS or FAIL.

An external hourly check is optional and owner-run. It is one bounded read of
the current canary evidence, not a background scheduler or task poller.
