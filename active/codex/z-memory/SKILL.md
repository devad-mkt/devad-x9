---
name: z-memory
description: "Use for Devad X9 durable memory work: searching or updating `.devad/memory`, extracting Codex session history into SESSION.md/topics/reports/md/extracted folders, maintaining CHAT-CATALOG.md and PROJECT-NAMES.md, creating read/no-read TLDR routing, preserving Devad requirements/decisions/proof without raw chats or secrets, and avoiding broad token-burning searches over old sessions."
---

# zMemory

## Authority

Default memory root:

```text
<repo>\.devad\memory
```

Resolve <repo> from the current Git worktree. If the user gives a different memory root, use the user-provided root.

Before any memory search or update, read only these startup files:

```text
<memory>\CHAT-CATALOG.md
<memory>\projects\PROJECT-NAMES.md
```

When creating or updating session memory, also read:

```text
<memory>\skill\X9-SESSION-EXTRACTION-SKILL.md
```

The shared memory root also carries a reusable method library:

```text
<memory>\prompts\README.md
<memory>\prompts\
<memory>\skill\
```

Read `prompts/README.md` when it exists, then select only the prompt and method
file that match the requested memory operation. Do not load every prompt or
skill by default. Current extraction instructions and the current canonical
layout outrank superseded prompt examples and hardcoded legacy paths.

Do not read the full `.devad`, `.devad/memory`, raw session archive, or feature folders by default.

Memory is not active routing truth. In `$z-loop-style`, use it only after a
current source-backed capsule has named the relevant paths; the Style packet
and direct result receipt remain authoritative. Do not write manager CURRENT.md,
CENTRAL_FACTS.md, STATUS.md, HANDOFFS.md, or Worker run files. Linx and Workers
own those files. Memory may distill replaced history only after the active
owner has preserved the current route.

## Routing

- For a quick answer, use `CHAT-CATALOG.md` first and read only the listed session/topic files that match the task.
- For extraction/backfill, follow `X9-SESSION-EXTRACTION-SKILL.md` exactly.
- For an exact Codex task UUID, prefer the task/thread reader and paginate that
  one task. Use raw rollout discovery only when the task reader is unavailable
  or the task itself identifies a required raw source.
- For implementation context, read only the relevant `SESSION.md`, `topics/*.md`, and copied `md/*.md` files selected by the catalog.
- For archive quality or recovery work, select the current archivist prompt
  listed by `prompts/README.md`. Treat prompts marked superseded as historical
  examples, not active instructions.
- For method changes, synthesize durable rules here and keep detailed examples
  in the shared prompt/method library. Never copy stale usernames, repository
  roots, folder layouts, or project decisions into active instructions.
- When a project has `.devad/ROUTER.md`, use it to locate the exact memory
  catalog; do not follow unrelated manager or feature routes.

## Search Rules

Start with unique anchors from the user request:

- exact chat UUIDs
- exact document titles
- exact unusual phrases, for example `gemini ast`, `POST Migration`, `laravel migration`
- exact feature folder names
- exact route names, provider names, or product names only when paired with the project/task

Do not start with broad terms such as `migration`, `post`, `laravel`, `plan`, `handoff`, `TASK.md`, or model names alone. Use broad terms only inside already-confirmed candidate sessions or repo folders.

For raw Codex sessions, inspect metadata and first user messages before reading full JSONL. Do not open large rollouts unless an exact anchor or catalog row makes them a strong candidate.

One chat UUID maps to one canonical session. Before creating it, search the
catalog and session tree for that exact UUID, then update the existing session
if found. Determine the next session number from existing canonical session
folders rather than guessing.

## Session Structure

Use canonical project folders:

```text
<memory>\projects\<exact Codex project name>\sessions\<session-folder>\
  SESSION.md
  ARTIFACTS.md
  topics\
  reports\
  md\
  extracted\
```

Never create `artifacts/` folders.

Use exact project names from:

```text
<memory>\projects\PROJECT-NAMES.md
```

## Content Rules

Each `SESSION.md` needs source paths searched, aliases, chat IDs, tags, status, read/no-read TLDR, read-this-for, do-not-read-this-for, topic links, copied markdown, search ledger, and sensitive material notes.

Each topic file must be useful enough for a new chat to resume without reading the old chat. Include objective, user requirements, options, what failed, correction, final/current decision, why, risks, relevant paths, related sessions, copied markdown, next safe steps, verification, and do-not-repeat lessons.

Each `CHAT-CATALOG.md` row must include a meaningful `Read for:` and `Skip for:` sentence.

Use explicit evidence states for claims that may drift: `VERIFIED`,
`HISTORICAL`, `INFERRED`, `UNKNOWN`, `BLOCKED`, or the narrower status vocabulary
already used by the source task. Preserve current-versus-historical boundaries,
accepted SHAs, default-off gates, and unresolved blockers. Memory must not turn
an unproved runtime claim into current truth.

Every major topic must pass this continuation-quality gate:

- objective and exact context boundary;
- user requirements and meaningful options considered;
- accepted decision and why it was accepted;
- rejected paths, failed attempts, and do-not-repeat lessons;
- local copied artifact paths first and original source paths second;
- concrete next safe step, remaining gates, and verification status.

Search exact artifact paths named by the task before marking an artifact
missing. Copy safe Markdown, HTML, text, extracted reports, or redacted images
into the owning session only when the copy materially improves future recovery.
Record the original path, local copy path, hash when practical, source status,
and whether the content was read. Do not create a global artifact source of
truth or leave useful session artifacts only in a global folder.

Do not store raw chats, full JSONL exports, secrets, `.env`, OAuth codes, cookies, provider logs, payment data, private emails, or credentials.

## Completion

After memory edits:

1. Update `CHAT-CATALOG.md`.
2. Update compact lookup files such as `INDEX.md` only when needed.
3. Update the affected project `PROJECT-CATALOG.md`.
4. Run or adapt the verification script from `X9-SESSION-EXTRACTION-SKILL.md`.
5. Verify exact chat-ID uniqueness, required files, local links, referenced
   artifact existence, catalog consistency, secret-pattern absence, and hashes
   for copied immutable artifacts when practical.
6. Report only the extracted TLDR, session folders, topics, copied markdown,
   known gaps, source-read boundary, and verification result.

## X9 Loop Lite v6 Boundary

`.devad/manager/loop-lite/SNAPSHOT.json` is active routing recovery truth and
outranks memory. Files under `.devad/manager/loop/` are historical evidence in
v6; memory may index them but cannot restore their old routing authority.

Memory may explain history but cannot assign a role, acknowledge a dispatch,
complete a task, release a resource, or open a deploy gate.

## Provenance (consolidated 2026-09-12)

Canonical body: `z-memory` (2026-08-13 00:38:44, 2 files, sha256 `f06dacc41fcc5ec6`).

Former names now disabled: `CODEX/devad-memory`, `LOOPX_PKG/devad-memory`, `NINELLC/devad-memory`.

Unique content from disabled copies is preserved under `references/preserved/` and is NOT authoritative; this body wins on any conflict.
