# Lesson 05: Product Candidate First, Not Perfect Baseline

Read this when GPT/Codex starts building proof infrastructure, transport
packages, manifests, wrappers, review packets, or capability gates faster than
it is building the requested product behavior.

## Failure pattern

The worker tries to make the test path production-grade before there is a
product candidate. It treats preferred transport failure as a program blocker,
re-reviews stable bytes, creates V2/V3 packet families, or waits for a reusable
gateway when an owner-approved disposable proof would validate the behavior.

## Required correction

1. Restate the visible user outcome in one sentence.
2. Name the current owned source/test slice that can move today.
3. Split proof rows: product behavior, disposable test proof, sealed RC proof,
   deploy/readback, browser proof, and provider/publication proof.
4. Continue every row whose hard invariants are satisfied.
5. For a failed route, preserve the invariant and change the mechanism once.
6. After one diagnostic and one structurally different route, stop route work:
   either execute the product slice, split the focused suite, or record the
   exact owner/operator boundary.
7. Do not create a reusable gateway or capability package when the user only
   needs a disposable test proof.

## Concrete regressions

| Pattern | Wrong response | Correct response |
|---|---|---|
| CHAT PG sealed gateway missing | Build multiple SSH/Tailnet/Dokploy packages before behavior proof | Run disposable PG behavior proof first; sealed gateway blocks only RC transport |
| Full PG suite timeout | Create new infra or declare `RESUME_ON` | Split migration/RLS, replay ledger, delivery intent, provider fake spines |
| Content browser/date issue | Declare runtime boundary | Patch/prove UI/backend persistence in the Content branch |
| Browser bridge reset | Stop whole lane | Mark `BROWSER_TOOL_ONLY`; continue source/test unless visual proof is the active row |
| Stable file-only review passed | Ask for another review after status/hash churn | Reuse the hash-bound review until material bytes or risk change |

## Hard safety boundary

This lesson never permits secret/raw config/log exposure, unapproved provider
spend, production mutation, destructive data action, collision bypass, or
claim expansion outside the authority envelope. It removes duplicated process,
not safety.
