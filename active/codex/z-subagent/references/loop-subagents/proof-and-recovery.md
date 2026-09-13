# Proof and Recovery

Use applicable tier verdicts independently: `SOURCE`, `TEST`, `BROWSER`,
`RUNTIME`, `PROVIDER`, `DEPLOYED`, `LIVE` with `PASS`, `FAIL`, `NOT_RUN`, or
`UNKNOWN`. One tier never proves another.

## Browser acceptance

For feature-rich UI, require a populated deterministic fixture and observe the
named list, selection/detail, enabled local interaction, disabled effect, invalid
and recovery state, keyboard flow, and required viewport. Empty/blank rendering,
a screenshot, HTTP 200, hidden properties, or string tests are `REQUEST_CHANGES`.

If the owner named a historical implementation as the baseline, Browser `PASS`
also requires the parent to open its populated default journey, compare every
`BASELINE_REQUIRED_FEATURES` row against the rendered destination, and report
the feature-count delta. A cleaner or safer rewrite that silently removes an
accepted baseline behavior is `REQUEST_CHANGES`, even when source tests pass.

## Bounded recovery

| Trigger | Parent action |
| --- | --- |
| Stale/ambiguous evidence | Refresh evidence once, then accept/decline. |
| Proof failure | Give exact command/output/invariant to same implementer once. |
| Review disagreement | Inspect contract-critical hunk and decisive proof. |
| Tool, sandbox, or role failure | Record route failure; use admitted safe alternate. |
| Collision or new owner boundary | Stop only that slice and rebind/seek authority. |
| Generic continuation conflicts with active recovery | Resume the canonical active slice; do not advance without owner acceptance or explicit defer. |
| Patch resolves outside target root | Stop immediately; restore exact preimages, verify hashes, and retry only with absolute target-bound paths. |
| Reference worktree changed or output was truncated | Treat scope as unknown; repair and hash-verify the reference before any further mutation. |

After one evidence refresh and one repair: shrink the slice, choose a cheaper
existing proof path, or report one exact boundary. Do not create another worker,
reviewer, package, transport, or status loop.

## Acceptance blockers

Never accept on prose claims, timeouts, stale receipts, unverified role metadata,
dirty owned output without a final patch/commit hash, unresolved P1/P2 findings,
or mismatched fixture/proof SHA. A stale Desktop panel is `DISPLAY_STALE` or
`STATUS_UNKNOWN_AFTER_RESTART` under X-SubAgent; never fix it by spawning,
polling, or altering runtime state.
