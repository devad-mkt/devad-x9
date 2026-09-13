# B05B1 Model-Selection Observation

Date: 2026-07-28
Scope: one-agent-at-a-time CHAT delivery

## What happened

- One Terra-high worker implemented the normal B05B0/B05B1 source slices with
  `TOKEN_MODE LOW`.
- Its first B05B1 proof omitted several Work Order cases. After a precise
  correction prompt, it found the important public workspace-scope defect, but
  its next frozen diff still covered only that defect and omitted the remaining
  filter, cursor, query-ceiling, and zero-effect cases.
- The Terra worker was stopped before commit; no weak result was accepted.
- One SOL-high worker then received a narrow, task-local correction packet. It
  added the missing behavioral proofs, preserved the three-path scope, and
  passed the focused and adjacent suites.
- Root review and R0 THINKER then resolved one truthful cursor-contract wording
  ambiguity before C1/C2 and manager integration.

## Model-routing lesson

- Terra-high remains suitable for normal implementation when the contract is
  explicit and root independently reviews the frozen diff.
- After a verified security/tenancy proof gap or two incomplete proof passes,
  switch the single active worker to SOL-high rather than adding parallel
  agents or increasing prompt history.
- SOL-high is justified for frozen-diff correction involving tenant isolation,
  contract ambiguity, or broad behavioral proof. It should not be the default
  for routine mapping or mechanical delivery.
- Spark remains experimental for low-low-risk, reversible mapping or
  mechanical checks only. This run did not test Spark, so no quality or token
  savings claim is allowed.

## Budget and quality cautions

- This was not a controlled model benchmark: the models received different
  prompts and the SOL worker received a more precise failure packet.
- Per-agent token usage was unavailable, so cost efficiency remains
  `UNKNOWN`.
- The observed benefit came from one active agent, durable file/hash context,
  a frozen diff, and independent acceptance—not from agent count.
- Continue recording task type, model, effort, retries, accepted defects, test
  delta, elapsed time, and token usage when available.

## Default derived from this observation

1. Start with no helper unless delegation clearly saves root time.
2. Use one Terra-high or SOL-medium worker for normal implementation.
3. Use SOL-high only after a verified serious gap or for security/tenancy
   frozen-diff work.
4. Keep `TOKEN_MODE LOW` explicit.
5. Never use Spark as final authority for critical review.
6. Never run more than one active helper unless the owner explicitly changes
   the current one-agent budget.
