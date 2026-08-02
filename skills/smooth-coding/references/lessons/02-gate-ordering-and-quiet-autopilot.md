# Lesson 02: Gate Ordering And Quiet Autopilot

Use this lesson when routine delivery consumes more coordination than coding.

| Problem | Effect | Fix |
|---|---|---|
| Intent is not classified first | A read-only verification is reported as installation, or a skill-only request creates project runtime state | Bind `VERIFY_ONLY`, `STYLE_ONLY`, `SKILL_ONLY`, or the project runtime intent before mutation and use an exact completion label |
| Expensive gates run before decisive prerequisites | A long suite or review finishes before discovering a missing tool, invalid path, dirty target, line cap, syntax error, or Git identity | Run cheaper prerequisites first when they can invalidate later work; otherwise run the first decision-changing runtime, migration, security, or compatibility gate |
| Deterministic failure is sent to a reviewer | Tokens are spent asking a model to restate a mechanical `NO_GO` | Fix the deterministic defect or stop at the exact external boundary before model judgment |
| Stable proof is rerun after an unrelated correction | Full suites and reviews multiply while unchanged behavior is re-proved | Rerun the failed gate and only affected later gates; reuse proof for unchanged bytes |
| Running or waiting is narrated repeatedly | Model turns and tokens are consumed without changing state | Wait silently and report only a transition, blocker, owner action, or final result |
| A task ends with an available `NEXT` | The owner or manager must wake it manually, so autopilot is false | Start the next authorized dependency-ready action in the same turn; stop only at completion or a genuine external blocker |
| Release states are collapsed | `built`, `published`, `installed`, `initialized`, `activated`, and `production-proven` are confused | Report each state separately and claim only what current evidence proves |
| Host policy is scoped globally | Unrelated operating-system jobs, applications, or projects block the current objective | Bind policy to the exact project/target identity; keep unrelated host state diagnostic and nonblocking unless the active boundary truly depends on it |
| Relevance uses broad words | Another Codex project or ordinary worktree is misclassified as current-project authority | Use exact project/profile/target identities or explicit configuration, never generic substring matching |
| Visible tasks and hidden helpers are confused | A wrong model capability is reported or duplicate roles are created | Choose visible task versus bounded hidden helper first and use that surface's actual capability list |
| Downstream work waits for a manager relay | A finished release does not wake the already-authorized consumer | Send one direct hash-bound handoff/callback after the durable result; never poll or require routine manager rescue |

The correction is not “skip safety.” Keep security, rollback, migration,
receipts, exact source proof, and owner-only destructive boundaries. Make them
decision-first, scoped, reusable, and connected to the next action.
