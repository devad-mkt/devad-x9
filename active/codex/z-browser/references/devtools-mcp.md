---
name: chrome-devtools-mcp
description: Use when Codex needs to use, test, repair, or explain the local Chrome DevTools MCP server named chrome-devtools, especially for Chrome page inspection, screenshots, DOM snapshots, console logs, network requests, Lighthouse, or performance traces.
---

# Chrome DevTools MCP

> Disabled as a standalone skill. Use
> `$CODEX_HOME\skills\z-browser\SKILL.md`.
> I will not use the isolated DevTools browser for authenticated evidence.

## Overview

Use the configured `chrome-devtools` MCP server for Chrome DevTools Protocol inspection through MCP. Keep it separate from the Codex in-app browser and the bundled Chrome plugin; this server is a standalone MCP process launched from `$CODEX_HOME\config.toml`.

## Local Setup

Expected config entry:

```toml
[mcp_servers.chrome-devtools]
command = "cmd"
args = [ "/c", 'set PATH=$LOCAL_APP_DATA\Local\OpenAI\Codex\runtimes\cua_node\1b23c930bdf84ed6\bin;%PATH%&& npx -y chrome-devtools-mcp@latest' ]
startup_timeout_sec = 120
```

The `PATH` prefix is required on this machine because `npx.cmd` needs `node` on `PATH`. Do not replace this with bare `npx` unless `cmd /c npx --version` works in the current shell.

## Profile Defaults

Default personal Chrome profile on this machine:

| Visible Chrome profile | Chrome profile directory | User data directory |
| --- | --- | --- |
| `dev` | `Default` | `%LOCALAPPDATA%\Google\Chrome\User Data` |

Treat `dev` as the user's default Chrome profile unless the user explicitly names another profile. Do not use MCP `isolatedContext: "dev"` as a substitute; isolated contexts are separate temporary storage, not Chrome profiles.

Fast profile lookup:

```powershell
$localState = Join-Path $env:LOCALAPPDATA 'Google\Chrome\User Data\Local State'
$json = Get-Content -LiteralPath $localState -Raw | ConvertFrom-Json
$json.profile.info_cache.PSObject.Properties |
  Where-Object { $_.Value.name -eq 'dev' } |
  Select-Object @{Name='Directory';Expression={$_.Name}}, @{Name='Name';Expression={$_.Value.name}}
```

Fast open in the real `dev` profile when the user asks to open a page and MCP control is not required:

```powershell
Start-Process -FilePath 'C:\Program Files\Google\Chrome\Application\chrome.exe' -ArgumentList @('--profile-directory=Default','https://devad.io')
```

For a different URL, replace only the URL argument. This may focus Chrome, so use it only when the user asked to open a page, not for background proof while the user is working. Verify with visible Chrome window titles or a Chrome-control tool; do not use cached profile files as proof of current page state.

## Background-Only Rule

Default to non-interrupting browser work. Do not click, type, focus, minimize,
restore, move, or navigate the user's active Chrome window while they are using
the PC.

Preferred order:

1. Use an existing Chrome DevTools Protocol endpoint for the real profile, such
   as `http://127.0.0.1:9222`, and control pages in the background.
2. Use exposed MCP tools only when they are connected to the intended browser
   context. If MCP opens an isolated browser or redirects to login, record
   `TOOL_FAILED:chrome-devtools-mcp:not-authenticated` and switch route.
3. If no background CDP/MCP route exists, stop with a clear tool blocker. Do
   not fall back to Windows mouse/keyboard automation unless the user explicitly
   allows foreground interruption for that action.

Background-safe checks:

```powershell
foreach ($port in 9222,9223,9224) {
  try {
    Invoke-WebRequest -Uri "http://127.0.0.1:$port/json/version" -UseBasicParsing -TimeoutSec 2
  } catch {
    "port_$port=closed"
  }
}
```

If a separate visible Chrome window is explicitly allowed, open it with
`--new-window` and restore the previously foreground window immediately. Treat
this as a brief-interruption fallback, not background proof.

## Verification

After config changes, expect the current Codex session not to hot-load new MCP tools. Restart Codex or open a fresh thread, then search for `chrome-devtools`.

Direct stdio smoke test:

```powershell
cmd /c "set PATH=$LOCAL_APP_DATA\Local\OpenAI\Codex\runtimes\cua_node\1b23c930bdf84ed6\bin;%PATH%&& npx -y chrome-devtools-mcp@latest --version"
```

Known-good version from setup: `1.5.0`.

Use an MCP initialize/list-tools smoke test when the question is whether the server itself works. A passing server exposes tools including `list_pages`, `new_page`, `navigate_page`, `take_snapshot`, `take_screenshot`, `evaluate_script`, `list_console_messages`, `list_network_requests`, `lighthouse_audit`, `performance_start_trace`, and `performance_stop_trace`.

Real-profile MCP control is different from opening a page in Chrome. If Chrome is already running with `%LOCALAPPDATA%\Google\Chrome\User Data`, DevTools MCP launched with that user-data directory may return:

```text
The browser is already running for $LOCAL_APP_DATA\Local\Google\Chrome\User Data. Use --isolated to run multiple browser instances.
```

That means MCP cannot take over the live personal profile through a second launch. To use MCP against the real `dev` profile, start Chrome in a debuggable mode first or close Chrome so MCP can launch the profile. Do not silently fall back to an isolated MCP profile when the user asked for the personal `dev` profile.

## Local Lessons Learned

- Visible profile `dev` maps to Chrome profile directory `Default`.
- MCP `about:blank` or an MCP page redirected to `https://devad.io/login` is not
  authenticated proof for the user's `dev` profile.
- Starting Chrome with `--remote-debugging-port=9222` while the real `Default`
  profile is already running can reuse the existing process and still leave
  `127.0.0.1:9222` closed.
- Missing `%LOCALAPPDATA%\Google\Chrome\User Data\Default\DevToolsActivePort`
  means there is no easy real-profile DevTools endpoint to attach to.
- Windows UI Automation may see the Chrome shell/title but not page controls.
  It is not reliable proof for modal labels or row controls.
- `SendKeys`, mouse clicks, `SetForegroundWindow`, `ShowWindow`, and screenshot
  capture of a visible window can interrupt the user's work. Do not use them
  while the user is active unless the user explicitly approves foreground
  control.
- Chrome process `MainWindowTitle` changes with the active tab, so do not rely
  on a title like `AI Tasks - CORE` after navigating or when multiple tabs are
  open.
- `Get-Process chrome` is not enough to count separate Chrome windows because
  Chrome may expose only one main process/window title. Use top-level Win32
  window enumeration for class `Chrome_WidgetWin_1` to verify a separate
  Devad/Codex window exists and that the user's active window stayed foreground.

## Usage Pattern

1. Prefer exposed MCP tools when available in the current tool list.
2. If the user asks for profile `dev`, resolve it to Chrome profile directory `Default` before opening or controlling anything.
3. Check whether the route is background-safe. A CDP endpoint or MCP connection
   to the intended profile is background-safe; foreground mouse/keyboard control
   is not.
4. Start read-only with `list_pages` or equivalent page listing.
5. Select or open a page only when the user asked for browser inspection or verification and the route will not disturb their active window.
6. Gather the smallest evidence that answers the task: URL/title, snapshot, screenshot, console logs, network request, Lighthouse result, or performance trace.
7. Report whether evidence came from live MCP tools, real-profile Chrome, a direct server smoke test, or a foreground fallback.

## Boundaries

- Do not treat this as the Codex in-app browser. It launches or connects to Chrome through Chrome DevTools MCP.
- Do not claim the MCP is available inside the current Codex session until tool discovery exposes its tools.
- Do not use cached browser profile files as proof of current page state.
- Do not use `isolatedContext: "dev"` when the user asks for their Chrome profile `dev`; use `--profile-directory=Default` for the real profile.
- Do not use the user's active Chrome window for proof, clicks, typing, or
  navigation while they are working. Stop and report a background-control
  blocker instead.
- Do not use Windows UI Automation, `SendKeys`, mouse events, or foreground
  screenshot capture as a silent fallback. These are foreground-control tools
  and need explicit user approval for interruption.
- Do not submit destructive, financial, permission-changing, account-creating, or third-party communication actions through the browser without explicit action-time confirmation.
