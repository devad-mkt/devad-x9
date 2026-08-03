# POST Adoption Patterns

Use this reference for POST, StackPosts, social channels, publishing, provider OAuth, account discovery, and provider UI parity.

## Core Pattern

Use the POST vertical bundle:

```text
Provider Contract -> Backend Service -> Metadata -> UI Composer -> Tests -> Browser QA -> Live Proof
```

Never migrate "a little bit of everything." Build one complete provider or bounded workflow before moving to the next.

## Six-Layer Completion Rule

Do not mark a provider/channel complete unless all six layers are implemented and verified:

| Layer | Required proof |
| --- | --- |
| Admin settings | Owner-entered credentials editable; provider internals read-only/copyable and backend-protected |
| Connect/setup | OAuth or manual connect, reconnect, callback/state/replay handling, and fake or approved live proof |
| Account discovery | Provider-shaped account discovery and picker when multiple pages/accounts/locations exist |
| Composer rules | Provider-specific fields, validation, disabled states, and publishability copy |
| Publisher adapter | Provider API call or exact HTTP fake with payload/status assertions |
| Browser/backend proof | Focused tests plus browser proof for UI flow and no fake states |

## Channels Authenticity

- Main Channels grid shows only real connected or paused account rows.
- Add Channels modal shows provider catalog entries for first-time connect.
- Never show never-connected provider catalog cards as account rows with `Reconnect`.
- Lifecycle controls such as Open, Reconnect, Pause/Resume, and Delete must be backed by real account state.
- Manual providers such as Telegram must open a manual setup dialog, not OAuth links.

## Visual Affordance Gate

Clickable controls must look clickable. Buttons, filters, dropdowns, tabs, copy actions, checkboxes, radio controls, and toggles need visible borders/backgrounds, hover/focus states, and understandable disabled states in light and dark modes.

Compact UI is not an excuse for text-only buttons or invisible selections.

## Live Proof

Local tests passing is not final provider completion. A live provider `PASS` requires:

- exact deployed SHA or local proof scope stated honestly,
- API/backend success,
- external provider page or URL showing the exact unique marker where applicable,
- sanitized proof with no OAuth code/token/cookie/raw response.

If external proof is unsafe or blocked, report `API_ONLY_PENDING_EXTERNAL` or `BLOCKED` with the exact missing approval, secret, scope, callback, or evidence.
