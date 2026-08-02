# Historical Validation Report - 2026-07-14

> Historical V6 record only. Current Style/Code package validation is performed
> by the bundled manifest, package, and secret-scan gates before publication.
> This retained report is not proof of a current installation, activation, or
> production Controller.

| Gate | Result |
| --- | --- |
| Full unittest discovery | PASS, 147 tests in 118.667 seconds |
| Retained v3/v5 behavior | PASS inside the same 147-test run |
| Official skill validator | PASS, 6/6 skills |
| Python AST | PASS, 40 active Python files |
| PowerShell AST | PASS, 5 active scripts |
| Secret scan | PASS, 430 text files and 0 findings |
| Manifest metadata guard | PASS; `.git` is excluded by the builder and rejected by the validator |
| Manifest line-ending guard | PASS; CRLF UTF-8 text is rejected before hashing |
| AIP real worktree shadow | PASS, 20 dirty paths unchanged; reconcile 0.319688 seconds |
| AIP disposable scope replay | PASS, 2 exact product claims accepted and 18 unrelated `.devad` paths rejected; reconcile 0.842138 seconds |
| CORE migration dry-run | PASS, 2,314 existing `.devad` files unchanged |
| OpenCode doctor | `TOOL_UNAVAILABLE`; one check, both configured model IDs missing, Worker not blocked |
| Independent review | 8 findings fixed and locked by regression tests; 2 later optional reviewers timed out and are not counted as proof |
| Model execution | NOT RUN; no GLM or Kimi request reached model execution |

`loop.db` remains disposable. `SNAPSHOT.json`, Worker receipts, and current Git are the recovery inputs. Markdown status and handoff files are generated views only.

Final source-manifest validation, temporary installation, final secret scan, and independent read-only review are recorded in the C1 security attestation before commit.
