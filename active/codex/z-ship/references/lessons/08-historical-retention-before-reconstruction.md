# Historical retention before reconstruction

Use this lesson when the owner says `restore`, `previous`, `old work`, `exact`,
`missing`, `lost`, or asks for parity with an earlier accepted surface.

| What went wrong | Honest cause | Fix for this project | LoopSub prevention |
|---|---|---|---|
| Rich Inbox appeared “lost” | It lived on divergent commit `2f9be0cf` under `pages/workspaces/chat/inbox.tsx`. A later branch built a smaller Inbox under `pages/workspaces/apps/chat/inbox.tsx` without reconciling the old version. | Freeze `2f9be0cf` as the owner-approved visual/interaction baseline. Integrate the current tenant-safe backend into it feature by feature. | Admission must list all branches, worktrees, renamed paths, merge base and exact baseline SHA before coding. |
| Unified theme looked responsible | The token/theme system did not remove the UX. We wrongly treated shell/theme consistency as permission to replace the page structure with generic dashboard cards. | Protect both layers: dashboard shell/tokens and exact Inbox pane topology, density, icons, controls and states. | Theme changes may adjust visual tokens, but cannot alter page topology or remove behavior without an explicit retention decision. |
| Several restoration attempts were wrong | We kept extending the newer simplified Inbox rather than starting from the exact historical component graph. | No more screenshot reconstruction. Use the actual historical files as the presentation base. | “Try the exact historical baseline locally before rebuilding” is now mandatory. |
| Empty/200 pages passed review | Source tests, route 200, fixtures and string assertions proved small scopes—not visible Inbox parity. | Require populated selected, empty and error browser journeys before visual closure. | Zero rows, route 200, screenshots alone and string-only tests are explicitly non-acceptance evidence. |
| Subagents lost the denominator | Evidence agents omitted the divergent internal branch; implementers then worked correctly on the wrong base; reviewers checked only their declared scope. | Root independently verifies baseline hashes and one populated rendered journey. | Reports are evidence, never acceptance authority. Reviewer must search for omitted denominator rows and counterexamples. |
| Long-running work produced versions | Dirty/untracked files, divergent branches, path replacement, context compression, partial slices and external PG work fragmented authority. | One frozen baseline and one active reconstruction slice at a time. Preserve both old and new preimages. | One historian, one exclusive implementer, one adversarial reviewer; no duplicate reading or repeated unchanged proof. |
| A continuation message skipped unfinished recovery | A Thinker/Looper message said to continue the main plan and was treated as authority even though the owner-selected recovery row was still open. | Keep `ACTIVE_PROGRAM_PHASE`, `ACTIVE_SLICE_ID`, `ACTIVE_SLICE_STATE`, and `ADVANCE_GATE` in the canonical plan. Generic continuation resumes the active row. | Helper messages propose evidence or next work only. They cannot close, defer, reorder, or advance an active recovery slice without an owner-accepted receipt. |
| A restoration patch hit the reference worktree | The command context and intended b01r target diverged; a broad/truncated patch modified three preserved reference files before the mismatch was caught. | Restore the exact Git preimages, verify their hashes, then use absolute target paths with root-containment checks. Reference worktrees remain read-only. | Admission and receipts bind target root, read-only reference roots, resolved write paths, preimage hashes, patch method, containment result, reference post-hashes, and wrong-root recovery. |

## Required behavior

1. Search immutable Git history, renamed paths, worktrees, accepted receipts and
   owner-marked behavior before selecting the implementation base.
2. Try the exact owner-selected historical component graph locally before
   recreating it.
3. Protect newer security, tenancy, RLS, audit, replay and recovery work, but do
   not call it trustworthy until its exact commits, tests and receipts are
   rebound.
4. Build a row-level retention denominator. Each row is `RETAIN`, `EXTEND`,
   `DROP_OWNER_APPROVED`, or `DEFER_GATED`.
5. Do not accept a restoration from a blank fixture, route 200, source strings,
   screenshots alone, or a worker narrative. Require a populated rendered
   journey plus focused positive and negative backend proof.
6. Treat the canonical active recovery row as a focus lock. Continuation text
   resumes it until the owner accepts or explicitly defers it.
7. Verify target-root containment before and after every recovery patch. On a
   wrong-root write or truncated output, stop and restore exact preimages before
   any further mutation.
