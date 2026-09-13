# Subagent Lesson

| Field | Value |
| --- | --- |
| Date | 2026-07-28 |
| Lane | main |
| Task class | Model selection and bounded low-risk calibration |
| Repository / packet identity | CHAT R1 local-preview route correction at aff6 `64ecc8d6ee5a2d2f8219ce1fcc9c97cdc53ddf6e` |
| Model / effort requested | `gpt-5.3-codex-spark` xhigh, then safe fallback |
| Model / effort attested | Spark did not run; `gpt-5.6-terra` high ran as `PROFILE_FALLBACK` |
| Main-agent profile | Root manager |
| Why this tier was selected | The task was bounded, reversible, environment-only, and had exact process and file stop predicates |
| Scope and forbidden actions | Correct one local PHP document-root route; no product or Git edits, dependency changes, provider, PostgreSQL, Reverb, or deployment |
| First-pass result | PASS for the bounded route correction; the app exposed a new independent HTTP 500 |
| Independent proof | Wrong-root PHP PID stopped alone; replacement reached Laravel from `public`; Vite and Git were preserved; worker stopped at the new exception |
| Retries / compactions | One fallback because the requested Spark profile was unavailable in the collaboration runtime |
| Wall time | Unavailable |
| Token telemetry | Unavailable |
| Approx. new-token volume | Unknown |
| Safety or truth errors | none |
| Ranking action | experimental |

## Result

- Evidence and concise outcome: Spark produced no quality evidence because it was not callable. Terra high followed the actionable packet correctly and stopped at the exact new-error boundary.
- Best use case learned: Try Spark only for low-risk work that Luna medium could safely complete, such as exact extraction, mechanical mapping, routine test triage, or a noncritical shadow review. Never use it as the accepted reviewer for critical security, tenancy, architecture, production, money, secret, destructive, or irreversible work.
- Next profile to try, if any: On a later immutable low-risk packet, compare Spark and a low-cost Luna or Terra profile using identical hidden facts and score first-pass correctness, missed and false findings, actionable evidence, retries, wall time, and available token telemetry. Keep one active agent at a time unless the owner explicitly changes the budget.

Do not promote or reject a model from one task. Require actionable dispatches
with exact objective, named evidence, risks, assertions, forbidden actions,
success predicate, stop rule, and compact output schema.
