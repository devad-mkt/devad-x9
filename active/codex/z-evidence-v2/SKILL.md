---
name: z-evidence-v2
description: Build privacy-safe, implementation-grade evidence libraries and execution contracts from authenticated UI, DOM/ARIA, licensed or historical source, current native code, settings, tests, public docs, and prior reviewer decisions. Use for parity/adoption audits, high-fidelity frontend reconstruction, feature denominators, migration or reverse-engineering reports, old-session/branch/addon reconciliation, native owner mapping, and plans a lower model must execute without guessing.
---

# Evidence to Implementation

## Canonical v2 identity

This is the single canonical `z-evidence-v2` body. The on-disk directory stays
`z-evidence` so existing explicit paths and saved prompts continue to resolve
to the same file; do not create a second `z-evidence` or `z-evidence-v2` copy.
When a caller names the legacy `$z-evidence`, use this v2 body and report the
compatibility mapping only if the caller needs to know it.

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

### Reviewer-refresh replay (mandatory)

Replay later reviewer corrections through the canonical evidence artifact. A
receipt must persist `CORRECTED_CLAIM`, `SAFE_CLASSIFICATION`,
`CORRECTION_EFFECT`, and `RECHECK_PROOF` before dependent implementation can
advance. In the Tickets lane, `ChatAccount`/`manual_user_id` is local lookup
evidence only; OWNER `23 parents + 25 nested = 48` and RAW `23 parents + 27
nested = 50` remain separate ledgers. Rebind hashes, crosswalk, owner binding,
and row-level allow/deny proof; chat-only advice is `RECEIPT_NOT_PERSISTED`.

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

## Complementary skill boundaries

`z-evidence` is the evidence spine. It may route to a companion skill when
that skill owns a decision that this packet deliberately does not own; it must
not turn every report into an always-on multi-skill process.

- **Durable memory — `$z-memory`:** use only when prior sessions, `.devad/memory`,
  or a restartable handoff materially changes the current evidence. Search the
  required startup files first, copy only safe Markdown or redacted artifacts,
  and label memory `VERIFIED`, `HISTORICAL`, `INFERRED`, `UNKNOWN`, or
  `BLOCKED`. Memory indexes evidence; it never upgrades a report, screenshot,
  or chat claim into current runtime truth.
- **External research — `$deep-research-work:deep-research`:** use when the
  owner requests a deep external investigation or a provider/vendor fact is
  unresolved. Start with supplied sources, prefer primary documentation, record
  title/date/URL/retrieval date, compare conflicts, and stop when the contract
  is decided. Do not use web research to replace current-source or live-proof
  checks, and do not add a research artifact when the existing packet already
  answers the decision.
- **Devad document placement — `$z-devad-docs`:** use when a durable document
  is explicitly requested. Keep private evidence under the selected
  `.devad/features/<feature>/` boundary, preserve unrelated worktree dirt, and
  do not create a second index, plan, or public documentation location merely
  to mirror this packet.
- **Native adoption — `$z-native-adopt`:** use when evidence must become a
  product change. Trace the current native owner first and classify each card
  `REUSE`, `EXTEND`, `NEW`, `PROTECT`, `DEFER`, or `DROP`; adopt semantic
  behavior rather than copying legacy ancestry. Keep provider, credential,
  storage, deployment, and live-effect receipts separate from source proof.
- **Notion documentation — `$notion:notion-research-documentation`:** use only
  when a Notion connector and a Notion source/page are actually available or
  explicitly requested. If the connector is unavailable, produce the requested
  local Markdown with normal citations and state that no Notion source/page was
  searched or created; never invent Notion links or citations.
- **Scope discipline — Ponytail (optional):** apply its minimum-solution check
  to the packet itself. Keep the five-file shape, ledgers, and one hash/receipt
  closure; skip extra dashboards, wrappers, screenshots, parsers, or helpers
  unless a named requirement cannot be proven without one. This is a scope
  check, not a second evidence authority.

When a companion skill is unavailable, continue with the evidence boundary and
record the limitation. Do not stop source-checkable rows simply because a
preferred companion tool or publication surface is missing.

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

### Single-file implementer handoff

Some lower-level coding agents read only one file. In that case the channel's
`05-MEGA-SPEC-GAPS-AND-IMPLEMENTATION-CONTRACT.md` is the executable handoff:
it must contain the user outcome, current source/reference identities, native
owners, settings, inputs, schemas, authorization/tenancy, persistence,
effects, states, errors, retries, recovery, rollback, security, accessibility,
performance, exact files, tests, exclusions, collisions, and the remaining
owner gate. `INDEX.md` and path lists are navigation aids, never the only
truth. Keep `01`–`04` as focused audit facets and make `05-MEGA` their
deduplicated, self-contained union; do not create a second mega file for the
same channel.

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

## Astra-light refresh invariant (2026-09-12)

Treat CORE `ChatAccount`/manual discovery as
`LOCAL_OWNER_RECORD`/`LOOKUP_SNAPSHOT`, never as external ownership. Require
an independently verified exact account/workspace/public-ID/site binding and
same-tenant allow plus foreign/manual-unverified deny tests before dependent
installer, direct-link, visitor, or notification rows advance. Otherwise
`EXTERNAL_AUTHORITY=UNKNOWN` and the rows stop.

Keep the owner denominator `23` parent + `25` nested = `48` separate from the
raw source inventory `23` parent + `27` nested = `50`; retain the two-row
crosswalk and do not force parent structure into nested counts. Packets missing
this correction are stale and must be re-bound with updated hashes.

## Refresh-delta replay rule (2026-09-12)

Persist each later reviewer correction before implementation. A discovered
`ChatAccount`/`manual_user_id` is `LOCAL_OWNER_RECORD`/`LOOKUP_SNAPSHOT` only;
external ownership remains `UNKNOWN` until an exact independently verified
account/workspace/public-ID/site binding and same-tenant plus foreign/manual-
unverified tests are recorded. Keep OWNER `23` parents + `25` nested = `48`
separate from RAW `23` parents + `27` nested = `50` and its crosswalk. Rebind
packet/progress/receipt hashes and obtain the same Astra-light `ADMITTED`
receipt when a refresh changes either classification; chat-only wording is
`RECEIPT_NOT_PERSISTED`.

### Qualified-claim normalization (mandatory)

Persist a refresh that contains an observation and a limiter as a structured
claim, not a stronger paraphrase:

```text
CLAIM_SUBJECT: <observed model/row/system>
OBSERVED_FACT: <bounded local fact>
LIMITER: <explicit non-proof or exclusion>
AUTHORITY_STATUS: <LOCAL_OWNER_RECORD | LOOKUP_SNAPSHOT | EXTERNAL_AUTHORITY | UNKNOWN>
COUNT_AXIS: <OWNER_COUNT | RAW_COUNT | NOT_A_COUNT>
```

Thus local `ChatAccount`/`manual_user_id` stays lookup evidence when it is not
external ownership proof, and 48 stays the OWNER 23-parent/25-nested ledger
while RAW remains 23-parent/27-nested. Missing fields are `REQUEST_CHANGES`;
the same reviewer must persist the correction and updated hashes.

### Astra-light quote replay checklist (2026-09-12)

For the refresh wording “CORE has a `ChatAccount` owner, but manual discovery is not proof of external account ownership” and “48 settings,” persist the qualified claim before implementation:

```text
CLAIM_SUBJECT: CORE ChatAccount + manual discovery
OBSERVED_FACT: local owner lookup/snapshot exists
LIMITER: manual discovery is not proof of external account ownership
AUTHORITY_STATUS: LOCAL_OWNER_RECORD | LOOKUP_SNAPSHOT | UNKNOWN
COUNT_AXIS: OWNER_COUNT=23 parents + 25 nested = 48; RAW_COUNT=23 parents + 27 nested = 50
```

The evidence packet must retain the row-level same-tenant allow and foreign/manual-unverified deny tests, exact dependent rows, and stop condition. Missing fields are `REQUEST_CHANGES`; a chat-only correction is `RECEIPT_NOT_PERSISTED`.

### Astra refresh quote ingestion (2026-09-12)

For a refresh containing both an observation and a limiter, persist this typed
claim before implementation or review admission:

```text
CLAIM_SUBJECT: CORE ChatAccount + manual discovery
OBSERVED_FACT: a local owner lookup/snapshot exists
LIMITER: manual discovery is not proof of external account ownership
AUTHORITY_STATUS: LOCAL_OWNER_RECORD | LOOKUP_SNAPSHOT | UNKNOWN
COUNT_AXIS: OWNER_COUNT=23 parents + 25 nested = 48; RAW_COUNT=23 parents + 27 nested = 50
CORRECTION_EFFECT: reopen installer/direct-link/visitor/notification rows and rebind settings crosswalk
RECHECK_PROOF: exact artifact hashes plus same-tenant allow and foreign/manual-unverified deny tests
```

Keep the owner and raw ledgers separate; chat-only reviewer notes are
`RECEIPT_NOT_PERSISTED` until the same Astra-light reviewer writes and hashes
the canonical correction.

### Control-isolation proof guard (2026-09-12)

Treat a negative result as proof of its named control only when the other
admission predicates are valid. Use schema-valid eligible controls, mutate one
tuple or state field at a time, and assert callback-not-run, unchanged consume
state/session count, and unchanged `last_seen_at`. A setup failure on an
earlier predicate is `SETUP_REJECTION`, not coverage of expiry, tuple drift,
revocation, disabled/suspended workspace, or foreign-workspace behavior; any
masked case reopens the packet and requires a new receipt hash.

## Preserved capabilities (merged 2026-09-12)

Unique content recovered from archived variants. The canonical body above
wins where they overlap; these sections are the non-overlapping remainder.

### From `AGENTS__evidence-to-implementation`

If the owner names a previously accepted implementation, commit, branch, or
live surface as the base, record `OWNER_SELECTED_BASELINE` and its observable
`BASELINE_REQUIRED_FEATURES`; do not downgrade those rows to optional history.
Before `IMPLEMENTATION_READY`, require one disconfirming pass: list the three
most likely omitted baseline behaviors, test them against immutable source and
the populated target journey, and record which evidence would make the current
plan wrong. Agreement between agents is not proof.
An owner-selected historical implementation is the presentation/behavior
baseline even when its architecture is obsolete. Preserve its accepted
observable behavior through current-native owners. Only the owner may reject a
baseline feature; an evidence worker may classify the implementation seam, but
may not silently reduce the denominator or authorize a simpler rewrite.

### From `LOOPX__z-evidence`

# zEvidence
If the owner names a previously accepted implementation, commit, branch, or
live surface as the base, record `OWNER_SELECTED_BASELINE` and its observable
`BASELINE_REQUIRED_FEATURES`; do not downgrade those rows to optional history.
Before `IMPLEMENTATION_READY`, require one disconfirming pass: list the three
most likely omitted baseline behaviors, test them against immutable source and
the populated target journey, and record which evidence would make the current
plan wrong. Agreement between agents is not proof.
An owner-selected historical implementation is the presentation/behavior
baseline even when its architecture is obsolete. Preserve its accepted
observable behavior through current-native owners. Only the owner may reject a
baseline feature; an evidence worker may classify the implementation seam, but
may not silently reduce the denominator or authorize a simpler rewrite.

### Split presentation from effects
Do not classify a whole page or channel as deferred because its save, provider,
storage, credential, callback, runtime, or live effect is not owned. For every
control, classify the layer as `PRESENTATION`, `READ_MODEL`, `LOCAL_DRAFT`,
`PERSISTENCE`, `EXTERNAL_EFFECT`, or `LIVE_PROOF`.
Current source plus a bound reference may make the first three layers
implementation-ready even when later layers are gated. A safe shell is ready
only when it uses current workspace authorization and secret-free projections,
states truthfully that unavailable actions are disabled/unconfigured/not saved,
and has focused local proof. It must never fabricate connection, persistence,
delivery, model output, upload, or provider success.
The handoff must therefore name both the smallest buildable local slice and the
separate forbidden effect boundary. Missing effect ownership is evidence for an
`EFFECT_GATED` action row, not evidence that the visible page is impossible.
After implementation, distinguish an executable local gap from a real browser
invariant. If current source/tests are green and the authentic page requires
PostgreSQL workspace context, HTTPS publication, or another product security
boundary, label the remaining evidence
`SOURCE_TEST_PROVED_BROWSER_PENDING_<INVARIANT>`. Do not generate a synthetic
tenant bypass or fake publication authority. Preserve that browser row and
advance the next executable product slice or the correctly ordered runtime
proof.
Use the five-file packet only when the owner requested a full evidence library
or the denominator is not already captured. Do not regenerate it for an active
delivery mission whose canonical plan, evidence library, and current owner map
already exist. In that case, add one compact source-bound checklist row or Work
Order and code immediately.
For a full evidence library, use exactly five files per major folder unless
explicitly amended:


## Provenance (consolidated 2026-09-12)

Canonical body: `evidence-to-implementation` (2026-09-12 07:42:30, 24 files, sha256 `3bfde6f57547a000`).

Former names now disabled: `AGENTS/evidence-to-implementation`, `LOOPX/z-evidence`, `NINELLC/evidence-to-implementation`.

Unique content from disabled copies is preserved under `references/preserved/` and is NOT authoritative; this body wins on any conflict.
