# OMP/Pi External Worker S0

This reference defines the provider-offline external-sidecar seam for one
Controller-selected Worker. It is an addon transport contract, not a second
Controller, scheduler, poller, callback owner, or task runtime.

## S0 boundary

S0 accepts one immutable request envelope and an injected fake/process runner.
The adapter validates the envelope, composes an argument array, checks the
bound files and worktree again, and returns a redacted receipt. It does not
start a real `omp` or `pi` process, call a provider, mutate a session, change
global settings, create a worktree, retry, poll, or fall back to another
driver. Every successful or idempotent receipt has `provider_calls: 0`.

The durable authority order remains Controller Work Order, acknowledged
dispatch, current Git/worktree identity, session manifest, and the adapter
receipt. Chat, a task title, a terminal handle, a most-recent session, or
assistant narration is not a session identity.

## Request identity

The request binds:

- `work_order_id`, `dispatch_id`, `target_actor_id`, and `project_profile_id`;
- `worktree_id`, absolute `worktree_path`, base/head SHA, clean state, Git
  directory, and common directory;
- `session_dir`, isolated `omp_profile`, executable path/hash, and version;
- session mode, exact session ID/path/hash, parent identity for a fork, model
  policy, prompt hash, settings hash, context-capsule hash, timeout, and a
  zero provider-call budget.

Session paths must already exist, be inside `session_dir`, and contain no
reparse or symlink escape. The adapter re-hashes the executable, settings,
session, and parent immediately before the runner boundary. Drift fails
closed before the runner receives a call.

## Modes and drivers

| Mode | OMP/Pi behavior |
| --- | --- |
| `NEW` | Start with the exact isolated profile/session directory and no resume target. |
| `RESUME_EXACT` | OMP uses `--resume <absolute-session-path>`; Pi uses `--session <exact-id>`. |
| `CONTINUE_EXACT` | OMP uses `--continue` only after the exact prior session was bound and hashed; Pi uses its exact `--session` identity. |
| `FORK_FROM_EXACT` | Bind and re-check the parent, launch the linked continuation with the parent target, and prove the parent bytes remain unchanged. |

The command is always an argv list with separate arguments. Prompt text is
sent only through the runner's input channel and is not included in the
command or receipt. The adapter emits the exact non-empty `allowed_tools`
allowlist, or `--no-tools` when the offline request allows none. OMP accepts
`--profile` and `--cwd`; Pi does not, so the adapter sets Pi's working
directory through the runner boundary and emits only Pi-supported flags.
OpenCode is a disabled future profile. Command Code has no resume contract and
returns typed `RESUME_UNSUPPORTED`; neither profile is a fallback for OMP/Pi.

## Model policy

`KEEP` preserves the recorded OMP/Pi model and emits no model or thinking
override. `CHANGE_EXACT` requires the exact requested provider/model and is
allowed for a new session, explicit fork, and OMP/Pi `RESUME_EXACT` or
`CONTINUE_EXACT` session. The 2026-07-24 live Pi canary proved saved-session
resume plus model change with `opencode-go/deepseek-v4-flash`,
`opencode-go/glm-5.2`, and `opencode-go/deepseek-v4-pro`. A separate safe
worktree OMP 17.0.9 canary then proved exact-argv session save and resume from
`opencode-go/deepseek-v4-flash` to `opencode-go/deepseek-v4-pro`.

The earlier OMP HTTP 400 reproduces because OMP discovers ambient Codex MCP
schemas even with `--no-tools`. A real passing zero-tool canary used a project
runtime `discovery_home` for `HOME` and `USERPROFILE`, retained authentication
only through the explicitly bound `omp_agent_dir` in `PI_CODING_AGENT_DIR`,
and removed inherited `OMP_PROFILE` and `PI_PROFILE`. The adapter passes only
that derived environment map to its process boundary; it never accepts raw
environment keys or credential values.

Provider-enabled OMP Work Orders must bind both isolation paths. The discovery
home must exist inside `session_dir`; the agent directory must exist and is
bound by canonical path without copying or hashing its credential contents.
Legacy provider-offline S0 packets may omit both fields. A safe built-in tool
allowlist is still required whenever tools are authorized; `--no-tools` plus
the isolated discovery home is the zero-tool form. A sidecar model selection
never changes the Codex task's model or thinking settings.

## Typed failures

Validation and runner failures are typed and secret-safe. The S0 contract
includes `SESSION_NOT_FOUND`, `SESSION_INCOMPATIBLE`,
`SESSION_VERSION_INCOMPATIBLE`, `SETTINGS_DRIFT`, `WORKTREE_MISMATCH`,
`WORKTREE_DIRTY`, `SCOPE_VIOLATION`, `CAPABILITY_UNPROVEN`,
`PROFILE_DISABLED`, `RESUME_UNSUPPORTED`, `TIMEOUT`, `CANCELLED`,
`PROCESS_FAILED`, `SESSION_MUTATED`, and `PROVIDER_CALLS_FORBIDDEN`. There
is no automatic retry after any of these.

Duplicate dispatches use a deterministic identity key and return the bound
receipt without invoking the runner again. A conflicting receipt is rejected.
Timeout and cancellation happen at the runner boundary; cancellation already
set before launch makes zero runner calls.

## Evidence and redaction

The receipt stores hashes, identities, status, return code effects, and
redacted stdout/stderr only. It stores no prompt, credential, raw command,
provider payload, or session transcript. Common API-key, token, password,
authorization, cookie, and Bearer assignments are replaced with
`[REDACTED]`. The result/proof layer records the S0 `provider_calls=0` claim
through its canonical Worker evidence without widening Controller schemas.

Later OMP-wrapper exact-resume and model-change canaries require separate
provider-spend Work Orders. Their approval cannot be inferred from this
offline adapter or from a passing fake-process test. Pi session/model support
has one real safe-worktree canary, but S0 execution still remains
provider-offline with `provider_calls=0`.
