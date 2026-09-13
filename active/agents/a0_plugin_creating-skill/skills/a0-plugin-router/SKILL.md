---
name: a0-plugin-router
description: Entry-point dispatch for Agent Zero plugin work. Use FIRST for any plugin-related request (create, review, contribute, manage, debug, or explain). This router does not plan or build — it reads the request, classifies it, and points at the right specialized skill's absolute path.
---

# a0-plugin-router

This skill only **dispatches**. It never plans, never builds, never reviews. Its job is to classify the user's plugin-related request in one step and tell the agent which specialist skill to load, then stop.

## Decision table

| User intent | Load |
|---|---|
| Create / extend / plan-out a new plugin, or execute a chunked plugin plan | `a0_plugin_creating` (this skill folder's parent `SKILL.md`) — research → plan → chunk → execute → verify |
| Review / audit / validate / check an existing plugin | `a0_plugin_creating` (parent `SKILL.md`) Mode C: AUDIT — dry-run of `ref/audit-checklist.md`, then `AUDIT-REPORT.md` (+ optional fixes). If the user wants a cross-plugin consistency sweep beyond single-plugin health, `a0-review-plugin` (if installed) |
| Contribute / publish / submit to the community Index | `a0-contribute-plugin` — standalone repo + `plugin.yaml` + LICENSE at repo root |
| Install / update / uninstall / remove / browse / scan | `a0-manage-plugin` |
| Plugin not working / crashing / missing / debugging | `a0-debug-plugin` |
| Explain / how does it work / architecture | Answer inline (or read `ref/a0-plugin-contract.md` for the contract) |

## Rule that must never be skipped

When routing to **PLAN/CREATE** (`a0_plugin_creating`), the loaded skill MUST be followed including its Plan step and its Verify/Dry-Run step — even under time pressure and even when running a small/cheap model. Skipping Plan/Dry-Run is the single biggest source of plugin errors. Do not compress the workflow.

When routing to **AUDIT/REVIEW** (`a0_plugin_creating` Mode C), run the checklist (`ref/audit-checklist.md`) even when the plugin looks fine — skipping it means reporting "healthy" based on gates alone, and gates miss contract violations (install/uninstall drift, stale names, imports).

## If intent is ambiguous

Ask ONE question before routing:

> "Are you trying to **create/plan** a new plugin, **review** one, **contribute** it to the community, **manage** (install/update/uninstall), or **debug** a plugin that isn't working?"

## Roots and discovery (quick facts)

- Discovery: `usr/plugins/<name>/` (user, priority) then `plugins/<name>/` (core). A directory is a plugin iff it contains `plugin.yaml`.
- User plugins import as `usr.plugins.<name>...`; never `sys.path` hacks.
- This router's sibling skills live under `skills/a0-plugin-router/` (this file) and the creating skill at the parent `SKILL.md`.

After dispatch: read the target skill fully before acting.