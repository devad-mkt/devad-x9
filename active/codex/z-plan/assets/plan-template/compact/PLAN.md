# <Feature> Delivery Plan

Status: `<BUILD_NOW | SAFE_SHELL_NOW | EFFECT_GATED | PROOF_GATED | EVENT_ONLY>`
Outcome: <one user-visible result>
Identity: <worktree; branch; HEAD>
Authority: <current source/test/receipt that wins>
Next action: <one executable step>

## Truth order

1. Current source, Git, tests, runtime evidence, and owner direction.
2. Current work order and immediate dependency receipt.
3. This plan and the canonical checklist.
4. Historical plans, exports, and external advice (discovery only).

## Minimum read

- `PLAN.md`, matching checklist row, exact owned source/tests, and one immediate receipt.
- Only the reference or workbook range named by that checklist row.

## Scope and boundaries

| Build or prove now | Explicitly gated | Forbidden |
| --- | --- | --- |
| <safe local slice> | <owner/provider/runtime proof> | <secrets, production, unrelated files> |

## Delivery order

| Order | Outcome | Owner/paths | Decisive proof | Fallback |
| ---: | --- | --- | --- | --- |
| 1 | <vertical slice> | <exact paths> | <command/evidence> | <safe different route> |

## Rules

- A failed browser, database, provider, or deploy route blocks only its proof row.
- Keep visible/read-only/local-draft work separate from save, provider, and live effects.
- Review once after bytes stabilize; record the result in a receipt.
- Stop only for scope collision, missing authority, security ambiguity, or destructive/live work.
