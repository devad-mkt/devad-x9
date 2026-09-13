# Browser, DOM, Interactions, and Live Testing

## 1. Bind browser authority

Record the visible profile and Chrome directory. Canonical CHAT uses `4dev`
mapped to `Default`. Use bundled Chrome control only. Never inspect cookies,
local storage, passwords, profile files, tokens, or session internals. Never
substitute in-app/isolated Chrome, standalone Playwright, Page Agent, or
Computer Use.

## 2. Bootstrap once

Discover the Node-backed browser-control tool. Import bundled
`scripts/browser-client.mjs` by absolute path, initialize only if no runtime
exists, obtain the extension browser binding, and emit/read the complete
`chrome.documentation()` once. Reuse the browser binding.

Tab bindings are disposable. List tabs, claim the exact target, and reacquire a
tab if stale/closed. Do not recreate the browser merely because a tab is gone.

## 3. Prove the real session

Record claimed URL/title and visible authenticated navigation/account cues,
such as Conversations, Users, Chatbot, Articles, and Reports. Login state,
`about:blank`, process presence, cached profile metadata, or an isolated context
is not authenticated-profile proof.

## 4. Define the proof matrix

For each surface list route/role, expected regions/controls/options,
hidden/disabled conditions, safe interactions, unsafe trace-only actions,
desktop/mobile, keyboard/focus/ARIA, optional console/network facts, external
readback for authorized tests, and the PASS/PARTIAL/BLOCKED predicate.

## 5. Extract privacy-safe DOM/ARIA

Allowlist structural facts:

- tag, role, accessible name, input type;
- `aria-expanded`, `aria-selected`, `aria-disabled`, `aria-checked`;
- disabled, required, read-only, hidden;
- option order and visible conditions;
- dialog/drawer ownership and focus behavior;
- secret-safe action/route identifiers.

Never retain raw DOM dumps. Exclude conversation, contact, phone/email, avatar,
attachment, and free-form customer regions. Replace unavoidable content with
`[CUSTOMER_REDACTED]`, `[PHONE_REDACTED]`, `[EMAIL_REDACTED]`,
`[MESSAGE_REDACTED]`, or `[SECRET_NOT_READ]`.

## 6. Classify before clicking

Potentially safe only when no persistence effect is expected:

- navigation tabs;
- accordion expansion;
- menu/dropdown reveal;
- modal/drawer opening;
- read-only filters;
- responsive inspection.

Unsafe or unclear:

- send/broadcast/upload/save/create/publish;
- assign/status/archive/delete/clear/logout;
- synchronize/reconnect/disconnect/revoke;
- provider/AI/call/billing actions;
- any effect not yet traced.

For unsafe controls, record locator/conditions/state, inspect safe DOM/action
metadata, trace CSS/JS/request/source/backend/persistence/provider/retry/receipt,
and mark `SOURCE_TRACED_NOT_CLICKED` plus `NOT_EXECUTED_UNSAFE`.

## 7. Capture a safe interaction

1. Take a sanitized pre-state.
2. Activate once.
3. Record immediate transition.
4. Take a sanitized post-state.
5. Close/revert the presentation state when safe.
6. Record error, focus, Escape, and restoration behavior.

Never infer backend success from a visual transition.

## 8. Responsive and accessibility

Cover desktop/mobile, overflow, reachable actions, control order/labels,
Tab/Shift+Tab/Enter/Space/Escape, visible focus, modal focus containment/return,
ARIA expanded/selected/disabled, and empty/loading/error/retry/offline/reconnect.
Unreachable unsafe states remain partial and are mapped by source.

## 9. Screenshots

Default to none for ordinary behavioral evidence. For frontend adoption,
visual parity, screenshot-led reconstruction, or an owner request to match a
reference, screenshots are required when privacy-safe capture is possible.

Add verified opaque client-side masks over every
customer/content/credential region before capture. Persist only the masked
image—never an unmasked precursor. Manifest path, SHA-256, bytes, viewport,
URL, time, state, mask regions and linked denominator IDs.

Capture reference and native states at identical viewports. Produce
side-by-side and overlay/diff evidence plus a mismatch ledger. Omit an image if
masking is unproved, mark the dependent visual state `NO_SCREENSHOT_SAFE`, and
do not claim parity for that state.

## 10. Authorized live tests

Require explicit action-specific authority naming source conversation/channel,
destination/readback, permitted action/count, synthetic marker pattern,
prohibited actions, and receipt path.

Use one unique non-customer marker:
`E2I-<channel>-<UTC timestamp>-<short random suffix>`. Perform the minimum
action once. Verify UI acceptance, source status, external readback, safe
timestamps/IDs, no duplicate, and failure behavior without automatic resend.

Never record recipient identifiers, customer messages, tokens, headers, request
bodies, provider secrets, or content beyond the synthetic marker. Authority for
one send does not authorize templates, bulk, settings, uploads, assignment,
deletion, reconnect, or another channel.

## 11. Failures and closeout

One route failure is not global failure. Try one structurally different allowed
route, such as same-profile DevTools for a read-only fact. Never use a different
profile to claim PASS.

If the required profile is unavailable, mark dependent rows `BLOCKED_4DEV` and
continue Sheet, public docs, licensed source, available DOM/JS, and native
mapping. Return PARTIAL when only live evidence remains.

Record routes, role/profile, facts, safe clicks, unsafe controls, live tests,
console/network scope, responsive/accessibility coverage, privacy policy, gaps,
and browser/tab cleanup. Browser proof never replaces backend, permission,
test, provider, or deployment proof.
