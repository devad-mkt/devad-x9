# Luna Subagent Runtime Findings

Checked: 2026-07-31.

## Verdict

The original desktop task exposed only Sol and Terra to native `spawn_agent`,
although Luna Max worked as a top-level model. On 2026-07-31, the safe V1
bridge was applied and a fresh read-only Sol CLI process successfully spawned
the custom `luna-max-worker` role. The runtime attested
`gpt-5.6-luna` at `max` and the child returned `LUNA_NATIVE_V1_OK` with receipt
`019fb827-936b-7761-9a49-82fd15fee4db`.

The persisted child rollout also supplies a real measurement, independent of
its parent: 20,477 input tokens, zero cached-input tokens, 29 output tokens
(17 reasoning-output), and 9,897 ms. At the official 2026-07-30 API rate this
is a $0.00413020 lower-bound estimate because cache-write telemetry was absent;
its separate Codex-credit estimate is 0.103255. This is a native smoke result,
not a quality comparison or a routing-default promotion. The durable meter row
is `measurements/native-luna-v1-smoke-cost-20260731.json`.

Treat the bridge as configuration-sensitive proof, not a permanent product
guarantee: old desktop tasks retain their initial tool schema, a Codex update
can change the catalog, and each fresh environment needs one bounded native
smoke test.

## Current Machine Evidence

- Codex CLI: `0.144.3`.
- Global top-level configuration: `model = "gpt-5.6-luna"` and
  `model_reasoning_effort = "max"`.
- Native probe:
  `Unknown model gpt-5.6-luna for spawn_agent. Available models:
  gpt-5.6-sol, gpt-5.6-terra`.
- Independent ephemeral Luna Max Exec probe returned
  `LUNA_MAX_EXEC_WORKER_OK`.
- That trivial Exec probe reported 19,837 input tokens and 11 output tokens,
  plus a warning that skill descriptions were shortened to fit the skills
  context budget. Do not use a separate Luna process for tiny work unless a
  later lean profile materially reduces this cold-start cost.
- Verified bridge precondition: the complete local catalog had Sol=`v2`,
  Terra=`v2`, and Luna=`v1`.
- Applied bridge backup:
  `$CODEX_HOME\backups\luna-native-subagent-20260731-152907`.
- Generated catalog: `$CODEX_HOME\models-luna-v1.json`; only
  `gpt-5.6-sol.multi_agent_version` and
  `gpt-5.6-terra.multi_agent_version` changed to `v1`.
- Generated custom profile:
  `$CODEX_HOME\agents\luna-max-worker.toml` with Luna Max. The
  profile inherits parent sandbox/approval state.

## 2026-07-31 Three-Task Benchmark

The attested native V1 Luna Max child solved the read-only diagnosis and
returned a correct implementation patch callback, both scoring 100 after
deterministic validation. The first direct nested `apply_patch` route failed.
The second parent timed out, but its orphan child wrote the correct task-1
artifact roughly 4 minutes 45 seconds later while subsequent benchmark work
was active. Both attempts consumed child tokens and their timed-out SOL wrapper
usage is unknown.

Across all three task classes, Luna eventually passed 3/3 with a 100 average
score, but Task 1 required a retry and completed after the parent timeout. Its
child cost was only 1.876098 Codex credits, but known SOL wrapper cost raised
the total to at least 15.894948 credits. Terra high passed 3/3 at 3.676750
credits. Therefore Luna remains conditional for read-only/final-callback or
patch-callback work; the orphan mutation makes it unsuitable for current
direct-write orchestration and it is not the total-cost winner.
See `benchmarks/2026-07-31-routing-v1/benchmark-report.md`.

The same V1 catalog completed all SOL-low, Terra-high, and Terra-xhigh runs, so
this sample did not show a V1 reliability regression for those models. It does
not prove parity across broader coding or V2 behavior.

The CLI run added a benchmark project trust entry to `config.toml`, while the
unrelated `mcp_servers.n8n.args` key also changed. Whole-config recovery now
fails closed on that drift; catalog and Luna-agent target verification still
pass. No automatic restore or manifest refresh was performed.

## Official Sources

- Codex Subagents:
  https://learn.chatgpt.com/docs/agent-configuration/subagents
- Codex Models:
  https://learn.chatgpt.com/docs/models

The current manual says custom agent TOML files may set `model` and
`model_reasoning_effort`, and global `[agents]` settings may set a default
subagent model. It also says effective settings resolve through custom-agent,
explicit-spawn, global-default, and parent layers. These configuration
capabilities do not override a narrower live tool allowlist in an already
running task. The bridge must be loaded by a fresh Codex process.

The model guide describes Luna as appropriate for clear, repeatable,
high-volume extraction, classification, transformation, and structured
summaries. It does not make Luna Max the automatic winner for coding or
critical review.

## Codex Repository Issues

- Native Luna rejection, matching the current error:
  https://github.com/openai/codex/issues/34909
- MultiAgentV2 model/role/metadata incompatibilities:
  https://github.com/openai/codex/issues/32705
- Subagent model and role configuration history:
  https://github.com/openai/codex/issues/11701
- Sol V2 hiding native model-routing fields:
  https://github.com/openai/codex/issues/31814
- Requested context-token composition breakdown:
  https://github.com/openai/codex/issues/13222
- Requested combined and per-agent token visibility:
  https://github.com/openai/codex/issues/14642

Issue #34909 reports that top-level Luna selection works while native
`spawn_agent` rejects Luna and accepts only Sol and Terra. Issue #32705 links
related failures involving hidden model controls, full-history forks, custom
agent settings, and missing effective-child metadata. These are issue reports,
not guarantees that every release behaves identically.

Issue #31814 identifies a related V2 behavior: model-routing fields can be
hidden from the native spawn schema. Its alternative workaround uses a V2 table
to unhide them; do not combine that table with boolean `multi_agent_v2 = false`.
The applied bridge instead aligns the copied catalog at V1 and verifies a fresh
native child. Issues #13222 and #14642 show why the token skill keeps raw
per-worker receipts instead of claiming automatic combined accounting.

## Reddit Reports

- https://www.reddit.com/r/codex/comments/1vb4sqx/how_to_utilize_luna/
- https://www.reddit.com/r/codex/comments/1vb7led/how_to_use_luna_56_subagents/
- https://www.reddit.com/r/codex/comments/1v20jzo/agents_in_codex_when_running_in_max_or_pro_no/
- https://www.reddit.com/r/codex/comments/1uvnei2/sol_low_luna_max_agreedisagree/
- https://community.openai.com/t/5-6-custom-agent-profile-model-selector-not-functioning/1386197/4
- https://www.mindstudio.ai/blog/gpt-5-6-sol-orchestrator-cheaper-sub-agent-models
- https://github.com/topics/token-usage

Community reports conflict. Some users report success through custom agents or
MultiAgentV1 model-catalog overrides; others reproduce the Sol/Terra-only
native allowlist. Reports also suggest SOL low may outperform Luna Max for
some implementation tasks. Treat Reddit as leads for testing, never as product
authority. The community thread also reports that a runtime can expose models
but no native dispatch tools; that is a separate capability blocker. MindStudio
is a non-Codex-specific routing opinion, useful only for the clear-task
Luna-versus-Terra hypothesis. The GitHub topic URL is discovery-only, not
telemetry evidence.

## Authorized Safe Bridge

The owner explicitly authorized the V1 workaround in this task. Use only
`scripts/configure-luna-native-subagent.ps1`; it guards the exact V2/V2/V1
catalog shape, makes a timestamped backup, derives a full copied catalog, makes
only the two required version changes, validates JSON, and gives an exact
rollback command. It does not modify the original catalog or repository files.

Never apply it automatically on another machine or after a Codex upgrade.
First run `-Mode Plan`; apply only when the guard passes; then use a fresh
process to prove `luna-max-worker` natively ran at Luna Max. If that proof fails,
restore the saved config rather than treating the custom agent file as success.

## Safe Routing

1. Prefer native Sol/Terra workers when the live tool exposes them.
2. Use independent Luna Exec for a substantial, clear, verifiable packet when
   its process and context overhead are justified.
3. Use Terra high for normal coding and SOL high/xhigh for material or critical
   review until comparative evidence says otherwise.
4. Require five comparable samples before changing permanent defaults.
