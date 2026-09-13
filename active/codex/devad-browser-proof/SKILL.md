---
name: devad-browser-proof
description: Run secret-safe Devad browser proof and sidecar evidence workflows. Use when validating CORE/XCO migration slices, admin/settings UI parity, authenticated Chrome proof, local proof servers, sidecar verification packets, or any Devad task where Codex must prove browser behavior without leaking cookies, passwords, API keys, or social credentials.
---

# Devad Browser Proof

## Overview

Use this skill to turn a migration claim into evidence: exact routes, expected UI facts, browser/console checks, saved artifacts, and an honest PASS/PARTIAL/BLOCKED result.

## Workflow

1. Load project truth first: use `$devad-x5`, read `.devad/X5.md`, `.devad/ACTIVE.md`, the feature `HANDOFF.md`, and only the routed rule files needed for the slice.
2. Define the proof matrix before browsing: route, role, required UI facts, required form interactions, backend assertions, console/network checks, screenshots, and what would count as failure.
3. Prefer deployed proof only when the branch is deployed. Otherwise use a local temp database/server proof and label it `LOCAL PROOF`, not production parity.
4. Use Chrome only for existing logged-in sessions or when explicitly requested. Do not inspect cookies, local storage, browser passwords, session files, or profile internals.
5. Never send secrets to sidecars. Replace user passwords, OAuth client secrets, API keys, tokens, and social credentials with placeholders in prompts and artifacts.
6. Keep test credentials ephemeral and clearly local, for example `*.example.test` users in a temporary SQLite database under the feature `tooling/` folder.
7. Save artifacts under the dated feature folder: prompts in `prompts/`, sidecar outputs in `outputs/<model-or-tool>/`, browser proof in `tooling/<proof-name>/`, and status in `reports/`.
8. Verify browser state with narrow DOM facts first, then screenshots only when visual evidence adds value. Capture console warnings/errors for the proof route.
9. Update the feature checklist with `DONE`, `PARTIAL`, or `BLOCKED`; include exact commands/artifacts and never claim broader parity than the evidence proves.
10. Clean up local proof servers and finalize browser tabs before ending the turn.

## Sidecar Packets

When asking Cursor, Claude, Gemini, Kimi, Qwen, or other assistants for verification:

- Request a bounded read-only or patch-scoped task with allowed files and exact output path.
- Ask for missing features, unknowns, risk ranking, and verification strategy before code when the task is plan review.
- For Claude-style verification prompts, include: `dont burn too much token use smart method to answer to tell us what is missing and what we dont know so your output is almost a verification for our plan. dont make any comment or message only your md file. dont show thinking silently think:`
- If the owner provides a typo-preserving Claude guard, include it literally in the saved packet too; current owner guard is: `dont burn too much token use smart method to answer to tell us what is missign and what we dont know so your output is almost a verifcation for our plan. dont make any comment or mesage only your md file. dont show thinking silently think:`
- Require the sidecar to write only a Markdown artifact, not chat output, unless the tool cannot write files.
- Treat sidecar output as input, not truth; verify with code, tests, browser proof, and repository diffs.

## Proof Labels

- `PASS`: tests/commands/browser facts prove the scoped claim.
- `PARTIAL`: code/tests prove part of the claim, but deployment, OAuth provider behavior, external platform review, or visual parity remains unproven.
- `BLOCKED`: required access, deploy state, credentials, provider approval, or tool capability is missing and cannot be safely inferred.

## POST Channels/Publishing Proof Matrix

For POST migration slices, do not mark Channels or Publishing parity as `PASS` until the browser proof covers the relevant rows below. If a browser tool cannot type, upload, or use the system file picker, record the exact tool limitation and mark only that sub-check `PARTIAL`; still verify safe non-side-effect facts with DOM/backend evidence.

Channels proof must cover:

- `/workspaces/apps/post/channels` renders for an authenticated workspace user.
- Provider cards show configured, available, pending/planned, and disconnected states without exposing secrets or tokens.
- Filters/search work for all, connected, available, pending/planned, and provider text.
- Connected account rows show provider, account name, username/provider account id, status, and sanitized diagnostics.
- Connect/reconnect use top-level navigation or a safe OAuth redirect, not hidden XHR.
- Pause/resume preserve credentials, change composer eligibility, and do not clear tokens.
- Disconnect/destructive actions are workspace-scoped and visually distinct from pause/resume.
- Mobile viewport has no horizontal overflow and keeps actions reachable.
- Browser console has no POST-specific errors or failed route requests.

Publishing proof must cover:

- `/workspaces/apps/post/publishing` renders for an authenticated workspace user.
- New Publishing Item opens the composer and exposes the expected draft/queue/schedule actions.
- Multi-channel account selection is visible and creates one grouped user-facing item, not duplicate cards.
- Caption/content entry saves full text, and edit mode reloads full `content`, not `content_excerpt`.
- Existing media picker attach, direct upload, upload validation error, and media preview are verified separately.
- Draft, queue, schedule, edit, delete, transition, publish-now, failed/retry, and sanitized error states are exercised where supported.
- Calendar month/week/today/prev/next and filters/tabs for queue/drafts/labels/campaigns work.
- Provider-specific rules are visible or blocked: unsupported native publishers are not selectable; Instagram requires media; TikTok/LinkedIn/X/YouTube stay adapter-pending until native publishers pass proof.
- Mobile composer/list/calendar have no horizontal overflow and keep primary actions reachable.
- Browser console has no POST-specific errors or failed route requests.

Admin POST settings proof must cover:

- `/admin/post/channels`, `/admin/post/schedules`, and `/admin/post/rss-automation` render for a superadmin and deny guests/non-superadmins.
- Channel credentials save without exposing client secrets in HTML, Inertia props, screenshots, or logs.
- Schedules and RSS settings save to `post_settings` and reload from persisted values.
- Sidebar links are active, not disabled `Soon` placeholders.
- Browser proof is not a substitute for focused settings tests; both are required for a broad settings parity claim.

## Minimum Report

Record:

- branch, HEAD, and dirty-file scope
- exact routes and role used
- exact browser facts checked
- screenshot/log/database artifact paths
- commands run and pass/fail counts
- secrets policy confirmation
- remaining gaps before production parity
