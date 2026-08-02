# Devad Adoption Gates

Use this reference for any source-to-CORE/X9 feature adoption.

## Source Authority

Use this order unless the task gives a stricter one:

1. Live app/browser behavior for current UX, text, states, and workflow.
2. Current source code for routes, controllers, views/components, models, migrations, request payloads, and backend effects.
3. Older reference apps or branches when current source is incomplete or suspicious.
4. Official provider/vendor docs for money, OAuth, billing, API, compliance, and provider behavior.
5. Native CORE runtime, tests, and browser proof as the only authority for what is implemented.

Reference apps are evidence. They are not architecture to transplant.

## Evidence Packet

Before implementation, create or update this packet shape:

```text
adoption-packets/<feature>/
  MANIFEST.md
  TASK.md
  source-controls.json
  local-controls.json
  parity-matrix.json
  action-contracts.json
  browser-proof.json
  backend-proof.json
  progress-ledger.json
  proof-checklist.md
```

Then capture:

- screenshots for source and local CORE, including modal, wizard, empty, error, success, mobile, and dark/light states when relevant,
- DOM, ARIA, or JSON summaries for labels, buttons, selects, options, toggles, tables, headings, links, disabled states, and validation text,
- interaction map for clicks, dropdowns, toggles, submit behavior, redirects, toasts, and failure states,
- AST/source map for routes, controllers, views/components, models, migrations, services, jobs, commands, and config,
- payload/backend map for request fields, validation, persistence target, credit/billing/provider effect, and async jobs,
- permission map for admin/user/workspace access and cross-workspace isolation.

If source evidence is missing, mark `BLOCKED_NO_SOURCE_EVIDENCE`. If live screenshot evidence is missing, mark `BLOCKED_NO_LIVE_SCREENSHOT` and do not call the feature production parity.

Implementation is forbidden until at least one failing proof test exists for the selected vertical slice. If the test passes before implementation, the test is fake or the scope is wrong.

## Control And Action Contracts

Every visible interactive control needs an entry in `action-contracts.json`:

```json
{
  "control_key": "writer.generate",
  "source_control": "button:Generate",
  "local_control": "button:Generate",
  "route": "POST /workspaces/{workspace}/ai/content-lab/generate",
  "request_fields": ["template", "company_id", "product_id", "title", "keywords"],
  "validation": ["workspace scoped", "credits sufficient"],
  "service": "ContentLabGenerationService",
  "persistence": ["ai_documents", "ai_usage_ledger"],
  "provider_effect": "dry-run none; live via Laravel AI only",
  "tests": ["ContentLabGenerationTest.php", "content-lab-writer.spec.ts"],
  "status": "PASS|PARTIAL|BLOCKED"
}
```

A visible interactive control without an action contract is a bug. Hide it or mark the slice `PARTIAL` or `BLOCKED`.

## Acceptance Gates

Reject a done claim unless the slice has:

- parity table: source control vs CORE control vs missing vs status,
- screenshot proof before and after implementation,
- DOM or ARIA proof for controls, dropdowns, modals, filters, empty states, and table actions,
- visual proof using Playwright screenshot comparison, Dusk/browser screenshots, or an explicitly documented fallback,
- backend proof that UI actions call real CORE services,
- tests for permissions, workspace isolation, validation, success, and failure,
- browser proof with console/log check,
- API/CLI/MCP proof when the feature claims agent/tool support,
- security proof: no secrets in artifacts and no cross-workspace leaks,
- missing disclosure with honest `PASS`, `PARTIAL`, or `BLOCKED`.

## Adoption Caps

- Missing source screenshot, DOM, or control inventory: `BLOCKED`, 0%.
- UI scaffold only, no backend action contracts: `PARTIAL`, max 35%.
- UI plus backend route, no browser proof: `PARTIAL`, max 60%.
- UI plus backend plus tests, no source parity matrix: `PARTIAL`, max 75%.
- Missing workspace or permission proof: `PARTIAL`, max 70%.
- Money, provider, billing, token-pack, or live-write behavior unproven: no live `PASS`.
- `PASS` requires scoped source, browser, backend, permission, test, and security proof.

Calculate adoption as:

```text
passed_material_items / required_material_items * 100
```

Material items include controls, routes, payload fields, validation, persistence, provider or queue effects, permissions, states, and tests. Cosmetic polish alone does not count.

## PixelRAG

PixelRAG may be used only as development evidence capture/search:

- sanitized screenshot tiles,
- visual hierarchy and density evidence,
- search across many reference screenshots,
- `tiles.json` stored under the adoption packet.

Do not use PixelRAG for `PASS`, backend/API proof, billing/token/provider proof, workspace isolation, or replacing Playwright, Dusk, Laravel tests, or browser proof. Do not store cookies, sessions, OAuth codes, API keys, provider responses, or raw production data in PixelRAG artifacts.

Optional capture when PixelRAG is available:

```bash
uv tool install pixelrag
mkdir -p adoption-packets/$FEATURE/source-pixelrag
pixelshot "$SOURCE_URL" --output adoption-packets/$FEATURE/source-pixelrag
```

For local authenticated CORE pages, retry with a login-chain capture before giving up:

```bash
pixelshot "http://127.0.0.1:<port>/local-dev-login/superadmin" "http://127.0.0.1:<port>/<protected-target>" --output adoption-packets/$FEATURE/local-pixelbrowse --tile-height 1568 --wait-network-idle --viewport-width 1280 --workers 1 --backend cdp
```

Use this only for local proof. For external authenticated source pages, do not store cookies, session headers, OAuth material, or API keys in PixelRAG artifacts. If PixelBrowse cannot authenticate safely, use browser/Chrome screenshot plus DOM summaries and mark the PixelBrowse limitation.

## Stop Conditions

Stop instead of guessing when:

- screenshots/DOM/interactions are missing for a visible feature,
- payload or backend effect is unknown,
- a worker exposes placeholders or fake tabs,
- secrets or raw provider data would enter artifacts,
- money, token-pack, shared-credit, billing, or provider debit behavior is unproven,
- live provider calls or external writes are not explicitly gated,
- workspace scoping or permission behavior is unclear,
- implementation would overwrite unrelated Devad work.
