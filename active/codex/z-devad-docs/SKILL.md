---
name: z-devad-docs
description: Create or update durable Devad project documents, including public guides under docs and private development plans, handoffs, decisions, contracts, reports, reviews, and evidence under .devad/features. Use when the owner/user explicitly requests a document or an accepted task requires a durable artifact.
---

# zDevadDocs

## Scope gate

Create files only when the owner/user explicitly asks for documentation or an
accepted task names a durable document as a required deliverable. Do not create
a document merely because a chat answer could be saved.

Resolve the project root with `git rev-parse --show-toplevel`. If the current
directory is not in a Git repository, use the explicit project folder from the
request, then the current working directory as the fallback.

## Required location

Classify the document before writing:

```text
<project-root>/docs/<doc-slug>/                          public project documentation tracked with Git
<current-worktree>/.devad/features/<feature>/plans/     private implementation plans and Work Orders
<current-worktree>/.devad/features/<feature>/artifacts/ implementation evidence and generated artifacts
<current-worktree>/.devad/features/<feature>/screenshots/ sanitized screenshots
<current-worktree>/.devad/features/<feature>/other/     private material that fits no narrower class
```

Examples:

```text
<project-root>/docs/provider-guide/README.md
<current-worktree>/.devad/features/provider-migration/plans/PLAN.md
```

- Use a short lowercase hyphenated slug that identifies the subject.
- Keep related revisions and supporting files in the same subject folder.
- If an existing folder is unrelated, append the current date to the new slug.
- Plans and execution artifacts belong to the task's current bound worktree.
  Do not write them directly into a shared integration anchor from another
  worktree.
- `.devad` is private Codex development material. Do not publish it as public
  documentation. Its approved backup route is a private per-change Contabo S3
  generation with a secret-safe manifest; S3 is backup, never task authority.
- Do not use `.docs`, `.devad/docs`, a skill folder, a drive root, a user
  profile temp folder, or another task's worktree.
- Do not overwrite unrelated files. Preserve existing project content.

## Document contract

Create only the files needed for the requested artifact. Do not add a README,
changelog, index, or evidence directory by default.

Make each document usable without chat history. Include, when relevant:

- purpose and bounded scope;
- current status and date;
- verified evidence and exact source paths;
- assumptions, unknowns, and blockers;
- decisions or acceptance criteria;
- ordered next actions and required owner action;
- rollback or recovery notes for changes that need them.

Use `VERIFIED`, `INFERRED`, `HISTORICAL`, or `UNKNOWN` when evidence strength
matters. Do not turn plans, attempts, or narration into proof.

## Finish

Validate that every created path is inside the selected `docs/<doc-slug>/` or
`.devad/features/<feature>/<category>/` boundary. Report the primary document
path and briefly state what was created or updated.

## Provenance (consolidated 2026-09-12)

Canonical body: `z-devad-docs` (2026-08-13 00:38:44, 2 files, sha256 `d227d187901dc5c5`).

Former names now disabled: `NINELLC/devad-docs`.

Unique content from disabled copies is preserved under `references/preserved/` and is NOT authoritative; this body wins on any conflict.
