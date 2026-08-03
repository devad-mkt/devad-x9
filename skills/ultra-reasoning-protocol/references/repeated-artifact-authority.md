# Repeated Artifact And Authority Failures

Read this only after the same authority or identity failure recurs, or after a
prior approval is invalidated by changed bytes.

## Required Response

1. Freeze the authority order: current immutable task, current live state,
   current artifact bytes, then durable history. Chat and memory are hints.
2. Bind every decision-relevant input by canonical path, byte hash, revision,
   and expected role. Validate the live checkout or runtime against that set.
3. Treat any changed decision-relevant byte as a new candidate. The old verdict
   is audit evidence only.
4. Resolve outputs, callbacks, and proof from the current task or packet. Never
   search an actor's older checkout first.
5. Verify repository, checkout, branch, base revision, index, staged, unstaged,
   and untracked state before judgment or action.

## Read-Only Guard

Classify commands by actual side effects, not their names. A command that
creates an index lock, cache, temporary file, refreshed metadata, or database
sidecar is not read-only for a locked review. Prefer an equivalent query that
does not write. If none exists, record the limitation instead of mutating.

## Receipt

Record `AUTHORITY`, `IDENTITY`, `LIVE_BINDING`, `SCOPE`, and
`READ_ONLY_SIDE_EFFECTS`. Block on any mismatch. Do not compensate with a
plausible narrative.
