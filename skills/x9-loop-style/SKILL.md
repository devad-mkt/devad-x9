---
name: x9-loop-style
description: Use as the default lightweight Devad X9 coordination style for normal project work. It keeps workers autonomous with compact packets and receipts, without a Controller, scheduler, polling, or a second manager.
---

# X9 Loop Style — Stable Default

Use this skill for normal work in new and existing projects. It is a working
style, not a runtime: no Controller, `loopctl`, Work Order, ACTION file,
registration, scheduler, polling loop, or replacement manager is created.

## Authority Envelope

Before a bounded chunk, record only:

```text
LANE_ID / TASK / ROLE
REPO / EXISTING_WORKTREE / BRANCH / BASE / HEAD
EXCLUSIVE_PATHS / SHARED_RESOURCES
ALLOWED_ACTIONS / FORBIDDEN_EFFECTS
ACCEPTANCE_PROOF / ROLLBACK / STOP_CONDITIONS
CANDIDATE_STATE: PRESERVED_CANDIDATE | INTEGRATED | LIVE_PROVED
NEXT_LOCAL:<action> | DEPENDENCY_WAIT:<EVENT>
```

For a dependency wait, add one `RESUME_ON`: receipt type and SHA-256, expiry or
staleness rule, and exact next action. A dependency pauses only that named
chunk. If no already-claimed safe local slice remains, record
`NO_CLAIMED_DISJOINT_SLICE` once; do not poll or repeatedly report it.

## Work autonomously

Inside the envelope, the Worker must diagnose, make the smallest correction,
run focused proof, and continue. Parser, quoting, fixture, test harness,
command, and local-tool failures are local repairs. Keep one same-root,
low-risk problem local through three bounded correction cycles.

Before an external question, use exactly one admission:

| Class | Meaning |
| --- | --- |
| `CONTINUE_LOCAL` | Safe local work or a known next action exists. |
| `LOCAL_FALLBACK` | A preferred local route failed; try a different safe route. |
| `SUBAGENT_ONCE` | One difficult same-scope route failed; use at most one bounded helper. |
| `THINKER_ALLOWED` | A frozen material diff, real architecture/security boundary, or two distinct failures where judgment is needed. |
| `OWNER_REQUIRED` | A true owner-only product, secret, destructive, spend, provider, production, or scope boundary. |

Missing or malformed admission is `CONTINUE_LOCAL`, never `BLOCKED`. Use the
stateless `scripts/style_autonomy_gate.py` only at that escalation decision;
it stores nothing and cannot send messages or wake a task.

## Receipts and handoff

A matching fresh receipt resumes the declared action without a new approval.
Use `--receipt-case` in the gate to classify one receipt:

- missing/invalid: `DEPENDENCY_WAIT`;
- matching fresh event and SHA-256: `RESUME_READY`;
- stale, mismatched, expired, or duplicate: `ZERO_DELTA`.

One Looper may verify a receipt and send one direct pointer:

```text
EVENT + receipt path/hash + exact resume action + stop conditions
```

That pointer is transport, not approval. A Thinker reviews one frozen material
diff or a real security/architecture decision. The execution-only
infrastructure helper performs one exact shared capability packet at a time;
it cannot select priorities, manage workers, or take product-code claims.
Linker transports path/hash/result pointers only.

## Context, docs, and memory

Before planning or the first behavioral edit, read the source-backed context
contract in `references/project-intelligence-v1.md`. After an accepted result,
`x9-project-docs` may create a compact sitemap and `devad-memory` may index
history. Both are derived aids, never routing authority.

Read `references/v6-style-operating.md` for the compact packet and
`references/style-result-receipt.md` before producing a result. Use
`x9-loop-code` only for its explicit fresh-project trial; it is not a fallback
for normal work.
