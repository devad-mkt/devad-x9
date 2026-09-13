---
name: z-tldr
description: Give short, plain-English, evidence-bounded verdicts only when the owner or user asks a THINKER, LINKER, LOOPER, or WORKER for a TLDR, summary, comparison, recommendation, or next-step answer. Use a compact issue/consequences/fix table, add WINNER only for real comparisons, then state an HONEST VERDICT and NEXT ACTIONS. Do not apply to role-to-role, automated, or system messages.
---

# zTLDR

## Activation gate

Apply this skill only when both conditions are true:

1. The message comes directly from the owner or user.
2. The message targets, or is being answered by, a `THINKER`, `LINKER`, `LOOPER`, or `WORKER`.

Do not apply it to role-to-role messages, automated events, callbacks, receipts,
or system instructions unless the owner/user explicitly asks for a TLDR.

## Output contract

Keep the whole answer compact. Default to no more than 180 words and use fewer
than 80 words when the decision is simple.

Start with one sentence:

`TLDR: <the most important result or decision>`

Then use one of these tables with one to four rows:

| ISSUE | CONSEQUENCES | FIX |
| --- | --- | --- |
| The real problem | What happens if unchanged | Smallest sound correction |

For a genuine comparison, add `WINNER`:

| ISSUE | CONSEQUENCES | FIX | WINNER |
| --- | --- | --- | --- |
| Decision point | Material tradeoff | Best correction | Option and short reason |

After the table, use exactly these sections:

**HONEST VERDICT:** State the conclusion in one or two direct sentences.

**NEXT ACTIONS:** Give one to three numbered actions in dependency order. Write
`NONE` when no action is needed.

## Honesty rules

- Lead with the actual result, not background or process narration.
- Separate proven facts from inference. Use `UNKNOWN` when evidence is missing.
- Do not call work complete without source, test, runtime, receipt, or other
  evidence appropriate to the claim.
- Name blockers narrowly. A failed route is not automatically a blocked goal.
- Do not invent a winner. Use `TIE` or `NO WINNER` when the evidence supports it.
- Omit jargon, analogies, history, and extra headings unless essential.
- Preserve material risk and constraints even when shortening.

## Provenance (consolidated 2026-09-12)

Canonical body: `z-tldr` (2026-08-13 00:38:44, 2 files, sha256 `66624d751ed8aef7`).

Former names now disabled: `NINELLC/tldr`.

Unique content from disabled copies is preserved under `references/preserved/` and is NOT authoritative; this body wins on any conflict.
