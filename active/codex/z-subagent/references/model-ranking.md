# Model Routing Evidence

Use this as a routing aid, not a model-enforcement mechanism. Runtime telemetry is authoritative for which profile actually ran.

## Contents

- Current Default Ladder
- Current Price And Benchmark Baseline
- Artificial Analysis Coding-Agent Evidence
- Cross-Harness Intelligence Ranking
- Latest Comparable Frozen-Packet Benchmark
- Qualitative Evidence From the Same Workflow Family
- Promotion Rule

## Current Default Ladder

| Use case | Preferred profile | Status |
| --- | --- | --- |
| General bounded subagent work | SOL medium | Best default |
| Exact source map and bounded evidence extraction | SOL medium | Preferred |
| Bounded backend/debug diagnosis | SOL high | Preferred |
| Difficult or cross-file implementation, diagnosis, test strategy, independent review | SOL high | Best escalation |
| Frontend integration review | Terra high | Pilot |
| Mechanical long-file extraction | LUNA medium | Pilot; no decisions or mutation |
| Failed SOL high proof or unusually high-risk independent review | SOL xhigh | Conditional |
| Architecture/security/conflicting proof | SOL ultra with the Ultra gate | Conditional |
| Terra max | Conditional escalation | Use only when the lower safe rung is insufficient |
| LUNA max | Experimental | Do not select by default |

The operational default is `SOL medium -> SOL high`. This is an owner routing
decision informed by task fit, cost, local evidence, and coordination overhead;
it is not a claim that these two profiles top every public leaderboard.

## Current Price And Benchmark Baseline

Checked: 2026-07-26.

Official OpenAI API prices per 1M tokens:

| Model | Input | Cached input | Output |
| --- | ---: | ---: | ---: |
| GPT-5.6 Sol | $5.00 | $0.50 | $30.00 |
| GPT-5.6 Terra | $2.50 | $0.25 | $15.00 |
| GPT-5.6 Luna | $1.00 | $0.10 | $6.00 |

For GPT-5.6, cache writes cost 1.25 times uncached input. Prompts above the
published long-context threshold can use higher rates. Verify current prices
before publishing a cost claim:

- https://developers.openai.com/api/docs/models
- https://developers.openai.com/api/docs/models/compare

Do not call API prices Codex subscription prices. Do not infer Plus, Pro, or
workspace quota consumption from API dollars.

CursorBench 3.2 updated GPT-5.6 costs on 2026-07-09 to include cache writes.
Its average cost per task applies published token prices to benchmark token
usage. It is an API-equivalent benchmark estimate, not direct Codex quota
telemetry:

- https://cursor.com/cursorbench

Artificial Analysis provides a separate coding-agent index and per-benchmark
harness comparisons:

- https://artificialanalysis.ai/agents/coding-agents
- https://artificialanalysis.ai/agents/coding-agents?agents=codex-gpt-5-6-luna-max%2Ccodex-gpt-5-6-sol-max%2Ccodex-gpt-5-6-terra-max%2Ccodex-gpt-5-6-luna-high%2Ccodex-gpt-5-6-luna-xhigh%2Ccodex-gpt-5-6-sol-high%2Ccodex-gpt-5-6-sol-medium%2Ccodex-gpt-5-6-sol-xhigh%2Ccodex-gpt-5-6-terra-medium%2Ccodex-gpt-5-6-terra-high%2Ccodex-gpt-5-6-terra-xhigh%2Ccodex-gpt-5-5-xhigh&coding-agents-harness-comparison-chart=harness-terminal-bench-v2

### Intelligence-first order above the Composer 2.5 floor

Sorted by CursorBench score, not by value:

| Rank | Profile | Score | Avg. cost/task | Balanced value |
| ---: | --- | ---: | ---: | ---: |
| 1 | SOL max | 67.2% | $5.69 | 28.17 |
| 2 | Terra max | 64.9% | $2.89 | 38.18 |
| 3 | SOL xhigh | 64.5% | $3.88 | 32.74 |
| 4 | SOL high | 63.5% | $2.79 | 38.02 |
| 5 | LUNA max | 61.1% | $1.97 | 43.53 |
| 6 | SOL medium | 60.0% | $1.95 | 42.97 |
| 7 | Terra xhigh | 59.2% | $1.44 | 49.33 |
| 8 | LUNA xhigh | 57.7% | $1.14 | 54.04 |
| 9 | LUNA high | 56.8% | $0.82 | 62.73 |

`Balanced value = score / sqrt(avg. cost/task)`. Use it only inside this frozen
table. It rewards cost efficiency and therefore is not an intelligence rank.
Small score differences may be benchmark noise.

### Operational SOL escalation

| Step | Profile | CursorBench score | CursorBench cost/task | Relative cost |
| ---: | --- | ---: | ---: | ---: |
| 1 | SOL medium | 60.0% | $1.95 | 1.00x |
| 2 | SOL high | 63.5% | $2.79 | 1.43x |

SOL high adds 3.5 CursorBench points for about 1.43x the benchmark cost. Start
with SOL medium for normal bounded work and move to SOL high for difficult work
or a specific insufficiency. Max/XHigh leaderboard leaders remain reference
evidence and conditional escalations, not automatic defaults.

## Artificial Analysis Coding-Agent Evidence

Checked: 2026-07-26. Artificial Analysis Coding Agent Index v1.3 averages
DeepSWE, Terminal-Bench v2, and SWE-Atlas-QnA. Each benchmark score averages
pass@1 across three attempts per task. The cost column below is the average API
cost per task across the full three-benchmark index; it is not a
Terminal-Bench-only cost and not Codex quota.

Sorted by the owner-selected Terminal-Bench v2 harness:

| TB rank | Profile | Terminal-Bench v2 | AA Index | AA avg. cost/task |
| ---: | --- | ---: | ---: | ---: |
| 1 | SOL max | 87.70% | 66.57 | $7.08 |
| 2 | SOL xhigh | 86.11% | 65.09 | $5.24 |
| 3= | Terra max | 84.13% | 62.28 | $2.76 |
| 3= | GPT-5.5 xhigh | 84.13% | 61.49 | $5.07 |
| 5 | SOL high | 82.54% | 64.11 | $4.14 |
| 6 | Terra xhigh | 80.56% | 57.07 | $1.90 |
| 7 | LUNA max | 79.76% | 58.66 | $1.57 |
| 8 | SOL medium | 77.78% | 60.61 | $2.99 |
| 9 | LUNA xhigh | 76.19% | 54.67 | $1.26 |
| 10 | Terra high | 75.99% | 55.79 | $1.59 |
| 11 | LUNA high | 71.83% | 51.42 | $0.96 |
| 12 | Terra medium | 69.44% | 47.80 | $0.90 |

Do not compare an Artificial Analysis score numerically with a CursorBench
score. The task suites, harnesses, scoring, and cost distributions differ.

## Cross-Harness Intelligence Ranking

Use average ordinal position only as a compact consensus signal. It does not
make the two benchmark scores commensurate.

| Tier | Profile | CursorBench rank | AA Terminal-Bench rank | Mean rank | Honest verdict |
| ---: | --- | ---: | ---: | ---: | --- |
| 1 | SOL max | 1 | 1 | 1.00 | Capability leader on both |
| 2 | SOL xhigh | 3 | 2 | 2.50 | Stronger AA terminal result; higher cost |
| 2 | Terra max | 2 | 3 | 2.50 | Cheaper second-tier choice; stronger CursorBench result |
| 3 | SOL high | 4 | 5 | 4.50 | Strong high-effort fallback |
| 4 | GPT-5.5 xhigh | 8 | 3 | 5.50 | Legacy contender; expensive for its consensus rank |
| 4 | LUNA max | 5 | 7 | 6.00 | Cost-efficient but still experimental |
| 4 | Terra xhigh | 7 | 6 | 6.50 | Efficient middle candidate |
| 4 | SOL medium | 6 | 8 | 7.00 | Stable task-fit default, not universal capability winner |
| 5 | LUNA xhigh | 9 | 9 | 9.00 | Lower-cost bounded work |
| 6 | Terra high | 11 | 10 | 10.50 | UI/frontend pilot remains task-specific |
| 6 | LUNA high | 10 | 11 | 10.50 | Economic first rung, not intelligence winner |
| 7 | Terra medium | 12 | 12 | 12.00 | Routine low-cost work only |

The operational subagent sequence is `SOL medium -> SOL high`. The capability
ranking above remains benchmark evidence: it does not replace the owner-selected
default. Use xhigh/max only when risk, task fit, or failed proof justifies the
additional rung.

## Latest Comparable Frozen-Packet Benchmark

Date: 2026-07-18. Task: classify an immutable AI Blog workflow packet as synchronous/queued and identify the missing proof. Expected answer: `synchronous`, `unknown`, and `deployed authenticated receipt`.

| Profile | First-pass quality | Wall time | Local telemetry | Approx. new-token volume | Result |
| --- | ---: | ---: | --- | ---: | --- |
| LUNA medium | 100/100 | 13.90 s | input 26,349; cached 25,344; output 65 | 1,070 | PASS |
| LUNA max | 100/100 | 12.72 s | input 26,349; cached 8,960; output 95 | 17,484 | PASS |
| Terra high | 100/100 | 11.72 s | input 27,540; cached 9,472; output 77 | 18,145 | PASS |

The packet was intentionally tiny; installed-skill context dominated input tokens and cache behavior varied. These figures are local telemetry estimates, not official billing and not a promotion decision. Two live-source LUNA trace attempts timed out without telemetry; exclude them from scoring.

## Qualitative Evidence From the Same Workflow Family

- SOL medium correctly mapped the synchronous route/controller/coordinator path, but its next test was less precise than the xhigh diagnosis.
- SOL xhigh found the configured-sidecar 503 persistence-test gap with concrete assertions; use it for bounded debugging.
- Terra high accurately isolated the future UI polling gap if the workflow becomes queued.
- Terra ultra with the Ultra protocol produced the best authority/proof-route analysis, but it was a different task and had no token telemetry; treat it as qualitative only.

## Promotion Rule

Require five comparable tasks, at least 90% first-pass quality, no critical truth/safety error, independent proof, and lower verified-result cost before changing a preferred profile.
