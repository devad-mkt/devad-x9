---
name: devad-x9
description: Use for Devad X9 repository work that changes or reviews code, tests, implementation-guiding docs, Git commits, security gates, proof, source pushes, deployment, local work, feature catalogs, worktrees, Worker execution, or the D:\CDx9 multi-project workspace layout. Also use as the repository router paired with x9-loop-style.
---

# Devad X9 v6

## Load First

Read `references/x9-shared-contract.md`. Before mutation also read
`references/destructive-action-guard.md`. The shared contract owns truth,
local work, Git safety, security, commits, proof, release gates, and durable
docs. `$x9-loop-style` owns the stable default packet, direct-result, Project
Intelligence, memory, and documentation flow. `$x9-loop-code` is an
experimental Controller trial for an explicit fresh disposable project only.
The retained `$devad-x9-loop` name redirects normal work to Style; neither it
nor Code is normal or production project authority.

For any path, project, worktree, reference, temporary artifact, or cleanup
under `D:\CDx9`, also read `references/cdx9-workspace-layout.md` before
creating or relocating anything. That policy works without X9 Loop; never
require Controller bootstrap unless the owner explicitly enables it for the
affected project.

Cached plugin skills are replaceable installation bytes, not durable policy.
Before relying on a cached plugin for Devad worktree placement, read
`references/plugin-cache-durability.md` and verify its bound override. Missing
or drifted protection is `PLUGIN_CACHE_NON_DURABLE`: do not fall back to
generic `.worktrees` or a new `D:\CDx9` root path.

Current repository evidence wins over durable narration. Never perform the
final destructive action.

Before a Worker asks for authorization, creates a repair packet, consults
THINKER/LOOPER, or declares a blocker, read
[references/worker-autonomy-and-escalation.md](references/worker-autonomy-and-escalation.md).
It links the separately installed `subagents` skill without copying or
replacing that skill.

## Role

X9 is the repository and Worker router. It codes only when this task is the
registered `WORKER`, or when the owner directly asks this task to implement.
Linx and Thinx never code or rescue a Worker by taking its scope.

## Startup

1. Resolve repo root, branch, HEAD, remotes, every worktree, and staged,
   unstaged, untracked, and committed paths from current Git.
2. Read `.devad/ROUTER.md`. Read
   `.devad/manager/loop-lite/SNAPSHOT.json` only when the owner or current
   durable task explicitly enables X9 Loop for this project.
3. For a Loop-governed task, read the exact `TASK.json` and verify task,
   Worker, dispatch, packet, worktree, base SHA, claims, resources,
   dependencies, gates, and finish line. Otherwise use the current app-local
   handoff/owner packet and verify the same repository, base, scope, and gates
   without inventing Controller state.
4. Read only linked central facts, mission lock, local-work truth, feature
   contract, and applicable project/security rules.
5. Keep manager-state, implementation, integration, deployment, and live-proof
   branches/HEADs separate.
6. If durable facts conflict with Git/runtime, stop the stale route and run
   deterministic reconciliation. Never patch orchestration state manually.

No push, deploy, integration, cleanup, or next-action decision is valid while
active local-only work is unclassified.

## Storage And Temporary Files

- Use native Codex worktrees only under `D:\CDx9\0-cdx-wt`. Do not create a
  second worktree root, copied repository, or project folder elsewhere on
  `C:` or `D:`.
- Put task downloads, generated evidence, scratch files, and disposable caches
  under `<current-worktree>\.temp\<task-id-or-short-slug>`. Before writing,
  prove the path is ignored with `git check-ignore`; otherwise stop and add or
  request the narrow ignore rule first.
- Do not place project artifacts in user-profile temp folders, a drive root,
  another task's worktree, or a shared project anchor merely because it is
  writable. Tool-owned ephemeral files are allowed only when the tool fixes
  their location and they are not project handoff or proof authority.
- Before a recursive copy, dependency install, archive extraction, download,
  or operation estimated above 250 MiB, record source, destination, estimated
  added bytes, free space, ceiling, cleanup owner, and expiry. Require free
  space of at least `max(15 GiB, 2 * estimated added bytes)`; stop when size is
  unknown or the reserve would be crossed.
- Never recursively copy `node_modules`, `vendor`, a package-manager store,
  Git objects, or a worktree. In particular, never use `robocopy /E` for pnpm
  stores or `node_modules`. Reuse the canonical package store through the
  package manager's normal linking/offline install behavior.
- Exceeding the declared ceiling is `STORAGE_BUDGET_BLOCKED`: stop the writer,
  preserve current bytes, and report exact paths and sizes. Do not start a
  second copy as recovery.
- Retirement requires a current task/process/Git inventory, at least 24 hours
  without a consumer, clean and pushed/merged proof, link/junction checks, and
  an owner-run removal plan. Age alone is never deletion authority.

## Project Documents And Private Development Files

These paths apply equally to the main task and every subagent:

- Public project documentation belongs under `<repo>\docs\<subject>\` and is
  tracked with the project's Git repository.
- Private Codex development plans, Work Orders, artifacts, and sanitized
  screenshots belong under the current bound worktree at
  `.devad\features\<feature>\plans`, `artifacts`, `screenshots`, or `other`.
- A Worker in `D:\CDx9\0-cdx-wt\<host-id>\1-core-x9` writes to that worktree's
  relative `.devad\features`; it does not write directly into the shared
  `D:\CDx9\1-core-x9` anchor. Integration brings accepted files to the anchor.
- Temporary project material belongs under the current worktree's ignored
  `.temp\<task-id-or-short-slug>`. When the current checkout is
  `D:\CDx9\1-core-x9`, this resolves to `D:\CDx9\1-core-x9\.temp`.
- Never use `C:\tmp`, a drive root, `D:\CDx9` loose files, another project's
  anchor, or another task's worktree for project material.

`.devad` is private development truth, not public documentation. For owner
projects configured for Contabo S3 backup, store each accepted change in one
private prefix:

`projects/<project-id>/changes/<change-id>/{manifest,plans,artifacts,screenshots,other}`.

The manifest binds project, feature/change ID, source Git SHA, relative path,
size, SHA-256, creation time, retention, and encryption state. Never upload
secrets, raw provider payloads, runtime databases, caches, dependencies, or
unredacted screenshots. S3 backup is a restore source, never Controller,
Work Order, Git, or live-runtime authority. Existing tracked `.devad` files
remain untouched until a separately approved migration; no agent untracks,
moves, or deletes them merely because this routing policy changed.

## Existing-System Admission

Before accepting an implementation plan, claims, or the first behavioral edit,
run one targeted existing-system pass against the current app branch:

1. Verify whether the owner-named predecessor or accepted integration commits
   are present at the current Git identity. A copied handoff without its code is
   not reuse proof.
2. Trace visible UI/settings and the request/route through the canonical
   service, model, job/queue, persistence, provider adapter, runtime consumer,
   and focused tests. DOM proves presentation only; source alone does not prove
   current visible behavior.
3. Search current source plus owner-named Sheets, handoffs, and app-domain
   contracts. Use those artifacts to find candidates, then verify decisive
   ownership in current source or runtime evidence.
4. Record in the existing task or Work Order, never a new report:
   `EXISTING_FEATURE`, `UI_SETTINGS`, `SERVER_AUTHORITY`,
   `PLAN_ENTITLEMENT`, `REFERENCE_REUSE`, `PERSISTENCE_CONSUMPTION`,
   `INTEGRATED_HISTORY`, `TEST_PROOF`, `GAP`, and `CHANGE_MODE`.
5. Set `CHANGE_MODE` to `REUSE`, `EXTEND`, `NEW`, or
   `REPLACE_AUTHORIZED`. `NEW` requires source-backed absence in the claimed
   scope. Replacement requires owner authority. Unknown ownership blocks only
   the dependent claim.

Prefer `rg`, Git history, route/service/test tracing, and installed
framework-native tools. Graphs and memories are advisory discovery only. Do
not install or build a graph/memory system for an ordinary Worker slice.

When an owner was discovered only after implementation, a merged app-domain
capability was overlooked, or UI and backend evidence conflict, read
[existing-system ownership miss](references/lessons/existing-system-ownership-miss.md)
before accepting the next plan or Work Order.

## Worker Pass

Normal Worker model is `gpt-5.6 Terra high`. Use Terra xhigh only when the
owner explicitly asks.

1. Verify identity and exact claims before editing.
2. Revalidate the Existing-System Admission evidence, then inspect the narrow
   implementation surface and active rules.
3. Make the smallest coherent change inside owned files.
4. If a new file is required, request `CLAIM_EXPANSION_REQUEST` first.
5. Run focused tests, formatting, and the full repository security gate.
6. Reconcile actual staged, unstaged, untracked, and committed paths. Any path
   outside claims is `SCOPE_BREACH` and cannot integrate.
7. Create source commit C1 from exact staged files only.
8. Write `.devad/docs/commits/<C1>.md` and commit only attestation files as C2.
   C2 does not require another record.
9. Write the exact hashed `RESULT.json` with changed files, proof, C1/C2, and
   blocker state, then send one direct callback.

Never use `git add .`, broad cleanup, reset, stash, worktree removal, database
or app deletion, or infrastructure destruction.

## Sticky Worker Lanes

Keep one task, native worktree, branch, and exact exclusive claims as a sticky
lane until its bounded source result is frozen. Remote-main movement alone is
`REBIND_DUE`: it never interrupts ordinary local coding, focused tests, local
proof, or safe disjoint work. Rebind only at an integration/release boundary,
or when task identity, a shared claim/resource, or an accepted assumption
actually changes. Read the lane-state contract in
`references/worker-autonomy-and-escalation.md`; never copy, replace, or
repeatedly reattach a valid worker worktree merely to chase main.

## Security And Release

Read applicable rules under `.devad/rules/security` before every commit. Run
the full security gate against exact staged scope and record evidence.

Release states are `PLANNED_ONLY`, `UNCOMMITTED`, `SOURCE_ONLY`,
`V105_READY`, `DEPLOYED`, and `LIVE_PROOF_PASS`. Source push, deploy
readiness, live deployment, and live proof are separate exact-SHA gates.
Historical PASS does not open a current gate.

## Durable Files

`SNAPSHOT.json`, `TASK.json`, and `RESULT.json` are machine authority.
`STATUS.md` and `HANDOFFS.md` are generated human views, never parser
authority. Detailed plan, worklog, security, tests, commits, decisions,
side reviews, and proof remain under `runs/<run-id>/` and are linked.

Use stable feature folders. Subfeatures exist only for independent acceptance
or lifecycle. Local-only artifact links are forbidden; large proof uses
private storage or LFS with path, hash, and meaning recorded.

## Sidecars And Blockers

For a verified difficult technical issue, choose at most one expert route that
can change the next action: one bounded internal subagent under the installed
`subagents` skill, or one secret-safe Reader/sidecar packet containing the
owner requirement, claims, relevant diff/proof, failure, and one question. Do
not run both by default. The Worker verifies all advice and remains accountable.

An in-scope, reversible safe action proceeds under the current task authority;
it does not require owner, THINKER, or LOOPER permission. One failed local
approach may justify one bounded subagent or one genuinely different local
approach. Only two distinct evidence-bound failures, or a real
owner/destructive/production/security/architecture/scope boundary, justify a
THINKER or owner escalation.

`TOOL_UNAVAILABLE` is nonblocking and never triggers a retry loop or stronger
model by itself. Environment and permission failures require a route
correction, not repeated consultation.

## Manager Shortcut

```text
Use $x9-loop-style as Thinker. Also use $devad-x9 as repo router.
Use $x9-loop-style as Linker. Also use $devad-x9 as repo router.
Use $x9-loop-style as Worker. Also use $devad-x9 as repo router.
```

Old `$devad-x9-manager` prompts use the temporary compatibility redirect.

## Completion

Require current code, Git, test, security, runtime, and release-gate proof,
plus exact Worker-owned completion identity. Unknown evidence is `Unknown`,
not a guessed PASS or blocker. Keep visible chat short and point to durable
proof.
