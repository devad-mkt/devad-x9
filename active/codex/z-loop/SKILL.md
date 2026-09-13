---
name: z-loop
description: Use as the single Addy-first entry point for normal project work. Read bounded project context, select the smallest matching lifecycle skill, load only matching rules, and use z-prefixed specialist overlays only when triggered. Addy-first governs skill selection; Style is the default coordination flow once a skill is selected; Code stays an explicitly approved experimental trial.
---

# zLoop

## Normal route

1. Read the project `AGENTS.md`, `.agent/STATE.md`, and `.agent/MAP.md` once.
2. Use `$using-agent-skills` to select the smallest matching Addy lifecycle
   skill. Reuse an accepted plan or evidence record instead of restarting it.
3. Read `.devad/rules/INDEX.md` and load only rules matching the current paths
   or effects.
4. Use a project-local `z-*` specialist only when its trigger matches. Load
   `$z-x9` for repository/worktree/release safety when that scope requires it.

Current Git and source evidence override stale context. Routine local coding,
tests, debugging, and reversible corrections continue without a manager,
queue, heartbeat, poller, or approval relay.

## Routing layer: selection vs flow

Addy-first and Style-default are two different layers and both apply:

- **Selection (Addy-first):** pick the *smallest* matching Addy lifecycle skill
  before dispatching work. This skill owns that choice.
- **Flow (Style-default):** once a skill is selected, `$z-loop-style` is the
  default coordination flow for normal project work — packets, direct results,
  Project Intelligence, memory, documentation. It is entered automatically after
  X9 routing; it is not compatibility-only and it does not need a request.

## Explicit-only route

`$z-loop-code` is an experimental fresh-project trial. It starts only with
explicit owner approval and its own admission checks. It is never inferred from
normal work, an old packet, or a missing proof mechanism.

An unavailable external effect pauses only that effect. Continue every safe
local slice, and escalate only a genuine owner, secret, production,
destructive, spend, architecture, or shared-resource collision boundary.

<!-- Unused initialization scaffold retained only as an inactive migration artifact.


### scripts/
Executable code (Python/Bash/etc.) that can be run directly to perform specific operations.

**Examples from other skills:**
- PDF skill: `fill_fillable_fields.py`, `extract_form_field_info.py` - utilities for PDF manipulation
- DOCX skill: `document.py`, `utilities.py` - Python modules for document processing

**Appropriate for:** Python scripts, shell scripts, or any executable code that performs automation, data processing, or specific operations.

**Note:** Scripts may be executed without loading into context, but can still be read by Codex for patching or environment adjustments.

### references/
Documentation and reference material intended to be loaded into context to inform Codex's process and thinking.

**Examples from other skills:**
- Product management: `communication.md`, `context_building.md` - detailed workflow guides
- BigQuery: API reference documentation and query examples
- Finance: Schema documentation, company policies

**Appropriate for:** In-depth documentation, API references, database schemas, comprehensive guides, or any detailed information that Codex should reference while working.

### assets/
Files not intended to be loaded into context, but rather used within the output Codex produces.

**Examples from other skills:**
- Brand styling: PowerPoint template files (.pptx), logo files
- Frontend builder: HTML/React boilerplate project directories
- Typography: Font files (.ttf, .woff2)

**Appropriate for:** Templates, boilerplate code, document templates, images, icons, fonts, or any files meant to be copied or used in the final output.

---

-->
