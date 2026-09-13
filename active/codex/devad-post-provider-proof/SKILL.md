---
name: devad-post-provider-proof
description: Use when executing Devad CORE POST provider migration slices that need fast, safe connect/publish proof, provider slice packets, Dokploy deploy/health gates, authenticated CORE browser checks, external social verification, and strict secret-safe handling. Applies to POST Channels/Publishing provider runs such as Telegram, Pinterest, Google Business Profile, YouTube, Facebook, Instagram, TikTok sandbox, X, OK, Tumblr, Reddit, Threads, or similar Devad-owned accounts.
---

# Devad POST Provider Proof

## Workflow

Use this skill to prove one provider slice without wasting time on blind browser polling or stale plans.

1. Load current repo truth first:
   - Use `$devad-x5` and, for browser proof, `devad-browser-proof`.
   - Work from `$DEVAD_ROOT\core-aio\core` unless the user gives a different CORE repo.
   - Read the active `.devad/features/...` plan/handoff for the current POST migration slice.
   - Do only narrow verification; avoid broad Git/rule sweeps unless the user asks.

2. Build or refresh a provider slice packet before live action:
   - Save under `.devad/features/post-direct-native-migration-2026-06-05/channels-long-run-2026-06-18/provider-slices/`.
   - Include provider, channel type, current live observation, source files checked, owner-approved account, safe media rules, exact publish text, blocked conditions, and external verification URL.
   - Redact tokens, secrets, cookies, OAuth codes, raw logs, and credential-like CSV cells.

3. Prove deploy before provider claims:
   - Trigger/poll Dokploy via API when the plan requires it.
   - Confirm latest deployment is `done`.
   - Confirm `https://devad.io/health` returns `200`.
   - Do not use browser for deploy checks.

4. Use browser only for the required authenticated live step:
   - Use Chrome only for existing logged-in CORE/social sessions or when the user explicitly approves.
   - Do not inspect cookies, local storage, browser passwords, session files, or profile internals.
   - Reuse open CORE/social tabs when possible.
   - Prefer narrow DOM facts and stable `data-testid` selectors.
   - Keep tabs open as handoff only when waiting on user/provider action.
   - Before handing back, finalize browser tabs/sessions and run a targeted stale-process check for Playwright, `run-ch-*`, browser-proof servers, and related node/php/cmd/powershell helpers.

5. Respect owner-gated actions:
   - Ask or stop for OAuth consent, exact provider app redirect/scope changes, production delete/disconnect, secrets/API keys, live publish if not already approved, and external account choices.
   - If the owner approved one low-risk test post, publish only that approved content.
   - Do not disconnect/delete production channels unless explicitly approved for that exact channel.

6. Connect proof:
   - OAuth providers: use CORE route and provider consent only for Devad-owned accounts.
   - Manual providers such as Telegram: submit token only through the CORE form, never print or save it, then read the CORE-generated verification text.
   - Tell the owner the exact verification text and target chat when the user asked to send it themselves.
   - Continue only after CORE shows the channel as connected.

7. Publish proof:
   - Use the provider's actual CORE Publishing path.
   - Generate a unique run marker for every live publish proof, for example `test-1`, `test-2`, or a timestamp suffix.
   - Include the unique marker in the live post text before publishing; never reuse the same proof text across runs.
   - If a previous failed card exists, repair it when safe; otherwise create a new queued item targeting only the provider account.
   - Apply provider rules before pressing publish:
     - Telegram: text-only is valid.
     - Pinterest: attach an image asset; text-only must not be retried.
     - Media-required providers: use only safe Devad/test media already provided by the owner.
     - Media URL providers: before pressing publish, verify the exact generated media URL is publicly fetchable with HTTP 200 from a non-browser shell. If it returns 404/403 or cannot be fetched, fix or mark the media-storage blocker before calling the provider.
     - TikTok sandbox: obey creator-info/privacy gates before video init.
   - Record the CORE card status and visible failure message when present.

8. External verification is required before PASS:
   - Wait 30 seconds after CORE says published unless the provider requires longer.
   - Open the owner-provided provider URL or provider permalink.
   - Verify the exact unique test text/media appears externally, including the run marker.
   - If the external text is not unique, mark the proof invalid or `PARTIAL`; do not claim the current run posted successfully.
   - Mark `PASS` only when both CORE status and external provider visibility are proven.
   - Mark `PARTIAL` if CORE is published but external visibility is unproven.
   - Mark `BLOCKED` only for real provider/app/access/tool blockers with proof.

9. Keep a temporary progress log:
   - Save under the provider proof directory in `proofs/live-reference/`.
   - Record deploy id, health result, local focused tests, connect state, publish state, external verification, and next action.
   - Never include secrets or raw provider logs.

10. Generate the next provider packet immediately after a provider passes:
    - Use the current live observations and code evidence, not model suggestions alone.
    - Include A/B fallback steps so a failed path returns to a known option instead of looping.
    - Stop at the next owner gate only when it is truly required.

## Telegram Pattern

- Channel route flow: CORE token form, then CORE-generated exact verification text.
- Test id anchors:
  - `post-telegram-manual-connect-dialog`
  - `post-telegram-bot-token`
  - `post-telegram-connect-submit`
  - `post-telegram-waiting-step`
  - `post-telegram-verification-text`
- PASS needs:
  - CORE channel row connected.
  - CORE publication card published.
  - Web Telegram target shows exact approved post text with a unique run marker such as `test-1`.

## Pinterest Pattern

- Channel type: `pinterest_board`.
- OAuth callback alias: `/workspaces/apps/post/channels/pinterest`.
- Native publisher: `app/Post/Services/Publishers/PinterestPublisher.php`.
- Publish requirements:
  - Attach one image asset.
  - Use post type `image` when possible.
  - Use `provider_options.title` and `provider_options.link_url` when useful.
  - Leave `provider_options.board_id` blank unless CORE requires it; the connected account board id should be used.
- Do not retry a text-only Pinterest failed card. Edit it to attach image media, or create a fresh image publication.
- External verification must use the Pinterest URL from the owner CSV, for example `https://tr.pinterest.com/wwwdevadio/?actingBusinessId=<business-id>`, unless CORE returns a stronger provider permalink.

## YouTube Pattern

- Channel type: `youtube_channel`.
- OAuth callback alias: `/workspaces/apps/post/channels/youtube/callback`.
- Account discovery must call YouTube `channels.list` with both `part=snippet` and a filter such as `mine=true`; if the configured `account_url` already has `part=snippet`, merge `mine=true` instead of dropping defaults.
- Publish requirements:
  - Attach one video asset.
  - Use post type `video`.
  - Set a short `provider_options.title`, `category_id` `22` / People & Blogs unless another category is required, and `privacy_status` `public` when external proof is required.
- PASS needs CORE `published`, a provider video id, and the exact marker visible on `https://www.youtube.com/watch?v={provider_post_id}` after the provider wait.

## Stop Rules

Stop and report exact evidence when:

- Deploy is not `done` or health is not `200`.
- CORE cannot reach the provider connect/publish UI.
- OAuth consent, provider app approval, or scopes are missing.
- A token/API key/env var is required but absent.
- External provider verification cannot prove the post after the wait period.
- The only remaining action is owner-gated.
