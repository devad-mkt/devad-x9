---
name: x-subagent
description: Route, dispatch, meter, and verify bounded Codex SOL and Terra workers without duplicating their work. Use when the owner asks for xSubAgent, native subagents, model-and-effort routing, mapper/implementer/reviewer delegation, risk-scaled manager verification, or evidence-based subagent cost and quality calibration. Luna is explicitly disallowed for new dispatches.
---

# xSubAgent

## Active Owner Policy

- `gpt-5.6-luna` is **DISALLOWED**. Do not configure a V1 bridge, custom
  Luna role, native child, or `codex exec` workaround. Return
  `LUNA_DISALLOWED_BY_OWNER` and choose an approved SOL/Terra fallback.
- Use a native child only when the live `spawn_agent` schema exposes the exact
  requested model and effort. Otherwise use `NO_DELEGATION` or report
  `PROFILE_UNAVAILABLE`; do not silently substitute a model.
- The manager remains the only authority. Borrow Devad X9 roles as style only:
  never create Controller state, ACTION files, a poller, or child nesting.
- Do not promote a model from this three-task benchmark. Require five
  comparable samples, 90%+ first-pass quality, no critical safety/truth error,
  and lower verified-result cost.

## Current Routing

| Work | Profile | State | Limit |
| --- | --- | --- | --- |
| Normal bounded coding | Terra high | Default pilot | Lowest measured direct aggregate cost: 3/3, 100. |
| Proven Terra-high insufficiency | Terra xhigh | Escalation | Only after Terra high demonstrably fails a bound acceptance predicate; no automatic escalation. |
| One known fact or small log | Direct manager; Terra medium only when delegation materially saves time | Candidate | Terra medium has no measured result in this run. |
| Bounded mapping, read-only diagnosis, deterministic hard check | SOL low | Pilot | Read-only only; never product coding. |
| Worker-ready plan chunks and action order | SOL medium | Pilot | Planning/packet lane; freeze the packet before handing coding to Terra. |
| Security, tenancy, architecture, contract, skeptical review | SOL high | Conservative | Review and decision lane; do not infer SOL-low security adequacy from general tasks. |
| Critical/repeated safety or architecture failure | SOL xhigh | Exceptional | Require a critical predicate and independent proof. |
| Main manager/chat | Terra high; Terra xhigh only on owner/evidence escalation | Pilot | Automatic xhigh risks repeating the observed manager-overhead problem. |
| Luna | No dispatch | Forbidden | `LUNA_DISALLOWED_BY_OWNER`. |

Private owner-facing routing tables and benchmark receipts are intentionally
excluded from this portable public distribution. Keep them in the private
release workspace; this skill carries only the reusable routing rules.

## Give Only Needed Skills

Every worker needs exact task details, limits, evidence identities, tests, and
only skills that change its next decision. Do not load all skills by default.

| Task condition | Packet skill | Why |
| --- | --- | --- |
| Any bounded worker | `$x-subagent` | Packet, callback, and meter rules. |
| Coding from an accepted plan | `$smooth-coding` | Execute the smallest proven slice without process loops. |
| Devad project repository or worktree | `$devad-x9` plus its routed references | Enforce project/worktree and safety authority. |
| Adoption, legacy/reference reconciliation, vendor hunk, parity behavior | `$semantic-adoption` | Trace the native owner and use its lean evidence intake. |
| Complex adoption/parity/migration with missing owners, versions, or contracts | `$evidence-to-implementation` | Manager builds a source-bound packet before dispatch. |
| Security/architecture review | Applicable security rules/skill plus SOL high/xhigh | Independent challenge where it can change acceptance. |

Do not make the full `$evidence-to-implementation` workflow a global
dependency of `$semantic-adoption`: the latter contains only a lean intake for
ordinary semantic changes. Escalate only when evidence/owner binding is
actually missing. `$devad-x9` applies to Devad project work, not unrelated
repositories. `$smooth-coding` applies to a coding worker, not a
read-only reviewer.

## Packet, Callback, and Acceptance

Freeze one objective, repository/worktree/base SHA, named read/write scope,
forbidden actions, invariants, evidence identity, success predicate, decisive
test, stop condition, and selected skills. Native spawn uses
`fork_turns="none"` with explicit model/effort and no full-chat fork.

```text
OBJECTIVE: <one outcome>
MODEL_REQUEST / REASONING_REQUEST: <exact callable profile>
READ_SCOPE / WRITE_SCOPE / FORBIDDEN: <exact boundaries>
SKILLS: <only the table-selected skills>
INVARIANTS: <security, tenancy, data loss, spend, authorization>
RED_GREEN / DECISIVE_TEST: <proof or NOT_APPLICABLE>
STOP: <scope or external boundary>
CALLBACK: status; attested profile; receipt; paths; patch ID; tests; risks; unknowns
```

The manager verifies receipts, scope/hash identity, contract-critical hunks,
and one decisive test. It does not reread a full transcript unless drift,
unexpected paths, failed proof, disagreement, missing identity, or critical
risk requires it. Use an in-manager THINKER checkpoint only for conflicting
evidence, two distinct failures, or a material security/architecture/contract
decision; then ask one SOL-high reviewer one decision-changing question.

## Cost Gate

Meter an attested child with `scripts/measure-subagent-run.ps1`, never a parent
aggregate. For native cumulative snapshots, use the final
`total_token_usage` for the receipt—never sum snapshots or use only
`last_token_usage`. Record input/cached/output, retry count, duration, packet
hash, proof, API-estimate quality, and Codex credits. API USD and credits are
different units; refresh the official price reference after seven days.

Measure the manager at owner-message, first-dispatch, and final-proof
boundaries. If `input - cached + output` exceeds combined child volume, emit
`ORCHESTRATOR_OVERHEAD_DOMINANT`, stop optional agents, batch deterministic
collection, use callbacks/hashes instead of transcripts, and start the next
benchmark in a fresh compact manager task.

## Historical Pre-Owner-Lock Contents (Not Active Instructions)

The following text is retained only as historical benchmark/recovery context.
It is not routing authority and must not be executed, especially any Luna,
bridge, wrapper, or older ranking instruction.

````text

# xSubAgent

Keep one accountable manager. Delegate only a bounded objective whose context
is smaller than the parent task and whose result has a decisive verification
gate. Default to one active worker and no child nesting.

## Choose the Execution Kind First

| Kind | Use when | Control and proof |
| --- | --- | --- |
| `NATIVE_SUBAGENT` | The live `spawn_agent` schema exposes the requested model and native steering/thread integration matters | Pass `fork_turns="none"`, explicit model and effort, then require runtime child metadata and a completed result. |
| `LUNA_EXEC_WORKER` | Luna is rejected by native spawn, but the task is substantial, clear, independently verifiable, and worth a separate Codex cold start | Run the bundled Luna script. Label it independent, not native. Require the JSON thread receipt, result, usage telemetry, and manager verification. |
| `NO_DELEGATION` | Dispatch/context/synthesis cost is greater than the bounded work, or no independent proof exists | The manager performs the task directly. |

## Luna Max Native Bridge

Use the reversible bridge only when the owner explicitly asks to enable Luna as
a native subagent and the live catalog guard passes. It is for the known
Sol/Terra-V2 versus Luna-V1 incompatibility; it is not a general fix for
missing entitlement, a missing native tool, or a session that has not reloaded.

Run the plan before applying it:

```powershell
& scripts/configure-luna-native-subagent.ps1 -Mode Plan
& scripts/configure-luna-native-subagent.ps1 -Mode Apply
```

The script captures the complete current `codex debug models` catalog, backs
up `~/.codex/config.toml` and an existing Luna role, writes a generated catalog
with only Sol and Terra changed from V2 to V1, enables `multi_agent`, disables
`multi_agent_v2`, and writes the narrow `luna-max-worker` custom profile
(`gpt-5.6-luna`, `max`). It never changes the parent default model, global
subagent default, permissions, MCP, hooks, or repository files.

After `Apply`, start a fresh Codex app task or CLI process. Verify one
read-only native child using `agent_type="luna-max-worker"`, then require its
child-thread receipt and attested model/effort. Roll back the saved config if
the fresh probe fails:

```powershell
& scripts/configure-luna-native-subagent.ps1 -Mode Rollback -BackupDirectory '<Apply backup path>'
```

Do not hand-edit the model catalog, downgrade a catalog without a complete
capture, enable an unbounded global Luna default, or present a bridge as proof
until the fresh native child completes.

### Recovery Package

Before a bridge change, capture a redacted, hash-bound recovery package; after
the native smoke test, capture the matching after-state and verify it. These
operations are read-only except `Apply` capture (which only writes the recovery
package) and the explicit restore `Apply`:

```powershell
& recovery/capture-bridge-recovery.ps1 -Mode Plan -BackupDirectory '<bridge backup path>'
& recovery/capture-bridge-recovery.ps1 -Mode Apply -BackupDirectory '<bridge backup path>'
& recovery/capture-bridge-recovery.ps1 -Mode Verify -BackupDirectory '<bridge backup path>'
& recovery/restore/restore-luna-native-subagent.ps1 -Mode Plan
& recovery/restore/restore-luna-native-subagent.ps1 -Mode Verify
```

The restore `Apply` is an owner-approved reversal: it checks the recovery
manifest hashes, makes an emergency backup, restores each original file, and
moves generated files aside instead of deleting them. It must never run merely
because a benchmark is inconclusive. See [recovery README](recovery/README.md).

Before any Luna dispatch:

1. Inspect the live native model allowlist and whether the fresh session exposes
   `agent_type="luna-max-worker"`.
2. If the native role is available, run one harmless probe with
   `agent_type="luna-max-worker"` and `fork_turns="none"`.
3. If the old session rejects Luna or does not expose the custom role, record
   `LUNA_NATIVE_UNAVAILABLE_IN_SESSION`; restart or use the already-proven Exec
   fallback. Do not retry renamed prompts or mutate the catalog again.
4. Use `LUNA_EXEC_WORKER` only when its independent-process semantics and
   cold-start token cost are acceptable.

Read [Luna runtime findings](references/luna-runtime-findings.md) before changing
Codex model catalogs, multi-agent versions, custom-agent files, or permanent
defaults. Never apply a Reddit workaround automatically.

## Pilot Routing

Use the lowest safe callable profile. These are provisional defaults based on
limited local evidence, not permanent winners:

| Work type | Preferred profile | Status and reason |
| --- | --- | --- |
| Bounded mapping or status audit | Terra high for cost; SOL low for latency | `PILOT`; both scored 100 in one frozen mapping sample, while Terra high used fewer credits and SOL low finished faster. |
| Normal implementation | Terra high | `PILOT`; pragmatic coding default. |
| Serious diagnosis or cross-file engineering | SOL medium | `PILOT`; current best balance for harder work. |
| Difficult security, tenancy, contract, or architecture review | SOL high | `PILOT`; stronger scrutiny is justified. |
| Critical or repeatedly failed boundary | SOL xhigh | Exceptional use only. |
| Terra xhigh | Only after evidence that Terra high is insufficient | More detail is not automatically a better decision. |
| Luna Max native worker | Clear, substantial, repeatable, read-heavy callback work when the fresh runtime attests `luna-max-worker` | Do not assign direct writes on this Windows V1 bridge until a fresh mutation canary passes; callback transport is currently safer. |
| Luna Max independent worker | Same task class when native Luna is unavailable | Not the default for small mapping because the separate process has cold-start context cost. |

Promote a permanent default only after at least five comparable samples reach
90% or better first-pass quality, contain no critical truth or safety error,
and have lower verified-result cost. One or two task classes may guide the next
trial but cannot establish a universal winner.

### 2026-07-31 Frozen Benchmark

Three bounded task classes were run on native V1 SOL low, Terra high, Terra
xhigh, and Luna Max. Full receipts, scoring, retries, telemetry, API estimates,
and Codex credits are in
[the benchmark report](benchmarks/2026-07-31-routing-v1/benchmark-report.md).
This is one sample per task class, so it updates the next trial but not a
permanent default.

| Profile | Task pass | Average score | Child credits | Known total credits | Evidence verdict |
| --- | ---: | ---: | ---: | ---: | --- |
| SOL low | 3/3 | 100 | 9.402675 | 9.402675 | Fast and correct, but costlier than Terra at current rates. |
| Terra high | 3/3 | 100 | 3.676750 | 3.676750 | Best aggregate verified-result cost; keep normal coding default. |
| Terra xhigh | 3/3 | 100 | 3.841630 | 3.841630 | No quality gain over high; small timing/token differences are noise until repeated. |
| Luna Max V1 | 3/3 after retry | 100 | 1.876098 | at least 15.894948 | Cheap child reasoning, but SOL wrapper overhead and a late orphan write after timeout erase the advantage. |

The Luna child identity was attested as `gpt-5.6-luna max`. Its read-only final
callback and patch callback were correct. The first direct `apply_patch` route
failed; the bounded danger-full-access retry timed out, then its orphan child
wrote the correct result about 4 minutes 45 seconds after the parent timeout
while later benchmark work was active. Failed wrapper usage was not recoverable
and the known Luna total is therefore a lower bound. This is a runtime/lifecycle
failure, not evidence that Luna reasoned incorrectly. SOL and Terra completed
all three tasks under the V1 catalog, so this sample found no V1 reliability
regression for them.

The CLI benchmark also added a project trust entry to shared `config.toml`;
`mcp_servers.n8n.args` changed concurrently. The recovery guard correctly
refused whole-config verification while catalog and Luna-profile hashes still
passed. Never refresh a bridge recovery manifest over unrelated config drift
or restore the whole config automatically; classify the changed keys first.

## Evidence-Bound Orchestrator

Borrow the X9 role separation as `STYLE_ONLY`; do not initialize Controller
state, ACTION files, polling, enrolled roles, or a second authority system:

- **Controller behavior (manager):** freeze one packet, fixture/hash, claims,
  STOP, validator, receipt ledger, and budget before dispatch. Deterministic
  checks decide ordinary PASS/FAIL.
- **WORKER/helper:** receives `fork_turns="none"`, named files, one writable
  result or patch callback, no child nesting, and a compact result contract.
- **THINKER checkpoint:** stays inside the accountable manager by default. Use
  it only for a validator/evidence conflict, two distinct proof-bound failures,
  or a material security/architecture/contract boundary. Spawn one independent
  SOL-high reviewer only when independence can change the decision.
- **Acceptance:** read the compact result and hashes, run the decisive test, and
  inspect only failed fields or contract-critical hunks. Do not reread the
  worker's complete transcript unless drift, failure, or disagreement requires
  it.

Measure the manager as a separate row at owner-message, first-dispatch, and
final-proof boundaries. If manager approximate new-token volume
`input - cached + output` exceeds the combined children, emit
`ORCHESTRATOR_OVERHEAD_DOMINANT`: stop optional agents, batch deterministic
collection/scoring into one command, reuse receipts instead of transcripts,
and recommend a fresh compact manager task before another benchmark. Keep
parent cost `UNKNOWN` when its effective model is not attested.

For Luna V1, do not pay a SOL wrapper for routine work. Prefer an app-native
Luna child when the live tool exposes it; otherwise use Luna only when the
read/patch callback's expected savings exceed wrapper startup and verification.
After one write-tool failure, switch to callback transport or a callable
SOL/Terra worker. Do not retry the same child mutation route.

## Dispatch Packet

Give every coding worker:

- exact desired behavior and the existing owner to reuse;
- repository, base SHA, branch/worktree, allowed paths, and forbidden paths;
- security, tenancy, data-loss, spend, and authorization invariants;
- edge cases only where ambiguity exists;
- required RED and GREEN tests plus the decisive acceptance command;
- stop conditions and actions requiring manager/owner approval;
- a compact callback: changed paths, patch identity, tests, risks, and
  uncertainties.

Use this header:

```text
EXECUTION_KIND: NATIVE_SUBAGENT | LUNA_EXEC_WORKER
MODEL_REQUEST: <exact model>
REASONING_REQUEST: <effort>
TOKEN_MODE: LOW
OBJECTIVE: <one outcome>
SUCCESS_PREDICATE: <decisive proof>
READ_SCOPE: <exact paths>
WRITE_SCOPE: <exact paths or NONE>
FORBIDDEN: <paths/actions>
STOP: <boundaries>
CALLBACK: changed paths; patch ID; tests; risks; unknowns
```

Do not pass full chat history. Native spawns use `fork_turns="none"` with a
complete task-local packet. A Luna Exec worker receives the same packet through
[run-luna-worker.ps1](scripts/run-luna-worker.ps1).

## Run Luna Max Honestly

Prefer the native role after its fresh smoke test. The dispatch must identify
`luna-max-worker`, use `fork_turns="none"`, and preserve the parent sandbox.
Record both the child receipt and runtime-attested `gpt-5.6-luna max`; the
custom-agent file is routing intent, not attestation.

Use the independent fallback only when the live native role is unavailable.
Default it to read-only:

```powershell
& scripts/run-luna-worker.ps1 `
  -WorkingDirectory 'C:\exact\repo' `
  -Prompt '<complete bounded packet>'
```

Set `-Sandbox workspace-write` only when the owner requested implementation and
the packet names exact writable paths. The script fixes the model to
`gpt-5.6-luna`, defaults effort to `max`, uses an ephemeral session, emits
JSONL, and returns the underlying Codex exit code.

Report:

```text
EXECUTION_KIND: LUNA_EXEC_WORKER
REQUESTED_PROFILE: gpt-5.6-luna max
ATTESTED_PROFILE: <runtime evidence or UNKNOWN>
THREAD_RECEIPT: <id or UNKNOWN>
TOKEN_USAGE: <telemetry or UNKNOWN>
RESULT: PASS | FAIL | UNKNOWN
```

An exit code and requested model are not sufficient model attestation when the
runtime omits effective child metadata. Keep `ATTESTED_PROFILE: UNKNOWN` unless
the runtime proves it.

## Measure Before Compare

Do not dispatch a comparative subagent test until one real worker has produced
an attested per-child meter row and the dated price reference is fresh. Measure
the child, never the parent total: native child rollouts expose
`event_msg/payload/info/last_token_usage` in their persisted session JSONL (or
the app-server `thread/tokenUsage/updated` event); independent workers expose
`turn.completed.usage` from `codex exec --json`.

Use the shared meter and retain its JSON output with the test packet:

```powershell
& scripts/measure-subagent-run.ps1 `
  -TelemetryPath '<one child rollout .jsonl or exec --json log>' `
  -Execution NATIVE_V1 `
  -RequestedModel 'gpt-5.6-luna' -RequestedReasoningEffort max `
  -AttestedModel 'gpt-5.6-luna' -AttestedReasoningEffort max `
  -ThreadReceipt '<child receipt>' -DurationMilliseconds <measured-ms>
```

`measurement_status: READY_FOR_COMPARISON` requires attestation and parseable
usage. `LOWER_BOUND_CACHE_WRITES_NOT_EXPOSED` is not an exact API bill: it
excludes cache-write charges that the telemetry did not expose. Do not bill
`reasoning_output_tokens` again; it is a subset of reported output tokens.

Current API standard rates (USD per million tokens; effort does not alter the
rate) and Codex credit weights live in
[the dated price reference](references/pricing-2026-07-30.json):

| Profile family | API input / cached / output | Codex input / cached / output credits |
| --- | --- | --- |
| SOL (low through xhigh) | $5 / $0.50 / $30 | 125 / 12.5 / 750 |
| Terra (low through xhigh) | $2 / $0.20 / $12 | 50 / 5 / 300 |
| Luna (low through max) | $0.20 / $0.02 / $1.20 | 5 / 0.5 / 30 |

API dollars and Codex subscription credits are separate units; never convert
credits to dollars or call the API estimate an account-quota charge. Refresh
the official price reference if it is more than seven days old before a
benchmark. Record per run: packet/hash, execution kind, requested and attested
profile, input/cached/output/reasoning tokens, API estimate quality, Codex
credits, duration, decisive proof, score, retries, and result. Compare only
same-packet, same-task-class, attested rows; no profile becomes a permanent
default before five comparable samples.

## Verify Without Paying Twice

The worker self-reviews and runs focused tests. The manager verifies evidence,
not the entire investigation:

| Risk | Worker responsibility | Manager verification |
| --- | --- | --- |
| Low | Implement or map, self-review, focused checks | Confirm exact paths/identity and run one smoke check. |
| Medium | RED/GREEN, frozen diff, relevant gates | Inspect behavioral hunks and rerun one decisive test. |
| High | Full self-gate, frozen diff, risk notes | Use a blind SOL-high review plus critical tests. |
| Critical | Security/tenancy proof package and frozen identity | Review the focused diff and require independent proof of the critical boundary. |

Deep-review everything only after drift, unexpected paths, test failure,
reviewer disagreement, missing patch identity, or critical risk. Never accept a
worker claim solely because it sounds confident.

## Callback Contract

Require every worker to return:

```text
STATUS: PASS | FAIL | BLOCKED | UNKNOWN
EXECUTION_KIND:
REQUESTED_PROFILE:
ATTESTED_PROFILE:
BASE_SHA:
CHANGED_PATHS:
PATCH_ID:
RED:
GREEN:
DECISIVE_TEST:
RISKS:
UNCERTAINTIES:
NEXT_SAFE_ACTION:
```

If the worker cannot prove branch/base, effective model, patch identity, or
test result, preserve `UNKNOWN`. The manager remains responsible for scope,
authority, integration, and the final user-facing verdict.
````
