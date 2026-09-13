# X9 Model Policy v3.2

Use the exact owner-selected canary profiles below. Unsupported values fail
setup; never substitute a different model or effort. Normal ACTION and
RESULT_READY delivery uses the zero-model Codex task adapter.

## Binding Profiles

| Role | Required profile | Rule |
| --- | --- | --- |
| Thinker (legacy THINX) | `gpt-5.6-sol medium` | Material mission binding and genuine architecture, security, or claim judgment |
| Looper | `gpt-5.6-terra xhigh` | Ordered queue, collision control, receipt validation, and deterministic Loop repair |
| Worker | `gpt-5.6-terra xhigh` | Product coding and proof inside one hash-bound mission |
| Linker (legacy LINX) | `gpt-5.6-luna high` | Exceptional transport audit/fallback only |

Linker never becomes a relay for routine messages, selects work, or takes over
a Worker. Thinker is not a routine approval desk. Looper does not write product
code unless a separately claimed Loop/runtime repair owns the exact files.

The remaining older Linx/Thinx task-class and promotion text is retained only
as inactive history. It cannot override the binding table above.

## Linx Task Class Gate

- `ROUTINE_BRIDGE`: exact status pickup, index refresh, receipt validation, or
  forwarding one approved action. Linx may answer from current durable proof.
- `JUDGMENT_REQUIRED`: owner correction, contradiction, "why" question,
  historical reconstruction, acceptance mismatch, screenshot/UI judgment,
  architecture, security, money, deploy, data risk, or an implemented/deployed
  claim. Linx preserves the exact input and routes current evidence to locked
  Thinx at xhigh; use ultra only when the very-hard gate below passes. Linx
  does not guess or answer the judgment itself.
- `WORKER_REQUIRED`: code, artifacts, tests, browser proof, commit, push,
  bridge, or deploy. Linx routes a Worker and remains the bridge.

Linx never takes over a stalled Worker. It corrects the packet, resumes the
Worker, or routes one replacement after durable handoff.

## Enforcement Gate

Set model and thinking explicitly on every create, wake, send, automation, or
handoff when supported. Naming a model in a prompt is not enforcement proof.
If the tool cannot confirm the required profile, record:

    MODEL_PROFILE_NOT_TOOL_ENFORCED:<role>:<required-profile>

The role may preserve input and perform mechanical reads, but it must not make
a decision outside its required profile. Use a capable task/tool or stop with
`MODEL_SWITCH_REQUIRED`.

## Very-Hard Thinx Gate

Use ultra only for unresolved contradiction after an xhigh pass, destructive
recovery, major security/money/data risk, high-risk architecture, production
incident, or repeated conflicting proof. Record one exact scope and return the
same Thinx task to xhigh after the pass.

## Promotion Gate

A pilot becomes permanent only when:

1. the task class has at least five real samples;
2. pass rate is at least 90%;
3. there is no critical truth, safety, scope, or owner-context error;
4. independent proof passes;
5. median verified-result tokens beat the current role baseline, with retries;
6. the owner approves the recorded promotion.

Record evidence in the package model ledger and the project
.devad/manager/MODEL_POLICY.md.

Until promotion, a lower profile requires
`LOWER_MODEL_OK:<role>:<task-class>:<reason>` for one bounded pass. Mechanical
Reader/CHUNK output is the only default exception and never becomes a decision
without xhigh verification.

## One-Task Rule

Keep one durable locked Thinx task. Do not create permanent xhigh and ultra
Thinx tasks. Change effort for one bounded pass only.

Every Ultra request and decision must include:

    ESCALATION_SCOPE: one pass
    RETURN_PROFILE: gpt-5.6 xhigh

After the pass, return the same Thinx task to xhigh. If tooling cannot enforce
the switch, record `MODEL_SWITCH_REQUIRED` or `MODEL_RETURN_REQUIRED`; never
create another Thinx silently.

Use scripts/model_router.py for the deterministic return-to-baseline dry test.

## Benchmark Override

The owner may authorize a controlled benchmark without a LOWER_MODEL_OK waiver
when all candidates use:

- fresh context;
- the same secret-safe packet;
- a hidden rubric/proof;
- no production mutation;
- full retry-token accounting.

A benchmark never changes the live default by itself.
