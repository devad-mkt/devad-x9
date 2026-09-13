# Direct Event Callback

Use the callback as a bounded wake signal. Durable Controller files and the
Worker receipt carry authority; a task message or transport envelope never
copies the result or an ACTION.

## V7.3.1 P0 flow

1. Controller binds `return_to_task_id` to the registered requester and stores
   the complete expected result identity: task, Worker, Work Order, dispatch,
   event, packet hash, result path, and result hash.
2. After the Worker receipt is durable, emit exactly one canonical,
   signal-only `RESULT_READY.json` for that identity.
3. The requester validates the signal and re-reads the durable `RESULT.json`
   by path and hash. It does not trust bytes supplied by the callback.
4. If the signal is lost, Controller permits one deterministic idempotent
   `reconcile_result_ready` redelivery. A duplicate signal or acknowledgement
   is a zero-delta replay.
5. If that repair is unavailable a second time, open the callback circuit and
   write one deduplicated `LOOP_INCIDENT.json`. Runtime roles report the
   incident to the Loop coder; they never patch Loop source.

There is no polling, scheduler, recurring wake, generic continuation, or
owner rescue in this path. Wrong requester, role, task, Work Order, dispatch,
event, packet hash, result hash, or path fails closed before any state write.

## RESULT_READY envelope

```json
{
  "callback_id": "rr-<deterministic-id>",
  "expected_result_identity": {
    "dispatch_id": "dsp-<id>",
    "event_id": "<id>",
    "packet_sha256": "<64 hex>",
    "result_path": ".devad/workers/<worker>/receipts/<event>.json",
    "result_sha256": "<64 hex>",
    "task_id": "<worker-task-id>",
    "work_order_id": "wo-<id>",
    "work_order_sha256": "<64 hex>",
    "worker_id": "<registered-worker-task-id>"
  },
  "expires_at": "<bounded-UTC-time>",
  "project_profile_id": "<profile>",
  "return_to_task_id": "<registered-requester-id>",
  "schema": "x9-loop-result-ready-v1",
  "source_role": "WORKER",
  "status": "READY"
}
```

The envelope contains no result bytes, command, provider, model, or thinking
override. `linker_once.py` validates it and prepares only event, task, pointer,
hash, and resume action. The `codex exec resume` adapter is forbidden for
existing desktop tasks because the live canary proved that it immediately
interrupts them. The Looper uses the Codex app's native task-delivery tool once,
without a Linker model turn, and only after a current task snapshot says the
target is not active.

The canonical Controller ACTION is the single pending item. When the target is
active, admission returns `HOLD_ACTIVE` without a prompt or delivery claim.
Thinker, helper, and Worker tasks must not send parallel direct messages. At
the next natural idle/needs-attention boundary, Looper delivers exactly one
admitted signal. No mailbox service, scheduler, polling loop, or second queue
is introduced.

Before launching a waking adapter, the transport atomically records a durable
claim keyed by event identity, target task, and receipt hash. A duplicate claim
never launches again. If launch stops before its acknowledgement is sealed,
replay fails closed until bounded reconciliation proves that no resume process
or accepted task turn exists.

## Delivery and recovery rules

- Send only to the bound requester and preserve the exact callback identity.
- Re-read the canonical result before acknowledging or repairing a callback.
- A successful repair writes the same signal bytes once; it does not create a
  new dispatch or mutate claims, STOP bounds, security gates, or external
  effect gates.
- A conflicting signal, state marker, or incident is an identity/hash error
  with zero state delta.
- `LOOP_INCIDENT.json` records task, Work Order, dispatch, result identity,
  claims hash, evidence hashes, expected/actual transition, repair outcome,
  reproducer, worktree, and host model-enforcement status.

The older `EVENT_READY` prose is not a second protocol. Existing inbox events
remain durable ingress; `RESULT_READY` is the one P0 completion wake layered on
that authority.

## Preserved worktree evidence

A canonical Worker `RESULT_READY.json` may remain beside its `INBOX_EVENT.json`
without becoming product dirt. Controller admits it only after full
requester/result/task/order/dispatch/packet/profile/Worker validation and only
while it is an ordinary untracked file. Previously consumed outboxes are
reusable for terminal `COMPLETE` or `SUPERSEDED` tasks only when the Work Order
has the same state and the dispatch is `COMPLETE`. See
[Lesson 52](lessons/52-callback-evidence-deadlock.md) for the failure and exact
rollback boundary.

## Legacy receipt vocabulary

Older V5 receipts remain readable as historical evidence and retain the exact
identity fields `LINX_TASK_ID`, `SOURCE_TASK_ID`, `SOURCE_ROLE`, `DISPATCH_ID`,
`PACKET_SHA256`, `EVENT_TYPE`, `RECEIPT_PATH`, and `RECEIPT_SHA256`. The legacy
manager wake boundary remains bounded to at most three attempts; a failed wake
is recorded as `MANAGER_WAKE_FAILED` under the existing release and
`MANAGER_PASS_LOCK` evidence. These names do not create a second callback
protocol or permit recurring pickup.
