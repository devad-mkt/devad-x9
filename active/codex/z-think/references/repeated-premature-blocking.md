# Repeated Premature Blocking And Route Collapse

Read this only after the same blocker class recurs, a preferred tool or route is
mistaken for the objective, current sources are repeatedly skipped, or a long
durable fix unnecessarily stops independent useful work.

## Blocker Decomposition

Record the objective, success predicate, hard invariants, failed route, observed
failure, missing capability, available interfaces, and work that remains
independent. Separate `ROUTE_BLOCKED`, `OBJECTIVE_BLOCKED`, `WAITING_EXTERNAL`,
and `STOP_BOUND_REACHED`.

## Escape Portfolio

For a nontrivial blocker, produce at least three genuinely different candidates:

1. **Direct:** repair or replace the failed component at its actual boundary.
2. **Orthogonal:** use another interface, runtime, evidence source, local shadow,
   deterministic parser, browser, API, CLI, or owner-run command without changing
   authority.
3. **Continuity:** use a reversible temporary bridge that keeps bounded value
   moving while the durable repair continues.
4. **Parallel:** advance a useful slice whose proof and ownership do not depend
   on the blocker.

Inspect local code, durable state, tool help, installed capabilities, and logs.
When allowed and decision-relevant facts are current, niche, or uncertain,
search the web and prefer primary sources. If network access fails, try cached
official docs, installed source, package metadata, or a deterministic local
probe before escalating. Do not repeat the same failing call with cosmetic
changes and count it as exploration.

Rank candidates by invariant coverage, evidence quality, time to first value,
reversibility, cost, and cleanup burden. Attempt the two cheapest safe
independent routes, including one orthogonal route, within declared stop bounds.

## Temporary Bridge Contract

A continuity route must declare:

- exact owner, scope, inputs, outputs, and forbidden effects;
- expiry or attempt bound and the durable-fix switch-back trigger;
- rollback and cleanup that restore the prior state;
- observability and proof that distinguish temporary success from completion;
- no weakening of authentication, authorization, validation, privacy,
  durability, data integrity, or spend controls.

Prefer a feature flag, compatibility adapter, local shadow, manual bounded step,
queued hold, or read-only evidence path over an invasive workaround. Never let
the bridge become an undocumented permanent architecture.

## Escalation Gate

Return hard `BLOCKED` only when an exact owner decision, authority, credential,
or external state is indispensable; all allowed independent routes have failed;
a hard stop bound is reached; or every remaining route violates an invariant.
For a soft blocker, route one safe next action, independent slice, or bounded
bridge. Ask the owner only for the smallest decision that cannot be derived.

Never bypass roles, claims, approval gates, security, proof, cost controls, or
user prohibitions. Never hide a mutation, invent evidence, create unauthorized
actors, or call a partial workaround `PASS`.

## Receipt

Record `OBJECTIVE`, `HARD_INVARIANTS`, `FAILED_ROUTE`,
`ALTERNATIVES_CONSIDERED`, `ALTERNATIVES_ATTEMPTED`,
`SAFE_PARALLEL_PROGRESS`, `TEMPORARY_BRIDGE`, and `ESCALATION_NEED`.