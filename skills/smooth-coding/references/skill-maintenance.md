# Maintaining Smooth Coding

Read this only when the owner asks to change `smooth-coding` itself or when a
task proposes promoting a local lesson into the reusable skill.

## Authority Boundary

- A Worker or Looper using this skill must not rewrite it during the same
  product-delivery loop. Record the observation and keep delivering.
- Make skill changes in a separate owner-requested or THINKER-owned maintenance
  action. Do not let a task optimize the rules that currently judge its own
  performance.
- Preserve the owner's full accepted scope and every hard safeguard. A speed
  lesson may remove duplicated process, never required quality or safety proof.

## Classify The Proposed Change

Place each correction at the narrowest reusable level:

| Level | Use when | Destination |
|---|---|---|
| Project-local | It names one repository, scheduler, provider, role topology, path, or release mechanism | That project's plan, contract, or lesson |
| Conditional lesson | It is a repeatable failure pattern but only applies after a clear trigger | `references/lessons/`; add one short trigger link from `SKILL.md` |
| Core rule | It applies to unrelated Worker/Looper implementations and cannot weaken their acceptance proof | A small edit in `SKILL.md` |

Promote a rule into the core only when it is demonstrated in at least two
unrelated delivery contexts or the owner explicitly declares it universal.
One project incident normally becomes a conditional lesson first.

## Quality Guardrails

- Optimize time to decisive evidence, not command price, token price, or test
  duration in isolation.
- "Cheaper first" is only a gate-ordering tactic when the cheaper gate can
  invalidate later work. It is never permission to skip or postpone the first
  real runtime, migration, security, compatibility, browser, or release proof.
- Keep per-slice risk classification. A large project is not automatically
  `HIGH`, and one `HIGH` boundary does not make adjacent work cheap or optional.
- Preserve focused tests during coding and the milestone gate required by the
  changed risk. Do not trade coding quality for fewer commands or reports.
- Keep domain-specific modes and labels out of the core unless they generalize
  beyond their source project.

## Update Procedure

1. State the observed failure and the behavior the change should produce.
2. Freeze the current skill hash and inspect the proposed diff; do not rewrite
   unrelated sections.
3. Choose project-local, conditional lesson, or core placement using the table
   above.
4. Make one bounded edit. Prefer a lesson plus a short trigger over expanding
   the always-loaded core.
5. Check three representative cases: a tiny reversible edit, ordinary
   application code, and a genuinely high-risk boundary. The rule must speed
   the first two without weakening the third.
6. Validate `SKILL.md` structure and confirm `agents/openai.yaml` still matches
   the skill's purpose. Regenerate it only when the public trigger or interface
   changed.
7. Report `DONE / NEXT / BLOCKED`; do not create a review packet, changelog, or
   extra approval cycle for routine skill maintenance.

## Rejection Tests

Reject or narrow an update when it:

- optimizes only one project or one recent incident;
- makes cost, token count, or command count outrank correctness;
- weakens tenancy, security, migration, spend, idempotency, rollback,
  accessibility, runtime, browser, or exact-source proof;
- adds another manager, reviewer, document, hash, or gate without changing a
  real decision;
- forces every task into one workflow despite different risk and dependency
  order.
