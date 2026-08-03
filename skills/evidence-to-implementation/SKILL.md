---
name: evidence-to-implementation
description: Build privacy-safe, implementation-grade evidence libraries and execution contracts from authenticated UI, DOM/ARIA, licensed or historical source, current native code, settings, tests, public docs, and prior reviewer decisions. Use for parity/adoption audits, high-fidelity frontend reconstruction, feature denominators, migration or reverse-engineering reports, old-session/branch/addon reconciliation, native owner mapping, and plans a lower model must execute without guessing.
---

# Evidence to Implementation

## Purpose

Turn scattered evidence into a read-by-need package that a fresh implementer
can use without rediscovery or architectural invention.

## Route References by Case

Read only matching references after this file:

| Case | Mandatory reference |
| --- | --- |
| Any serious mission | [IMPLEMENTATION-READINESS-CONTRACTS.md](references/IMPLEMENTATION-READINESS-CONTRACTS.md) |
| Adoption, migration, old session, branch, addon, version drift | [ADOPTION-AND-VERSION-GATES.md](references/ADOPTION-AND-VERSION-GATES.md) |
| Image/video/editor, Content Lab, CHAT, settings, failed report | [CASE-LESSONS.md](references/CASE-LESSONS.md) |
| Authenticated UI, DOM/ARIA, screenshots, responsive/live proof | [BROWSER-DOM-LIVE-TESTING.md](references/BROWSER-DOM-LIVE-TESTING.md) |
| Any request to match, adopt, clone, reproduce, or reach visual/interaction parity with a frontend | [FRONTEND-VISUAL-PARITY.md](references/FRONTEND-VISUAL-PARITY.md) |
| Sheet, docs, Git, licensed source, native owners | [SOURCE-TO-NATIVE-MAPPING.md](references/SOURCE-TO-NATIVE-MAPPING.md) |
| Privacy, action safety, status, hashes, closeout | [SAFETY-STATUS-VALIDATION.md](references/SAFETY-STATUS-VALIDATION.md) |
| Graphify, CodeFlow, Cognee, browser and search routing | [METHODS-AND-TOOLS.md](references/METHODS-AND-TOOLS.md) |
| CHAT all-features packet only | [CANONICAL-PLAN.md](references/CANONICAL-PLAN.md) |

Do not load the CHAT plan for unrelated products. Do not skip a mandatory case
lesson because an earlier report exists.

## Execute in This Order

1. **Bind authority.** Record owner goal, exclusions, output paths, source
   identities, browser profile, live permissions, privacy, and finish token.
2. **Build the owner-requirement ledger.** Give every owner sentence, question,
   URL, branch, session, addon, setting, screenshot family, performance target,
   review callback, and output a stable ID.
3. **Freeze versions independently.** Separate current native, deployed,
   authenticated live, licensed reference, addon, historical, and official-doc
   identities.
4. **Allocate the denominator.** Create packet/row ownership before broad
   browsing or source reading. Material channels/addons/editors stay separate.
5. **Collect bounded evidence.** Targeted source/Git first; safe authenticated
   UI/DOM next; official docs for unresolved vendor facts. Advisory graphs
   never outrank current source/runtime.
6. **Map native ownership.** Trace control, route, authorization, validation,
   service, persistence, job/provider, receipt/recovery, settings, frontend,
   and tests.
7. **Freeze implementation contracts.** Specify schemas, state machines,
   settings, errors, retries, rollback, security, performance, accessibility,
   responsive behavior, file ownership and tests.
8. **Review and validate.** Close semantic requirements, reviewer checkpoints,
   visuals, contradictions, links, hashes, privacy and no-mutation proof.

Factual claims in plans, reports, model answers and historical memory are leads
until rebound. Owner-named sources, actions, reviews, outputs and exclusions
remain binding until explicitly waived.

## Core Truth Rules

- Keep current native code/tests, authenticated UI, deployed build, licensed
  source, addon source, historical implementation, public docs, and prior
  receipts independent.
- DOM proves presentation; source proves a possible contract; tests prove
  bounded assertions; deployment proves only the deployed artifact.
- A menu, registration, marketplace listing, or conditional include does not
  prove an addon exists.
- Read admin settings and user/workspace frontend settings before proposing
  behavior. A hardcoded current value is still a gap.
- Give each channel/addon/editor its own denominator. Never infer equality
  across providers, roles, plans, data states, desktop or mobile.
- Keep editor engine, background renderer, AI provider and automation API as
  separate decisions.
- Use `REUSE`, `EXTEND`, `NEW`, `OWNER_DECISION`, `DROP`, or `UNKNOWN`.
  `REUSE` means the proven native seam, not copied predecessor code.
- Preserve `UNKNOWN`, `SOURCE_MISSING`, `NOT_RUN`, and
  `NOT_EXECUTED_UNSAFE`.
- Maintain `OWNER_REQUIREMENT -> GATE -> EVIDENCE -> PACKET/ROW ->
  NATIVE_OWNER -> DECISION -> TEST/PROOF`.
- Never translate identical or high-fidelity UI into a generic native
  dashboard, gallery, card shell, or merely responsive information
  architecture. Freeze and prove visual density and interactions.
- A first visible milestone must resemble the bound reference or be labeled
  `NON_PARITY_SCAFFOLD__NOT_UI_ACCEPTANCE`. Never present a platform/read-only
  shell as frontend parity progress.
- Do not claim implementation-ready while a requirement, reviewer callback,
  component/dependency decision, schema, state machine, setting or security
  boundary remains unresolved.

## Lower-Model Handoff Gate

A chunk is executable only when it names the user outcome, evidence, current
owners/gap, types/schemas, routes, authorization, workspace scope, settings,
persistence, side effects, state transitions, errors, retry/cancel/recovery,
rollback, responsive/accessibility/security/performance behavior, exact paths,
tests, exclusions, collisions and PRE_CODE reviewer/source rebind. A
frontend-parity chunk also names exact reference screenshots/states,
viewports, geometry/density tokens, permitted deviations, comparison method
and the visual reviewer.

If the implementer must choose architecture, dependency, owner, schema,
provider, permission or error policy, the contract is not ready.

## Write the Standard Packet

Use exactly five files per major folder unless explicitly amended:

1. `01-SURFACES-CONTROLS-AND-STATES.md`
2. `02-SETTINGS-PERMISSIONS-AND-CONDITIONS.md`
3. `03-JOURNEYS-INTEGRATIONS-ERRORS-AND-RECOVERY.md`
4. `04-NATIVE-FRONTEND-BACKEND-AND-TEST-MAP.md`
5. `05-MEGA-SPEC-GAPS-AND-IMPLEMENTATION-CONTRACT.md`

Copy the small starters from `templates/` and replace every placeholder. Every
file includes author, snapshots, evidence legend, TOC, sibling/master links,
and source links. The mega spec is a deduplicated union.

Also use the requirement-ledger, source-version, visual-manifest, and Work
Order templates. Cite exact URLs, paths, lines, hashes and observation dates;
describe contracts instead of copying source bodies.

## Run the Whole Mission

Continue through authorized disjoint phases:

1. Preflight identities, hashes, write boundary, and output collision.
2. Parse indexes/ledgers and build included/excluded denominators.
3. Enumerate public docs, feature subpages, and changelog contradictions.
4. Map licensed UI/action/backend source.
5. Audit authenticated UI, DOM/ARIA, responsive, and accessibility states.
6. For frontend parity, measure the complete reference and compare a
   same-viewport native render; structural prose or source-only tests cannot
   close this phase.
7. Map native frontend/backend/tests at the frozen SHA.
8. Write master, shared, channel, feature, integration, and platform packets.
9. Validate, review stable bytes once, correct, and freeze hashes/receipts.

A blocked page/tool blocks only dependent rows. Continue source-checkable work.
Stop globally only for missing authority, secrets, destructive/live boundaries,
unisolatable output collision, or invalidated source identity.

## Keep the Method Lean

Reuse existing evidence/owners, `rg`, Git object reads, standard libraries, and
native tools. Create only required packets, master/manifest, and receipts. Do
not add ceremonial reports, screenshots, parsers, abstractions, or helpers.

One bounded helper may perform secret-safe mechanical counts/extraction when
explicitly useful. The parent owns browser work, classification, writing,
validation, and final truth.

## Validate and Close

Run:

```powershell
python scripts/validate_packet_library.py <output-root> --expected-packets N `
  --packet-index <output-root>/PACKET-INDEX.json `
  --requirement-ledger <output-root>/REQUIREMENT-LEDGER.json `
  --expected-requirements M
python scripts/validate_skill_pack.py <skill-root>
```

Set counts from the canonical plan. When historical or superseded packet
folders remain in the same root, use `--packet-index` to name only canonical
packet directories; never inflate completion totals with retained history.
Then verify hashes, source snapshots,
classifications, exclusions, privacy and no-mutation state. Human semantic
review remains mandatory; structural validation never proves completeness.

Return output root, packet/report totals, receipt/manifest hashes and bytes,
native SHA, live-proof status, classification totals, exclusions, privacy
result, and no-mutation proof. Use `PARTIAL` for bounded missing live/provider
proof and `BLOCKED:<exact gate>` only when the whole objective cannot proceed.
