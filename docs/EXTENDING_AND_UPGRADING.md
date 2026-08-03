# Extending And Upgrading X9 Loop

This guide applies to V7.3 Lite and later optional modules. The objective is to
keep the small deterministic kernel usable while versions, integrations, and
project history grow.

## Source And Authority Boundary

Edit source only in the X9 Loop repository:

- engine behavior: `skills/devad-x9-loop/scripts/`;
- role instructions and contracts: `skills/devad-x9-loop/`;
- project bootstrap files: `templates/x9-project/.devad/`;
- package tooling: `scripts/`;
- regressions: `tests/`; and
- durable design and operations guidance: `docs/` and `.devad/features/`.

Do not develop by editing `CODEX_HOME/skills/devad-x9-loop/` or a managed
project's `.devad/manager/loop-lite/`. The installed skill is a verified build
output. Project Loop files are state/evidence, not a source-code fork.

## Classify The Change First

| Change | Required route |
| --- | --- |
| Controller state or behavior | Versioned contract, minimal failing regression, side-by-side migration, exact rollback, crash/replay tests |
| LINKER or WORKER adapter | Optional adapter behind the canonical ACTION/event boundary and common conformance suite |
| THINKER policy | Predeclared decision type and deterministic admission; never a routine call |
| Documentation or generated view | No routing authority; current code/state verification remains mandatory |
| S3, Obsidian, Orca, memory, dashboard, or cold storage | Deferred module packet, removable implementation, isolated failure and rollback |

Do not add architecture because it may be useful later. Start with a written
acceptance contract or a demonstrated P0/P1 failure and the smallest reproducer.

## Schema And Migration Process

For every state or packet change:

1. Capture current package, Git, schema, snapshot/action, and recovery hashes.
2. Add a failing test for the exact old/new boundary before implementation.
3. Version the schema. Keep canonical JSON/JSONL byte rules and size caps.
4. Define old-reader/new-reader behavior and any legacy display alias.
5. Build the new database, snapshot, profile, and generated artifacts as
   side-by-side `.next` files.
6. Validate all foreign keys, hashes, referenced shards, active identities,
   claims, resources, Work Orders, outbox actions, and receipts.
7. Record a durable migration journal before replacing a fixed path.
8. Replace atomically and prove deterministic recovery at every crash point.
9. Prove exact rollback to the prior package and complete state recovery set.
10. Run affected tests, then one full suite when focused tests are green.

SQLite WAL/SHM are not normal durable truth, but preserve their exact bytes when
the source version requires them for rollback. Never call a partial copy a
complete backup.

## Re-code And Adoption Rules

When adopting another project, agent, or older X9 feature:

- adopt behavior and proven invariants, not directory shape or marketing
  claims;
- inspect current source before assuming a setting, UI control, entitlement,
  migration, or runtime consumer is missing;
- map owner intent to UI, request/API, server authority, persistence, runtime,
  and tests before coding;
- preserve passing behavior and legacy data unless a versioned migration proves
  replacement safer;
- translate external messages into immutable owner input, never directly into
  ACTION or Work Order authority;
- keep legacy `Linx`/`Thinx` names as import aliases while displaying
  LINKER/THINKER; and
- retain rejected approaches and deferred plans under `.devad/features/`
  instead of deleting the reasoning that future versions may need.

A large plan should be split into machine-readable child features and bounded
Work Orders. Minification may remove repetition, but must not discard claims,
dependencies, acceptance gates, rollback, or source references.

## Optional Adapter Contract

Every external execution adapter must:

1. receive one exact project-profile-bound ACTION or Work Order;
2. advertise capability without selecting or authorizing work;
3. enforce claims, STOP bounds, worktree identity, and canonical result schema;
4. acknowledge exact bytes once and handle delayed/duplicate/out-of-order input;
5. report real telemetry or `Unknown`;
6. make no provider call on validation failure; and
7. be removable without breaking Controller, local LINKER, migration, doctor,
   or rollback.

Orca, OpenCode, Cursor, and other coding tools are WORKER/transport adapters,
not a second Controller. A provider profile that the host cannot attest must be
recorded as `MODEL_PROFILE_NOT_TOOL_ENFORCED`.

## Deferred Pro Admission

Pro modules enter one at a time after Lite autonomy acceptance:

- **S3:** project-scoped credentials, client-side encryption, canonical
  manifests, interrupted-upload handling, commit marker, download/decrypt/hash
  proof, merge preview, and real restore drill.
- **Obsidian/Graph/RAG:** generated from source-cited facts, deletable and
  rebuildable, freshness/conflict aware, and incapable of dispatch or gate
  approval.
- **Project/worktree archive:** active/historical catalog, exact Git identity,
  dirty-byte patch manifest, receipt/proof closure, cold-storage manifest, and
  restore proof. It never removes a worktree automatically.
- **Orca/agent adapters:** version-pinned transport, trust/permission preflight,
  shared conformance suite, and failure isolated from the Lite kernel.
- **Multi-project profiles:** independent state, claims, role bindings, memory,
  and backup namespaces with cross-project access denied by default.

Module failure disables that module. It must not stop or reinterpret routine
Controller/LINKER operation.

## Upgrade And Release Sequence

1. Preserve the prior release branch/tag, installed skill hashes, project state,
   current Git status, and exact recovery set.
2. Build and test in an isolated worktree; never use a dirty product checkout as
   the integration checkout.
3. Install into a temporary `CODEX_HOME` and migrate a sanitized byte-preserving
   shadow of realistic state.
4. Prove forward migration, crash recovery, replay/idempotency, and exact prior
   rollback.
5. Run focused tests, the full suite, package/template validators, syntax
   checks, secret scan, source-manifest verification, staged-scope inspection,
   and `git diff --check`.
6. Review the stable staged source bytes. Any source-byte change invalidates the
   review and gates.
7. Commit source, then commit only its validation/rollback attestation when the
   release contract uses C1/C2.
8. Verify the remote parent chain before push. Security evidence must exist
   before GitHub receives the source.
9. Take a fresh live backup, install atomically, run doctor, and execute the
   bounded one-WORKER then compatible three-WORKER acceptance.
10. Roll back immediately on identity, migration, receipt, action, security,
    remote, or autonomy mismatch; preserve failed evidence.

No upgrade may introduce polling, a hidden heartbeat, automatic worktree
cleanup, speculative model calls, cache warming, duplicate Controllers, or a
second canonical database.
