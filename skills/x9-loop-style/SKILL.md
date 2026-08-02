---
name: x9-loop-style
description: Use as the default lightweight Devad X9 coordination style for normal project work. It keeps V6-style self-contained packets, exact Git evidence, direct result handoffs, and autonomous Workers without starting the V7 Controller, Work Orders, ACTION transport, recovery, or recurring monitors.
---

# X9 Loop Style

## Default

Use `STYLE_ONLY` unless the owner explicitly selects a separately proven V7
canary. Read `$devad-x9` first, then
[the operating reference](references/v6-style-operating.md). This skill is
the normal route for Thinker, Looper, Linker, and Worker project coordination.

Do **not** run `loopctl`, activate a Controller, create a Work Order, dispatch
an ACTION, register a role, recover V7 state, or start a recurring monitor.
The retained `$devad-x9-loop` compatibility name redirects to this skill.
`$x9-loop-code` is the separately named, quarantined Controller trial; it is
not the default operating authority.

## One bounded work packet

Before implementation, create or reread one compact durable packet containing:

- owner goal, repository/worktree/branch/base, exact claimed paths and
  exclusions;
- current source evidence, acceptance tests, security/release gates, rollback,
  and STOP conditions;
- the next safe action and the task that owns it.

Existing Git, source, tests, and durable receipts are truth. Chat is a
signal-only pointer to a packet or result; do not resend history. Verify a
capability before planning replacement work. A missing owner relation blocks
only that affected task.

## Optional context, memory, and docs

Style can use the existing source-backed Project Intelligence contract at
[project-intelligence-v1.md](references/project-intelligence-v1.md),
`$devad-memory`, and `$x9-project-docs`. Before planning and before the first
behavioral edit, re-read the capsule’s source spans at the current Git SHA.
Memory, chats, graphs, Sheets, and RAG only help locate candidates; none can
authorize a task.

After an accepted Style result, generate the compact feature sitemap and docs
from the bound `x9-loop-style-result-v1` receipt described in
[style-result-receipt.md](references/style-result-receipt.md). The generated
docs and profile-local memory are derived context, never a Controller,
dispatch, claim, or routing authority.

## Roles

| Role | V6-style responsibility |
| --- | --- |
| Thinker | Review one stable material diff or real architecture/security boundary; concrete findings are defect evidence. |
| Looper | Maintain the packet ledger, identify dependency-ready safe work, and unblock or route a bounded fix. It leads; it does not merely report. |
| Linker | Relay one exact path/hash signal when asked; it never selects or transforms work. |
| Worker | Implement inside the packet claims, run focused proof, record a durable receipt, and continue the next safe authorized action. |

Use short task titles: `Thinker`, `Looper`, `Linker`, or `Worker` plus a one-
or two-word suffix. Creation defaults never overwrite an existing task's model
or thinking; every follow-up omits both. If a task must be created with an
explicit setting, use only a host-advertised model/reasoning pair; never send
the unsupported `thinking=minimal` value to Terra.

## Autonomous flow

1. Check repository, base, local changes, claimed paths, and the packet.
2. Classify a question as `CONTINUE_LOCAL`, `LOCAL_FALLBACK`,
   `SUBAGENT_ONCE`, `THINKER_ALLOWED`, or `OWNER_REQUIRED`.
3. Implement and run cheap/focused proof first. A blocked dependency pauses
   only its lane; immediately continue any disjoint safe work.
   Keep the current task, worktree, branch, and exclusive paths as a sticky
   lane while its bounded result is in progress. Remote-main movement alone is
   `REBIND_DUE`, not a reason to stop, reattach, rebase, copy, or replace the
   Worker. Rebind only at an integration/release boundary or on an actual
   identity, shared-claim, resource, or assumption change.
4. Request one Thinker review only for a stable material diff, a real
   architecture/security boundary, or two distinct proof-bound failed routes.
5. Write a compact durable result with base, changed paths, tests/security,
   remaining risk, rollback, and next owner. Send one `RESULT_READY` signal.

Routine local/read-only/reversible inspection, coding, tests, formatting,
commits, push/readback, and dependency-ready next actions are already
authorized inside the packet. Never call a lane `BLOCKED` because a reviewer
has not approved routine work. After one difficult same-scope failure, use at
most one bounded helper according to `$subagents`; do not create an escalation
loop.

## Safety and fallback

Never use style mode to bypass a live controller action, identity/receipt
mismatch, claim conflict, security gate, provider/deploy boundary, destructive
action, or production decision. Those remain fail-closed or owner-bound.

If there is no active V7 action and the host cannot route a task or worktree,
record `STYLE_FALLBACK_AVAILABLE` and continue only through this packet flow.
Do not automatically switch on test or code failures; fix those locally first.
The host cannot enforce arbitrary Codex messages, task models, or task wakes;
record that limitation honestly.

## Completion labels

Use exact labels only when proven: `STYLE_APPLIED`,
`SKILLS_VERIFIED_EXISTING`, `SKILLS_INSTALLED`,
`LOOP_PROFILE_INITIALIZED`, and `LOOP_ACTIVATED`. `VERIFY_ONLY` is never an
installation claim.
