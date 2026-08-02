# X9 Project Router

Read this file first. Then read only the smallest linked file needed.

## X9 Loop V7.3 Lite Fast Route

| Need | Read | Writer |
| --- | --- | --- |
| Project identity | manager/loop-lite/PROJECT_PROFILE.json | `loopctl.py` |
| Current recovery truth | manager/loop-lite/SNAPSHOT.json | `loopctl.py` |
| One permitted LINKER action | manager/loop-lite/runtime/ACTION.json | `loopctl.py` |
| Immutable Work Order | manager/loop-lite/runtime/work-orders/<id>/WORK_ORDER.json | Controller |
| Owner message schema | manager/loop-lite/contracts/OWNER_PACKET.json | Controller intake |
| WORKER result schema | manager/loop-lite/contracts/RESULT.json | Package template |
| WORKER result and proof | workers/<worker-id>/ | WORKER/finalizer |
| Feature lookup | features/features.index.json | Catalog builder |
| One WORKER view | manager/workers/<lane>/ROUTER.md | generated view |
| One feature | features/<feature-id>/TASK.md | Feature owner |

Controller consumes one canonical inbox event with `loopctl.py run-once`.
LINKER reads only `runtime/ACTION.json`, transports those exact bytes once,
and returns the exact acknowledgement envelope. Role comes from registered
actor ID, never title. SQLite is ignored cache; `SNAPSHOT.json` plus all
referenced shards are tracked recovery truth.

## Stable Project Truth

These files remain useful when the exact task or shared X9 gate links them:

| Need | Read |
| --- | --- |
| Mission and exclusions | manager/MISSION_LOCK.md |
| Stable facts | manager/CENTRAL_FACTS.md |
| Local-only work | manager/LOCAL_WORK_LEDGER.md |
| Answered owner decisions | manager/ANSWERED_DECISIONS.md |
| Known tool lessons | manager/TOOL_LESSONS.md |
| Exact owner packet index | manager/owner-input/INDEX.md |
| Old project context | memory/CHAT-CATALOG.md |

## Historical Evidence

Existing `manager/loop/`, `MANAGER_PASS_LOCK.md`, `LINX_HANDOVER_STATE.md`,
and large manager Markdown remain historical V5/V6/V7 evidence. Do not delete,
rewrite, or parse them as V7.3 Lite authority.

## Rules

- Do not scan all manager, Worker, feature, memory, run, proof, or archive files.
- `STATUS.md` and `HANDOFFS.md` are generated human views, never parser authority.
- Current Git/runtime evidence beats stale durable narration.
- Missing required truth is `MISSING_MD`, not permission to read old chats.
- No recurring heartbeat, periodic poll, sleep loop, or Markdown pass lock.
- Preserve all worktrees and uncommitted work.
- Dispatch only dependency-ready tasks with exact, disjoint claims.
- Record unknown evidence as `Unknown`; never infer PASS.
