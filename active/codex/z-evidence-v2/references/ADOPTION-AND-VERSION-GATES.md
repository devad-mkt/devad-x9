# Adoption and Version Gates

## Table of Contents

1. [Lesson](#lesson)
2. [Requirement ledger](#requirement-ledger)
3. [Version matrix](#version-matrix)
4. [Historical reviewer loop](#historical-reviewer-loop)
5. [Addon and UI parity](#addon-and-ui-parity)
6. [Framework adoption](#framework-adoption)
7. [Required gates](#required-gates)
8. [Semantic closeout](#semantic-closeout)

## Lesson

A structurally valid packet can still be unusable. The AI-media attempt passed
file-count and hash validation while missing the required recovered-session
review, branch comparison, addon source, screenshots, deep interactions,
framework migration, and component decision.

The causes were:

- treating binding owner actions as optional discovery leads;
- validating folders instead of owner-requirement coverage;
- collapsing distinct addons into a generic canvas gap;
- treating registration hooks as proof that addon source existed;
- allowing partial browser evidence to imply implementation readiness;
- failing to compare historical framework choices with the current target.

Never repeat this pattern. Validate the meaning of the report against the owner
request, not only its folder shape.

## Requirement ledger

Before research, convert every owner sentence and question into a stable row:

| Requirement ID | Exact requirement | Required source/action | Output | Gate | Status |
| --- | --- | --- | --- | --- | --- |

Include every named:

- session, task, reviewer and review checkpoint;
- URL, route, repository, branch, backup, addon and version;
- visible/hidden interaction, screenshot state and viewport;
- historical architecture and resource decision;
- framework, component, setting and admin owner;
- UI, API, CLI, MCP, worker, queue and provider behavior;
- output path, packet, manifest and validation requirement.

No requirement may disappear through summarization. End it as `SATISFIED`,
`SUPERSEDED_BY_OWNER`, `NOT_APPLICABLE_WITH_PROOF`, `UNKNOWN`, or
`BLOCKED:<gate>`.

## Version matrix

Freeze these independently:

| Layer | Required identity |
| --- | --- |
| Current native target | repository, branch, SHA and package versions |
| Current deployed product | deployment/build SHA or `UNKNOWN` |
| Authenticated live reference | URL, profile and observation timestamp |
| Licensed local reference | root, hash, product/framework version |
| Addon package | package root/version/hash or `SOURCE_MISSING` |
| Historical implementation | repository, branch, SHA and date |
| Official reference | URL and retrieval date |

Compare every owner-named branch. Record ahead/behind/diverged state and its
semantic purpose. Latest commit does not automatically mean correct adoption
base. Old framework code is behavioral evidence until a current-target
contract explicitly accepts it.

## Historical reviewer loop

When the owner names a prior task as a reviewer:

1. Recover exactly that task; never substitute another task.
2. Read its durable memory and the minimum raw history needed to distinguish
   discussion from accepted decisions.
3. Pin or unarchive it only when authorized.
4. Send the draft plan before analysis and record its response.
5. Send stabilized evidence and the proposed contract before coding.
6. Send the final diff, tests and runtime evidence after implementation.
7. Resolve its findings before claiming completeness.

If task control is unavailable, keep `REVIEWER_NOT_RECOVERED`. Reading a
summary helps discovery but does not satisfy the callback.

## Addon and UI parity

Give each material addon or editor subsystem its own denominator and normally
its own five-file packet. Menu entries, conditional includes, provider
registrations and marketplace prose prove integration intent only.

For each addon/editor subsystem capture:

- routes, entry modes, dependencies and plan gates;
- every control, icon, menu, panel, drawer, modal and option;
- hidden, disabled, empty, loading, error and data-dependent states;
- pointer, selection, focus, keyboard, responsive and accessibility behavior;
- transitions, smoothness, undo/redo, autosave, conflicts and recovery;
- DOM/ARIA and secret-safe request metadata;
- masked screenshots for each materially different safe state;
- licensed source owners and missing packages;
- current target owner and clean-room component decision;
- CPU, RAM, bundle and interaction budgets when requested.

Reconcile live behavior, source, screenshots and tests. None substitutes for
the others.

## Framework adoption

Compare predecessor and target:

- backend/frontend framework versions;
- canvas/rendering engine and scene schema;
- state, routing, styling, accessibility and testing conventions;
- browser versus queue/worker responsibility;
- dependency, license, bundle, CPU, RAM and operating costs;
- admin/settings authority versus hardcoded behavior.

Choose per component family:

`NATIVE_REUSE | CLEAN_ROOM_REIMPLEMENT | LICENSED_ADAPTER |
THIRD_PARTY_SDK_OWNER_DECISION | DROP | UNKNOWN`.

Do not paste old framework UI code into a current React target. Preserve
verified behavior and accepted schemas while using current-native owners.

## Required gates

### PRE_ANALYZE

- owner ledger complete;
- output and safety boundary bound;
- named reviewer located;
- source/version/branch matrix planned;
- addon and screenshot packets allocated.

### PRE_PLAN

- required reviewer received the draft;
- accepted historical decisions separated from stale implementation;
- every requirement maps to a phase and artifact;
- no generic packet hides a material addon.

### PRE_CODE

- target SHA/package versions rebound;
- evidence rows closed or explicitly unknown;
- reviewer accepted the proposed implementation contract;
- component/dependency decision recorded;
- settings, authorization, persistence, errors, rollback, performance and tests
  specified.

### PRE_REPORT

- semantic requirement coverage is complete or status is `PARTIAL`;
- screenshots/interactions reconcile with the denominator;
- source hooks are not reported as installed addons;
- every reuse decision cites current evidence;
- hash, link, privacy and no-mutation checks pass.

### POST_RESULT

- implementation matches the accepted contract;
- tests, build, browser parity, accessibility and performance are attached;
- prior reviewer received the result;
- corrections are resolved before final acceptance.

## Semantic closeout

Every master index includes:

| Requirement ID | Evidence IDs | Packet rows | Decision | Proof/blocker | Reviewer |
| --- | --- | --- | --- | --- | --- |

`READY` requires all binding rows and reviewer gates closed. Structural
validator success alone never proves semantic completeness.

