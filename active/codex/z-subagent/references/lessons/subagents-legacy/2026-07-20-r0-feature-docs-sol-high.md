# Subagent Lesson

| Field | Value |
| --- | --- |
| Date | 2026-07-20 |
| Lane | side-question |
| Task class | read-only R0 feature-document and generator review |
| Repository / packet identity | D:\\CDx9\\0-cdx-wt\\f22d\\1-core-x9; R0 decisions a3daffc4aed7bb8a20b646420096c957c8e2eda1fc62ee952e878c5b13b1315a |
| Model / effort requested | gpt-5.6-sol / high |
| Model / effort attested | requested through the collaboration tool; runtime telemetry unavailable |
| Main-agent profile | Unknown |
| Why this tier was selected | Multi-file deterministic-doc review with security and provenance implications |
| Scope and forbidden actions | Read current feature conflicts and accepted recipes; no writes, Git mutation, broad tests, secrets, or authority changes |
| First-pass result | PASS |
| Independent proof | Current index generator and nine unresolved feature paths were checked against frozen decisions and Git objects |
| Retries / compactions | 0 / 0 |
| Wall time | Unknown |
| Token telemetry | unavailable |
| Approx. new-token volume | Unknown |
| Safety or truth errors | none; found three P1 pre-C1 defects |
| Ranking action | keep |

## Result

- Evidence and concise outcome: Found culture-sensitive sorting, an insufficiently bound decision epoch, and personal identity text in a historical report; supplied exact bounded corrections and validation order.
- Best use case learned: Sol High is effective for a read-only multi-document contract audit while a single executor owns edits.
- Next profile to try, if any: SOL medium for a purely mechanical projection check after the contract is frozen.

## Follow-up Re-review

- The corrected generator at SHA-256 `a45e94e36961278fde9068038bea44e2f1affb3bc1612f8e2cba0764a4825612` passed the read-only contract review for exact epoch binding, ordinal ordering, empty arrays, UTF-8/LF bytes, and deterministic design.
- Actual two-run output hash equality remains an executor gate.
