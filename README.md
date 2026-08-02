# X9 Loop: Style (Stable) + Code (Trial)

**Make long Codex jobs finish without turning your project into an orchestration experiment.**

X9 starts with a small, durable packet: current Git, a clear owner, focused
proof, a compact result, and one direct handoff. That is **X9 Loop Style**, the
safe default for new and existing Codex projects.

> This repository is the source package. It does not mean your live Codex
> skills or project are already installed or activated.

## TLDR

| Problem | Use | Benefit |
| --- | --- | --- |
| A Worker needs clear next steps | **Style**: one packet and direct `RESULT_READY` receipt | Normal work continues without a Controller or recurring monitor. |
| A plan may rebuild existing behavior | **Style + Project Brain**: re-read source-backed ownership before planning and code | Reuse the real owner instead of guessing. |
| Later tasks need compact project context | **Style + Docs/Memory**: a verified sitemap links the plan, source evidence, and proof | Less chat-history rereading and cheaper handoffs. |
| You want to research the old Controller engine | **Code trial**: a fresh disposable-project canary only | It cannot become production infrastructure by accident. |

> **Default: X9 Loop Style.** It is stable for normal and existing projects.
> **X9 Loop Code is experimental.** It is not production-ready and may run
> only in an explicitly owner-approved fresh disposable project with one
> bounded canary.

**Honest status:** this source package installs sixteen skills. Style, project
docs, source-backed context, and historical memory are the normal path.
Controller work, live providers, deployments, multi-project orchestration,
encrypted S3 execution, dashboards, and graph views are not production claims.

## Why Codex users may want it

- **Fewer stuck tasks:** one callback, one deterministic repair, then one clear
  incident instead of endless retries.
- **Less context waste:** Workers get compact, hash-bound packets and direct
  links to the exact feature docs.
- **Less duplicate code:** current Git must prove whether to reuse, extend,
  create, or explicitly replace a feature.
- **Cheaper coordination:** LINKER transports exact action bytes with zero model
  calls.
- **Safer releases:** source, installation, activation, provider calls, and
  deployment are separate proof gates.

## Start here

| Document | Use it for |
| --- | --- |
| [X9 Loop Style](skills/x9-loop-style/SKILL.md) | Start normal work safely: packet, proof, receipt, and direct handoff. |
| [Style Project Intelligence](skills/x9-loop-style/references/project-intelligence-v1.md) | Source-backed `CONTEXT_CAPSULE` and ownership admission before planning/code. |
| [Project Docs skill](skills/x9-project-docs/SKILL.md) | Create an exact feature sitemap from a Style receipt or a Code-trial result. |
| [Devad Memory](skills/devad-memory/SKILL.md) | Keep historical context discoverable, never authoritative. |
| [X9 Loop Code trial](skills/x9-loop-code/SKILL.md) | Fresh-project Controller experiment only; not production-ready. |
| [Code-trial operating reference](skills/x9-loop-code/references/fresh-project-trial.md) | Optional external one-hour Looper check and strict exit rules. |

## The simple picture

```text
                  X9 LOOP STYLE (DEFAULT)
                            |
             current Git + one bounded packet
                            |
   source-backed capsule -> focused proof -> Style receipt
                            |
      feature sitemap + memory (derived, never authority)
                            |
              direct signal to the next owner

                 X9 LOOP CODE (TRIAL ONLY)
     fresh disposable project -> Controller canary -> exit to Style
```

Style does not require a Controller. Its context, docs, and memory are
profile-local derived aids, while current Git and the direct receipt remain
truth. A Controller trial must prove isolation before it is considered for any
future use.

## What ships now and what comes later

| Need | V7 baseline | V7.3 Lite source release | V7.3 Pro, deferred |
| --- | --- | --- | --- |
| Deterministic work | Controller, immutable Work Orders, hashed ACTION/RESULT | Retained; one transactional inbox/state/outbox `run-once` | Retained unchanged |
| Routine transport | Model-mediated Linx task | Zero-model LINKER transports exact ACTION and acknowledgement | Optional adapters use the same contract |
| Worker completion | Canonical result and callback | Bound result validator, deterministic finalizer, typed schema repair | Additional replaceable WORKER adapters |
| Worker result ingest | Canonical Controller inbox only | Registered Worker-worktree result ingest with zero-delta replay | Cross-profile/federated ingest only after isolation proof |
| Migration | V6 to V7 recovery model | Side-by-side V7 to Lite migration, crash recovery, exact V7 rollback | Module-specific migrations only |
| Projects | One project state root | One repository/profile today | Independently isolated profiles and federation |
| Project understanding | Packets and current source inspection | Source-backed `CONTEXT_CAPSULE`, ownership admission, and Project Brain/docs MVP | Advisory graph/vector/Obsidian projections only |
| External sidecars | Outside runtime | OMP/Pi provider-offline S0 adapter, `provider_calls=0` | Live provider calls, OpenCode, Command Code, and richer adapters as separate Work Orders |
| Backup | Existing full-profile rescue | Existing rescue retained; no new S3 implementation | Selected-project encrypted S3 generations and restore drills |
| Graph/RAG/Obsidian | Advisory discovery | Not a Lite dependency | Rebuildable views only; never canonical truth |
| Orca and coding apps | Outside runtime | Not required by Lite; OMP/Pi is the first sidecar seam | Optional bounded transport/WORKER adapters |

## Where Code And State Live

```text
x9-loop source repository/
  skills/                            sixteen packaged skills
  scripts/                           install, migrate, and validate tools
  templates/x9-project/.devad/       new-project overlay
  tests/ and docs/                    proof and guidance

CODEX_HOME/
  skills/<packaged-skill>/            installed skill copies
  x9-install-backups/<generation>/   package rollback copy

one managed project/
  .devad/manager/loop-lite/          sole active Loop state root
  .devad/features/<feature>/plans/   private plans and Work Orders
  .devad/features/<feature>/artifacts/ private generated evidence
  .devad/features/<feature>/screenshots/ sanitized screenshots
  .devad/features/<feature>/other/   other private development material
  .devad/memory/                     advisory memory
  .devad/manager/workers/            generated Worker views and routers
  .devad/workers/                    immutable Worker results and proof
  docs/<subject>/                    public project documentation in Git
  .temp/<task-or-change>/            ignored disposable task material
```

Engine code does not live in `.devad/loop/`. Historical
`.devad/manager/loop/` remains evidence only. Do not create a second state
root, edit the installed skill as source, or treat project state as a code
fork.

Within `.devad/manager/loop-lite/`, `PROJECT_PROFILE.json` binds identity,
`SNAPSHOT.json` plus referenced shards preserve recovery truth,
`runtime/ACTION.json` exposes the current Controller-selected action, and
`loop.db` is the disposable working cache. The exact database/WAL/SHM set is
still preserved while a migration is in flight.

See [Lite Operations](docs/V7.3_LITE_OPERATIONS.md) and
[Project Layout And Worktree Lifecycle](docs/PROJECT_LAYOUT_AND_WORKTREE_LIFECYCLE.md)
for the complete folder, role, migration, rollback, and worktree contract.

## How it prevents duplicate or stale implementation

Before coding, Codex should not guess whether a setting, plan, entitlement,
migration, UI control, or runtime consumer already exists. Lite retains V7's
deterministic packet completeness and adds a source-backed context gate:

```text
memory/graph suggests where to look
             -> read current repository bytes
             -> verify Git SHA, paths, hashes, and evidence spans
             -> map requirement to UI/API/authority/storage/runtime/tests
             -> reject missing, stale, duplicate, or conflicting authority
             -> create the immutable Work Order
             -> code
```

Memory accelerates discovery; it does not replace verification. Current Git,
tracked `.devad` evidence, canonical Work Orders/results, and current runtime
proof remain authoritative.

## What is new in V7.3.1 Lite

| Area | What changed | Hard boundary |
| --- | --- | --- |
| Result ingest | `loopctl.py ingest-worker-result` accepts a registered Worker-worktree `INBOX_EVENT.json` and replays consumed results as `ALREADY_CONSUMED`. | Strict `run-once --file` still rejects arbitrary Worker paths. |
| Callback/self-heal | One bound `RESULT_READY`, one deterministic redelivery/reconcile, then one deduplicated incident. | No scheduler, poller, duplicate manager, or generic continuation authority. |
| Project Brain/docs | `project_brain.py` stores profile-isolated, FTS-backed project memory and validates source-backed ownership before planning/coding. `x9-project-docs` generates docs only from accepted result evidence. | Graphs, chats, Sheets, Obsidian, and RAG remain advisory locators, never authority. |
| OMP/Pi sidecar S0 | `omp_worker_adapter.py` validates sessions, model policy, worktree/settings drift, timeout/cancellation, redaction, idempotency, exact tool flags, and a derived isolated-discovery environment. A real safe-worktree OMP 17.0.9 canary proved zero-tool launch, saved-session resume, and an exact model change without the reproduced HTTP 400. | The packaged S0 adapter still enforces `provider_calls=0`; provider-enabled activation, OpenCode, and Command Code require separate Work Orders and canaries. |
| Task naming and model boundaries | Visible future task names are short (`Thinker`, `Looper`, `Linker`, `Worker` plus one short suffix). Follow-up messages omit model/thinking. | Host model enforcement is recorded only when attested; otherwise `MODEL_PROFILE_NOT_TOOL_ENFORCED`. |
| Smooth execution rules | Cheap deterministic gates first, silent waits, continue while an authorized dependency-ready action exists, deterministic `NO_GO` before THINKER. | Skills guide agents; they do not retroactively change running tasks or bypass Controller authority. |

## V7.3 Pro Vision: Backup And Project Intelligence

Everything in this section is deferred Pro design, not installed Lite behavior.
It remains documented now so later modules can integrate without weakening the
kernel.

The V7.3 target backs up only the project profile the owner selected, not every
unrelated Codex project. A future committed generation may contain selected
sessions and attachments, tracked `.devad` truth, Git/worktree identity, reviewed project
memory, relevant skills, a canonical manifest, and restore proof.

```text
daily incremental candidates -> encrypted S3 generation -> commit marker
weekly integrity sample       -> download/decrypt/hash proof
periodic restore drill        -> staging -> merge preview -> app-visible proof
```

The target requires client-side encryption before upload. S3 versioning,
Object Lock, and server-side encryption add defense in depth. Credentials stay
in the OS/provider credential store and never enter Git, SQLite, Work Orders,
logs, or the pack. An upload without its final commit marker must be incomplete and
cannot restore. The existing full-profile rescue remains a separate disaster
recovery mode.

Lite now owns a small profile-local `project-memory.sqlite` MVP with source
identities, facts, relations, decisions, contradictions, confidence, expiry,
and SQLite FTS search. Future Pro may expand its projections and hydration, but
raw evidence becomes reviewed truth only through:

```text
deterministic candidate -> optional bounded model draft -> preview
  -> Controller/owner policy decision -> canonical write + receipt -> rollback
```

SQLite FTS, local vectors, knowledge graphs, Graphify, GraphRAG, and Obsidian
views are disposable indexes. They may point Codex to likely source files, but
they cannot dispatch work, approve a claim, complete a task, or prove behavior.

## Result Evidence And Worktrees In Lite

Lite binds the exact Worker-result schema and validator into each new Work
Order. The deterministic finalizer rejects obsolete results before publication.
A rejected receipt remains immutable in a typed registry, and a corrected new
event can complete the same dispatch without consuming another implementation
attempt. Replay, wrong identity, tamper, and stale action failures remain
zero-delta.

Worktree cleanliness remains strict. Existing worktrees are never reset,
cleaned, moved, deleted, or archived automatically. Content-addressed cold
storage and a visual active/historical catalog remain deferred Pro modules.

## V7.3 Pro Vision: Multi-project And Optional Agents

Lite creates an immutable profile identity for its one repository. Future Pro
profiles must keep Controller state, LINKER bindings, claims, Work Orders,
receipts, memory, and backup namespaces independent. Paths and repository
lineage remain evidence rather than identity. Cross-project knowledge requires
an explicit content-hashed, read-only federation packet and never transfers
authority.

The target permits Orca, OpenCode, Pi, Claude Code, Cursor, and other tools only as replaceable,
bounded Workers or computer-use helpers behind the same claims, STOP limits,
receipts, and proof gates. Codex remains truth steward. External tools cannot
become a second Controller, scheduler, EventStore, memory authority, or backup
authority.

## Release and installation claims

This repository records source readiness. A project is active only when the
installed skill bytes and project-local profile are verified against the desired
source SHA and the Controller doctor, migration/rollback, install, and runtime
proofs pass.

| Claim | Meaning |
| --- | --- |
| Source release | The `v7.3-lite` branch contains the source, tests, manifest, and attestation commits. |
| Installed skill | The live `CODEX_HOME/skills` bytes match the intended source package or a hash-bound installed package. |
| Project initialized | The target repository has a project-local profile and Controller state initialized from the verified package. |
| Loop activated | Doctor, runtime ACTION, callbacks, rollback, and canary proof pass for that specific project profile. |

Live project work remains the priority. V7.3 work cannot pause, reset, clean,
push, deploy, or mutate unrelated project work.

## How Lite works in five steps

1. Verify the selected repository, Git status, project profile, current
   snapshot/action, claims, resources, and exact Work Order.
2. Give one canonical inbox event to `loopctl.py run-once`; Controller commits
   at most one inbox/state/outbox transition.
3. LINKER reads only the current ACTION, transports exact bytes, emits the exact
   acknowledgement, and stops without a model call.
4. WORKER executes only its immutable Work Order. `worker_finalizer.py`
   validates its result and emits the canonical WORKER_RESULT event.
5. Run `run-once` for that event. Controller publishes the next eligible action
   or a deterministic WAIT/NOOP; LOOPER observes and rescues only after a proven
   invariant failure.

No polling, recurring heartbeat, sleep loop, speculative model call, or hidden
manager is part of this path.

## Experimental Code-Trial Inventory

| State | Scope |
| --- | --- |
| Code-trial source | Project-profile identity, transactional `run-once`, Controller result contracts, bounded sidecar seams, and migration/recovery research. These are trial code, not production workflow. |
| Install/activation proof | Must be proven only for an owner-approved fresh disposable trial; do not infer activation from a source branch alone. |
| Deferred Pro | S3, Obsidian/Graph/RAG views, multi-project multiplexing/federation, live provider sidecars, advanced Orca/agent adapters, dashboard, cold artifact archive, public installer |

A feature is released only when its current evidence says PASS. Working code or an older attestation is not enough.

## Roles

| Role | Profile | One job |
| --- | --- | --- |
| Controller | Deterministic Python | Select work and write immutable Work Orders |
| LOOPER | Profile-bound lifecycle steward | Install, onboard, observe, diagnose, and propose versioned upgrades |
| LINKER | Registered transport task | Read ACTION only, transport, record acknowledgement |
| THINKER | Configurable reviewed profile | Conditional file-only judgment; high assurance for stable staged-C1 and final go/no-go |
| WORKER | Registered implementation task | Implement, test, secure, attest, push, install, prove |
| Reader/CHUNK/SIDE | Bounded | Extract, split, or challenge; no authority |

The default coordination skill is `x9-loop-style`. `devad-x9-loop` and
`devad-x9-manager` redirect old prompts without starting Controller state.
`x9-loop-code` is the explicit experimental engine name, available only for a
fresh isolated canary or forensic diagnosis.

## LOOPER onboarding and autonomy

The future Lite installation begins in a profile-bound chat named
`X9 LOOPER V7.3`. LOOPER explains the system, discovers one project, and shows
a dry-run profile plan. Only after explicit approval does a deterministic
installer register Controller state, LINKER, THINKER, existing WORKERs, proof,
and the rollback route. S3 and project-memory namespaces are not Lite setup
steps. LOOPER never becomes a second Controller or selects routine work.

After activation LOOPER enters `OBSERVE_ONLY`. For a bounded event window
after a WORKER result, it sends no rescue prompt, edits no state, and makes no
hidden model call. Autonomy PASS requires:

```text
WORKER result -> Controller reconciliation -> hashed ACTION
  -> LINKER acknowledgement and transport -> existing WORKER continuation
```

If that sequence completes, LOOPER records proof and stays silent. If its
deadline or an invariant fails, it reports the exact deterministic failure and
prepares a tested, versioned correction in isolation. It never hotfixes live
state, bypasses ACTION/Work Order rules, or hides a LINKER/Controller defect by
doing their job for them.

## Fast Loop

    packet/Git verification
      -> deterministic import, hash, coverage, doctor and context gates
      -> Controller creates immutable Work Order
      -> LINKER reads ACTION and records transport acknowledgement
      -> WORKER implements, tests and runs security
      -> conditional THINKER only when predeclared or evidence conflicts
      -> unchanged reviewed C1
      -> attestation-only C2
      -> gated push, installation and proof

No recurring heartbeat or frequent polling. Hard STOP limits are checked before
every model call. Unexplained prompt-prefix or tool-schema drift emits
CACHE_PREFIX_CHANGED before another call.

## Rollout

| Clean dispatches | Coding Workers | Rule |
| --- | ---: | --- |
| 0-2 | 1 | Shadow and first live passes |
| 3-9 | 2 | Exact non-overlapping claims |
| 10+ | 3 | Zero safety, identity, scope, or context incidents |

Three coding Workers are the maximum. Database, browser, runtime, integration,
deployment, and live proof remain serialized.

## Performance Gates

- Deterministic reconciliation: under five seconds.
- Routine LINKER callback: median under 60 seconds, p95 under two minutes.
- Zero LINKER model calls and at most one state transaction per event.
- No manual Controller-state patches.
- Track wall time, prompt bytes, reads, writes, retries, compactions, and
  first-pass success.
- Real token telemetry only. Missing telemetry is `Unknown`; fallback lifetime
  totals are forbidden.

<details>
<summary>Existing X9 Worker features</summary>

- Current Git/runtime truth and mission lock.
- Local-work ledger, release states, worktree preservation, exact staging.
- Full security before C1; C2 attests C1 without recursive documentation.
- Separate source push, deploy readiness, deployment, and live-proof gates.
- Destructive-action guard, feature catalog, compact lane state, durable proof.

</details>

<details>
<summary>Existing X9 Manager features</summary>

- Immutable owner text and attachment hashes.
- Locked, file-only THINKER with verified read receipts.
- Answered decisions, tool lessons, central facts, and collaborative handover.
- Role identity by task ID, honest delivery receipts, and local-work checks.
- Secret-safe Reader plus a bounded external challenge profile before hard blockers.

</details>

<details>
<summary>New Loop v5 features retained</summary>

- Task and dispatch identity, packet SHA-256, dependency graph, decision gates.
- Role/title mismatch warning and worker-owned completion receipt.
- Direct event callback instead of recurring pickup.
- Worktree and resource ownership plus stale-completion rejection.

</details>

<details>
<summary>New X9 Loop V7 features</summary>

- Controller-only immutable Work Orders referencing Program and Feature Packets.
- Mechanical full inventory with canonical JSON, JSONL shards, coverage, and
  exact root hashes outside model context.
- V1-to-V2 side-by-side migration with the complete untouched V6 recovery set
  and exact rollback.
- STOP contracts, sequenced call receipts, cache/tool-schema drift detection,
  local disposable checkpoints, and exact event mapping.
- Empty-by-default approved recurring-job manifest and read-only doctor
  inventory that blocks activation on unknown or unauthorized jobs.
- ACTION below 4 KB as LINKER's only read surface; RESULT includes Work Order
  identity, structured proof, C1/C2, and a compact change map.
- Deterministic and security gates before one stable staged-C1 THINKER review.

</details>

<details>
<summary>Safety and deployment gates</summary>

The X9 shared contract remains authority. Security precedes source commit C1.
C2 contains only C1 attestation. No GitHub push occurs until the exact staged
scope, full security evidence, secret scan, source manifest, tests, migration,
rollback, and remote parent chain validate. Source push, deploy readiness, live
deploy, and live proof remain separate. Final destructive actions remain
owner-run.

</details>

<details>
<summary>Supporting skills</summary>

- `x9-loop-style`: stable default V6-style packet, source-backed context, receipt, and autonomous role coordination.
- `x9-loop-code`: experimental fresh-project Controller trial; never normal or production authority.
- `devad-x9-loop`: compatibility redirect to Style; it retains the Code-trial Controller implementation.
- `devad-x9`: repository routing, Git, security, proof, C1/C2, and release discipline.
- `x9-project-docs`: Style-receipt and Code-trial documentation and feature sitemap generation.
- `codex-x9-backup`: private profile backup, secret scan, restore proof.
- `codex-token-budget`: model, task, callback, and orchestration cost diagnosis.
- `devad-memory`: historical retrieval, never active routing truth.
- `devad-x9-manager`: compatibility redirect for older prompts.
- `smooth-coding`: default autonomous WORKER and LOOPER implementation flow.
- `sdlc`: risk-scaled THINKER lifecycle review; Lite is the default.
- `xplan`: compact, read-by-need durable plans and handoffs.
- `tldr`: short owner-facing, evidence-bounded receipts.
- `devad-docs`: routes public `docs/` and private `.devad/features/` records.
- `devad-adoptions`: prevents unproven source-to-Core adoption claims.
- `dokploy`: secret-safe Dokploy diagnosis and exact-SHA deployment boundary.

The sixteen-skill installer validates and stages every skill before changing
the live set, backs up all existing copies, then replaces skills sequentially.
It restores the previous set after a handled package or project-initialization
failure; its printed backup path is the recovery point after process or host
interruption.

</details>

<details>
<summary>Retired and rejected mechanisms</summary>

- No X7 broad polling, 15/19-minute heartbeat, sleep loop, or blind resend.
- No role inference from titles or completion from old handoffs.
- No embedded Orca runtime, message bus, global reset, or database truth;
  optional adapters remain removable and non-authoritative.
- No automatic Worker kill, worktree cleanup, or four-Worker default.

</details>

<details>
<summary>Migration and rollback</summary>

For an existing V7 project, run `loopctl.py migrate-v3` first on a sanitized
shadow. Lite builds `.next` state, validates it, journals replacement, and
preserves an exact V7 recovery generation. `recover-migration` resolves an
interrupted replacement; `rollback-v7 --recovery <id>` restores the bound V7
state. Package rollback remains a separate timestamped installed-skill backup.
No route moves, cleans, deletes, or resets a worktree. See [Lite
Operations](docs/V7.3_LITE_OPERATIONS.md), [migration](docs/MIGRATION.md), and
[rollback](docs/ROLLBACK.md).

</details>

`features.registry.json` classifies every inherited and new feature. Validation
fails if an old feature disappears without a migration status and test.

## Documentation

- [V7.3 Lite Operations](docs/V7.3_LITE_OPERATIONS.md)
- [Extending And Upgrading](docs/EXTENDING_AND_UPGRADING.md)
- [Project Layout And Worktree Lifecycle](docs/PROJECT_LAYOUT_AND_WORKTREE_LIFECYCLE.md)
- [Project Continuity and Intelligence](docs/V7.3_PROJECT_CONTINUITY_AND_INTELLIGENCE.md)
- [LOOPER Onboarding and Autonomy](docs/V7.3_LOOPER_ONBOARDING_AND_AUTONOMY.md)
- [Live Lessons Addendum](docs/V7.3_LIVE_LESSONS_ADDENDUM.md)
- [Style Project Intelligence contract](skills/x9-loop-style/references/project-intelligence-v1.md)
- [X9 Loop Code trial](skills/x9-loop-code/SKILL.md)
- [Public Style + Code release notes](docs/PUBLIC_STYLE_CODE_RELEASE_NOTES.md)
- [OMP/Pi External Worker S0](skills/devad-x9-loop/references/omp-external-worker.md)
- [Project Docs Skill](skills/x9-project-docs/SKILL.md)
- [Third-party notices](THIRD_PARTY_NOTICES.md)

## License

Licensed under the [MIT License](LICENSE). See
[third-party notices](THIRD_PARTY_NOTICES.md).
