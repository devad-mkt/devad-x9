# Implementation-Readiness Contracts

## Table of Contents

1. Mission quality gate
2. Canonical ledgers
3. Evidence denominator
4. Settings and ownership
5. Schemas and state machines
6. Screenshot denominator
7. Security, performance, and accessibility
8. Lower-model Work Orders
9. Review gates
10. Completion test

## 1. Mission Quality Gate

An implementation-grade report answers both:

1. What behavior exists, including hidden and failure states?
2. How should current native owners implement it without copying obsolete
   architecture or inventing missing decisions?

Reject attractive prose that lacks exact denominators, versions, settings,
owner paths, schemas, transitions, tests, or blockers.

## 2. Canonical Ledgers

Create these before research:

- `REQUIREMENT-LEDGER.json`
- `SOURCE-VERSION-MANIFEST.json`
- `DECISION-REGISTER.md`
- `VISUAL-MANIFEST.json`
- `REVIEW-RECEIPTS.json`
- `MANIFEST.json` and `MANIFEST.sha256`

Each requirement row contains:

```json
{
  "id": "OWN-001",
  "requirement": "Owner wording without semantic loss",
  "sources_or_actions": ["exact source or action"],
  "artifact_rows": ["packet/row"],
  "gate": "PRE_ANALYZE|PRE_PLAN|PRE_CODE|PRE_REPORT|POST_RESULT",
  "status": "SATISFIED|SUPERSEDED_BY_OWNER|NOT_APPLICABLE_WITH_PROOF|UNKNOWN|BLOCKED",
  "evidence_ids": ["EV-001"],
  "decision": "REUSE|EXTEND|NEW|OWNER_DECISION|DROP|UNKNOWN",
  "proof_or_blocker": "citation or exact gate"
}
```

No owner question may disappear because it is awkward, cross-cutting, or
unanswered.

The version manifest independently records repository/branch/SHA or
version/hash for the current native target, deployed product, authenticated
live reference, licensed reference, each addon, historical branches/sessions,
and official documentation.

## 3. Evidence Denominator

Before prose, allocate stable rows for:

- feature, page, route, region and locator;
- label, icon meaning, role, ARIA, order and shortcut;
- visible, hidden, selected, disabled, read-only, loading, empty, error and
  data-dependent states;
- desktop, mobile, compact, overflow, keyboard and screen-reader alternatives;
- role, plan, workspace, provider, connection and settings conditions;
- trigger, transition, validation, final effect, undo and recovery;
- request/event, payload, handler, persistence, queue/provider, callback,
  receipt and reconciliation;
- evidence class, native owner, decision, tests and unknowns.

Shared behavior gets one owner row plus explicit aliases. Never infer that
channels, editors, addons, providers, roles, or viewports are equal.

## 4. Settings and Ownership

Inventory administrator/platform settings and user/workspace/frontend settings.
Trace:

`setting key -> UI owner -> validation -> storage/config -> capability
projection -> consumer -> test`.

Cover engines, models, providers, dimensions, limits, quotas, plans, credits,
feature gates, defaults, queues, concurrency, timeouts, exports, asset limits,
callbacks, retention and audit.

A hardcoded value is still a gap when a setting owns it.

Map:

`control -> frontend -> Wayfinder/route -> request -> policy -> service ->
model/storage -> job/provider -> receipt/recovery -> tests`.

Record exact paths, symbols, lines and frozen SHA. Use `ABSENT_AT_SHA` only with
searched paths and queries.

## 5. Schemas and State Machines

Separate proven current schema, accepted compatibility semantics, proposed
target schema, and vendor/engine transient state.

Every proposed schema states field types, nullability/defaults, validation,
sanitization, workspace ownership, revision/compatibility, mutability,
serialized/API form, indexes/uniqueness, and prohibited vendor fields.

For editable media, prefer an engine-neutral document with version, canvas,
pages/scenes, typed nodes/layers, stable field keys, assets, metadata and
revision. Do not persist raw vendor/engine nodes without an accepted adapter.

Every async or editable flow defines states, transitions/actors, terminal
states, idempotency/correlation, lease/timeout, retries, cancellation/races,
callback/polling receipt, reconciliation, unknown outcomes, rollback, and UI
projection.

## 6. Screenshot Denominator

Allocate screenshot IDs before capture for materially different:

- page/list/grid/table;
- empty/loading/error/permission/disabled;
- modal/drawer/dropdown/accordion/overflow;
- selected object and major property panels;
- layers/pages/timeline;
- desktop, compact/tablet and mobile;
- keyboard focus/accessibility states;
- addon and historical/current deltas.

Each row records route, time, viewport, state, safe interactions, masks, hash,
bytes, linked denominator IDs, and `NO_SCREENSHOT_SAFE` when needed.

Screenshot presence is not parity. Reconcile it with DOM/ARIA, source, settings
and effects.

For frontend adoption/parity, screenshots and comparison evidence are
mandatory when privacy-safe capture is possible. Bind identical reference and
native viewports, measure material geometry/density, declare permitted
differences, and require side-by-side plus overlay/diff review. A route render,
DOM assertion, responsive layout, zero-console result, or “screenshot-ready”
state cannot pass visual parity.

## 7. Security, Performance, and Accessibility

Specify workspace isolation, policies, assets, URL/MIME/size/sanitization,
provider/model policy, safety/provenance, secrets/callback verification,
idempotency, rate limits, credits, audit, export authorization and retention.

Bind actual browser, app server and render-worker CPU/RAM/concurrency/storage
topology before performance decisions. Measure representative small, normal
and stress fixtures for load, interaction, memory, bundle, render, concurrency
and failure behavior.

Define breakpoints, touch targets, overflow, focus order/restoration, shortcuts,
Escape, announcements, reduced motion, contrast and screen-reader names.

## 8. Lower-Model Work Orders

One Work Order owns one vertical outcome and normally 5-15 exclusive files. It
includes base SHA, owned paths, evidence/decision IDs, current owners/gap,
interfaces/schemas, routes, authorization, settings, persistence/jobs/receipts,
state machine, failures/recovery/rollback, accessibility, security,
performance, migrations/compatibility, focused tests, browser proof,
exclusions, collision checks and stop gates.

Split by owner boundary instead of creating a giant page, controller or
service.

For frontend parity, also include exact screenshot/state IDs, viewports,
measured geometry/density, permitted deviations, the first recognizable
visible outcome, comparison procedure, mismatch ledger and named visual
reviewer. Do not authorize a generic native shell when the owner asked to
adopt a specific reference experience.

## 9. Review Gates

- `PRE_ANALYZE`: ledger, identities, packets, safety and reviewer bound.
- `PRE_PLAN`: historical decisions separated from stale implementation; every
  requirement maps to an artifact.
- `PRE_CODE`: paths rebound; schemas, states, settings, tests and dependency
  decisions accepted; no choice delegated to the implementer.
- `PRE_REPORT`: every requirement has proof/blocker; visual/source/native
  evidence reconciles; privacy and hashes pass.
- `POST_RESULT`: diff, tests, browser, accessibility, performance and reviewer
  corrections match the contract.

For frontend parity, `POST_RESULT` remains open until same-viewport
reference/native visual comparisons pass. Structural/browser tests are
necessary but insufficient.

## 10. Completion Test

Ask a fresh lower-capability implementer to identify remaining decisions. If it
must choose architecture, dependency, owner, schema, transition, permission,
provider, setting precedence, failure behavior or proof method, the package is
not implementation-ready.
