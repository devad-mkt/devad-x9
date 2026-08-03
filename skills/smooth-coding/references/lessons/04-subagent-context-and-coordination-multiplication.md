# Subagent Context and Coordination Multiplication

Read this only when delegation is proposed or an active delegation starts
creating repeated waits, follow-ups, duplicate work, or large context transfer.

## Failure Pattern

Subagents can reduce wall time when work is genuinely independent. They become
slower and more expensive when the parent sends broad history, starts several
children, polls them repeatedly, duplicates a slow child's objective, or adds a
review agent for proof a deterministic gate already provides.

The cost is multiplicative:

```text
parent context and model steps
+ child context and model steps
+ dispatch, waiting, follow-up, and synthesis
+ duplicated work or repeated review
```

## Correction

1. Default to no subagent.
2. Run at most one active subagent per parent task. Do not permit nested agents.
3. Delegate only a bounded objective that is independent and likely to save
   more time than dispatch and synthesis cost.
4. Send a compact task-local capsule: objective, success predicate, exact
   paths or packet, authority boundary, forbidden actions, output schema, and
   stop condition. Do not send full chat history.
5. Dispatch once and wait once. Allow one evidence-driven follow-up; stop
   repeated polling or conversational correction loops.
6. The parent continues only disjoint work and never silently redoes the
   child's objective. Cancel the child before taking over.
7. Use deterministic tests, hashes, validators, and required repository gates
   directly. Do not hire a model to reinterpret a deterministic PASS or FAIL.
8. Record a reusable lesson only for a novel failure, repeated coordination
   problem, or comparable model benchmark. Routine success needs no new file.

## Quality Boundary

One-at-a-time delegation is a delivery and context budget, not permission to
skip security, tenancy, migration, spend, rollback, browser, runtime, or
release proof. For a serious independent high-risk review, finish or stop the
current child first, then run the reviewer against the stable changed bytes.

## Exit Condition

Return to the main implementation lane when the child supplies a decisive
answer or reaches its stop condition. Report only `DONE / NEXT / BLOCKED`; do
not create a delegation dashboard, percentage audit, or review of the review.
