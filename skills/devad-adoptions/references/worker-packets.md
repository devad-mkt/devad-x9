# Worker Packets And Sidecar Control

Use this reference when creating or reviewing work for Cursor, another Codex thread, OpenCode, Kimi, GLM, Gemini, or any sidecar worker.

## Compact Packet Shape

Every long-running worker packet must include:

- `MANIFEST.md` with source checksum or source list,
- `TASK.md` with current branch, base SHA, allowed scope, hard rules, read routes, execution order, and stop conditions,
- source evidence folder,
- gap/adoption matrix,
- progress ledger,
- allowed files,
- forbidden files,
- proof checklist,
- secret-safety rules.

Use split reference files for large plans. Do not send huge historical context blindly.

## Worker Rules

- Cursor and sidecars can analyze or implement bounded chunks, but Codex verifies.
- Ask workers for a plan first when scope is broad or risky.
- Give exact allowed files and stop conditions.
- Never send secrets, `.env`, cookies, OAuth codes, tokens, raw provider responses, raw production logs, or full customer data.
- Verify every useful worker claim locally against files, screenshots, DOM, tests, runtime logs, and browser proof.
- If a worker reports "done" without proof, treat it as `UNVERIFIED`.

## Merge Gate

Do not merge worker code into canonical CORE/X9 until:

- tests pass,
- browser proof exists,
- route/API proof exists,
- CLI/MCP proof exists when claimed,
- screenshots and DOM evidence are attached,
- no secrets are in artifacts,
- no unrelated work was reverted or overwritten,
- cross-thread file overlap is resolved.

## Manager Behavior

Managing workers is active verification, not summarization. On each check:

- classify the worker as working, idle, blocked, failed, completed, or drifting,
- inspect worktree status and changed files read-only first,
- compare against the main packet and source evidence,
- send concise correction if drifting,
- approve only the next compatible slice,
- report exact blockers and next action.
