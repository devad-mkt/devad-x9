---
name: sdlc
description: Use when software work needs risk-scaled planning, implementation, review, testing, integration, or release controls, especially when process, proof, or coordination may be growing faster than delivery.
---

# SDLC

## Purpose

Deliver the smallest correct change with evidence proportional to its real risk. Combine deep reasoning, secure lifecycle awareness, and a minimal-solution ladder without turning every task into a compliance program.

This skill is advisory. It does not override user or developer instructions, repository rules, role boundaries, permissions, model judgment, or safety controls. The agent may critique, replace, or skip a suggested practice when current evidence supports a better route. State the reason; never silently bypass a hard requirement.

## Select One Mode

Default to **Lite**. Select by the changed risk, not by project prestige, repository size, or a desire to appear thorough.

| Mode | Use when | Core behavior |
|---|---|---|
| **Lite** | Narrow, reversible, well-understood change; no new trust, persistence, migration, or deployment risk | One targeted read, smallest implementation, focused proof, stop |
| **Medium** | Ambiguous or multi-file change; user-controlled data, shared service, API, persistence, compatibility, or moderate operational impact | One compressed Ultra loop plus only the relevant SDLC checks |
| **High** | Auth, tenancy, payments, secrets, destructive/stateful migration, production activation, safety, major architecture, repeated serious failure, or hard-to-reverse impact | Predeclared invariants, adversarial challenge, failure/rollback proof, and separated source/integration/deploy readiness |

An explicit user mode is a preference, not permission to weaken safety. Recommend a higher or lower mode when evidence warrants it, but do not silently switch or stall. Read exactly one matching playbook: [Lite](references/lite.md), [Medium](references/medium.md), or [High](references/high.md).

Classify the overall program and the current slice separately. A program may
remain High while ordinary code chunks use Medium and documentation, hashes, or
workbook maintenance use Lite. PostgreSQL, tenancy, stateful migrations,
external publishing, deployment, and activation remain High when they are the
current changed boundary.

## Delivery Budget

Process is a budget, not a measure of quality.

- **Lite:** no plan document unless needed for handoff; one implementer, one
  focused proof, then stop.
- **Medium:** at most one compact checkpoint, one active implementation slice,
  focused iteration, and one review of the stable changed diff.
- **High:** one authoritative plan/contract, one accountable implementer, and
  one independent stable-candidate review. Broad test, security, migration, and
  browser checks run at declared milestones, not after every micro-edit.
- The final independent review may also be the milestone review. Do not add a
  second review merely because both labels appear in a process description.
- New agents, artifacts, hashes, scans, or gates require a decision-changing
  question and must not duplicate existing evidence.
- Progress reports, checklists, and percentage audits are advisory. They get one
  bounded pass and cannot become a prerequisite for known product work unless
  they reveal a material acceptance or safety defect.
- A full-program inventory or audit cannot gate a known safe delivery slice by
  default. Inspect the slice, its callers, direct dependencies, and changed risk;
  widen only when that evidence exposes a real cross-program boundary.
- Historical-versus-current dual environments, every-platform UI proof, and
  exhaustive evidence matrices are required only for an affected regression or
  release claim. Reuse accepted evidence for unchanged behavior.
- Owner review occurs at changed product decisions and declared milestones, not
  between every preapproved chunk. Routine closure remains with the accountable
  implementer and one independent reviewer.

## Universal Flow

1. **Frame current truth.** Identify the objective, acceptance predicate, authority, touched flow, constraints, existing repo gates, and material unknowns. Search the relevant code before proposing new structure.
2. **Map the risk delta.** Ask what this change newly affects: behavior, trust, data, tenants, compatibility, reliability, performance, accessibility, deployment, or recovery. Unchanged domains do not generate work.
3. **Climb the minimum-solution ladder.** Stop at the first sound rung: no change needed; reuse existing behavior; standard library; native platform; installed dependency; small local change; only then a new abstraction or dependency. Trace the real flow first. Small code in the wrong owner is not minimal.
4. **Choose evidence before edits.** Prefer a failing reproduction or focused acceptance check. Reuse existing project checks. Add one new check for each material changed risk, not one artifact for each framework category.
5. **Implement one bounded vertical slice.** Preserve existing patterns, ownership, and interfaces. Do not add scaffolding for hypothetical futures.
6. **Challenge once when material.** Test the strongest plausible changed-risk edge. Use another agent or specialized tool only when it answers a named question that local deterministic evidence cannot answer efficiently. Skip a separate challenge phase when focused proof already covers the only changed risk.
7. **Verify and stop.** Prove the acceptance predicate, inspect the diff, label unknowns, and separate source readiness from integration, deployment, activation, and live proof. Stop when required evidence passes and no material risk remains unresolved.

## Existing-System Admission Gate

Before approving an implementation plan or allowing its first behavioral edit,
prove that the proposed capability is actually missing or identify the current
owner to extend. Keep this as one row in the authoritative plan, not a separate
inventory or report:

- `EXISTING_FEATURE`
- `UI_SETTINGS`
- `SERVER_AUTHORITY`
- `PLAN_ENTITLEMENT`
- `REFERENCE_REUSE`
- `PERSISTENCE_CONSUMPTION`
- `INTEGRATED_HISTORY`
- `TEST_PROOF`
- `GAP`
- `CHANGE_MODE`: `REUSE`, `EXTEND`, `NEW`, or `REPLACE_AUTHORIZED`

Use `VERIFIED:<evidence>`, `NOT_APPLICABLE:<reason>`, or `UNKNOWN`. `NEW`
requires source-backed absence in the touched scope. `REPLACE_AUTHORIZED`
requires an explicit owner decision. A material unknown blocks only its
dependent plan item.

For user-facing behavior, trace both the visible UI/settings path and the
request-to-service-to-persistence-to-runtime path. DOM evidence alone cannot
establish backend ownership; backend source alone cannot establish the current
visible contract. Recheck decisive evidence against the implementation branch
before coding. Search current Git, accepted integration history, routes,
services, models, jobs, settings, migrations, and focused tests before adding a
new subsystem. Sheets, handoffs, memories, and graphs are discovery inputs;
current source/runtime evidence must confirm their decisive claims.

## Proportional Evidence Rules

- Existing repository gates beat invented parallel process.
- A framework is a lens, not a task generator. Use only SAMM practices and ISO quality characteristics affected by the change; see [standards map](references/standards-map.md).
- Full SAST, DAST, SCA, threat modeling, compliance scoring, architecture records, dashboards, runbooks, multi-agent panels, or new MCP servers require a concrete capability gap, external obligation, or material risk.
- Do not install a tool to produce evidence already available from source, tests, current CI, or a focused command.
- Do not confuse a score with proof. Findings need exact evidence, impact, and a bounded remediation or accepted-risk decision.
- Keep required, recommended, optional, and rejected work distinct. Optional work never blocks completion.
- Default review cadence is one accountable implementer and one independent review of the materially changed stable diff. The final milestone gate may satisfy that review. Reuse hash-bound acceptance for unchanged bytes.
- Token or time pressure may shrink narration and route breadth; it may not remove validation at trust boundaries, tenant isolation, data-loss protection, accessibility basics, required rollback, or explicit user requirements.

## Ingenuity Without Boundary Breaking

A failed route is `ROUTE_BLOCKED`, not necessarily a blocked objective. Inspect current tools, source, logs, interfaces, and primary documentation when allowed. Try a cheaper independent route or continue a safe non-dependent slice. A temporary bridge must be reversible, isolated, observable, time-bounded, and no weaker than the hard invariants.

Declare the objective blocked only when required authority, owner choice, secret, environment, or evidence is genuinely unavailable; every allowed route is disproved; or a hard stop bound is reached. Return the smallest safe next action.

## Anti-Overengineering Gate

Before adding an abstraction, dependency, service, artifact, agent, scan, or process, answer:

1. Which accepted requirement or demonstrated risk needs it?
2. Why can existing code, platform behavior, dependency, or gate not cover it?
3. What is the smallest cheaper alternative?
4. What new maintenance, attack surface, runtime cost, or coordination does it add?
5. What evidence will prove it can be removed or was worth keeping?

No concrete answer means do not add it.

## Process-To-Delivery Reset

Trigger this reset when two completed cycles add only plans, chunk checklists,
hashes, memory updates, reviews, or status narration while the requested product
can still advance.

1. State the user-visible finish line in one sentence.
2. Name the single current blocker and whether it is product, test, tool,
   authority, integration, or activation.
3. Choose the smallest direct action that can remove it.
4. Choose one focused proof and one final milestone gate.
5. Defer nonblocking cleanup, progress auditing, optional UI, refactoring,
   observability, and future architecture.
6. Resume implementation. Do not create another planning artifact for the reset.

Keep immutable contracts separate from mutable status. Checking a box, updating
a percentage, or recording progress must not invalidate accepted code evidence.
Likewise, reversible local setup must not wait for unrelated production
certification when the limitation can be stated and later integration remains
gated.

## Standards Boundary

This skill supports engineering judgment; it does not certify ISO compliance, perform an organizational SAMM maturity assessment, or replace legal, regulatory, AppSec, accessibility, privacy, or operations specialists. For a formal assessment, scope it explicitly and use the authoritative standard and current organizational evidence.

## Conditional References

- Read [standards-map.md](references/standards-map.md) only when mapping security or product quality.
- Read [sources-and-adoption.md](references/sources-and-adoption.md) when maintaining this skill or deciding whether to adopt an external SDLC tool.
- Read [validation-scenarios.md](references/validation-scenarios.md) only when validating or revising the skill.
- Read [simplification-checkpoint.md](references/simplification-checkpoint.md) only when a stable, dependency-setting slice has named duplication, indirection, ownership, or reviewability concerns.
- Read [existing-system ownership miss](references/lessons/existing-system-ownership-miss.md) when a plan assumes a capability is absent, accepted integration history is not represented, or frontend/backend ownership is unclear.
- When repeated route blocking, stale evidence, transaction failure, or false completion occurs, use `ultra-reasoning-protocol` and load only its matching repeated-error lesson.

## Rationalization Guards

| Rationalization | Correction |
|---|---|
| "High mode means every possible gate." | High mode deepens proof for changed risks; it does not expand scope indiscriminately. |
| "Lite means skip security and tests." | Lite minimizes process, not correctness at a real trust or data boundary. |
| "The standard lists it, so we must build it." | Standards provide questions. Requirements and demonstrated risk decide work. |
| "More agents make the decision safer." | Independence helps only when roles have distinct evidence or questions. |
| "A compliance score proves readiness." | Exact behavior and risk evidence prove readiness. Scores summarize; they do not replace proof. |
| "The preferred tool failed, so work is blocked." | Challenge the route, preserve constraints, and test another mechanism. |
| "Minimal code means minimal reading." | Read the touched flow fully, then minimize the solution. |
| "A large LOC count proves overengineering." | LOC is an inspection signal, not a defect or deletion target; require a named complexity or duplication finding. |
| "Simplify before proving the current runtime behavior." | When refactoring would change the proof target, prove and integrate it first, then simplify before dependent work adopts the interface. |
| "The model found more possible work, so the plan should grow." | More insight should improve pruning. Only requirements and demonstrated material risks enter scope. |
| "Every progress chunk needs its own plan, hash, review, and memory sync." | Use one canonical checkpoint; create another artifact only for a distinct external contract or decision. |
| "Project setup must wait for full production certification." | Gate irreversible release actions rigorously, but allow reversible setup from an explicit accepted base when it cannot affect production. |
