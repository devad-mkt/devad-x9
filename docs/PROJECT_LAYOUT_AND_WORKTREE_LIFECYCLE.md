# Project Layout And Worktree Lifecycle

This document defines the V7.3 Lite folder and worktree boundary. It is an
operator guide, not a new state contract. The existing Controller paths remain
unchanged.

## Current Layout Truth

X9 Loop separates reusable engine source, installed engine bytes, project
authority, human-readable context, and target application source:

```text
x9-loop source repository/
  skills/devad-x9-loop/                 reusable engine, role instructions, scripts
  scripts/                              package install, migration, and validation
  templates/x9-project/.devad/          bootstrap overlay for a managed project
  tests/                                deterministic package regressions
  docs/                                 operator and contributor documentation

CODEX_HOME/
  skills/devad-x9-loop/                 verified installed copy of the engine

managed-project/
  .devad/
    manager/
      loop-lite/                        sole authoritative per-project Loop state
    features/                           human-readable plans, decisions, evidence
    memory/                             advisory memory with source references
    workers/                            Worker receipts and proof artifacts
  <application source and tests>        the product being managed; outside .devad
```

The reusable engine lives at `skills/devad-x9-loop/`. A managed project must
not copy or fork the engine into `.devad/loop/`, and must not introduce another
Controller or state root. `.devad/manager/loop-lite/` is the only active
per-project Controller state root. Historical `.devad/manager/loop/` content,
when present, is evidence only.

The boundaries are deliberate:

- `.devad/manager/loop-lite/` contains canonical project profile, snapshot and
  shards, Work Orders, actions, events, migration state, and runtime indexes.
- `.devad/features/` keeps plans and evidence readable and shareable by humans.
  Its prose cannot dispatch work or override canonical state.
- `.devad/memory/` is advisory context. Every important fact should retain a
  source reference and must be rechecked against current code and state.
- `.devad/workers/` holds result receipts and their hash-bound proof. These
  bytes are evidence; a Worker cannot grant itself authority by writing them.
- Product source, tests, configuration, and normal Git history stay outside
  `.devad/`. X9 Loop manages that source but does not relocate it.

## Recommended Project Tree

Projects may use their own application layout. The following is the recommended
X9 boundary, not a requirement to rename existing source folders:

```text
project/
  .devad/
    manager/
      loop-lite/
        PROJECT_PROFILE.json
        SNAPSHOT.json
        APPROVED_JOBS.json
        runtime/
          ACTION.json
          work-orders/
        snapshots/
        recovery/
    features/
      <feature-id>/
        TASK.md
        evidence/
      deferred-features-plans/
    memory/
      sources/
      topics/
    workers/
      <worker-id>/
        results/
        proof/
  src/                                  example product source
  tests/                                example product tests
  docs/                                 product documentation
  <project-native configuration>
```

Only paths already defined by the active schema are authoritative. Optional
subfolders shown beneath `features`, `memory`, or `workers` organize
non-authoritative artifacts; they do not create a new routing or state system.

## Worktree Registry Semantics

The registry describes worktree lifecycle without manipulating Git worktrees.
Status is based on current canonical ownership and verified Git identity, never
age, folder name, a chat message, or an old status document.

### ACTIVE

A worktree is `ACTIVE` when any current task, Work Order, dispatch, claim,
resource, or accepted in-flight result references it. An active entry must bind
at least its repository identity, absolute worktree path, branch or detached
state, reviewed HEAD, owning Worker, and active Controller references.

An `ACTIVE` worktree must:

- exist at the registered path;
- resolve inside the registered repository's worktree set;
- match its recorded HEAD and expected branch/detached identity;
- preserve every claimed source and proof path; and
- remain unavailable to overlapping work until the Controller completes an
  explicit lifecycle transition.

A missing or mismatched active worktree is fatal for the affected task. It must
not be silently reclassified as historical.

### RETIRED

`RETIRED` is a Controller lifecycle state, not a filesystem operation. It means
the worktree has no active task, Work Order, dispatch, claim, or resource after
a tested terminal, supersede, or retire-paused transition. The transition must
bind the final Git identity, terminal result or owner-decision evidence, and the
Controller generation that released ownership.

Retiring an entry does **not** move, delete, clean, reset, stash, or prune its
Git worktree. A retired worktree may remain on disk for inspection or reuse,
but it cannot receive new work until it passes fresh admission and clean-state
preflight.

### ARCHIVED

`ARCHIVED` is a storage/catalog property layered on a `RETIRED` entry. It means
the required history and non-Git artifacts have a complete verified archive;
it does not mean the local Git worktree was removed. Archive status never
releases Controller ownership by itself and never makes archived prose or
memory authoritative.

The safe sequence is:

```text
ACTIVE
  -> terminal/supersede/retire-paused Controller transition
  -> RETIRED
  -> exact manifest + archive verification + restore drill
  -> ARCHIVED
```

There is no automatic transition based on date. An old worktree can still be
`ACTIVE`; a newly completed one can be eligible for `RETIRED`.

## Manifest-Driven Archive And Restore

Before labeling a retired entry `ARCHIVED`, create a canonical manifest that
separates Git-reconstructable data from bytes that Git cannot reproduce.

The manifest should bind:

- project profile and repository identity;
- worktree path, branch/detached state, HEAD, and relevant commit range;
- clean/dirty status and an exact path/hash/size list for every retained file;
- dirty tracked patches and untracked files without exposing secrets;
- Work Order, dispatch, result, rejected receipt, security, test, and browser
  proof hashes;
- feature-plan and deferred-plan hashes;
- archive format/version, created time, encryption identity when used, and
  archive root hash; and
- the Controller generation and terminal evidence that permit archival.

Large immutable import inventories may use separate content-addressed shards,
but the root manifest must reference every shard. A recursive copy without a
complete verified manifest is a partial copy, not a backup.

Restore is complete only after a clean destination is rebuilt and the system
verifies Git identity, every manifested non-Git byte, canonical receipt/proof
closure, and project-profile binding. Restore first to a new path. It must not
overwrite an active worktree. Re-admission as `ACTIVE` is a separate Controller
decision with fresh claims, resources, Work Order, and preflight.

## Clean-Worktree Preflight

Run preflight before program import and again before creating a Work Order. It
must be read-only and report exact paths and reasons.

Preflight must prove:

1. the path resolves to the registered worktree and does not escape through a
   symlink or Windows reparse point;
2. repository, HEAD, and branch/detached identity match the requested base;
3. no other active entry owns overlapping claims or resources;
4. tracked modifications and unrelated untracked files are absent;
5. exact canonical receipt/proof files that are already validated and
   hash-bound to completed work are recognized as system evidence rather than
   unrelated dirt; and
6. rejected receipts remain preserved in their typed immutable registry and do
   not poison a valid corrected result.

Recognition is exact: any unexpected file, hash mismatch, missing proof,
tampered receipt, or ambiguous ownership fails preflight. The response is to
use a verified clean worktree or a tested lifecycle/archive transition, never
to reset, clean, stash, move, or delete evidence automatically.

## Optional Pro Projections And Backup

Obsidian and S3 are deferred optional V7.3 Pro modules. Lite must operate fully
without either one.

- **Obsidian** may project source-cited feature plans, memory, relationships,
  worktree status, and proof indexes into a human-friendly vault. The vault is
  deletable and rebuildable. It cannot create tasks, approve gates, select a
  Worker, or override current code and canonical state.
- **S3** may store selected-project encrypted backups and content-addressed
  archive shards. Upload success is not backup proof: a commit marker,
  manifest verification, download/decrypt/hash verification, and a real restore
  drill are required. S3 is not a live Controller database.

If either module is unavailable, stale, or corrupted, disable that projection
or backup route. Routine Controller, LINKER, WORKER, THINKER, migration, doctor,
and rollback behavior must continue unchanged. Canonical project state and
verified Git/runtime evidence always outrank Obsidian, S3, chat, or memory.
