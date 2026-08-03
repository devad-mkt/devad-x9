# Autonomous Mission Protocol

Use with the canonical `../PLAN.md` and exactly one current immutable Work
Order. This protocol is guidance; it never expands the Work Order.

## Mission envelope

- Default duration: 90-240 minutes.
- Coding: normally 5-15 exclusive files.
- Evidence/browser: one complete denominator segment.
- One done token closes the whole outcome, not a file, command, page, test,
  review, receipt, commit, or periodic checkpoint.

## Routine decision rights

Inside exact claims, the worker may:

1. use current source, Git, focused docs/tests, and sibling conventions;
2. correct deterministic owned-output path/hash/count/wording mistakes;
3. choose the smallest current-repo-compatible internal arrangement when
   behavior is frozen;
4. fix and rerun in-scope test/format failures;
5. try one structurally different safe route after one route failure;
6. mark only a dependent claim `PARTIAL/BLOCKED` and continue all disjoint
   authorized phases;
7. complete stable review, C1/C2, normal push/readback, and clean proof only
   when the Work Order authorizes those gates.

## Fallbacks

- Failed writer/command: record once, use the named structural alternative.
- Missing locator: targeted current-source/owner/test trace, then mark only
  that claim partial.
- Missing browser: finish source/DOM/CSS/JS mapping; keep live status partial.
- Missing database/provider/shared resource: finish source/test/contract
  readiness without activation or substitution.
- Missing routine answer: use the smallest frozen current-repo convention.

## Hard stops

Stop for wrong identity/base, unexpected dirty overlap, missing claims, shared
collision, secrets/customer data, security ambiguity, invalidated design, or
destructive/provider-spend/database/live/public/production/deploy action
without exact authority.

## Stable closeout

After bytes stabilize, review once for correctness, security/privacy, reuse,
hidden dependencies, implementability, and overengineering. Keep C1 source and
C2 receipt separate. When authorized, run exact security/pre-push gates, push
normally, and prove local/upstream/remote equality plus clean state. Never infer
runtime/browser/provider PASS from source evidence.

## Wake and redispatch

Immediately before `DONE` or genuine hard `BLOCKED`, send:

```text
<PROJECT>_LANE_WAKE
LANE: <lane>
STATE: DONE | BLOCKED
TOKEN_OR_BLOCKER: <exact>
BRANCH_HEAD: <branch>@<sha>
RECEIPT: <path>|SHA256:<hash>|BYTES:<n>
NEXT_GAP: <one dependency-ready mission proposal>
```

The callback grants no next authority. If messaging is unavailable, return it
as final. The manager verifies the receipt, paths, privacy, proof, C1/C2 split,
branch/base, remote equality, and clean state, then immediately issues the next
hash-bound Work Order.

A periodic snapshot is fallback recovery only. It is a dispatch deadline, not
a worker stop point. Send no unchanged progress message.

## Anti-patterns

No chat-only todo lists, one-command prompts, implicit continuation, early stop
after one phase, repeated route aliases, filler research, broad history/repo/
workbook rereads, representative UI samples, wrong browser/runtime
substitution, duplicate stable reviews, shared-lane edits, false runtime PASS,
or routine owner escalation.
