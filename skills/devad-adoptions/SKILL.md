---
name: devad-adoptions
description: Evidence-gate Devad source-to-Core adoptions, migrations, parity work, reference UI, ai.devad.io, Creative Suite, Image/Video Agent, Content Lab, POST/StackPosts, provider integrations, API/CLI/MCP claims, and worker packets. Use to prevent obsolete framework ports, hardcoded settings, missing addon/UI denominators, or fake production-ready claims.
---

# Devad Adoptions

Use this skill to prevent fake Devad adoption claims. A feature is not adopted because a route renders, a static page exists, a tab label appears, or a worker says it is done. A feature is adopted only when source evidence, native CORE behavior, tests, browser proof, and API/CLI/MCP proof match the declared scope.

## Start

1. Read repo truth first: current branch, dirty files, worktree path, source target, canonical CORE target, and active feature packet.
2. Identify the adoption type and load only the needed reference:
   - General evidence gates: `references/adoption-gates.md`
   - POST/provider/channel work: `references/post-patterns.md`
   - API/CLI/MCP proof: `references/api-cli-mcp-proof.md`
   - AI Content Lab, MagicAI, ai.devad.io: `references/ai-content-lab-lessons.md`
   - Creative Suite, Image Agent, Video Agent, editor/addon work:
     `references/creative-suite-media-lessons.md`
   - Worker/Cursor/sidecar packets: `references/worker-packets.md`
3. Treat reference apps as evidence, not architecture. Rebuild natively in CORE/X9.

## Required Workflow

Run one vertical bundle at a time:

```text
adoption packet -> source evidence -> control/action matrix -> failing proof/test -> native CORE implementation -> browser/API/CLI/MCP proof -> progress ledger
```

Implementation is forbidden until the packet exists and at least one failing proof test exists for the selected vertical slice. If the test passes before implementation, the test is fake or the scope is wrong.

Before implementation, create or update:

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

Capture source screenshots, DOM/ARIA, interactions, AST/source routes, payloads, backend effects, persistence targets, and permission boundaries. If any user-visible feature lacks evidence, hide it or mark it blocked.

Before code, freeze current/deployed/licensed/addon/historical identities,
administrator plus user/workspace frontend settings, schemas, state machines,
dependency/component choice, production resource topology, and a bounded Work
Order with no architecture left for the implementer.

## Non-Negotiables

- Do not claim parity from route rendering, scaffold tabs, static screenshots, or UI contract text.
- Do not expose a visible tab, menu link, provider row, or admin page unless it is backed by real source evidence and native backend behavior.
- Do not delete or overwrite unrelated Devad work, especially AI Tasks, POST channels, pricing, sidebar, or existing docs.
- Do not let Cursor, sidecars, other Codex threads, or external models be final authority. Verify their claims locally.
- Do not write secrets, cookies, OAuth codes, raw API keys, `.env`, raw provider responses, or session data into docs, screenshots, JSON, prompts, packets, logs, or Git.
- Use adoption percentages honestly. If source has ten material controls and CORE has three, call it partial.
- Every visible interactive control needs an action contract. A visible control without a backend contract is a bug; hide it or mark the slice `PARTIAL` or `BLOCKED`.
- A marketplace listing, registration, menu, include, or historical branch is
  not proof that an addon is present or accepted.
- Treat old Laravel/Blade/Alpine/Passport/editor/renderer choices as historical
  until reconciled with current Core owners and settings.
- Separate UI engine, background renderer, AI provider, and automation API.
- Read both admin and frontend settings. A hardcoded UI value is a gap even
  when it matches the current screen.
- Use Playwright/Dusk/browser proof for visual and structural parity. Prefer screenshot comparison and ARIA/control snapshots when the project stack supports them.
- PixelRAG may be used only for sanitized visual evidence capture/search. PixelRAG evidence never counts as `PASS` without browser, backend, permission, test, and security proof.
- For local authenticated CORE pages, give PixelBrowse a real chance before fallback: run the local login URL immediately before the protected target URL in one `pixelshot` command with `--workers 1`, `--backend cdp`, `--tile-height 1568`, and `--wait-network-idle`. Do not save cookies, headers, sessions, or secrets; external authenticated source pages still need a safe browser/Chrome capture fallback.

## Adoption Caps

- Missing source screenshot, DOM, or control inventory: `BLOCKED`, 0%.
- UI scaffold only, no backend action contracts: `PARTIAL`, max 35%.
- UI plus backend route, no browser proof: `PARTIAL`, max 60%.
- UI plus backend plus tests, no source parity matrix: `PARTIAL`, max 75%.
- Missing workspace or permission proof: `PARTIAL`, max 70%.
- Money, provider, billing, token-pack, or live-write behavior unproven: no live `PASS`.
- `PASS` requires scoped source, browser, backend, permission, test, and security proof.

## Proof Output

Every adoption report must include:

- source URL and local CORE URL,
- screenshots and DOM evidence paths,
- feature/provider/status matrix,
- adoption percentage and missing items,
- backend/API/CLI/MCP proof status,
- tests run and exact result,
- blockers and stop conditions,
- explicit `PASS`, `PARTIAL`, or `BLOCKED`.

Use `scripts/validate_adoption_packet.py <packet-folder>` to sanity-check packet completeness before trusting a worker or calling a slice ready.
