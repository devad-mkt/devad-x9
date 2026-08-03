---
name: semantic-adoption
description: Adopt proven behavior, UX patterns, provider contracts, vendor fixes, or accepted branch work into the current native application without copying stale architecture or overwriting local ownership. Use for reference-driven implementation, current-main reconciliation, legacy-to-native migration, parity work, provider/channel adoption, vendor hunk comparison, or any task that must preserve customized behavior while applying the smallest verified semantic diff.
---

# Semantic Adoption

Adopt behavior, not ancestry. Keep the current application and its owners as
the destination authority. Use references, earlier branches, vendor releases,
and live products only to identify facts the native application still lacks.

This workflow is self-contained. Do not load broader migration, delivery, or
reasoning skills by default. Load another specialized skill only when the user
explicitly requests it or a current critical boundary cannot be resolved here.

## Finish Line

Deliver the smallest native vertical change that preserves existing features,
adds only the proven gap, uses current platform owners, proves the changed risk
and rollback, and keeps source, merge, deploy, and live states separate.

## 1. Bind Current Truth

Before behavioral edits, bind only decision-changing facts:

- repository, worktree, branch, HEAD, upstream, remote, and dirty paths;
- destination source and accepted integration target;
- reference version/SHA or official external contract;
- claimed paths, shared-path exclusions, tests, and runtime resources;
- current authority and forbidden actions.

Plans, reports, Sheets, memories, screenshots, and prior messages are discovery
input until current source or runtime evidence confirms them.

## 2. Trace The Existing Owner First

Trace the actual path:

`UI/settings -> request/route -> authorization -> service -> persistence -> queue/runtime/provider -> result -> tests`

Record one compact row in the current plan, Work Order, or response:

| Field | Required decision |
|---|---|
| `EXISTING_FEATURE` | Existing equivalent behavior and locator |
| `UI_SETTINGS` | Control, setting, flag, plan, or permission |
| `SERVER_AUTHORITY` | Current policy/service/config owner |
| `PERSISTENCE_RUNTIME` | Stored form, async path, and runtime consumer |
| `INTEGRATED_HISTORY` | Accepted work already represented at destination |
| `TEST_PROOF` | Reusable focused source/browser/runtime proof |
| `GAP` | Exact accepted behavior still missing |
| `CHANGE_MODE` | One classification below |

Use one classification:

- `REUSE`: the current owner already satisfies the requirement.
- `EXTEND`: add the gap inside the current owner.
- `NEW`: no owner exists; require source-backed absence.
- `PROTECT`: destination behavior must not be overwritten.
- `DEFER`: an external dependency or owner decision blocks only this item.
- `DROP`: reference behavior is unaccepted, redundant, unsafe, or obsolete.
- `REPLACE_AUTHORIZED`: replacement is explicitly owner-approved.

## 3. Compare Three Semantic Sources

Build a bounded three-way view by behavior card:

1. **Current destination:** authoritative owners and later local behavior.
2. **Accepted source/reference:** workflow facts, tests, fixes, and UX states.
3. **Current external contract:** official provider/API rules or verified live
   behavior when required.

Classify every behavior card. Never wholesale replace a customized file or
import historical ancestry when a semantic hunk can be reconstructed at the
real owner. Reference code may reveal facts; it never automatically owns native
architecture, schemas, dependencies, settings, queues, policies, or UI.

## 3A. Evidence Intake (Only When It Changes The Contract)

Use this small gate when a reference UI, legacy route, provider rule, or
accepted branch could change the chosen native behavior:

1. Reuse the matching current packet, report, or official source; do not
   recreate an evidence library because a new task began.
2. Collect only the missing fact that can change the owner, contract, or test.
   Keep source, reference UI, deployed/runtime, and provider proof separate.
3. Bind a URL, path, SHA, screenshot, or normalized observation only when the
   Work Order or decision needs it. Otherwise keep a compact locator.
4. Rebind the selected fact to current destination preimages immediately before
   coding, then classify `REUSE`, `EXTEND`, `NEW`, `PROTECT`, `DEFER`, or `DROP`.

This is a lean intake, not the full evidence workflow. Escalate to
`$evidence-to-implementation` only when the missing evidence spans many
surfaces, roles, settings, responsive states, or provider/runtime contracts and
would otherwise force the implementer to invent behavior. An unresolved fact
parks only its dependent behavior card.

## 4. Freeze One Small Vertical Contract

Freeze only implementation-changing facts:

- user outcome, exact gap, reused owners, and protected behavior;
- inputs, outputs, validation, authorization, tenancy, and plan gates;
- persistence, idempotency, effects, errors, retry, and recovery;
- controls, states, responsiveness, and accessibility basics;
- exact files, tests, exclusions, rollback, and stop conditions.

Reuse an accepted contract when it matches current preimages. Do not create a
second plan, packet, matrix, or review because a new task or turn began.

## 5. Use The Minimum-Solution Ladder

After tracing the flow, stop at the first sound option:

1. no change;
2. reuse existing behavior/helper;
3. standard library or framework/native platform;
4. installed dependency;
5. smallest local change in the real owner;
6. new abstraction or dependency only for a demonstrated current need.

Reject speculative scaffolding, parallel catalogs, duplicate policies, generic
provider frameworks, test-only production seams, one-implementation
interfaces, and broad rewrites. Fix a shared root cause once.

## 6. Implement And Prove

1. Use an existing focused test as the failing probe when available. Add one
   real failing check for a material unproved gap; do not manufacture fake RED.
2. Apply the smallest semantic hunk manually inside the current owner.
3. Run focused tests and deterministic security/syntax/format checks while
   editing.
4. Run broad tests, build, browser, migration, and release gates once at the
   milestone that needs them.
5. Review one stable material diff once. Reuse exact proof for unchanged bytes.
6. Integrate feature cards serially and keep rollback commits or inverse
   operations small.

Every changed nontrivial branch, parser, trust boundary, persistence path, or
provider decision leaves one runnable regression check.

## Provider And Channel Completion

Keep provider families separate even when they share a small transport seam.
Prove the relevant layers:

1. settings and encrypted credential owner;
2. connect/callback/verification and replay-safe state;
3. account/page/location discovery and selection;
4. inbound normalization, tenant identity, persistence, dedupe, and recovery;
5. outbound intent, queue/outbox, lifecycle, receipts/reconciliation, and
   outcome-unknown behavior;
6. honest UI/browser proof and provider fake or authorized live proof.

Default live behavior off until credentials, approvals, callback registration,
exact deployed SHA, spend, and authority pass. Local fake PASS is not live PASS.
Before a live claim require:

`local candidate SHA == deployed release SHA == health/readback SHA`

Never store secrets, OAuth codes, tokens, cookies, raw provider payloads, or
secret-bearing URLs in Git, plans, screenshots, prompts, or receipts.

## Risk And Proof Budget

- `LITE`: documentation, hashes, reversible mechanical edits; direct proof.
- `MEDIUM`: ordinary multi-file behavior; focused proof and one stable-diff
  review when material.
- `HIGH`: tenancy, auth, secrets, stateful migrations, provider activation,
  destructive action, money, production, or rollback; explicit invariants,
  negative tests, atomicity, rollback, and independent challenge.

High program risk does not make every slice High. For migrations, remove only
owned objects. Prove forward shape, failure atomicity, scoped rollback,
predecessor preservation, and the next earlier rollback in a disposable DB.

## Blocker Routing

A failed tool, fixture, browser, database, or preferred route is
`ROUTE_BLOCKED`, not an automatically blocked objective.

1. Preserve current bytes and state.
2. Diagnose the failed mechanism.
3. Try one structurally different safe route within authority.
4. Continue the highest-value independent slice.
5. Escalate only for a real owner/security/architecture/destructive/live
   boundary or after two distinct evidence-backed failures.

Declare the full objective blocked only when every useful lane has a genuine
external boundary. A parked lane includes its exact restart gate.

## Ceremony Gate

Before adding a document, helper, agent, abstraction, scan, hash, review, or
gate, ask which accepted requirement needs it, why an existing owner/check
cannot cover it, and whether it changes the next decision. Without a concrete
answer, skip it. After two process-only cycles, restate the finish line, name
one blocker, choose one direct action and proof, and resume implementation.

## Output

Use `DONE`, `NEXT`, `BLOCKED`, and `OWNER_ACTION`. Always distinguish
`PLANNED`, `SOURCE_ONLY`, `TEST_PROVED`, `LOCAL_BROWSER_PROVED`, `MERGED`,
`DEPLOYED`, and `LIVE_PROVED`.
