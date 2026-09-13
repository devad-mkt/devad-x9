---
name: z-dokploy
description: Use when operating or diagnosing Dokploy MCP, API, or CLI, especially Authentication failed, HTTP 401 or 403, stale credentials, deployments, applications, PostgreSQL or Redis resources, domains, logs, and health checks.
---

# zDokploy

## Core rule

Separate the MCP client from the Dokploy server. An MCP authentication error proves only that the MCP process failed authentication. Do not retry it repeatedly or claim Dokploy is unavailable until a narrow direct API check resolves the boundary.

## Required sequence

1. Record the exact server URL, requested read or mutation, resource type, and internal resource ID. Never substitute an app slug for an internal ID.
2. Prefer the official `mcp__dokploy__*` tool for the requested operation.
3. On `Authentication failed`, stop MCP retries. Confirm that `DOKPLOY_URL` and `DOKPLOY_API_KEY` are configured without displaying either value. A stdio MCP process keeps the environment it received at startup.
4. With an owner-approved credential already held securely, test:

```powershell
$headers = @{ 'x-api-key' = $env:DOKPLOY_API_KEY }
$response = Invoke-WebRequest -UseBasicParsing `
  -Uri "$env:DOKPLOY_URL/api/settings.getOpenApiDocument" `
  -Headers $headers -Method Get
[int] $response.StatusCode
```

5. Classify the result before taking another action.

| Evidence | Meaning | Next action |
| --- | --- | --- |
| Direct `200`, MCP `401` | MCP has stale or different credentials | Restart Codex/MCP, then retry once |
| Direct `401` | Key is invalid, expired, revoked, or for another server | Replace the credential and restart MCP |
| Direct `403` | Key is valid but lacks permission | Fix scope; do not rotate blindly |
| Direct `200`, resource `404` | Authentication works; endpoint or ID is wrong | Re-resolve the internal ID |
| Network or TLS failure | Connectivity or server-route problem | Diagnose DNS, TLS, proxy, and health |

Use `/api/settings.getOpenApiDocument`, not the obsolete `/api/trpc/settings.getOpenApiDocument`, as the authentication sentinel. Swagger redirects are not an authentication test.

## Safe operation

- Keep credentials in approved secret configuration or process memory. Never place them in a skill, repository, chat, Google Sheet, screenshot, command argument, or proof artifact.
- Do not print headers, environment values, full OpenAPI documents, full application objects, environment payloads, or broad logs. Return only exact IDs, status, branch or SHA, timestamps, health, and short sanitized errors.
- Default to narrow GET/read operations. Perform writes only when the owner explicitly requested that exact mutation.
- Treat cleanup, delete, drop, prune, credential rotation, and service removal as destructive. Apply the active repository destructive-action guard; never infer authorization from a successful read.
- If direct API fallback is necessary, use the same official endpoint and schema the MCP exposes. Do not invent tRPC wrappers or alternate authorization headers.

## Source and semantic deploy gate

Deploy only an exact reviewed integration SHA. If the release reconciles an
owner-approved predecessor or divergent branch, first prove at that SHA that
the decisive paths or semantic regression survived integration. Commit
reachability, a conflict-free merge, CI, and a healthy prior deployment are
not that proof.

After deployment, verify the exact deployed SHA and the requested visible or
API behavior. Keep source merge, deployment, health, and live semantic proof
as separate states. Do not deploy a historical feature branch wholesale to
repair one regressed surface.

## Completion

State separately: MCP status, direct API status, target resource proof, mutation status, deployment status, and live health. A working API does not prove a deployment, and a deployment does not prove live behavior.

## Preserved capabilities (merged 2026-09-12)

Unique content recovered from archived variants. The canonical body above
wins where they overlap; these sections are the non-overlapping remainder.

### From `CODEX__dokploy`

## Owner-approved cleanup/delete exception
For Devad/X9 test and proof work, Dokploy access is not create-only. Deleting
or cleaning up exact disposable resources is allowed when all conditions below
hold:
1. The target is an exact worker/proof-owned disposable resource, nonce residue,
test service, test database, temporary runner, temporary network, or
rollback-owned artifact; or the owner explicitly names the exact production
or Stage1 target to delete.
2. The worker has bound the exact internal ID/name plus resource type, project
or environment, purpose, creation/ownership evidence, and stop condition.
3. The action is the narrowest cleanup for that exact target only. No prefix,
wildcard, broad project/environment prune, inferred sibling cleanup, raw
config/env/log read, or credential projection.
4. The surface is already authorized and available: official Dokploy API/MCP,
authenticated owner Chrome profile, or owner-approved Tailscale/host route.
5. The receipt is marker-only: deleted/absent/released state, target identity
hash or sanitized ID, timestamp, and residue check. Do not output secrets,
environment, raw logs, DSNs, passwords, tokens, or broad object payloads.
Deletion failure blocks only that cleanup row. Try at most one structurally
different authorized cleanup surface when it preserves the exact target and
does not expose secrets. If deletion still cannot be performed by the worker,
record a user cleanup reminder instead of looping:

```text
USER_CLEANUP_REMINDER:
TARGET_TYPE:
TARGET_ID_OR_NAME:
SAFE_SURFACES: Dokploy API | authenticated Chrome profile | Tailscale host route
WHY_WORKER_COULD_NOT_DELETE:
POST_DELETE_RECEIPT_NEEDED:
Do not classify the product/source goal as blocked when only disposable cleanup
or nonce residue remains and the exact cleanup reminder/receipt is recorded.


## Provenance (consolidated 2026-09-12)

Canonical body: `z-dokploy` (2026-08-13 00:38:44, 2 files, sha256 `c0efc03c6cc49f9f`).

Former names now disabled: `CODEX/dokploy`, `NINELLC/dokploy`.

Unique content from disabled copies is preserved under `references/preserved/` and is NOT authoritative; this body wins on any conflict.
