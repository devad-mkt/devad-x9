# Optional Addons And Loop-Fix Routing

Use this before installing, assigning, or repairing OMP/Pi, OpenCode, Cognee,
S3, project Brain/docs, or another optional Loop-adjacent addon.

## Classify Current Truth

Re-read the current source manifest, release SHA, installed bytes, Worker
receipt, tests, and runtime proof. Keep these states separate:

- `RELEASED`: present in the hash-bound released package and its manifest.
- `INSTALLED`: installed bytes match that released package.
- `CANDIDATE`: useful local Worker bytes exist but release gates are incomplete.
- `BLOCKED`: a named deterministic gate failed.
- `DEFERRED`: design or later Work Order only.

Never install or advertise a `CANDIDATE`, `BLOCKED`, or `DEFERRED` addon as
released. A dated matrix is evidence to recheck, not permanent truth.

As of source `29b4fad633ce760cc1984bd0d19e49634e754909`, the released Lite addon
surface is Project Brain/context, `x9-project-docs`, and provider-offline
OMP/Pi S0. OpenCode, Cognee, and S3 are not released at that SHA.

## Standalone Task Use

An addon may run without Loop only when its own package contract permits it and
the owner assigns it directly to an exact task. Do not initialize Controller,
enroll roles, or import a Work Order merely because a task uses an addon.
Treat this as `SKILL_ONLY` or direct tool use, not `FULL_PROJECT_LOOP`.

Bind the exact task ID, profile/state root, allowed operations, source/package
hash, network/provider policy, and rollback. Keep addon output advisory:
Git, current source, canonical project memory, citations, and validated context
remain authority.

Task exclusivity must be enforced by a wrapper or adapter. A caller-supplied
`profileId` alone is not an allowlist.

Cognee P0 is not a THINKER memory service: the current local candidate exposes
configuration and local `warm()` only, not add/search/recall, and has no task
allowlist. Do not route it to a THINKER until a released package adds bounded
ingestion/retrieval, exact task binding, tests, security proof, and rollback.

## Reuse Before Creation

Before creating a visible Worker, reuse the existing Worker for the same addon
or closely related work when its task identity, worktree, base, claims, STOP,
receipts, and lessons are compatible. Preserve its model/thinking settings on
follow-up. If its worktree is dirty, stale, or incompatible, return the exact
typed blocker; never clean, reset, move, or silently replace it.

Create another Worker only when the owner authorizes it and current evidence
proves reuse is unsafe or impossible. Do not create a fresh Worker merely to
avoid reading the existing Worker's durable result.

## Loop Defects

LOOPER owns diagnosis, minimal reproduction, lesson intake, regression scope,
and routing. LOOPER does not repair a defect by consuming Controller authority,
performing LINKER transport, editing another Worker's files, or taking an
addon's implementation scope.

Route a code fix to the compatible existing Loop-fix Worker when available.
The fix Worker must bind current source, the failing invariant, exact claims,
focused regressions, security gates, stable review when required, C1/C2, push,
install, and rollback. A small defect may be fixed immediately only through
that exact Worker/release boundary; “small” does not waive it.

Missing security rules, source manifest coverage, clean worktree identity, or
release proof is a real blocker. Record one reusable lesson and the smallest
correction, but do not bypass the gate or call the candidate installed.
