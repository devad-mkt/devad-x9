# Frontend Visual and Interaction Parity

## Table of Contents

1. Admission rule
2. Truth sources
3. Reference denominator
4. Measurement contract
5. Interaction and responsive contract
6. Native implementation contract
7. Comparison and acceptance
8. Work Order requirements
9. Failure lessons

## 1. Admission Rule

Use this contract whenever the owner says identical, same UX/UI, parity,
adopt, reproduce, clone, like the reference, or provides screenshots to guide
a frontend.

Do not reduce that request to:

- the same information architecture;
- a responsive page with the same major regions;
- generic cards, badges, tables, drawers, or dashboard primitives;
- passing DOM/source-string tests;
- a route that renders without console errors;
- a screenshot-ready localhost page;
- a backend/platform foundation whose first visible surface does not resemble
  the reference.

If exact visual evidence cannot be captured safely, mark visual parity
`PARTIAL_VISUAL_EVIDENCE`; do not silently substitute prose.

## 2. Truth Sources

Bind these independently:

1. owner screenshots and annotations;
2. authenticated live reference in the required real browser profile;
3. privacy-safe DOM/ARIA and computed presentation measurements;
4. licensed/reference source when authorized;
5. current native source and settings;
6. current local target render;
7. browser tests and screenshot comparison;
8. human visual review.

The implementer must be able to view the bound reference while implementing,
unless the owner explicitly accepts an offline evidence package. A textual
report alone is insufficient when authenticated comparison is available.

## 3. Reference Denominator

Allocate stable IDs for every materially distinct surface and state:

- page shell, rail, header, toolbar, pane, list row, canvas/content region,
  details panel, composer, footer and overlay;
- default, hover, focus, active, selected, expanded, disabled, loading, empty,
  error, permission, offline, retry and outcome-unknown;
- drawer, dropdown, filter, search, accordion, modal, context menu and tooltip;
- desktop, wide desktop, tablet/compact and mobile;
- keyboard and screen-reader alternatives;
- every transition in the owner’s primary journeys.

Record exact safe-click sequences and pre/post-state screenshot IDs. An unsafe
visible control still needs its placement, state, conditions, accessible name
and source-traced effect.

## 4. Measurement Contract

For each reference region/control record, when observable:

- viewport width/height and device scale;
- x/y position, width and height;
- pane/header/row/control height;
- padding, gap, alignment and wrapping;
- font family, size, weight, line height and truncation;
- foreground/background/border colors;
- border width/radius, shadow and divider treatment;
- icon identity, size and placement;
- sticky/fixed/scroll ownership and z-index relationship;
- visible item count and information density;
- collapsed/open footprint;
- breakpoint transition and overflow behavior.

Use computed browser facts or careful screenshot measurement. Do not guess
from visual memory. Dynamic/customer regions may be masked while their
geometry remains measurable.

Freeze permitted deviations explicitly, for example:

- Devad branding, logo and product copy;
- masked/dynamic customer content;
- native icon substitutions with equivalent meaning;
- fields intentionally omitted for privacy or authorization.

Everything else is a mismatch until reviewed.

## 5. Interaction and Responsive Contract

For each journey record:

`start state -> control -> immediate transition -> active region -> focus ->
close/back/Escape -> restored state`.

Prove:

- which controls are permanently visible versus on-demand;
- default collapsed/expanded state;
- independent scroll containers and sticky regions;
- selection, history and scroll preservation;
- modal/drawer focus containment and return;
- keyboard order and shortcuts;
- mobile one-pane/overflow alternatives;
- touch targets without inflating desktop density;
- no horizontal overflow or occluded composer/actions.

Responsive parity does not mean stacking desktop cards. Reproduce the
reference’s navigation and disclosure model at each viewport.

## 6. Native Implementation Contract

Preserve clean-room boundaries and current native owners, but do not let
“reuse native primitives” override the reference appearance.

- Reuse routes, policies, services, settings, persistence and behavior owners.
- Recompose or locally style UI primitives when defaults visibly differ.
- Do not introduce a generic layout framework for one parity surface.
- Do not enlarge buttons, filters, cards or whitespace merely to satisfy touch
  targets; use viewport-specific density.
- Do not expose a generic foundation/gallery as the accepted first frontend
  chunk. Build the reference-recognizable shell first, then wire deeper
  behavior behind it.
- Keep production data honest. Use test/browser fixtures for visual states
  instead of fake production rows.

## 7. Comparison and Acceptance

Capture reference and native output at identical viewports and states.
Privacy-mask before persistence. Produce:

1. side-by-side images;
2. a transparent overlay or deterministic image diff where practical;
3. a mismatch ledger keyed to denominator IDs;
4. a human visual-review verdict.

Automated comparison must ignore only declared masks/dynamic regions. It never
replaces human review.

For an owner request of “100% identical,” acceptance means:

- all declared regions, controls, ordering and interactions match;
- no material geometry, density, typography, color, spacing or responsive
  mismatch remains outside the permitted-deviation register;
- every required state has comparison evidence;
- the owner/reference reviewer accepts the stable render.

Do not invent a similarity percentage. If the owner accepts 95% or another
threshold, define the calculation/mismatch budget before implementation.

`PASS` requires actual comparison evidence. `Screenshot-ready`, `rendered`,
`zero-console`, `responsive`, and `tests pass` are not parity statuses.

## 8. Work Order Requirements

Every frontend-parity Work Order must include:

- exact reference URLs/screenshots/hashes and required browser profile;
- reference-state and interaction IDs;
- required viewports;
- measurement/density table or linked artifact;
- permitted deviations and forbidden generic substitutions;
- exact first visible outcome;
- same-viewport reference/local comparison procedure;
- mandatory screenshots/overlay/mismatch ledger;
- named visual reviewer and rejection authority;
- stop predicates for unavailable reference, unsafe masking, unmeasured
  material region, or unresolved material mismatch.

The worker must compare during implementation, not only afterward. Require an
early screenshot after the first recognizable shell and a stable post-result
comparison.

## 9. Failure Lessons

Reject these known failures:

- Image Agent: replacing an AI-first project home/editor with a read-only
  generated-image gallery because backend persistence was scheduled later.
- CHAT Inbox: describing three panes and responsive switching without freezing
  actual control density, filter footprint, row heights, typography, composer
  geometry and same-viewport screenshots.
- Applying mobile touch sizing unchanged to desktop controls and filters.
- Forbidding a parity worker from viewing both the live reference and a
  complete offline visual package.
- Accepting source/static/DOM proof as visual parity.
