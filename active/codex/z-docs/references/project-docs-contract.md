# X9 Project Docs V1 Contract

The package schema is `x9-project-docs-v1`. Stable generation consumes one
accepted `x9-loop-style-result-v1`; experimental Controller generation can
consume one accepted canonical `x9-loop-result-v2`. Narration, an unconsumed
result, a Worker-local checkpoint, or an advisory memory hit is not enough for
`VERIFIED` evidence.

## Bound inputs

For Style, the generator re-reads the exact plan, Git base/current SHA, source
spans, proofs, profile, changed files, and rollback route. For a Controller
trial, it re-reads the exact feature, Work Order, dispatch, Worker,
project-profile, base Git, result, proofs, and source manifest identities. It
records the Style receipt or Controller result SHA, `profile_id`, and generated
file inventory. A changed input is a new generation, not an in-place rewrite.

## Feature packet

A packet lives under `.devad/features/<feature-id>/`:

- `TASK.md` is the compact sitemap and links directly to every numbered file;
- `FEATURE.json` records the feature, profile, accepted result hash, and file set;
- `MANIFEST.sha256` records the exact SHA-256 and repository-relative name for
  every packet file;
- `00-overview.md` through `06-decisions.md` contain bounded evidence labels.

Links are relative to `TASK.md`, stay within the packet directory, and resolve
to regular files. The sitemap and manifest are validated together. The packet
is idempotent for identical canonical inputs and immutable for changed inputs.

## Profile-local memory

The only supported memory database is derived from the bound profile ID:
`.devad/profiles/profile-<sha256(canonical-profile-id)[:32]>/memory/project-memory.sqlite`.
The store uses SQLite FTS5 and keeps sources, facts, relations, decisions,
contradictions, episodes, and derived incidents separate from Controller
state. It never stores ACTION, Work Order, claim, dispatch, gate, completion,
credential, or provider payload authority.

## Authority and boundaries

Git, the accepted Style receipt or experimental Controller state/canonical
packet, and exact source bytes remain authoritative. Generated docs and FTS
search are derived. No result is promoted to `VERIFIED` without its exact
accepted contract, and no document can grant permission to call a model,
dispatch work, push, deploy, or replace an installed skill.
