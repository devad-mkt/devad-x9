# Subagent Lesson

| Field | Value |
| --- | --- |
| Date | 2026-07-19 |
| Lane | side-question |
| Task class | Laravel behavior-neutral refactor rule check |
| Repository / packet identity | `$DEVAD_ROOT/1-core-x9` at `59c50c603e86cb7b37a0e680468ffccc0fc2e880` |
| Model / effort requested | `gpt-5.6-sol` / medium |
| Model / effort attested | unavailable |
| Main-agent profile | inherited subagent implementer |
| Why this tier was selected | Small read-only convention check over four source files and three rule files. |
| Scope and forbidden actions | Read only; no edits, tests, staging, commits, secrets, or scope expansion. |
| First-pass result | FAIL |
| Independent proof | Direct comparison with the parent lane invariant forbidding public API changes. |
| Retries / compactions | none |
| Wall time | unavailable |
| Token telemetry | unavailable |
| Approx. new-token volume | `Unknown` |
| Safety or truth errors | Recommended changing a private method to public despite the explicit no-public-API invariant. |
| Ranking action | keep for bounded reads, but strengthen invariant restatement |

## Result

- Evidence and concise outcome: The reader correctly located duplicated stage/call-slot policy, but its proposed public-static consolidation was rejected because it widened the public API.
- Best use case learned: SOL medium is useful for narrow convention mapping when every non-negotiable invariant is repeated in the short packet and checked mechanically by the parent.
- Next profile to try, if any: None; the parent can evaluate internal-only refactors directly.

