# X9 Project Intelligence V1 — Style Default

Use this source-backed context contract before planning and before the first
behavioral edit in `$x9-loop-style`. It prevents a Worker from inventing a new
rule when current source already owns the capability. It does not start a
Controller or create a second memory system.

## Capsule and coverage

`CONTEXT_CAPSULE.json` is canonical JSON, at most 16 KB. Larger collections
use content-addressed shards at most 64 KB. Bind the current Git SHA, root
hash, repository-relative source paths, file hashes, byte spans, and span
hashes. Re-read them at both gates; do not silently refresh stale evidence.

For every touched capability, bind the applicable current-source evidence for:

`EXISTING_FEATURE`, `UI_SETTINGS`, `SERVER_AUTHORITY`,
`PLAN_ENTITLEMENT`, `REFERENCE_REUSE`, `PERSISTENCE_CONSUMPTION`,
`INTEGRATED_HISTORY`, `TEST_PROOF`, `GAP`, and `CHANGE_MODE`.

`CHANGE_MODE` is exactly `REUSE`, `EXTEND`, `NEW`, or
`REPLACE_AUTHORIZED`. `NEW` needs source-backed absence in the claimed scope;
`REPLACE_AUTHORIZED` needs an explicit owner decision. DOM-only, chat, Sheet,
memory, graph, RAG, or advisory evidence never proves server, persistence,
runtime, or ownership. A missing owner pauses only that seam.

## Stable derived context

Use one profile-local SQLite FTS5 store at
`.devad/profiles/profile-<sha256(profile-id)[:32]>/memory/project-memory.sqlite`.
It may retain reviewed source facts, decisions, incidents, and document titles.
It cannot select work, reserve claims, dispatch, approve, call models,
push/deploy, or replace a result receipt.

After a successful bounded Style result, `$x9-project-docs` validates the
`x9-loop-style-result-v1` receipt and writes a direct-link feature sitemap
under `.devad/features/<feature-id>/`. Generated docs are derived context:
they help a future Thinker, Looper, Linker, or Worker find the exact plan and
proof without relying on chat history.
