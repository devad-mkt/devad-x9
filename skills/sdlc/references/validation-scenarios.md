# Skill Validation Scenarios

Use these only when revising SDLC behavior. Run fresh-context comparisons without and with the skill.

## Baseline Observation

The 2026-07-19 no-skill baseline was generally safe but expanded work without evidence:

- A private CLI rename added CI inspection, changelog/release handling, and optional threat-model notes.
- A moderate settings bug unconditionally added queue/log review, release monitoring, and documentation steps.
- A high-risk migration appropriately rejected an eight-agent/MCP mandate, but still proposed docs, alerts, canary, and broad gates before proving which existing controls were insufficient.

The skill should preserve the baseline's security judgment while reducing unneeded process.

## Scenario A: Lite

A private internal CLI flag has two callers and focused tests. The user asks for production-grade OWASP/ISO/SDLC quickly.

Expected:

- Select Lite.
- Search definition/callers/tests, change coherently, run focused and required existing gates, inspect diff, stop.
- Reject full threat model, compliance matrix, new CI, changelog, release process, or tools unless repository policy requires them.

## Scenario B: Medium

A multi-tenant saved notification preference is ignored by one email path. A canonical service may already exist. Low token use requested.

Expected:

- Select Medium.
- Map canonical authority/persistence/consumption, reproduce, compare reuse versus local patch, add red/green and cross-tenant denial proof, run focused gates.
- Review async/cache/logging only when the traced path actually uses them.
- No broad redesign, infrastructure, compliance packet, or mandatory monitoring work.

## Scenario C: High

A production payment webhook idempotency migration had two failed attempts. Existing gates already cover tests, audit, secrets, staged security, migration dry-run, rollback, and exact-SHA deploy. The team asks for eight agents, SAMM scoring, MCP, all scanners, dashboards, and automation.

Expected:

- Select High.
- Bind exact state, invariants, failure reproduction, concurrency/replay/atomicity, rollback, and source/deploy separation.
- Reuse existing gates and add only demonstrated gaps.
- Reject fixed agent counts, new MCP, score-as-proof, duplicate scans, and optional observability/docs unless needed for safe operation.
- Stop after stable exact-byte review and applicable release evidence.

## Scenario D: Mixed Depth And Simplification

A High-risk program contains routine documentation and workbook updates,
ordinary multi-file code, and a safety-sensitive stage executor with several
thousand new production lines. Runtime proof for the stage executor is pending;
a later slice will depend on its interfaces. A read-only review identifies
specific duplicated policies and helpers but no behavior defect.

Expected:

- Keep the program High while selecting Lite for docs/workbooks, Medium for
  ordinary code, and High for the runtime, tenancy, migration, and release gate.
- Treat LOC as an inspection signal, not a defect or deletion quota.
- Finish runtime proof and integration before behavior-neutral refactoring when
  refactoring would change the proof target.
- Run at most one hash-bound simplification review and one closure review for
  changed bytes before the dependent slice begins.
- Preserve schema, API, status, SQL, receipt, spend, replay, tenancy, and
  rollback behavior; accept `LEAN_ENOUGH` when no safe candidate remains.
- Do not delay unrelated lane release or base tokens for optional cleanup.

## Pass Criteria

- Correct mode in all three scenarios.
- No hard safety or user requirement is removed.
- Optional framework work cannot block completion.
- Every added gate maps to a changed risk or repository requirement.
- The answer remains useful and concise in Lite and Medium.
- High remains rigorous without architecture expansion.
- Mixed-depth work does not inherit High ceremony from the parent program.
- Large code is simplified only from concrete findings and preservation proof.
