# CHAT All-Features Evidence-to-Implementation Plan

**Author:** Codex  
**Date:** 2026-07-26  
**Status:** Canonical planning document  
**Supersedes:** `plan-codex.txt` and the earlier WhatsApp-only proposed plan  
**Output root:** `$DEVAD_ROOT\1-core-x9\.temp\temp-chat-migration-v2\answers-by-model-name\CODEX-answer`

## Table of Contents

1. [Mission](#1-mission)
2. [Owner Corrections and Scope](#2-owner-corrections-and-scope)
3. [Deliverable Folder Taxonomy](#3-deliverable-folder-taxonomy)
4. [Standard Five-File Packet](#4-standard-five-file-packet)
5. [Required Coverage by Packet Family](#5-required-coverage-by-packet-family)
6. [Evidence Sources and Authority](#6-evidence-sources-and-authority)
7. [Tools and Model Routing](#7-tools-and-model-routing)
8. [Authenticated 4dev Browser Method](#8-authenticated-4dev-browser-method)
9. [Canonical Evidence and Action Schema](#9-canonical-evidence-and-action-schema)
10. [Execution Phases](#10-execution-phases)
11. [Privacy and Non-Mutation Rules](#11-privacy-and-non-mutation-rules)
12. [Validation and Completion Gates](#12-validation-and-completion-gates)
13. [Assumptions and Failure Handling](#13-assumptions-and-failure-handling)

## 1. Mission

Build a complete, navigable evidence-to-implementation library for the approved CHAT channels and major product features. The library must let a future Codex worker understand what the reference product does, where each behavior appears, how it is triggered, what backend effect it has, what the current native CHAT implementation already provides, and exactly what remains to implement.

This is not a marketing summary and not a list of screenshots. Each packet must combine:

- Authenticated reference UI behavior from `chat.devad.io`.
- Public vendor capabilities, documentation, and version history from Board.
- The local offline Google Sheet export.
- Existing evidence files and receipts.
- Licensed reference frontend and backend source.
- Current native Laravel/Inertia/React/Wayfinder code and tests.
- A deduplicated implementation gap map with exact evidence.

The library is documentation and planning evidence only. It does not authorize product code, test, database, provider, Sheet, runtime, deployment, or live-record mutation.

## 2. Owner Corrections and Scope

### 2.1 Corrected global scope

The mission covers all approved channels and all main CHAT feature surfaces, including:

- Inbox, conversations, contacts, users, agents, departments, queue, and routing.
- Website visitor widget.
- Chatbot and all Chatbot tabs.
- Knowledge training, RAG, citations, and catalog context.
- Flow Builder.
- Automations, triggers, and actions.
- Playground.
- Intents, tools, AI runtime, agent assist, and human takeover.
- Dialogflow at `https://chat.devad.io/?setting=dialogflow`.
- Devad E-commerce Sync at `https://chat.devad.io/?setting=devad_ecom_sync`.
- Articles, tickets, reports, marketing, campaigns, popups, proactive messages, and booking.
- Settings, permissions, design, localization, accessibility, developer surfaces, security, billing, and legacy cutover.

WhatsApp remains one channel packet, not the entire mission.

### 2.2 Excluded by owner

The following channels must not receive folders or active denominator work:

- LINE
- Viber
- WeChat
- Zalo

If their rows appear in the Sheet, licensed source, Board pages, or shared controls, record only:

`EXCLUDED_BY_OWNER`

Do not silently delete the source rows and do not allow their shared references to inflate approved-channel coverage counts.

### 2.3 Other boundary decisions

- Slack is an internal synchronization/integration packet, not a customer-origin messaging channel.
- Tickets are a support product surface, not a provider channel.
- WhatsApp calls, WhatsApp Shop, templates, and SMS fallback remain inside the WhatsApp packet.
- Facebook comments and comment-to-DM remain inside the Messenger/Instagram packets.
- Board-only integrations remain in a reference-gap packet until live UI, licensed source, or a distinct native contract proves they deserve an independent packet.

## 3. Deliverable Folder Taxonomy

### 3.1 Global master packet

- `00-master-index-and-global-gap-ledger/`

This packet indexes every approved folder, page, feature ID, control ID, setting ID, journey ID, source, code owner, evidence state, dependency, version conflict, duplicate, exclusion, and missing native capability.

### 3.2 Approved customer messaging channels

- `channels/website-live-chat-widget/`
- `channels/whatsapp/`
- `channels/messenger-facebook/`
- `channels/instagram/`
- `channels/telegram/`
- `channels/email-and-email-piping/`
- `channels/twitter-x/`

Every channel remains independent through payload, provider account, callback, webhook, send, delivery, read, error, retry, revoke, reconnect, and responsive behavior.

### 3.3 Agent workspace and conversation features

- `features/inbox-conversations-and-contact/`
- `features/users-agents-departments-and-routing/`
- `features/message-composer-rich-messages-and-media/`
- `features/realtime-presence-delivery-and-read-state/`
- `features/notifications-email-push-sms-and-sound/`

### 3.4 Chatbot, AI, knowledge, and flows

- `features/chatbot/`
- `features/knowledge-training-rag-and-citations/`
- `features/flow-builder/`
- `features/automations-triggers-and-actions/`
- `features/playground/`
- `features/intents-tools-and-human-handoff/`
- `features/ai-agent-assist-and-runtime/`
- `features/dialogflow/`
- `features/devad-catalog-intelligence/`

Dialogflow remains independent because it has a large setting/action denominator and may contain version or deprecation conflicts that must not be merged silently into the current AI architecture.

### 3.5 Content, help, and analytics

- `features/articles-and-knowledge-base/`
- `features/tickets-and-help-center/`
- `features/reports-ratings-and-analytics/`

### 3.6 Marketing and proactive engagement

- `features/marketing-campaigns-direct-and-bulk-messaging/`
- `features/popup-welcome-follow-up-subscribe-and-newsletter/`
- `features/booking-calendars-and-proactive-chat/`

Shared audience, campaign, progress, failure, automation, and reporting contracts live here. Channel-specific payloads and provider restrictions remain linked to the applicable channel packet.

### 3.7 Commerce, CRM, and external integrations

- `integrations/devad-ecom-sync/`
- `integrations/opencart/`
- `integrations/perfex-crm/`
- `integrations/whmcs/`
- `integrations/zendesk/`
- `integrations/slack/`
- `integrations/commerce-and-platform-reference-gaps/`

The reference-gap packet covers Board capabilities such as WooCommerce, Shopify, Active eCommerce, Martfury, WordPress synchronization, and membership plugins until an independent live or source contract is proved.

### 3.8 Administration and platform foundations

- `platform/core-settings-permissions-and-admin/`
- `platform/design-branding-panel-widget-and-pwa/`
- `platform/localization-rtl-accessibility-and-responsive/`
- `platform/developer-api-javascript-php-cli-mcp-and-webhooks/`
- `platform/security-privacy-gdpr-observability-and-recovery/`
- `platform/billing-entitlements-launch-and-legacy-cutover/`

No additional folder may be created merely because a new label is discovered. A new folder requires a genuinely independent major surface, lifecycle, ownership boundary, or implementation domain.

## 4. Standard Five-File Packet

Every folder uses exactly these five Markdown files unless this plan is explicitly amended:

1. `01-SURFACES-CONTROLS-AND-STATES.md`
2. `02-SETTINGS-PERMISSIONS-AND-CONDITIONS.md`
3. `03-JOURNEYS-INTEGRATIONS-ERRORS-AND-RECOVERY.md`
4. `04-NATIVE-FRONTEND-BACKEND-AND-TEST-MAP.md`
5. `05-MEGA-SPEC-GAPS-AND-IMPLEMENTATION-CONTRACT.md`

### 4.1 Required header in every file

Each file starts with:

- Title.
- `Author: Codex`.
- Generation date.
- Packet name and canonical folder.
- Packet evidence snapshot.
- Current native Git SHA.
- Licensed-reference version/hash snapshot.
- Live 4dev observation state and date.
- Evidence-state legend.
- TOC immediately after metadata.
- Links to the other four files in the same packet.
- Links to the master packet.
- Links to the live and offline Sheet.

Use these Sheet links:

- `[Live Google Sheet](https://docs.google.com/spreadsheets/d/1lK4CC8lApUGzqh1W_iGasLqD1M3V3HZdfwufC_rDQnI/edit)`
- `[Sheet link source](../../../GOOGLE-SHEET-LINK.txt)`
- `[Offline Sheet export](<../../../sheet-html/AUDIT- CHAT devad.io aio 2026 (1)/README.html>)`
- `[Offline Sheet archive](<../../../AUDIT- CHAT devad.io aio 2026 (1).zip>)`

For deeper nested folders, calculate and validate the correct relative path instead of copying an invalid link.

### 4.2 File responsibilities

#### File 01: Surfaces, controls, and states

- Every page, tab, region, modal, drawer, menu, dropdown, icon, button, input, checkbox, repeater, hidden state, disabled state, loading state, empty state, selected state, desktop state, mobile state, and keyboard/accessibility state.
- Exact label, icon, ARIA locator, visible condition, trigger, immediate transition, and final state.
- Safe live observation status or a precise source-only status.

#### File 02: Settings, permissions, and conditions

- Every relevant setting ID and option.
- Roles, workspace permissions, plan requirements, provider requirements, channel conditions, data conditions, viewport rules, and feature dependencies.
- Credential fields are named but their values are never read or stored.
- Connection, synchronization, callback, webhook, rate-limit, retry, revoke, and disconnect state machines.

#### File 03: Journeys, integrations, errors, and recovery

- Multi-step user journeys and channel-specific lifecycles.
- Success, partial success, validation error, authorization denial, rate limit, provider rejection, ambiguous provider result, timeout, retry, cancel, undo, offline, reconnect, duplicate, stale event, and recovery behavior.
- Unsafe actions are traced through DOM/source/request metadata/code and remain `NOT_EXECUTED_UNSAFE`.

#### File 04: Native frontend, backend, and test map

- Reference frontend and backend code.
- Current native React/Inertia/Wayfinder frontend.
- Laravel routes, controllers, requests, policies, services, models, migrations, jobs, events, outbox, provider adapter, callback, receipt, and reconciliation paths.
- Pest unit/feature/browser coverage and missing proof.
- Every path includes an exact line range and Git SHA or file hash.
- Absence is recorded as `ABSENT_AT_SHA` with the searched scope.

#### File 05: Mega specification and implementation contract

- Deduplicated union of Files 01-04.
- Canonical feature/control IDs.
- Version and contradiction ledger.
- Current native status.
- Implementation decision: reuse, extend, new, owner decision, or drop.
- Dependencies and safe implementation order.
- Required future tests and smallest acceptance proof.
- Included/excluded denominator counts that reconcile with the master index.

## 5. Required Coverage by Packet Family

### 5.1 Shared Inbox and thread coverage

The shared Inbox packet must cover the complete applicability denominator, not only controls containing a channel name:

- Conversation list, source/channel/status filters, search, sorting, pagination, refresh, and empty/loading/error/retry.
- Thread selection and deep links.
- Contact/profile panel.
- Composer, attachments, rich messages, saved replies, private notes, reply-to, transcript, tags, and departments.
- Read/unread, delivery/read receipts, assignment, queue, archive, delete, and collision states.
- Realtime updates, reconnect, duplicate/stale events, desktop/mobile, keyboard, and accessibility.

Channel packets reference shared Inbox controls and document only channel-specific deviations and provider effects.

### 5.2 Website widget

Cover the complete widget tree:

- Embed initialization.
- Launcher.
- Shell and dashboard.
- Visitor identity and authentication.
- Active conversation.
- Rich content.
- Forms.
- Lifecycle messages.
- Articles.
- Recovery, reconnect, offline, responsive, and accessibility.

### 5.3 WhatsApp

Preserve all detail from the earlier WhatsApp plan:

- Inbox and `https://chat.devad.io/?conversation=112`.
- Users page and “Send a WhatsApp message template.”
- Marketing and bulk broadcasting.
- `https://chat.devad.io/?setting=whatsapp`.
- Templates, variables, languages, buttons, quick replies, attachments, phone numbers, departments, tags, progress, partial failure, retry, and 24-hour messaging rules.
- Cloud API automatic/manual/embedded connection.
- Multiple numbers.
- Synchronize/reconnect.
- Template and SMS fallback.
- Calls.
- Flows.
- Shop, catalog, and order webhook.
- Twilio and 360dialog.
- Delivery/read receipts, callback/webhook, errors, rate limits, revoke/disconnect.
- All known Sheet WhatsApp settings and lifecycle rows, with zero unexplained omissions.

### 5.4 Messenger and Instagram

- Shared Meta credentials and page/account selection.
- Messenger and Instagram separation.
- Messages, comments, comment-to-DM, direct messages, attachments, read/delivery behavior, routing, department/tags, synchronization, callback/webhook, retries, and revoke.
- Never assume one Meta channel proves the other.

### 5.5 Telegram, Email, and Twitter/X

For each:

- Connection and credential/configuration controls.
- Account/channel selection.
- Inbound and outbound behavior.
- Attachments and message-format restrictions.
- Callback/webhook or polling.
- Delivery/error/retry/revoke lifecycle.
- Channel-specific Inbox and notification behavior.

Email additionally covers SMTP, email piping, templates, test actions, threading, sender/recipient behavior, and notification overlap.

### 5.6 Chatbot

Inspect `https://chat.devad.io/?area=chatbot` and every discovered tab:

- Training sources and synchronization.
- Q&A.
- Files, URLs, text, and structured information.
- Models, prompts, assistant behavior, languages, takeover, and escalation.
- Knowledge provenance, versions, deletion, and re-ingestion.
- Error, retry, progress, provider, and budget states.

### 5.7 Flow Builder

- Full page and control tree.
- Draft, node, edge, option, validation, version, test, publish, activation, execution, history, failure, retry, and recovery states.
- Trigger/action catalog and conditional nodes.
- Channel-specific branches.
- AI/tool actions.
- Hidden, disabled, unsupported, and role-gated controls.

### 5.8 Playground

- Session/run lifecycle.
- Model and assistant selection.
- Prompt/input modes.
- Files and multimodal behavior.
- Tool calls and trace output.
- Token/cost/usage state when safely observable.
- Cancel, retry, replay, history, errors, and provider-disabled behavior.
- No live provider call without explicit authority.

### 5.9 Dialogflow

Inspect the complete `?setting=dialogflow` surface and all indexed controls:

- Credentials/configuration names without reading values.
- Synchronization and language behavior.
- Entities, intents, contexts, fulfillment, bot behavior, and handoff.
- Provider lifecycle, callback/webhook, error/retry, and revoke/disconnect.
- Current Board changelog and documentation contradictions.
- Explicit decision between retained compatibility, migration, replacement, deprecation, or removal.

### 5.10 Devad E-commerce Sync

Inspect `?setting=devad_ecom_sync`:

- Connection and credentials without values.
- Product, catalog, seller, user, order, and inventory synchronization.
- Mapping and filtering.
- Manual/automatic synchronization.
- Callback/webhook.
- Progress, partial failure, retry, duplication, revoke, and disconnect.
- Relationship to Catalog Intelligence and Board-only commerce integrations.

### 5.11 Content, marketing, and platform

Include:

- Articles, categories, search, widget exposure, help center, tickets, and reports.
- Popup, welcome, follow-up, subscribe, newsletter, proactive chat, campaigns, direct/bulk messages, audience selection, scheduling, progress, and reporting.
- Booking and calendar actions.
- Users, agents, registration/login, departments, routing, permissions, and profile fields.
- Settings groups: Chat, Messages, Admin, Notifications, Users, Design, Miscellaneous, Articles, Apps, and provider-specific groups.
- Web API, JavaScript API, PHP API, native versioned API, CLI, MCP, and webhooks.
- Localization, RTL, accessibility, responsive states, PWA/offline, design, branding, privacy, GDPR, security, logs, performance, observability, rollback, and release.

## 6. Evidence Sources and Authority

### 6.1 Authority order

1. Current native Git code and tests at one frozen SHA.
2. Rendered authenticated 4dev CHAT reference facts.
3. Licensed reference source at a recorded version and hash.
4. Board changelog for additions, fixes, removals, and version drift.
5. Board features and documentation for advertised behavior.
6. Offline Sheet and existing evidence for prior IDs, observations, and unresolved gaps.

No single source proves another:

- Board documentation does not prove live UI.
- Live reference UI does not prove native implementation.
- Licensed reference source does not prove current native architecture.
- Native source does not prove rendered browser behavior.
- A test does not prove production deployment.
- A provider-fake result does not prove live provider delivery.

### 6.2 Local packet sources

- `$DEVAD_ROOT\1-core-x9\.temp\temp-chat-migration-v2\evidence`
- `$DEVAD_ROOT\1-core-x9\.temp\temp-chat-migration-v2\sheet-html\AUDIT- CHAT devad.io aio 2026 (1)`
- `$DEVAD_ROOT\1-core-x9\.temp\temp-chat-migration-v2\MANIFEST.sha256`
- `$DEVAD_ROOT\1-core-x9\.temp\temp-chat-migration-v2\START-HERE.md`
- `$DEVAD_ROOT\1-core-x9\.temp\temp-chat-migration-v2\CURRENT-PROGRESS.md`
- `$DEVAD_ROOT\1-core-x9\.temp\temp-chat-migration-v2\REVIEW-REQUEST.json`

The Sheet must be parsed by stable IDs and relationships, not keyword search alone.

### 6.3 Public sources

- `https://board.support/changes`
- `https://board.support/features`
- Every feature subpage linked from the feature catalog.
- `https://board.support/docs/`
- `https://devad.io/help`

Deduplicate repeated public content by canonical URL, slug, title, and content hash. Record aliases rather than counting repeated pages as separate features.

### 6.4 Licensed reference source

Primary root:

`D:\Ref1\chat\public_html`

Search:

- UI components and JavaScript.
- App-specific `functions.php`, `post.php`, settings JSON, and assets.
- Shared AJAX/API handlers.
- Account and administration pages.
- Version constants and app versions.

Reference code is labeled `LICENSED_REFERENCE`. Extract behavior and contracts, not copyrighted implementation wholesale.

### 6.5 Native source snapshot

At plan creation, the remote CHAT manager branch was:

`worker/chat/r0-main-20260721@81d7a662f890f555e396ebe669e5cae7ef666041`

At execution start:

1. Re-run `git ls-remote`.
2. Freeze the returned SHA for the whole audit run.
3. Use `git grep <SHA>` and `git show <SHA>:<path>`.
4. Do not mix working-tree changes or later commits.
5. If the remote advances mid-run, record it as a later snapshot; do not silently change the audit base.

## 7. Tools and Model Routing

### 7.1 Primary tools

- `rg` and `rg --files` for inventories and exact searches.
- Git object reads for native code.
- PowerShell for hashes, line numbering, link validation, and privacy scans.
- Bundled Python or Node for read-only HTML table extraction without installing dependencies.
- Public web access for Board citation extraction.
- Bundled Chrome extension for authenticated CHAT UI.
- `apply_patch` for report files.

No persistent parser, raw DOM dump, cookie export, network body archive, or screenshot collection is created.

### 7.2 Skill use

- Smooth Coding: bounded, evidence-first work.
- Ponytail: minimum sufficient files and no ceremonial artifacts.
- Devad Browser Proof: privacy-safe proof matrix and honest partial states.
- Devad Adoptions: reference behavior remains separate from native implementation.
- Devad Docs: durable, implementation-usable Markdown.
- XPlan: read-by-need structure and denominator closure.
- Devad X9: current code and evidence authority.

Do not use the POST chunk runner for CHAT packets.

### 7.3 Subagent policy

Use at most one task-local helper at a time:

- Closest available “Sol light” route: `gpt-5.6-sol` with `low` reasoning.
- Allowed only for mechanical, secret-safe, read-only extraction, counts, ID lists, and link checking.
- No browser, live UI, product decisions, report writing, mutations, or nested agents.
- The parent verifies every returned count and classification.

## 8. Authenticated 4dev Browser Method

### 8.1 Required route

Use only the bundled Chrome extension attached to the real authenticated profile:

- Profile name: `4dev`
- Chrome directory mapping: `Default`

Never substitute:

- In-app Browser.
- Isolated Chrome.
- Standalone Playwright.
- Page Agent.
- Computer Use.
- An unauthenticated or different profile.

### 8.2 Initialization

Use the persistent Node REPL and bundled Chrome browser client. Before interaction:

1. Initialize the extension browser binding if absent.
2. Read `chrome.documentation()` completely once.
3. Read current open tabs.
4. Claim the existing authenticated CHAT tab.
5. Prove the session through visible authenticated navigation such as Conversations, Users, Chatbot, Articles, and Reports.

Do not inspect browser profile files, cookies, local storage, password stores, or tokens.

### 8.3 Safe interaction policy

Safe only after proving no persistence effect:

- Page and tab navigation.
- Accordion expansion.
- Menus and dropdown reveals.
- Modal and drawer opening.
- Read-only filters or responsive layout inspection.

Do not execute:

- Send, broadcast, upload, save, create, publish, synchronize, reconnect, clear, assign, status change, archive, delete, logout, provider call, AI run, call start/answer/decline, or unclear controls.

If opening a conversation marks it read or otherwise writes state, do not use that route unless the target state is already open and unchanged. Use DOM/source/licensed-source fallback and label the live row partial.

### 8.4 Responsive and accessibility coverage

For every live surface:

- Desktop viewport.
- Mobile viewport.
- Keyboard navigation.
- Focus order and visible focus.
- ARIA names, roles, expanded/selected/disabled states.
- Modal focus containment and escape behavior when safely testable.
- Empty, loading, error, retry, offline, reconnect, and conditional states.

Use text/DOM/ARIA evidence by default. Do not persist screenshots unless a future Work Order explicitly requires privacy-masked images.

## 9. Canonical Evidence and Action Schema

Every canonical row includes:

- Feature ID and control ID.
- Packet and source aliases.
- Page, route, surface, region, and locator.
- Control type, label, icon, ARIA, classes, and option order.
- Desktop/mobile visibility.
- Hidden, disabled, selected, required, read-only, and conditional rules.
- Role, permission, plan, channel, provider, data, and viewport conditions.
- Trigger.
- Immediate UI transition.
- Final state.
- Request/event and payload/schema.
- Validation.
- Authorization and workspace scope.
- Handler, service, persistence/read authority, transaction, job, outbox, provider, callback, and receipt.
- Success, failure, retry, undo, offline, reconnect, and recovery.
- Evidence citation.
- Native status.
- Implementation decision.
- Smallest future proof.

### 9.1 Evidence classification

- `NATIVE_PROVED`
- `NATIVE_PARTIAL`
- `REFERENCE_PROVED`
- `DOCS_ONLY`
- `ABSENT_AT_SHA`
- `UNKNOWN`
- `NOT_APPLICABLE`
- `DEPRECATED`
- `EXCLUDED_BY_OWNER`

### 9.2 Interaction classification

- `SAFE_LIVE_OBSERVED`
- `SOURCE_TRACED_NOT_CLICKED`
- `NOT_EXECUTED_UNSAFE`
- `BLOCKED_4DEV`

### 9.3 Implementation decision

- `REUSE`
- `EXTEND`
- `NEW`
- `OWNER_DECISION`
- `DROP`

These dimensions remain independent. For example, a feature can be `REFERENCE_PROVED`, `NOT_EXECUTED_UNSAFE`, and `NEW`.

## 10. Execution Phases

### Phase 0: Preflight

- Verify the canonical plan and source paths.
- Confirm output destinations do not contain conflicting packets.
- Hash-check packet sources and the original manifest entries.
- Freeze the current native SHA.
- Record Board retrieval date and licensed-reference version.
- Create no Git branch and change no Git ref.

### Phase 1: Build the full denominator

Parse:

- Feature Index.
- Page Index.
- Chunk Index.
- Control Denominator.
- Setting Denominator.
- Journey Denominator.
- Acceptance, gaps, coverage, traceability, decisions, and implementation ledgers.

Build exact included and excluded sets. Every row ends as included, aliased, superseded, deprecated, not applicable, unknown, or excluded by owner.

### Phase 2: Public Board and help audit

- Enumerate every feature subpage.
- Capture approved-channel and major-feature capabilities.
- Walk changelog history by product/app version.
- Capture additions, fixes, behavior changes, removals, and contradictions.
- Record unrelated or excluded pages with reasons.

### Phase 3: Licensed-source mapping

- Trace UI to request/action to backend handler.
- Map setting IDs, provider lifecycle, callbacks, errors, retries, and conditional states.
- Record line ranges and file hashes.
- Do not copy large code bodies.

### Phase 4: Authenticated 4dev audit

Audit every safe page/control across:

- Approved channels.
- Inbox/thread/contact/users.
- Chatbot and all tabs.
- Flow Builder.
- Playground.
- Articles, Reports, Tickets, Marketing, and Settings.
- Dialogflow and Devad E-commerce Sync.
- Responsive and accessibility states.

One unavailable page blocks only its own live rows. Continue all source-checkable work.

### Phase 5: Native implementation mapping

At the frozen SHA:

- Locate frontend routes/pages/components.
- Locate Wayfinder calls.
- Locate Laravel routes/controllers/requests/policies/services/models/jobs/events.
- Locate migrations, outbox, provider adapter, webhook, receipt, retry, and reconciliation.
- Locate Pest unit/feature/browser tests.
- Record exact absence searches.

### Phase 6: Write packets in dependency order

1. Master schema and index.
2. Shared Inbox/workspace packets.
3. Approved channel packets.
4. Chatbot/AI/knowledge/flow packets.
5. Content/marketing packets.
6. Integration packets.
7. Platform packets.
8. Final master reconciliation.

Write one coherent packet at a time. Shared controls live once and are linked from dependent packets.

### Phase 7: Stable review and validation

- Validate structure, counts, links, TOCs, IDs, citations, privacy, and hashes.
- Run one stable self-review.
- Correct only evidence-backed defects.
- Recompute hashes and byte counts after the final correction.

## 11. Privacy and Non-Mutation Rules

Never retain:

- Customer names.
- Phone numbers.
- Email addresses.
- Avatars.
- Message bodies.
- Attachments.
- Credentials or setting values.
- Cookies, tokens, secrets, headers, request bodies, or raw DOM dumps.

Use placeholders:

- `[CUSTOMER_REDACTED]`
- `[PHONE_REDACTED]`
- `[EMAIL_REDACTED]`
- `[MESSAGE_REDACTED]`
- `[SECRET_NOT_READ]`

The mission must not mutate:

- Product or test code.
- Git branches, refs, staging, commits, or remotes.
- The live Google Sheet.
- Live CHAT records or settings.
- Database or runtime state.
- Providers or AI services.
- Deployment state.

The only writes are the approved evidence-to-implementation Markdown packets under `CODEX-answer`.

## 12. Validation and Completion Gates

### 12.1 Per-file gates

- `Author: Codex` is present.
- Metadata and TOC are present.
- All TOC anchors resolve.
- Sheet and cross-packet links resolve.
- Every material claim has a source.
- Every code path has a line range and SHA/hash.
- No unsupported “implemented,” “complete,” “live,” “delivered,” or “read” claim.
- No secrets or customer content.

### 12.2 Per-packet gates

- Exactly five Markdown files.
- File responsibilities do not overlap without links.
- Every candidate row is classified.
- Control/settings/journey counts reconcile.
- No duplicate canonical IDs.
- Channel-specific and shared behavior remain separated.
- All unsafe actions are listed under `NOT_EXECUTED_UNSAFE`.
- Native gaps include an implementation decision and future proof.

### 12.3 Global gates

- Every approved folder exists and is indexed.
- LINE, Viber, WeChat, and Zalo have no folders and are recorded as `EXCLUDED_BY_OWNER`.
- Every Sheet feature/page/chunk is included, aliased, superseded, deprecated, not applicable, unknown, or excluded.
- Every Board feature subpage is applicable or explicitly excluded.
- Version conflicts are resolved or remain visibly `UNKNOWN`.
- Master totals equal the sum of packet totals without double counting shared controls.
- A privacy/secret scan passes.
- Final SHA-256 and byte counts are produced for every report.
- A no-mutation proof is returned.

## 13. Assumptions and Failure Handling

- Markdown is the canonical report format; the damaged duplicate TXT plan remains historical and is not edited.
- No screenshots are needed by default.
- Missing 4dev access produces partial live proof only; it does not block Sheet, Board, licensed-source, or native-source work.
- Missing evidence becomes `UNKNOWN`; it is never guessed.
- A missing native feature becomes `ABSENT_AT_SHA` only after a recorded bounded search.
- Contradictory versions enter the contradiction ledger.
- Output collision stops only the affected packet; do not overwrite unknown work.
- A feature discovered during execution gets a new folder only when it has an independent major surface or implementation ownership boundary.
- Excluded channels cannot be reintroduced without a new owner correction.

Completion must return:

- Canonical output root.
- Packet and report counts.
- Per-file SHA-256 and bytes.
- Native snapshot SHA.
- Licensed-reference and Board snapshot dates.
- 4dev live-proof status.
- Evidence-state and implementation-decision totals.
- Excluded-channel proof.
- Privacy scan result.
- No-mutation proof.


---
ready allowed to test 
https://chat.devad.io/?conversation=89 instagram https://www.instagram.com/direct/t/17846064651544965/ 
https://chat.devad.io/?conversation=128 facebook send https://www.facebook.com/www.devad.io 
https://chat.devad.io/?conversation=112 whatsapp send https://web.whatsapp.com/send/?phone=15513000024&text&type=phone_number&app_absent=0
https://chat.devad.io/?conversation=125 live chat to send https://devad.io/help 
