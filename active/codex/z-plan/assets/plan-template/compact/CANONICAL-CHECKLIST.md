# <Feature> Canonical Checklist

This is the live dependency-ordered ledger. Keep one row per user outcome or
effect boundary; do not copy historical narration here.

| ID | User outcome | Current owner / exact paths | Status | Local proof | Later gate | Next action |
| --- | --- | --- | --- | --- | --- |
| <ID> | <visible outcome> | <module; paths> | `<BUILD_NOW>` | <test/fixture> | <browser/PG/provider/live> | <one action> |

- `BUILD_NOW`: decision-complete implementation and local proof.
- `SAFE_SHELL_NOW`: honest visible/read-only/local-draft UI; effect is separate.
- `EFFECT_GATED`: missing owner, provider, storage, or authorization input.
- `PROOF_GATED`: code exists; only named proof remains.
- `EVENT_ONLY`: no local action until the named receipt exists.

Channels: shell/read -> connect/credential -> callback/signature -> inbound ->
outbound -> receipt/retry -> live. Pages: shell -> read -> persistence -> async
effect -> browser parity.
