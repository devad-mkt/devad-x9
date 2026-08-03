---
name: chrome-control
description: Unified browser-control router for authenticated Chrome-profile evidence, local web-app testing, public web fetching, DOM/ARIA inspection, screenshots, console and network diagnostics, Lighthouse and performance traces, and final-fallback Page Agent recovery. Use whenever Codex must choose among bundled Chrome control, the Codex in-app Browser, Chrome DevTools MCP, or Page Agent, especially for authenticated Devad, n8n, Dokploy, site.devad.io, chat.devad.io, or post.devad.io work.
---

# Unified Chrome Control

## Non-Negotiable Authentication Rule

**I will not use the isolated DevTools browser for authenticated evidence.**

For authenticated sites—including `devad.io`, `n8n`, Dokploy,
`site.devad.io`, `chat.devad.io`, and `post.devad.io`—use the real Chrome
profile named by the owner in the current task. If none is named, use visible
profile `4dev`, currently mapped to Chrome directory `Default`.

The current task's explicit profile or browser choice overrides the default.
Resolve a visible profile through Chrome `Local State`; never treat an MCP
`isolatedContext` with the same label as the real profile. Prove the session
with the live URL/title and visible authenticated UI cues. Login redirects,
`about:blank`, cookies, profile files, process presence, or cached metadata are
not authenticated evidence.

## Fast Route by Use Case

Choose one route once. Do not initialize every browser surface.

| Use case | First route | Escalation | Time/token rule |
| --- | --- | --- | --- |
| Authenticated UI evidence or action | Bundled Chrome control attached to the named real profile | Same-profile CDP/DevTools only when attachment is proven; Page Agent last | Reuse one browser binding and one target tab; capture only decisive evidence. |
| Local server or unauthenticated app testing | Codex in-app Browser | Isolated DevTools for console/network/DOM/Lighthouse/performance | Use the in-app Browser for interaction; add DevTools only for diagnostics it uniquely answers. |
| Public page or web fetching | Connector/API/web fetch when semantic access is enough; otherwise Codex in-app Browser | Isolated DevTools for rendered or diagnostic facts | Avoid browser startup when direct fetching answers the question. |
| DevTools/MCP setup or repair | Chrome DevTools MCP smoke test | Read the archived DevTools manual | Do not open an authenticated target to prove server health. |
| Real-profile Chrome bridge failure | One bounded Chrome troubleshooting pass | Page Agent final fallback | Record the concrete blocker; do not loop or start Page Agent speculatively. |

Explicit browser intent wins. If the owner explicitly says Chrome, Browser,
DevTools, or Page Agent, use that surface while preserving the authentication
rule. A URL alone does not require UI automation: prefer a purpose-built
connector, API, CLI, or web fetch when it can answer the request.

## Authenticated Chrome Workflow

1. Discover the bundled Chrome browser-control runtime and reuse an existing
   Chrome binding when present.
2. Obtain the extension/real-profile browser binding and read its complete
   runtime documentation once before first interaction.
3. Confirm the binding reports the requested profile. Default to `4dev` only
   when the current task names no other profile.
4. List tabs read-only, select the exact target, and reacquire a stale tab
   rather than recreating the browser.
5. Gather the smallest evidence that proves the requested fact: URL/title,
   sanitized DOM/ARIA state, screenshot, console/network fact, or authorized
   interaction result.
6. Never inspect cookies, passwords, local storage, tokens, headers, or session
   stores. Never switch to isolated DevTools to bypass sign-in.
7. If sign-in is missing in the required real profile, ask the owner to sign in
   there. Do not substitute search results or a different profile.

For authenticated evidence, a same-profile DevTools attachment is acceptable
only when the endpoint is positively attached to that real profile. An isolated
DevTools browser remains prohibited.

## Local, Public, and Diagnostic Workflow

Use the Codex in-app Browser for local UI interaction and ordinary rendered
page inspection. Use isolated DevTools only for unauthenticated/local/public
work where its unique capabilities are needed:

- DOM snapshots and screenshots;
- console messages and network requests;
- script evaluation;
- Lighthouse audits;
- performance traces.

Label evidence with the actual surface used. Do not infer persistence,
deployment, provider delivery, or authentication from a visual state alone.
Results subject to variance or incomplete attachment remain `PARTIAL` or
`UNKNOWN`, not PASS.

## Action Safety

Start read-only. Opening menus, tabs, accordions, or read-only filters is
normally safe when no persistence is expected. Sending, saving, publishing,
creating, uploading, assigning, archiving, deleting, reconnecting, changing
permissions, billing, provider actions, and unclear controls require explicit
action authority. A timeout after a side-effecting action is `UNKNOWN`; inspect
state before replay.

Do not interrupt the owner's active Chrome window with focus, typing, mouse,
navigation, or screenshots unless the owner requested visible interaction or
approved foreground control. Prefer background-safe tab control.

## Page Agent Final Fallback

Use Page Agent only after one bounded check shows the bundled Chrome route is
unavailable or unusable and the task still requires real-profile control.

1. Record the Chrome blocker; do not retry it in a loop.
2. Read the archived Page Agent manual and its task-matching reference.
3. Check status before starting work. Require `connected: true` and
   `busy: false`.
4. Run one bounded task with target, allowed actions, forbidden actions, and
   return data.
5. Require a harmless live result before claiming browser control.
6. Treat timed-out side effects as `UNKNOWN` and clean up only the process tree
   started by this route.

Never kill all Node processes, enable permanent hub auto-approval, or expose
provider keys, cookies, tokens, headers, or browser storage.

## Preserved Capability Manuals

The three former entrypoints are disabled, but their detailed features and
recovery procedures are preserved:

- Read [Chrome plugin manual](references/chrome-plugin.md) for runtime
  bootstrap, browser selection, tab lifecycle, and troubleshooting.
- Read [DevTools MCP manual](references/devtools-mcp.md) for configuration,
  smoke tests, screenshots, DOM, console, network, Lighthouse, performance,
  and real-profile attachment diagnostics.
- Read [Page Agent manual](references/page-agent.md) only after the final
  fallback gate opens. Resolve its `./scripts`, `references/`, and `lessons/`
  paths against
  `<CODEX_HOME>\skills\controlling-chrome-with-page-agent`.

## Honest Closeout

Report the browser surface, real profile when relevant, target URL, actions
taken, evidence gathered, authentication status, and exact blocker or unknown.
Do not claim authenticated evidence from an isolated or in-app browser.
