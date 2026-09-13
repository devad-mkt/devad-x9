---
name: controlling-chrome-with-page-agent
description: Use only as the final browser-control fallback after the bundled Chrome plugin, Chrome DevTools MCP, and the Codex in-app Browser are unavailable or fail; then start, operate, or recover Alibaba Page Agent/@page-agent/mcp and diagnose hub/localhost 38401/EADDRINUSE/no-tabs failures.
---

# Control Chrome with Page Agent

> Disabled as a standalone skill. Use
> `$CODEX_HOME\skills\z-browser\SKILL.md`.
> I will not use the isolated DevTools browser for authenticated evidence.

Page Agent is the fourth and final browser-control route. Never start, probe, register, or recover its server as the default response to a browser task. Resolve paths relative to this `SKILL.md`.

## Mandatory route order

An explicit user choice of browser surface overrides the default order. Otherwise, try exactly these routes in order:

1. Use `[@Chrome](plugin://chrome@openai-bundled)` through `chrome:control-chrome`.
2. Use the configured `chrome-devtools` MCP through `$chrome-devtools-mcp`.
3. Use the Codex in-app Browser through `browser:control-in-app-browser`.
4. Only after the first three routes are unavailable or fail, enter the Page Agent fallback below.

Give each route one bounded availability and connection check. Switch routes only for a concrete blocker such as a missing tool, failed connection, wrong browser context, missing authentication, or missing required capability. Do not call `page-agent` tools, run `page-agent-tools.ps1`, or probe localhost port `38401` while routes 1-3 remain viable.

## Page Agent fallback

1. Record the concrete blockers from routes 1-3. Do not retry them in a loop.

2. Search lessons before repeating research:

   ```powershell
   rg -n -i '<goal|component|symptom>' lessons
   ```

   Open only the one to three closest matches. Read [lessons/protocol.md](lessons/protocol.md) before recording a new lesson.

3. Check local truth only after the fallback gate has opened:

   ```powershell
   & ./scripts/page-agent-tools.ps1 -Action Check -ProfileName '4dev' -Json
   ```

   Require Node 20+, the expected profile/extension, and either a free port or one positively identified Page Agent owner. A filesystem manifest proves installation, not that Chrome enabled the extension.

4. Reuse server-qualified native tools when they are already exposed:

   - Call `page-agent:get_status` first.
   - Require `connected: true`; require `busy: false` before starting work.
   - Call `page-agent:execute_task` with explicit target, allowed actions, forbidden actions, and requested return data.
   - Use `page-agent:stop_task` when the user asks to stop or a bounded operation must be cancelled.

5. Start or reuse the bundled Page Agent server only when native tools are absent or unusable:

   ```powershell
   & ./scripts/page-agent-tools.ps1 -Action Probe -ProfileName '4dev'
   & ./scripts/page-agent-tools.ps1 -Action Task -ProfileName '4dev' -Task '<bounded task>'
   ```

   The client pins the tested package, reuses a positively identified Page Agent owner when safe, otherwise starts the hub in the named Chrome profile, verifies all three tools, bounds waits, and cleans only its own process tree.

6. Verify the outcome. `connected: true` proves only the hub WebSocket. Require a real task result for browser-control claims. Treat a timed-out side-effecting task as `UNKNOWN`; inspect page state before replaying it.

## Setup and recovery

Register only when the user authorizes persistent MCP configuration:

```powershell
& ./scripts/page-agent-tools.ps1 -Action Register
```

Preview orphan recovery first. Confirm termination only after the script positively identifies the listener as Page Agent:

```powershell
& ./scripts/page-agent-tools.ps1 -Action Recover -Json
& ./scripts/page-agent-tools.ps1 -Action Recover -ConfirmKill -Json
```

Never kill all `node.exe` processes. Never enable permanent hub auto-approval. Never print or save provider keys, cookies, tokens, headers, or browser storage.

## References

- Read [references/official-protocol.md](references/official-protocol.md) for architecture, tools, profile routing, version policy, and primary sources.
- Read [references/troubleshooting.md](references/troubleshooting.md) after a reproducible failure.
- Use [lessons/_template.md](lessons/_template.md) only after a new reusable path or fix has live proof.

## Common mistakes

| Mistake | Corrective action |
|---|---|
| Assume `4dev` is a directory | Resolve Chrome `Local State`; here it currently maps to `Default`. |
| Treat status as end-to-end proof | Run a harmless live round trip. |
| Replay after timeout | Inspect state first; report `UNKNOWN` meanwhile. |
| Treat a UUID as a hub credential | The documented bridge uses a numeric localhost port, not a UUID. |
| Diagnose Page Agent from OpenAI-extension CSP alerts | Keep the two extension paths separate. |
