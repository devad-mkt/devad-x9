---
name: oc-subs
description: Run a bounded OpenCode Go or Zen worker through the local OpenCodex proxy. Use when a task needs an external OpenCode model such as opencode-zen/deepseek-v4-flash-free, requires a compact sidecar receipt, or must distinguish that sidecar from a native Codex subagent.
---

# OpenCode Sidecars

Use an OpenCode model only for a frozen, independently verifiable task. It can
run as a native Codex child when the current `spawn_agent` call accepts the
exact catalog ID, or as an external OpenCode sidecar. Do not confuse the two.

## Admission

1. Confirm `ocx ready --json` reports `ready`.
2. Confirm the model is visible in Codex's picker/catalog and check `ocx v2 status`.
3. For cross-provider native delegation, use OpenCodex `v1` mode and start a
fresh Codex session after any mode change. The actual `spawn_agent` acceptance
is the final runtime gate.
4. Freeze one packet: objective, working directory, read scope, write scope,
forbidden effects, decisive proof, timeout, and callback fields.
5. Use one active child. Do not nest, poll repeatedly, or retry the same
failure without changing the packet.

If native spawn rejects the model, report `PROFILE_UNAVAILABLE`; do not silently
substitute another model. Use the external route only when the task permits it.

## Run

For a native child, use the Codex catalog ID in a fresh, no-history spawn:

```text
model: opencode-zen/deepseek-v4-flash-free
fork_context: false
```

For an external sidecar, use the OpenCode CLI ID, not the Codex catalog ID:

```powershell
opencode run --model 'opencode/deepseek-v4-flash-free' '<frozen packet>'
```

| Codex catalog ID | OpenCode CLI ID |
| --- | --- |
| `opencode-zen/deepseek-v4-flash-free` | `opencode/deepseek-v4-flash-free` |
| `opencode-go/deepseek-v4-flash` | `opencode-go/deepseek-v4-flash` |

Use a disposable directory for any write canary. Keep production, deployment,
provider administration, secrets, and destructive actions out of the packet.

## Callback And Acceptance

Require this compact result:

```text
STATUS: PASS | FAIL | UNKNOWN
EXECUTION_KIND: OPENCODE_SIDECAR
MODEL: <requested CLI model ID>
WRITE_SCOPE: <NONE or exact paths>
PROOF: <decisive result>
```

Accept native work only after the completed child result, scoped artifacts, and
decisive proof agree. Accept sidecar work only after its process exit status,
declared model, scoped artifacts, and proof agree. Provider self-identification
is provider-reported, not independent billing attestation.

## Availability And Reference

Treat `429 Too Many Requests`, a timeout, missing output, or a mismatched model
ID as `FAIL` or `UNKNOWN`. Do not retry the same free-model task automatically;
record the failure and choose a different approved model or wait for the quota
window. Read [OpenCodex Sub-agent Surface](https://opencodex.me/guides/sub-agent-surface/)
before changing collaboration mode, roster, or fallbacks.
