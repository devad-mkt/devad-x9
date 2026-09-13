---
name: devad-assistant
description: Devad sidecar routing card. Use when Codex should save tokens by delegating bounded plan, risk, checklist, migration, or frontend architecture review to direct headless CLI assistants while Codex keeps ownership of code, verification, safety, and final claims.
---

# Devad Assistant

Use this as a current-session sidecar router. It does not replace Codex judgment.

## Current Policy

- Use headless CLI only.
- Do not use ACP for OpenCode or PI.
- Do not use PI as an execution dependency.
- Do not use OpenRouter routes or OpenRouter model IDs.
- Use one sidecar by default. Multi-model fan-out needs explicit owner approval.
- Codex writes the packet, reviews the result, verifies locally, and owns all edits/tests/final claims.

## Active Routes

| Route | Use | Default phase |
| --- | --- | --- |
| `opencode run --model opencode-go/kimi-k2.7-code` | Coding-oriented migration plans, implementation options, risks, stop conditions | Plan/options |
| `opencode run --model opencode-go/glm-5.2` | Test matrix, acceptance gates, plan critique, checklist | Plan/checklist |
| `opencode run --model opencode/deepseek-v4-flash-free` | Free-model summary/check only when owner asks | Summary/checklist |
| `opencode run --model opencode/mimo-v2.5-free` | Free-model summary/check only when owner asks | Summary/checklist |

## Readiness

```powershell
opencode --version
opencode models | Select-String -Pattern "opencode-go/glm-5.2|opencode-go/kimi-k2.7-code"
```

Use the repo wrapper when present:

```powershell
.\.devad\tooling\opencode-cli\run-opencode-cli-packet.ps1 `
  -RepoRoot $DEVAD_ROOT\core-aio\core `
  -Packet .devad\features\<feature>\prompts\<packet>.md `
  -Model opencode-go/glm-5.2 `
  -Output .devad\features\<feature>\sidecar\<packet>-glm.md
```

If model-not-found, provider, auth, quota, credit, or max-token errors appear, record the route unavailable for the task and stop. Do not retry in a loop.

## Packet Shape

Send a saved full-context markdown packet, not a tiny inline prompt:

```markdown
# Task

## Goal
Concrete outcome.

## Workspace
- Target repo:
- Branch:
- HEAD:
- Dirty state:

## Allowed Files And Slices
- Path:

## Denied Areas
- No secrets.
- No .env.
- No deploys.
- No DB writes.
- No provider dashboards.
- No files outside the allowed list.

## Known Facts
- Verified local facts only.

## What Codex Already Tried
- Command/evidence:

## Required Output
- Plan/options or checklist only.
- Risks and stop conditions.
- Smallest safe next step.
- Tests/browser checks Codex should run.

## Phase Rule
PLAN/REVIEW ONLY. Do not code. Do not edit files. Do not run commands.
```

For any approved build packet, add an exact write scope and stop immediately on drift. Codex must inspect the diff and run local verification before trusting it.

## Good Uses

- Migration plan critique after Codex has local facts.
- Risk and stop-condition review.
- Frontend verification matrix before a UI edit.
- Failure-mode brainstorming after one local debugging attempt.
- Compact checklist or handoff drafting from a known diff.

## Safety

- Never send `.env`, tokens, passwords, private keys, cookies, raw production logs, customer data, provider secrets, or full old chat history.
- Never delegate production/staging deploys, SSH/server config, provider dashboard changes, live DB writes, tenant creation/deletion/reset, or final factual claims.
- Use local `rg`, file reads, tests, logs, browser evidence, and official docs as proof. Assistant output is advice only.

## Handoff Row

Every feature handoff that used a sidecar includes:

```markdown
| Model/tool | Route | Useful? | Misses/risks | Use again? |
| --- | --- | --- | --- | --- |
```
