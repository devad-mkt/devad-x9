# <plugin-name> — Plan Index

Goal: convert the current <plugin-name> source at `<build-root>\<plugin-name>` into a
scoped, documented, testable A0 plugin build in `<plan-root>`, driven by the
chunk files under `<chunks-root>`. Every chunk is self-contained, verifiable by
dry-run tests only, and adds a visible capability to the final plugin.

## Approved decisions (by user, <date>)

1. <decision-1>
2. <decision-2>
3. <decision-3>
4. Add more numbered decisions as they are agreed. Do not act on undecided items.

## Files in this folder

| File | Content |
| --- | --- |
| `00-README.md` | This index: decisions, file map, how to execute, hard constraints. |
| `01-research-summary.md` | Current shape of the plugin, framework facts, external-API caveats. |
| `02-decisions-winners.md` | Every scored option per decision, with the winning pick in bold. |
| `03-target-architecture.md` | Target file layout, data model, signatures, import rules. |
| `04-test-strategy.md` | Mock strategy, test files, gates that must pass before any chunk. |

## Execution assets

| Root | Purpose |
| --- | --- |
| `<chunks-root>\SKILL.md` | The builder (`<builder-name>`) that reads the plan and writes the plugin. |
| `<chunks-root>\chunks\chunk-*.md` | Ordered, dependency-linked work units. Each chunk has a Goal, Files to write, Acceptance, and a DO NOT list. |

## How to execute (human quickstart)

1. Copy `<chunks-root>` (SKILL.md + `chunks\`) and this plan folder so the builder can read both.
2. Prompt `<builder-name>` to read `SKILL.md`, then execute `chunk-01..` in order.
3. Let the builder run chunks one at a time; stop whenever an Acceptance gate fails
   and fix before moving on. Re-run verify steps at the end.

## Constraints (non-negotiable)

- No real network calls anywhere; every test and demo must run against local fakes.
- No `sys.path` hacks; import only via `from usr.plugins.<plugin-name>...`.
- No secrets stored in code or committed files; they live in the plugin config.
- No edits outside the paths listed under `03-target-architecture.md`.
- No full file bodies inside chunk specs, only signatures and behavior.
- Any deviation from an approved decision requires user approval before work starts.