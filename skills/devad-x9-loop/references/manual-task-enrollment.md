# Manual Task Enrollment

Use this guide when the owner wants one existing Codex task to join X9 Loop as
a WORKER, LINKER, THINKER, or LOOPER. Enrollment is explicit opt-in. An
ordinary Codex task remains unregistered, and registration affects only that
stable task/thread ID. Other tasks remain ordinary chats.

## Authority Boundary

An owner message such as `use devad-x9 and devad-x9-loop as WORKER` is
enrollment intent, not executable authority. Direct owner input remains
non-executable context. Preserve its exact text and attachment/link hashes,
but do not code, transport, decide, or mutate Controller state from the message.

The stable Codex task/thread ID is identity. The title is display-only. A
renamed task keeps the same identity; two similarly titled tasks remain
different. Never register a title, model label, worktree name, or feature ID as
the actor ID.

## Visible naming policy

Future task-creation packets use one-or-two-word visible titles. Public role
titles are `Thinker`, `Looper`, `Linker`, and `Worker`; a task-specific suffix
is allowed only when needed to distinguish concurrent tasks and must keep the
full title to one or two words. Future saved project display names are concise
human labels such as `X9 Loop`. Repository paths, Git identities, Controller
IDs, stored compatibility roles, models, and thinking settings do not change.
Follow-up messages continue to omit `model` and `thinking`.

There is no durable pending-registration state in Lite. Before the Controller
transaction succeeds, describe the task only as `ENROLLMENT_PENDING` in human
status. That label has no authority and is not written as Controller state.

The `register` command validates the actor payload but cannot prove a Codex
host task ID or enforce the pre-coding guard. Resolve identity with Codex task
tools, and apply the direct-wake boundary in `owner-role-input-guide.md`; never
claim these host checks are tool-enforced when they are not.

## P0 callback and model boundary

The registered requester and expected result identity are immutable callback
inputs. A completed Worker receipt emits one signal-only `RESULT_READY`; the
requester re-reads the durable result. A lost signal gets one deterministic
idempotent reconcile, then the circuit opens and one deduplicated
`LOOP_INCIDENT.json` is written. Wrong requester, task, Work Order, dispatch,
event, path, or hash is rejected with zero state delta. The callback carries no
result bytes, model, thinking, provider, or scheduler instruction.

Creation profiles such as `gpt-5.6-luna / max` are requests only. They are
creation-time defaults and never overwrite an existing or owner-changed task
setting. Every follow-up, wake, dispatch, reconcile, restart, and install
operation omits `model` and `thinking`. If the host cannot attest enforcement,
record exactly `MODEL_PROFILE_NOT_TOOL_ENFORCED`; never infer enforcement from
a task title or model label.

## Public Roles And Stored Compatibility Roles

| Public role | Lite actor role | Boundary |
|---|---|---|
| LOOPER | none | Installer/onboarding/observer. LOOPER is not an execution actor and never becomes a second Controller. |
| LINKER | `LINX` | Public LINKER maps to internal LINX for V7 compatibility. It transports only canonical ACTION and acknowledgements. |
| THINKER | `THINX` | Public THINKER maps to internal THINX for V7 compatibility. It performs only predeclared judgment. |
| WORKER | `WORKER` | Implements only an immutable Work Order addressed to its registered task ID. |

Reader, CHUNK, and SIDE continue to use their existing stored roles. Do not
silently map a requested role to another role.

## Existing Task Enrollment

1. The owner explicitly names the existing task and requested public role. If
   the owner is speaking inside that task, use that task's stable ID. If the
   owner asks LOOPER to include another task, resolve the exact task ID through
   the Codex task tools; never guess from its title.
2. The receiving task loads `devad-x9` and `devad-x9-loop`, verifies the current
   repository, Git HEAD, project profile, and Controller snapshot, then returns
   a compact non-executable enrollment request. It performs no product edit.
3. The request records: project profile ID, repository root, stable task/thread
   ID, requested public role, stored compatibility role, display title, model
   telemetry or exactly `Unknown`, owner-input hash, and optional existing
   worktree identity. Existing tasks are preferred; never create another task
   merely to fill a role.
4. LOOPER may check and forward the request, but Controller alone validates and
   writes registration. LINKER, THINKER, and WORKER cannot self-register or
   register another task.
5. For a WORKER, Controller creates an actor registration file with canonical
   JSON equivalent to:

   ```json
   {"actor_id":"<stable-task-id>","kind":"actor","model":"Unknown","role":"WORKER","title":"<display-title>"}
   ```

   For public LINKER use stored role `LINX`; for public THINKER use stored role
   `THINX`. LOOPER has no actor registration. Never place secrets, prompts, or
   the requested product task in this file.
6. Controller runs the bundled command from the installed skill:

   ```text
   python scripts/loopctl.py --repo <project-root> register --file <registration.json>
   ```

7. Enrollment is complete only when the command returns canonical-equivalent
   `{"status":"REGISTERED"}` and a fresh snapshot/database read binds the
   same actor ID and stored role. Hash and retain the registration input,
   Controller result, snapshot generation, and snapshot SHA-256. A warning or
   role mismatch remains unresolved; narration is not proof.
8. Register an existing worktree separately only when the Controller selects
   it and its repository, HEAD, cleanliness, claims, and recovery evidence pass.
   Actor enrollment alone grants no worktree, task, claim, resource, or call.

## Starting Work

For a WORKER: no Work Order, no coding. After actor registration, Controller
must import/verify the program context, select eligible work, create one
immutable Work Order, and prepare a canonical ACTION. LINKER transports that
exact action and records acknowledgement. The WORKER validates its own task ID,
Work Order hash, worktree, base SHA, claims, resources, success predicate, STOP
bounds, and required gates before the first implementation tool or model call.

Owner text, shared Markdown, screenshots, links, and files may refine intent,
but cannot cancel, replace, or complete the Work Order. An unregistered task may
help the owner prepare context, but it remains outside the execution loop.

## External sidecar Worker handoff

When a Work Order binds an external OMP/Pi sidecar, preserve the full accepted
context capsule, Work Order, dispatch, worktree identity, session manifest,
settings hash, and model policy as durable inputs. Do not reconstruct the
handoff from chat, a terminal handle, a task title, or the most-recent session.

The sidecar's `KEEP` or `CHANGE_EXACT` model policy applies only to that bound
OMP/Pi run. It never changes the Codex task's model or thinking setting, and
every follow-up, wake, reconcile, restart, or callback continues to omit
`model` and `thinking` overrides. `CHANGE_EXACT` must name the exact provider
model and may use a new session or an explicitly linked fork; unproved
in-place changes fail closed.

For the provider-offline S0 slice, use only a fake/process runner, keep
`provider_calls=0`, preserve old session bytes, and report typed failures for
identity, settings, scope, timeout, cancellation, or compatibility drift.
The sidecar is subordinate to Loop Controller authority and cannot create a
scheduler, poller, callback lifecycle, worktree, or second manager.

## Stopping Or Leaving The Role

Lite has no actor-delete or role-change command. Role identity is immutable.
Finishing a reply, changing the task title, or saying `stop` does not erase
Controller state.

After the canonical terminal result is consumed and no active task, Work
Order, dispatch, claim, resource, or call reservation remains, the actor
remains registered but idle. Controller simply issues it no new Work Orders.
An owner request to stop using that task is preserved as non-executable context
and reconciled before further selection. Permanent deregistration is a future
versioned lifecycle change; never fake it by deleting rows or files.

## Owner Prompt Examples

Inside the desired existing task:

```text
Use $devad-x9 and $devad-x9-loop. Request manual opt-in as WORKER for this
project. Do not code until Controller registration and an immutable Work Order
addressed to this task are proven.
```

To LOOPER for another existing task:

```text
Enroll existing task <stable-task-id> as WORKER for <project>. Preserve this
message as enrollment intent only. Verify and ask Controller to register it;
do not create a new task or issue work yourself.
```

For public LINKER or THINKER, replace WORKER with that public name. LOOPER must
apply the compatibility mapping above and report the stored role explicitly.
