# Subagent Lesson

| Field | Value |
| --- | --- |
| Date | 2026-07-31 |
| Lane | CHAT manager, read-only calibration |
| Task class | RC route diagnosis and Meta OAuth/webhook readiness |
| Repository / packet identity | `$DEVAD_ROOT\0-cdx-wt\3bcf\1-core-x9@8ecb23bd4e384f850d1f8f82b2dbcf94868cd145` |
| Models / efforts attested | `gpt-5.6-sol` low and medium; `gpt-5.6-terra` high and xhigh |
| Why these tiers were selected | Owner-requested same-harness comparison on two real, nontrivial CHAT tasks |
| Scope and forbidden actions | Named files and read-only Git only; no writes, fetch, browser, provider, Dokploy, deploy, or secrets |
| First-pass result | PASS for all four runs |
| Independent proof | Parent compared verdicts with current Git, PLAN gates, Work Order constraints, route source, and the Meta cutover checkpoint |
| Retries / compactions | 0 / 0 |
| Wall time | Pair 1 about 1m55s; pair 2 about 4m11s |
| Token telemetry | unavailable |
| Approx. new-token volume | Unknown |
| Safety or truth errors | none; minor differences in detail and compactness |
| Ranking action | CHAT-specific pilot only; do not change global defaults before five comparable samples |

## Result

| CHAT task | Profile | Parent score | Learned fit |
| --- | --- | ---: | --- |
| Bounded route/status diagnosis | SOL low | 97/100 | Best compact mapper in this sample |
| Same diagnosis | Terra high | 95/100 | Stronger hash and line detail, but longer |
| Serious OAuth/webhook readiness | SOL medium | 98/100 | Best balance of precision, safety, and actionability |
| Same readiness review | Terra xhigh | 96/100 | Correct but added no decision-changing assurance |

- Best current CHAT routing: SOL low for bounded read-only mapping; Terra high for normal implementation; SOL medium for serious cross-file diagnosis; SOL high for difficult security/architecture review; SOL xhigh only for critical or verified difficult failure.
- Luna and Spark were not callable in this runtime. Report `PROFILE_FALLBACK`; never claim they ran.
- Keep every dispatch task-local with `fork_turns=none`, `TOKEN_MODE: LOW`, named files, one success predicate, forbidden actions, and a compact callback.

## Low-token verification pattern

Do not have the manager redo the worker's implementation.

1. Freeze an actionable contract: exact behavior, invariants, paths, exclusions, tests, and stop conditions. Add examples only for ambiguous edge cases.
2. Require the worker to self-gate and return the changed-path manifest, frozen diff or patch ID, focused test results, security results, and uncertainties.
3. Let the manager run deterministic checks first: branch/base, exact path set, hashes, diff scope, test command identity, and receipt consistency.
4. Rerun only the smallest decisive tests and inspect only security-sensitive or contract-critical hunks.
5. Use one blind reviewer on the frozen diff only for material behavior, tenancy, security, provider, or architecture risk.
6. Deep-review the whole change only after drift, an unexpected path, a failing decisive test, reviewer disagreement, or a critical boundary.

This pattern keeps the manager accountable without paying twice for the same source exploration.
