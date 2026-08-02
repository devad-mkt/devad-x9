# X9 Project Intelligence V1

This is the V7.3 deterministic pre-code context contract. It prevents a
Worker from inventing a new hardcoded rule when a setting, server-owned plan,
mapping, migration, or runtime consumer already exists.

Project intelligence helps discovery. It never replaces current Git bytes,
the Controller, a Work Order, or deterministic acceptance.

## Required Coverage

Each accepted requirement must bind current source evidence for every
applicable relationship:

1. UI control
2. request/API field
3. server authority
4. persistence/default/migration
5. entitlement
6. runtime consumer
7. regression test

Bidirectional parity is required. A UI option that is not serialized,
persisted, or consumed fails. A backend option that should be user-controlled
but has no matching UI path also fails.

## Canonical Capsule

`CONTEXT_CAPSULE.json` uses the existing canonical JSON and path rules. Its
root is at most 16 KB. Larger fact and relationship collections use
content-addressed shards of at most 64 KB, referenced by path, SHA-256, byte
size, and item count.

Minimum fields are:

```json
{
  "schema": "x9-loop-context-capsule-v1",
  "capsule_id": "ctx-example",
  "repository_id": "sample-project",
  "source_git_sha": "<git-sha>",
  "source_root_sha256": "<sha256>",
  "requirements": [],
  "source_refs": [],
  "facts": [],
  "relations": [],
  "must_reuse_fact_ids": [],
  "forbidden_authority_locations": [],
  "advisory_refs": []
}
```

Every `source_ref` contains a repository-relative canonical path,
`file_sha256`, byte start/end, and `span_sha256`. Every behavioral fact has at
least one current source reference. Facts sharing one semantic key require a
source-backed precedence rule; otherwise they conflict.

`FEATURE_PACKET.json` references the canonical capsule path and hash instead
of embedding it. The Work Order inherits that immutable identity.

## Advisory Memory Boundary

Codex/Orca sessions, owner chat, project memory, OpenClaw, MiMo, Nanobot,
MGP adapters, Graphify, Obsidian, GraphRAG, embeddings, and graph/vector
indexes are advisory discovery sources. An advisory result cannot satisfy a required relation.
Its proposed source nodes must be promoted only after the
Controller-side validator re-read exact current repository bytes and created
verified source references.

Project memory never creates, dispatches, acknowledges, or completes a task.
It cannot select features, reserve claims, approve security, authorize push or
deploy, or resolve an owner decision.

## Deterministic Validation

Validate before Work Order creation and again before dispatch:

1. Verify the bound Git SHA and source-root hash.
2. Canonicalize paths and reject absolute paths, traversal, case-fold
   collisions, symlink escapes, and Windows reparse escapes.
3. Re-read exact current repository bytes.
4. Match every `file_sha256`, byte range, and `span_sha256`.
5. Require source-backed evidence for every applicable relationship.
6. Reject duplicate or conflicting authorities without explicit precedence.
7. Hash the exact capsule bytes and bind the hash into the Feature Packet and
   Work Order.

Do not silently rebuild a stale capsule during dispatch. Return the exact
failure, preserve the old capsule as evidence, and require a new Controller
generation.

## Fail Codes

- `CONTEXT_CAPSULE_INVALID:<field>`
- `CONTEXT_SOURCE_ESCAPE:<ref_id>`
- `CONTEXT_SOURCE_DRIFT:<ref_id>`
- `CONTEXT_SPAN_DRIFT:<ref_id>`
- `CONTEXT_ADVISORY_ONLY:<fact_id>`
- `CONTEXT_AUTHORITY_DUPLICATE:<semantic_key>`
- `CONTEXT_AUTHORITY_CONFLICT:<semantic_key>`
- `CONTEXT_COVERAGE_MISSING:<requirement_id>:<relation>`
- `CONTEXT_CAPSULE_DRIFT:<capsule_id>`

- `PROJECT_CONTEXT_PROFILE_DRIFT`
- `PROJECT_CONTEXT_SITEMAP_DRIFT`
- `PROJECT_OWNERSHIP_NEW_CONFLICT`
- `PROJECT_OWNERSHIP_REPLACEMENT_UNAUTHORIZED`
- `PROJECT_MEMORY_FTS5_UNAVAILABLE`
- `PROJECT_MEMORY_FTS_DRIFT`
- `PROJECT_MEMORY_FACT_IMMUTABLE`
- `PROJECT_MEMORY_ROLLBACK_RESIDUE`
- `PROJECT_MEMORY_ROLLBACK_FAILED`
- `PROJECT_MEMORY_CIRCUIT_OPEN`
These failures block only the affected task. They do not pause unrelated
Workers or turn project memory into orchestration state.

## Profile-local memory and documentation

Project memory is one standard-library SQLite database per bound profile at
`.devad/profiles/profile-<sha256(profile-id)[:32]>/memory/project-memory.sqlite`.
The derived directory and `PROJECT_MEMORY_ROOT.json` bind the unhashed profile
identity. SQLite FTS5 is required for deterministic fact, decision, episode, and document-title retrieval. Migration builds and validates a side-by-side .next database, atomically swaps it, and automatically restores the in-memory pre-swap image if post-swap validation fails; rollback validates and installs a guarded .rollback.next copy. Root manifest, schema, database integrity, and exact FTS projections are required. Memory may
record accepted, typed incident projections and reviewed source facts, but it
never stores Controller state and never authorizes a model call, task, claim,
acknowledgement, dispatch, completion, provider, or deployment.

The optional `x9-project-docs` add-on accepts only an exact canonical identity binding and emits a profile-local feature packet with
`TASK.md`, `FEATURE.json`, `MANIFEST.sha256`, and numbered Markdown documents.
`TASK.md` is a direct-link sitemap; every link must resolve to a local,
manifest-bound Markdown file. Identical accepted inputs are idempotent and
byte-identical. A planned bootstrap packet may label unexecuted claims
`UNKNOWN`; `VERIFIED` requires an accepted canonical result.

## Ownership admission

Each claimed seam binds these fields: `EXISTING_FEATURE`, `UI_SETTINGS`,
`SERVER_AUTHORITY`, `PLAN_ENTITLEMENT`, `REFERENCE_REUSE`,
`PERSISTENCE_CONSUMPTION`, `INTEGRATED_HISTORY`, `TEST_PROOF`, `GAP`, and
`CHANGE_MODE`. `CHANGE_MODE` is `REUSE`, `EXTEND`, `NEW`, or
`REPLACE_AUTHORIZED`. `NEW` fails when current evidence proves an owner;
`REPLACE_AUTHORIZED` requires an exact approved owner decision. `REUSE` and
`EXTEND` require a current owner and reusable seam. DOM-only or advisory-only
evidence never proves server, persistence, runtime, or ownership.

## Gate phases and repeated failures

The same source-bound identity is checked at
`PROJECT_CONTEXT_PLAN_READY`, `PROJECT_CONTEXT_WORK_ORDER_READY`, and
`PROJECT_CONTEXT_DISPATCH_READY`. A stale capsule is preserved and rejected;
dispatch does not rebuild it. The existing Controller call reservation and
receipt ledger remains the only model-call breaker. Three identical typed
product failures with no progress open `PROJECT_MEMORY_CIRCUIT_OPEN`; an
infrastructure failure is recorded for telemetry without consuming the product
streak.