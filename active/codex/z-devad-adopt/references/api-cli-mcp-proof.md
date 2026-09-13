# API, CLI, And MCP Proof

Use this reference when an adoption claims API, CLI, MCP, agent, or external automation support.

## Authority

The Laravel API/service layer is the write authority. CLI and MCP are thin wrappers around the same API client, validator, and permission model. Do not let CLI, MCP, browser scripts, Node tools, sidecars, or external agents write directly to providers or bypass CORE services.

## Live Write Gates

Any live write must require explicit gates appropriate to the feature, such as:

- `--live`,
- `--confirm-live-write`,
- an environment allow flag,
- workspace API key or authenticated workspace user,
- idempotency key,
- queue/status tracking,
- permission and scope checks.

Dry-run mode must never call providers, debit credits, mutate external systems, or imply success.

## PASS Semantics

- `PASS`: API/service success plus external proof where applicable.
- `API_POST_CREATED` or equivalent: internal create succeeded but external proof is not complete.
- `API_ONLY_PENDING_EXTERNAL`: external proof could not be checked safely.
- `PARTIAL`: some layers work, but parity or proof is incomplete.
- `BLOCKED`: missing source evidence, credentials, approval, callbacks, scopes, permissions, or safety gates.

## Progress Ledger

Every feature/provider/variant needs a ledger row, including unsupported variants. Minimum columns:

```text
feature/provider | source proof | backend proof | browser proof | API proof | CLI proof | MCP proof | status | blocker
```

Do not silently skip unsupported providers or hidden features.

## MCP Rules

- MCP tools must expose dry validation/progress/payload helpers first.
- MCP live tools must be absent or hard-gated until API security and live-write proof are accepted.
- MCP proof is not UI text saying "MCP supported." It requires a callable tool contract or documented mock with tests.

## Secret Safety

Never write API keys, OAuth tokens, cookies, raw provider responses, `.env`, customer logs, session headers, or full callback URLs with secrets into progress docs, payload templates, screenshots, sidecar packets, or Git.
