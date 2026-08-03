# Style Result Receipt

Use this compact receipt after one bounded Style packet has focused proof. It
is the stable input for `$x9-project-docs`; it does not require a Controller,
Work Order, dispatch, or Worker registration.

## Required shape

```json
{
  "schema": "x9-loop-style-result-v1",
  "outcome": "SUCCESS",
  "feature_id": "short-feature-slug",
  "profile_id": "project-profile-id",
  "base_sha": "<40-lowercase-git-hex>",
  "current_sha": "<40-lowercase-git-hex>",
  "plan_ref": {"path": ".devad/features/short-feature-slug/plans/PLAN.md", "sha256": "<sha256>"},
  "source_refs": ["<canonical context source ref>"],
  "proof": [{"kind": "tests", "path": ".devad/features/short-feature-slug/artifacts/tests.json", "sha256": "<sha256>"}],
  "changed_files": ["src/example.py"],
  "unknown_items": [],
  "rollback": "restore the prior Git commit"
}
```

`source_refs` use the Project Intelligence canonical source-ref shape: a
repository-relative path plus current file/span SHA-256 evidence. The current
Git HEAD must equal `current_sha`; plan and proof hashes are reread before docs
are generated. A stale, failed, incomplete, advisory-only, or changed receipt
is rejected. A different accepted input uses a new feature slug rather than
rewriting an old packet.
