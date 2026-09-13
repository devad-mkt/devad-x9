---
name: devad-cursor-post-chunk-runner
description: Use when migrating or verifying Devad CORE POST features from StackPosts/post.devad.io, especially Channels, Publishing, provider OAuth, admin settings, account pickers, TikTok, live browser parity, Cursor/sidecar chunk packets, or production-ready social channel migration.
---

# Devad POST Migration Runner

Use this skill to run StackPosts/post.devad.io to native CORE POST migration chunks without fake parity claims. Codex owns final code, verification, deploy claims, and security decisions even when Cursor or another sidecar helps.

## Start Here

Read minimal repo truth first, then load only the case-specific files below:

```text
$DEVAD_ROOT\core-aio\core\.devad\X5.md
$DEVAD_ROOT\core-aio\core\.devad\ACTIVE.md
$DEVAD_ROOT\core-aio\core\.devad\features\post-direct-native-migration-2026-06-05\HANDOFF.md
```

Do not rely on old chat memory. If docs conflict with source/runtime evidence, verify from code, browser, tests, or official provider docs and then update the docs.

## Case-Based Reads

Do not load every POST migration artifact by default. Pick the narrow case first:

| Case | Read next | Purpose |
|---|---|---|
| Channels chunk status | `CHANNELS-MIGRATION-METHOD.md`, `CHANNELS-LONG-RUN-PLAN.md`, `PROGRESS.md` | Find current provider row, scope, blockers, and proof gaps. |
| Live `devad.io` failed after local pass | Latest sidecar/debug packet, `PROGRESS.md`, deploy proof, `/health` output, focused browser/network notes | Separate code bug from deploy/session/cache mismatch. |
| OAuth callback or token exchange | OAuth routes/controller, provider settings/config service, state/token storage, official provider docs, `devadio/post` fallback if unclear | Verify redirect URI, scopes, state, token payload, and app mode. |
| Account picker/discovery | Provider discovery service, picker React component, `post_social_accounts` model/resource, browser proof | Prove provider-shaped rows and real lifecycle controls. |
| Publisher failure | Provider adapter, queue/job, HTTP fake tests, sanitized API error shape | Convert live request shape into focused regression tests. |
| Channels grid/UI authenticity | Channels page/components, account query/resource, screenshots or Playwright proof | Ensure grid shows only real connected/paused rows, not catalog cards. |
| Deploy/live proof | Local SHA, Dokploy deployment commit, `/health` 200 commit, sanitized deploy log excerpt | Enforce three-way SHA match before live claims. |
| Sidecar escalation | Embedded-facts packet and the latest GLM/Kimi output only | Extract hypotheses; Codex still verifies locally. |

## Source Authority Gate

Treat StackPosts as evidence, not architecture.

Use this source order for every future migration goal:

1. Live `https://post.devad.io` for current visible workflow, admin copy, OAuth handoff boundaries, account picker behavior, and UX states.
2. Current Laravel 13 StackPosts source or zip for nearby implementation hints and provider field names.
3. Old Laravel 10/11 reference source at `https://github.com/devadio/post` when live StackPosts or the Laravel 13 source appears incomplete, messy, vibe-coded, or missing provider sandbox/production details.
4. Official provider docs when StackPosts sources disagree, appear unsafe, or omit required fields/scopes.
5. Postiz (`gitroomhq/postiz-app`) only as a modern cross-check for OAuth/publisher payload patterns, never as CORE admin parity or UX authority.
6. Native CORE source, tests, and browser proof as the only authority for what is implemented.

Never copy StackPosts code structure into CORE. Extract workflow facts, then implement small native CORE services, policies, settings, migrations, tests, and compact React components.

Mandatory legacy fallback trigger: when a provider flow has a sandbox/production mismatch, missing admin setting, unclear OAuth parameter name, missing picker/account-discovery behavior, or suspicious Laravel 13 implementation, check `devadio/post` before marking the item unknown, blocked, or complete. Record either `devadio/post checked` with the useful finding or `devadio/post not needed` with the reason in the chunk proof.

## Production Objectives

Keep CORE POST:

- lightweight for available CPU/RAM,
- secure by default,
- settings-driven instead of hardcoded,
- tenant/workspace scoped,
- token/secret safe,
- browser-proofed before parity claims.

Avoid large all-in-one files. Prefer provider-specific services, strict validation, encrypted tokens, sanitized diagnostics, and focused tests.

## Six-Layer Completion Rule

Do not mark a social channel complete unless all six layers are implemented and verified:

| Layer | Required proof |
|---|---|
| Admin settings | Owner-entered credentials editable; provider internals read-only/copyable and backend-tamper-resistant |
| OAuth/connect | Connect, reconnect, callback, state/replay handling, and local fake or approved live proof |
| Account discovery | Provider-shaped account discovery and picker when multiple accounts/pages/locations exist |
| Composer rules | Provider-specific fields, validation, disabled states, and publishability copy |
| Publisher adapter | Provider API call or exact HTTP fake with payload/status assertions |
| Browser/backend proof | Focused tests plus browser proof for UI flow and no fake states |

If secrets, approval, callback registration, or API permissions are missing, mark the provider `BLOCKED` with the exact missing item. Do not silently call it complete.

## Channels UX Truth

Before visual polish, prove account state authenticity:

- Main Channels grid shows only real connected or paused `post_social_accounts` rows.
- Add Channels modal shows provider catalog entries with first-time `Connect`.
- Never show never-connected provider catalog cards as account rows with `Reconnect`.
- If `Reconnect` exists for a row, `Open`, `Pause`/`Resume`, and `Delete` must also be meaningful for that real account.
- Disconnected rows must not consume quota and must not appear as connected provider choices.
- Official provider logo and provider-returned profile image/name are parity requirements, not polish.
- `Check all`, selected count, and bulk lifecycle actions operate only on real account rows.
- Manual providers must never use OAuth `/connect` links from the Add Channels catalog. Telegram first-time `Connect` opens the manual bot-token dialog, and browser proof must assert the action is a button with no OAuth href.

## Accessibility And Clickable Affordance Gate

POST migration parity includes accessible controls, not only matching labels.

- Any clickable element must look clickable in the compact CORE UI. `Connect`, `Open`, `Reconnect`, `Pause`, `Delete`, copy buttons, filter buttons, and tab/action controls need visible borders, button treatment, hover/focus states, and disabled styling that is still understandable.
- Unchecked checkboxes/radios/toggles must have visible contrast in light and dark surfaces. Do not rely on low-contrast `border-input` alone for critical selection controls.
- Browser proof for channel/account-picker UI should check visible control facts, not just text presence. When feasible, include computed-style checks for border width/color and screenshots for unchecked and checked states.
- Keep Google Lighthouse accessibility as a 90-100 target for POST frontend routes. Do not claim a Lighthouse score unless the audit was actually run; otherwise record `accessibility proof: local DOM/control checks only`.
- If compact styling hides affordance, change the UI. Preserving compact layout does not justify fake-text buttons or invisible selection states.

## Admin Settings Truth

Super-admin channel settings should expose only owner-supplied credential fields as editable:

- enabled/status,
- app id, client id, or client key stored internally as needed,
- client secret,
- provider API key where required,
- provider app/public key where required.

Provider internals must be read-only/copyable and backend-protected:

- callback/redirect URL,
- authorize URL,
- token URL,
- account URL,
- scopes/permissions,
- Graph/API version.

If StackPosts exposes an internal field as editable, do not copy that blindly. Decide from security, provider docs, and CORE config authority.

## Callback And Picker Proof Rule

Provider redirect URIs are exact evidence, not suggestions:

- Compare the owner credential map, super-admin copyable callback URL, provider developer-console registration, and generated OAuth `redirect_uri`.
- If the registered URI uses an alias such as `/workspaces/apps/post/channels/meta/callback` or a bare path such as `/workspaces/apps/post/channels/pinterest`, CORE must either generate that exact URI or the provider must be reconfigured before live testing.
- Alias callback support must validate against the original OAuth state channel; never accept arbitrary callback aliases.
- A provider success toast or console message is not enough. Browser proof must show picker state, confirm action, resulting connected `post_social_accounts` row, and meaningful lifecycle controls in the Channels grid.
- For connected rows, prove `Open`, `Reconnect`, `Pause`/`Resume`, and `Delete` are enabled only when backed by real account state and safe profile/open URL data. If an external API does not provide a safe public URL, mark only `Open` as unavailable with honest copy rather than inventing a URL.

## TikTok Rule

TikTok requires extra skepticism:

- `post.devad.io` may use a production TikTok app.
- `devad.io` may use sandbox/custom TikTok settings.
- A mismatch is an environment boundary until callback URL, app mode, approval status, scopes, and provider parameter names are verified.
- TikTok uses `client_key` in OAuth/token requests even if CORE stores it as `client_id`.
- Request/profile-proof behavior may require `user.info.profile` in addition to `user.info.basic`.
- If live StackPosts or Laravel 13 source does not explain TikTok sandbox/production settings, app mode, scope approval, or direct-post behavior, check `https://github.com/devadio/post` before changing CORE code or declaring an external blocker.

Do not claim live TikTok publish without creator-info, privacy levels, commercial disclosure, upload/direct-post adapter, polling, app approval, and browser proof that unapproved states are honestly blocked.

## Telegram Rule

Telegram is manual and workspace-owned:

- Super-admin enables/disables Telegram only.
- Do not expose or store Telegram Client ID, Client Secret, or a global/admin bot token in POST channel settings.
- Workspace connect collects bot token, bot username, chat id, and display name.
- Verify `getMe`, verify the username matches the supplied bot username, then verify `getChat`.
- Store the bot token encrypted on the resulting social account only.
- Never write the raw token to docs, tests, browser artifacts, sidecar prompts, logs, or final reports.

## Code-Only Provider Exceptions

Do not run real browser OAuth/connect for X/Twitter, Reddit, Threads, or OK Group until the owner confirms valid credentials and app approval. Verify these with code, HTTP fakes, admin settings tests, publisher payload tests, and browser proof that CORE does not falsely show live readiness.

These providers must default to a disabled live gate:

- `POST_X_LIVE_CONNECT_ENABLED=0`
- `POST_REDDIT_LIVE_CONNECT_ENABLED=0`
- `POST_THREADS_LIVE_CONNECT_ENABLED=0`
- `POST_OK_LIVE_CONNECT_ENABLED=0`

Configured credentials alone must not make workspace `oauth_ready=true` or create a real OAuth state. Fake/code tests that intentionally exercise OAuth can set `post.oauth.providers.{provider}.live_connect_enabled=true` inside the test only.

For browser proof, stop every PHP process listening on `127.0.0.1:8146` before restarting the proof server. Multiple stale proof servers can coexist and make the browser hit an older mock-enabled process. Code-only provider browser proof must run with `POST_TESTING_MOCK_OAUTH=0` and the four live-connect gates above set to `0`.

## Direct Tab Link Rule

POST tabbed surfaces must support query links before they are called complete:

- `/workspaces/apps/post/publishing?tab=channels`
- `/workspaces/apps/post/settings?tab=billing`
- `/admin/post/channels?provider=youtube`

## Chunk Loop

Run one provider or bounded feature chunk at a time:

1. Confirm branch, HEAD, dirty files, and deploy target.
2. Build or update the provider matrix row.
3. Inspect live/reference/source evidence using the source authority gate.
4. Write one focused failing test for the missing behavior.
5. Implement the smallest native CORE change.
6. Run the focused test, then the provider suite.
7. Run `pnpm run types` and `pnpm run build` when React/config/routes changed.
8. Run browser proof for Channels/Publishing/Admin when UI changed.
9. Update `PROGRESS.md` with exact pass/fail output and blockers.
10. Commit/push/deploy only after scoped verification passes and intended files are staged explicitly.

## Live OAuth Debug Pattern

When local tests pass but `devad.io` fails, classify the failure layer before patching:

- frontend/Inertia state,
- route or middleware,
- OAuth config/callback/scopes,
- token exchange,
- account picker/discovery,
- publisher adapter,
- deploy/session/cache mismatch.

Use a three-lane factory for each provider fix:

1. Focused Pest or HTTP fake regression test.
2. Local owner Chrome/Playwright proof.
3. Deployed `devad.io` proof against the exact deployed SHA.

Do not skip lanes. Local tests passing is not provider completion.

For live OAuth and picker failures, prefer owner Chrome/Playwright over the Codex in-app browser. When safe, capture a CDP trace or Playwright trace viewer artifact, sanitize request shape, then convert the useful request/response contract into a focused `Http::fake` regression test. Never store OAuth codes, tokens, cookies, raw callback URLs with secrets, or provider app JSON.

Before claiming live proof, require the three-way deploy match:

```text
local git rev-parse == Dokploy deployment commit == /health 200 reported commit
```

If any side is missing, report `deploy SHA unproven` and do not make live claims.

Recommended provider workflow:

```text
REF_CAPTURE -> GAP_ROW -> RED_TEST -> MIN_PATCH -> GREEN -> BROWSER_PROOF -> DEPLOY_SHA -> LIVE_RETRY -> PUBLISH_PROOF
```

Every provider must end as either `LIVE PASS` with exact proof or `HONEST BLOCKER` with the missing approval/secret/callback/scope/evidence. Do not convert `local green` into `done`.

Keep the main Channels grid authentic: it shows real connected or paused rows only. Provider catalog cards belong in Add Channels. If a row exists in the grid, its lifecycle controls must be backed by a real `post_social_accounts` row.

## Sidecar Use

Use Cursor/sidecars for bounded analysis, not final authority:

- Send full-context markdown packets, not tiny prompts.
- Ask for plan/options first before write mode.
- Provide exact allowed files and stop conditions.
- Never send secrets, `.env`, passwords, cookies, OAuth codes, tokens, raw provider app JSON, or full production logs.
- Verify every useful sidecar claim locally before editing code or making final claims.
- Use OpenCode Go plan `GLM 5.2` for live-vs-local checklists, acceptance gates, deploy/SHA proof, and test-matrix critique.
- Use OpenCode Go plan `Kimi K2.7 Code` for migration/code/risk questions, stop conditions, and smallest-safe-patch review.
- Ask a sidecar only after Codex has gathered local facts and failed the first debugging attempt, or when the issue is high-risk. Use embedded facts, exact file slices, and sanitized logs; do not let the model browse broadly.
- Lesson: full context means Codex embeds the relevant facts, snippets, live failure, and proof gaps. If one sidecar times out while reading/snapshotting, tighten the packet once; do not send the same broad packet to another model.
- Verify sidecar ideas against source, `facts.json` or provider matrix facts, focused tests, browser proof, and deployed SHA before acting.

## Stop Conditions

Stop and report instead of guessing when:

- live provider flow asks for owner consent or destructive account deletion,
- provider approval/secrets/callback registration are missing,
- production deploy cannot be proven to the expected branch and commit,
- OAuth state/token storage/admin settings show a security risk,
- a browser proof would expose secrets or raw OAuth URLs,
- current StackPosts evidence is incomplete and `devadio/post`/official docs have not been checked.
