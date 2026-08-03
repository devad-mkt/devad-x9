# High Mode

Use High for high-impact or hard-to-reverse work. High means deeper proof and stronger boundaries, not more features, files, agents, or ceremony.

## Program And Slice Depth

A High program preserves High release and integration gates without forcing
every slice into High mode. Use Lite for mechanical documentation, hashes, and
workbook updates; Medium for ordinary bounded implementation; and High only
when the current slice changes or proves a high-risk boundary such as
PostgreSQL, tenancy, migration, external publishing, deployment, or activation.

## Predeclare Relevant Invariants

Mark each `REQUIRED`, `NOT_APPLICABLE`, or `UNKNOWN`:

- Authority and exact source identity
- Repository, worktree, ownership, and dirty-state scope
- Functional acceptance and preservation behavior
- Trust boundaries, permissions, tenancy, secrets, and abuse cases
- Data/schema compatibility and migration preconditions
- Atomicity, idempotency, retry/interruption behavior, and residue
- Capacity and resource admission
- Rollback to a validated prior state
- Source readiness
- Integration readiness
- Deployment/activation authority
- Runtime and user-like proof

Do not start an irreversible action while a material invariant is `UNKNOWN`.

## Bounded Workflow

1. Bind current artifacts, revisions, environment, and owner authority.
2. Reproduce the real failure or establish a pre-change acceptance baseline.
3. Compare at least two structurally different routes, including reuse/minimal repair.
4. Threat-model only changed trust and data flows; include the strongest realistic attacker or failure actor.
5. Implement the smallest bounded slice in isolated ownership.
6. Prove red-to-green behavior, negative cases, interruption/replay, and rollback where applicable.
7. Run existing deterministic security/build/test gates; add a specialized scan only for a specific uncovered risk.
8. Use one independent challenge of stable exact bytes. Repeat only after material evidence or bytes change.
9. Separate commit/source acceptance from integration, installation, deployment, activation, and live proof.
10. Preserve evidence and stop at the declared finish line.

## Pre-Dependency Simplification

When a stable slice introduces substantial production code or interfaces that
later work will depend on, a named maintainability concern may justify one
bounded behavior-neutral simplification checkpoint. LOC alone is not a
finding. Read [simplification-checkpoint.md](simplification-checkpoint.md), and
do not let optional simplification delay an unrelated accepted release or base
token.

## Required Anti-Overengineering Challenge

Reject or defer unless tied to a demonstrated gap:

- Fixed counts of specialist agents
- A new orchestrator, MCP server, service, datastore, or framework
- Organization-wide SAMM assessment for a feature decision
- Composite compliance or quality scores as a release gate
- Full SAST/DAST/SCA duplication when current gates cover the changed boundary
- New dashboards, runbooks, ADRs, templates, or automation that do not affect safe operation or recovery
- Optional future architecture on the current critical path

Formal regulation, contractual compliance, or organizational policy can require these artifacts. Bind the exact requirement rather than assuming it.

## Evidence Receipt

For each material claim label the source:

- `DIRECTLY_VERIFIED`
- `PACKET_CLAIMED`
- `INFERENCE`
- `UNKNOWN`

A packet claim is not direct proof. A passing source review does not imply integration or deployment readiness.

## Stop Conditions

Stop before mutation or release when authority, source identity, tenant/security boundary, atomicity, migration compatibility, rollback, or exact deployment identity is unresolved. Otherwise stop after the predeclared acceptance evidence passes; do not extend the task with optional maturity work.
