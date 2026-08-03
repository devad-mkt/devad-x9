# <Project or Feature> Plan Router

Status date: <YYYY-MM-DD>
Owner outcome: <measurable outcome and deadline>
Repository/worktree: <absolute path>
Branch/HEAD/upstream: <exact identity>
Current state: <one honest sentence>

## TLDR

This is the only startup document. Read the current authority, one dependency
receipt, exact source files, and only the workbook rows needed by the current
slice. This plan routes evidence; it does not grant product, database,
provider, browser, deployment, or production authority.

## 1. Truth and authority

Use this order when sources disagree:

1. system/developer/user instructions and newest immutable Work Order;
2. current source, Git, test, browser, database and runtime evidence;
3. latest relevant receipt;
4. exact live workbook/ledger readback;
5. this router;
6. current detailed plans;
7. historical plans and external opinions.

Before writes, prove repository identity, clean/known dirt, exact authority,
owned paths, shared resources, dependency state, and rollback boundary.

## 2. Minimum mandatory read

Every worker reads only:

1. this `PLAN.md`;
2. one current immutable Work Order;
3. one immediate dependency receipt;
4. exact owned source files and nearest conventions;
5. bounded workbook/ledger rows below.

## 3. Read-by-need router

| Slice signal | Required first | Optional only if unresolved | Do not read by default |
|---|---|---|---|
| Resume/status | Latest receipt; Git/runtime truth | Current strategy status section | Archives and raw model answers |
| Database/security | Exact order; schema/policy/context/tests | Named design sections | UI/provider evidence |
| Backend feature | Route/request/policy/service/model/tests | One source-map reference | Whole repository |
| Frontend/UI | Exact page/control/journey rows; current components | Correct-profile browser evidence | Unrelated pages/channels |
| Queue/realtime | Actual transaction/job/event/config/tests | Named operations section | New infrastructure |
| Provider/channel | One provider contract and its feature/chunk rows | Licensed source locator | Other channels |
| Release/deploy | Exact candidate SHA, gates, rollback authority | Named runbook section | Production mutation from this plan |

## 4. Workbook or ledger routing

Workbook/ledger: <URL or absolute path>

Always read only:

- <overview/status range>;
- one feature/page/chunk row;
- exact control/setting/journey/gap IDs;
- acceptance/release rows only when closing.

Use live connector readback for current writes. Treat exports as read-only
snapshots. Never read every tab by default.

## 5. Current checkpoint

| Gate | Current truth | Evidence |
|---|---|---|
| <gate> | `PASS/FAIL/NOT_RUN/UNKNOWN/BLOCKED` | <path, SHA, test, range> |

## 6. Dependency-ordered priorities

Priority is delivery order, not silent scope deletion.

| Order | User outcome | Included IDs | Complete proof |
|---:|---|---|---|
| 1 | <essential outcome> | <feature/chunk IDs> | <source/test/browser/runtime> |

Remaining accepted scope stays in the full ledger unless the owner explicitly
retires it.

## 7. One-slice delivery loop

1. Freeze one denominator segment.
2. Classify `REUSE`, `ADAPT`, `REIMPLEMENT`, or owner-approved `RETIRE`.
3. Trace current source before reference or new design.
4. Implement one vertical path from request through recovery.
5. Run focused tests while coding.
6. Run one review after the diff stabilizes.
7. Prove browser/runtime behavior when applicable.
8. Produce receipt, commit/push readback, and bounded ledger update.

## 8. Long-run workers

| Lane | Whole-mission outcome / done token | Envelope | Internal queue and safe fallback | Write boundary |
|---|---|---|---|---|
| <lane> | <observable outcome / token> | `90-240 min`; `<5-15 files or one denominator>` | <ordered phases; one structural fallback; disjoint continuation> | <exact EXCLUSIVE paths plus SHARED/READ_ONLY/FORBIDDEN resources> |

Each mission exists as one hash-bound Markdown Work Order. It binds the worker
identity/base, read-first list, claims, internal queue, routine decision rights,
fallbacks, proof, stable review, authorized C1/C2/push/readback, hard stops, and
one whole-mission done token.

Workers continue through authorized queue items without stopping after one
file, command, test, page, review, receipt, or commit. A blocked dependency
marks only its dependent claim partial; every disjoint authorized phase
continues.

Immediately before `DONE` or genuine hard `BLOCKED`, the worker wakes the
manager with lane, state, token/blocker, branch/HEAD, receipt path/hash/bytes,
and one proposed next gap. The callback grants no new authority. The manager
verifies the result and immediately issues the next dependency-ready Work
Order. A periodic snapshot is only fallback recovery, never a stop point.

## 9. Owner attention

| Decision | Recommended default | Consequence if unanswered |
|---|---|---|
| <major decision> | <smallest safe choice> | <exact blocker/default> |

## 10. Supporting files

| Path | Read rule |
|---|---|
| `PLAN.md` | Mandatory entrypoint |
| `HANDOFF.md` | Resume navigation only; current evidence wins |
| `VALIDATION.md` | Package maintenance only |
| `work-orders/<order>.md` | One current immutable execution authority |
| `decisions/<decision>.md` | Read only when a named decision blocks the slice |
| `reviews/<packet>.md` | External review only; never execution authority |
| `runs/<receipt>.md` | Immediate dependency or closeout only |
| `references/<reference>.md` | Read only for its matching signal |
| `guardrails/WORKER-GUARDRAILS.md` | Attach matching subsection to workers |
| `guardrails/AUTONOMOUS-MISSION-PROTOCOL.md` | Long-run missions only; decision/fallback/wake/redispatch contract |

Only `PLAN.md` is required. Copy optional templates only when each has a
distinct routing purpose.

## 11. Completion and stop rules

Complete means every owner-accepted item has the required source, test,
database, browser, integration, operational, release and rollback proof.
Unknown, deferred, documented, or model-recommended does not mean complete.

Stop for authority mismatch, dirty overlap, wrong runtime/resource, secret
exposure, destructive/live action without permission, or missing rollback.
