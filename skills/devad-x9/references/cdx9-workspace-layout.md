# CDx9 Multi-Project Workspace Layout

Read this for any work under `D:\CDx9`. It governs filesystem placement and
cross-project coordination. It does not replace current Git, app-local
`.devad`, tests, runtime evidence, or release gates.

## Architecture

Devad uses one Git repository with multiple Codex app projects and isolated
branches/worktrees. Do not create one repository per app.

- `D:\CDx9\1-core-x9` is the common repository/integration anchor. It is not a
  scratch directory, and a dirty checkout is not automatically integration
  authority.
- Each registered app gets one stable `N-core-<app>` Codex project anchor and
  one paired `N-core-<app>-ref` reference directory.
- App branches start from one accepted common SHA. Product work remains in
  separate worktrees; shared routes, navigation, dependency manifests, common
  models/config, and migrations integrate serially.
- Native Codex task worktrees belong under `D:\CDx9\0-cdx-wt`. Never rename,
  move, or reorganize that host-managed tree manually.
- X9 Loop is optional orchestration. File-first handoffs and native Codex
  worktrees remain valid without Loop or Controller registration. SITE and
  CHAT must not be asked to bootstrap Loop unless the owner later opts in.

Folder names do not prove app identity. The cross-project registry must map
app ID, folder, reference folder, branch policy, and accepted base SHA. Until
that registry exists, empty anchors such as `5-core-mkt` are reserved and
unconfirmed; do not infer that they represent CHAT or another app.

## Workspace Truth

`D:\CDx9\1-core-x9-ref\.devad-aio` is the cross-project source of truth. It should contain a
compact workspace policy, project registry, accepted shared-base/integration
SHAs, ownership ledger, shared-file claims, migration order, and links to each
app's local evidence.

Authority order is:

1. Current Git, filesystem, tests, and runtime evidence.
2. App-local tracked `.devad` facts for that exact branch/SHA.
3. Current `D:\CDx9\1-core-x9-ref\.devad-aio` cross-project registry and decisions.
4. Reference folders and historical handoffs.

`.devad-aio` must not contain product source, secrets, raw chats, customer or
provider data, build caches, copied repositories, or active Loop runtime. Its
backup/versioning state must be declared; an unversioned local file is not
remote-safe merely because it is under `.devad-aio`.

## Root Allowlist

New top-level entries under `D:\CDx9` are limited to:

- `1-core-x9-ref\.devad-aio`: cross-project durable truth.
- `.temp`: task-scoped temporary artifacts.
- `.temp-old`: preserved old or uncertain material after inventory.
- `0-cdx-wt`: native Codex worktrees.
- registered `N-core-<app>` project anchors.
- paired registered `N-core-<app>-ref` reference directories.
- the existing workspace readme/pointer.

`D:\CDx9\.temp-old\2026-07-22\devad-aio-pre-relocation` is `OLD_UNCERTAIN` preserved material, not active authority.

Do not create new loose scripts, archives, test bootstrap files, timestamped
repo copies, `content-agent-*`, `v73s-*`, or generic `worktrees` folders at the
root. Existing examples are migration evidence, not precedent and not proof
that they are safe to move.

## Placement

- Product source and tests: the owning app task worktree.
- Cross-app integration: the common integration worktree after exact gates.
- Public project documentation: `<current-worktree>\docs\<subject>\`, then Git
  integration with the same source branch.
- Private implementation plans and evidence:
  `<current-worktree>\.devad\features\<feature>\plans`, `artifacts`,
  `screenshots`, or `other`. Main tasks and subagents use the same categories.
  A native task never writes directly to another checkout's `.devad`.
- External mockups, source archives, screenshots, and research: the owning
  `N-core-<app>-ref\<topic>\<yyyy-mm-dd>-<slug>` directory.
- Cross-project decisions and registries: `.devad-aio`.
- Short-lived generated material:
  `<current-worktree>\.temp\<task-id-or-date-slug>`. For work performed in the
  common anchor itself, this is `D:\CDx9\1-core-x9\.temp\...`.
- Old or uncertain material approved for preservation: `.temp-old\<yyyy-mm-dd>\<original-name>`.

Reference folders are non-executable. Do not run dependencies, providers,
deployments, migrations, or product tests from them. Temporary and old folders
do not become source authority and must never contain secrets.

## Private `.devad` Backup

The owner-facing `docs/` tree is Git documentation. `.devad` is private Codex
development truth and must not be exposed as public documentation or shipped
in a production image.

When a project selects Contabo S3 for private `.devad` continuity, use one
immutable prefix per accepted change:

```text
projects/<project-id>/changes/<change-id>/
  manifest/
  plans/
  artifacts/
  screenshots/
  other/
```

The manifest records the exact project/profile, feature/change ID, Git SHA,
relative paths, byte counts, SHA-256 values, encryption state, creation time,
retention, and restore order. Upload only secret-scanned, sanitized material.
Do not upload `.env`, credentials, provider payloads, runtime databases,
dependency trees, caches, raw logs, or unredacted screenshots.

S3 is backup and hydration evidence only. Current Git, Controller state, Work
Orders, and runtime proof keep their existing authority. A routing-policy
change does not authorize untracking, moving, overwriting, or deleting existing
`.devad` files.

## Workspace Pointers

- `D:\README.md` is a drive-level pointer: project work belongs under
  `D:\CDx9`, never as a new loose drive-root file.
- `D:\CDx9\readme.txt` is the human workspace pointer.
- `D:\CDx9\1-core-x9-ref\.devad-aio\WORKSPACE.md` and `PROJECTS.md` remain the
  current cross-project registry after live verification.

These pointers explain placement only; they never override Git, the registry,
or an exact task/worktree binding.

## Worktree-Local Temporary And Storage Policy

- The official native Codex worktree root is `D:\CDx9\0-cdx-wt`. Do not create
  alternative worktree roots or copied repositories elsewhere on `C:` or `D:`.
- Default task-local scratch placement is
  `<current-worktree>\.temp\<task-id-or-short-slug>`. Verify the exact path is
  ignored with `git check-ignore` before writing. A writable path is not enough.
- Do not use user-profile temp directories, drive roots, project anchors,
  reference folders, or another worktree for project downloads, proof,
  dependencies, or generated handoffs. Tool-fixed ephemeral transport files
  may exist there only transiently and never become project authority.
- Before any recursive copy, dependency install, archive extraction, download,
  or estimated write above 250 MiB, bind a storage claim with source,
  destination, estimated added bytes, free-space preimage, maximum bytes,
  cleanup owner, and expiry. Require at least
  `max(15 GiB, 2 * estimated added bytes)` free.
- Never recursively copy `node_modules`, `vendor`, package-manager stores,
  Git objects, or whole worktrees. Never use `robocopy /E` for pnpm stores or
  `node_modules`; use the canonical package store and normal package-manager
  linking/offline installation.
- Stop as `STORAGE_BUDGET_BLOCKED` before writing when size is unknown, the
  reserve would be crossed, or a second full copy would be required.
- Temporary material is not self-deleting. Retirement still requires current
  task/process/Git ownership proof, 24 hours without a consumer, link/junction
  checks, and an exact owner-run removal request.

## Inventory Before Relocation

No agent may tidy the root by appearance. For every candidate, record:

- exact path, type, size, timestamps, link/junction/reparse identity, and hash
  manifest where bounded;
- Git top-level/common directory, branch or detached state, HEAD, upstream,
  staged/unstaged/untracked counts, unique commits, and remote reachability;
- owning task/app, active consumers, durable handoff, and intended destination;
- classification: `ACTIVE`, `CANONICAL`, `NATIVE_CODEX`, `REFERENCE`,
  `TEMP`, `OLD_UNCERTAIN`, `SUPERSEDED`, or `UNKNOWN`.

An active, dirty, unpushed, uniquely committed, linked, junction-backed, or
unknown item stays in place. Never use Explorer, `Move-Item`, copy-and-delete,
or a raw filesystem move for a Git worktree. A clean inactive worktree can only
receive an exact owner-run retirement or `git worktree move` plan after Git and
restore proof. X9 agents do not execute the final relocation or deletion.

For non-Git material, first copy to the proposed destination, verify the copy
by hash, and retain the original until the owner performs the final move.
Placing material under `.temp-old` never authorizes later deletion.

## Required Project Preflight

Before an app Worker edits product files, prove:

- project registry entry and app-to-folder mapping;
- repository/common Git directory, branch, HEAD, status, and accepted base;
- native task worktree location or explicitly registered stable anchor;
- exact file/resource ownership and shared-file exclusions;
- app-local durable handoff and required external-reference hashes.

If `.devad-aio` policy/registry is missing or contradictory, allow read-only
inventory but stop new root creation, relocation, and cross-app integration as
`WORKSPACE_POLICY_MISSING` or `WORKSPACE_POLICY_CONFLICT`.

An already-started Worker with a proven Git identity, accepted base, and exact
scope may finish its current bounded checkpoint while the registry is being
bootstrapped. It must not create another root entry, move existing material,
or widen into cross-app integration; record `REGISTRY_BOOTSTRAP_PENDING` in
its handoff. This compatibility rule does not authorize SITE/CHAT product
edits before their own project entries and clean worktrees are bound.
