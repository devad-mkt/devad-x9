# Lite Mode

Use Lite by default for a narrow, reversible change with a known owner and no material new trust, data, migration, or deployment risk.

## Budget

- One targeted source/search pass.
- One bounded implementation slice.
- One focused reproduction or acceptance check.
- Existing cheap formatting, lint, type, diff, and security checks only when they apply or are repository-required.
- One concise completion statement with any remaining unknown.

## Workflow

1. Restate the exact behavior to change and what must remain unchanged.
2. Search the definition, callers, tests, and local pattern.
3. Use the first safe rung of the minimum-solution ladder.
4. Make the smallest coherent diff.
5. Run the focused test plus required existing gate.
6. Inspect the diff and stop.

## Do Not Add by Default

- Threat-model documents
- Architecture records
- New CI, scanners, dashboards, MCP servers, dependencies, or agent teams
- Broad test suites unrelated to the touched behavior
- Changelog, release, rollout, or monitoring work when the repository/task does not require it
- SAMM/ISO matrices or compliance scores

## Escalate to Medium When

- The real flow or source of truth is ambiguous.
- User-controlled input crosses a trust boundary.
- Persistence, tenant state, compatibility, shared services, or asynchronous behavior changes.
- The focused check exposes a sibling regression or broader ownership problem.

## Stop Condition

The requested behavior and preservation conditions are proven by focused evidence, the diff is clean, and no material unknown remains.
