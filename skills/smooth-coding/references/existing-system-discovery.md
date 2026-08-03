# Existing-System Discovery

Use this only when a behavioral slice crosses frontend/backend or app-domain
ownership, or a targeted source pass cannot identify the current owner. It is a
bounded discovery aid, not a second planning project.

## Why Agents Rebuild Existing Systems

| Failure | Root cause | Correction |
|---|---|---|
| A requested capability is treated as absent | The plan starts from request wording instead of current source | Prove `EXISTING_FEATURE` before choosing `NEW` |
| A merged subsystem is rediscovered late | The new branch is not rebound to integrated Git history and prior owner work | Inspect merge-base, accepted commits, and current call sites before design |
| A Sheet or handoff is read but ignored | Narrative evidence is not connected to a plan admission decision | Rebind its claim to current source and record the owner/reuse seam |
| DOM inspection misses ownership | DOM shows controls and labels, not services, jobs, tables, provider policy, or persistence | Trace UI/request to server authority and runtime consumer |
| Backend inspection misses product behavior | Source may not prove which settings are visible, enabled, or understandable | Check current UI/settings and a focused browser path when behavior is visible |
| New tests validate a duplicate design | Tests are written only after the replacement architecture is assumed | Reuse an existing acceptance test or add a red seam test before new structure |
| File-by-file reading obscures the flow | Similar names across domains hide the canonical owner | Trace one vertical journey instead of reading the whole repository |
| A graph or memory index is treated as truth | Generated indexes can be stale, incomplete, or detached from current Git | Use them only to find candidates; verify decisive facts in current bytes |

## Run Twice

### Pre-plan

Do not approve a plan that says build, create, replace, or refactor a capability
until the plan records:

- `EXISTING_FEATURE`
- `UI_SETTINGS`
- `SERVER_AUTHORITY`
- `PLAN_ENTITLEMENT`
- `REFERENCE_REUSE`
- `PERSISTENCE_CONSUMPTION`
- `INTEGRATED_HISTORY`
- `TEST_PROOF`
- `GAP`
- `CHANGE_MODE`

Use `VERIFIED:<evidence>`, `NOT_APPLICABLE:<reason>`, or `UNKNOWN`. Set
`CHANGE_MODE` to `REUSE`, `EXTEND`, `NEW`, or `REPLACE_AUTHORIZED`.

### Pre-code

Revalidate the decisive paths and Git identity immediately before the first
behavioral edit. If they drifted, update the existing plan row; do not create a
new report. `UNKNOWN` blocks only the edit that depends on it.

## Evidence Ladder

Stop as soon as the owner, seam, and true gap are proven:

1. Current Git status, branch, merge-base, accepted integration commits, and
   exact call sites.
2. `rg` over routes, request fields, controllers, services, models, jobs,
   migrations, settings, flags, entitlements, provider adapters, and tests.
3. Current UI/DOM and settings for visible behavior; inspect the request path
   or network contract when needed.
4. Framework-native inspection such as Laravel routes, schema, container, and
   test helpers. Laravel Boost may accelerate this when already installed and
   callable, but it is not authority.
5. A one-time Graphify map only when the system spans many modules and the
   targeted pass still cannot identify ownership. Promote every decisive node
   back to current source evidence.

Do not auto-install CodeFlow, Cognee, Graphify, or another memory/graph system
for a delivery slice. Persistent graphs and memories need a separate adoption,
freshness, privacy, cost, rollback, and source-rebinding decision.

## Frontend/Backend Parity

For user-facing settings or options, prove both directions:

```text
UI/settings -> request -> server owner -> persistence/default -> runtime consumer -> result
result/current policy -> response -> UI/settings
```

A visible control without server consumption is inert. A backend capability
that should be configurable but has no current UI path is incomplete. Neither
DOM-only nor source-only evidence closes the complete path.
