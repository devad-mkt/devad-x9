# X9 Project Docs Contract

The public contract is `x9-project-docs-v1`. A normal Style packet starts from
one accepted `x9-loop-style-result-v1` receipt; narration, unconsumed results,
and memory hits are not enough for `VERIFIED` evidence.

Re-read the exact plan, base/current Git SHA, source references, proof hashes,
profile ID, changed files, and rollback route. Then write a feature sitemap at
`.devad/features/<feature-id>/` with `TASK.md`, `FEATURE.json`,
`MANIFEST.sha256`, and only the compact files needed to link evidence.

Links stay inside the packet and resolve to regular files. Inputs that differ
create a new packet. Docs and optional SQLite/FTS indexes are derived context;
they never contain or replace task routing, secrets, claims, dispatches,
credentials, provider payloads, or deployment authority.
