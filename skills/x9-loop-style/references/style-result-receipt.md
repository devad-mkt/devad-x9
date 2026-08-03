# Style Result Receipt

Use one compact durable receipt after a bounded Style packet has focused proof.
It is the only normal input to `x9-project-docs`.

```json
{
  "schema": "x9-loop-style-result-v1",
  "outcome": "SUCCESS",
  "feature_id": "short-feature-slug",
  "profile_id": "project-profile-id",
  "base_sha": "<40-lowercase-git-hex>",
  "current_sha": "<40-lowercase-git-hex>",
  "plan_ref": {"path": ".devad/features/short-feature-slug/plans/PLAN.md", "sha256": "<sha256>"},
  "source_refs": ["<current source evidence reference>"],
  "proof": [{"kind": "tests", "path": ".devad/features/short-feature-slug/artifacts/tests.json", "sha256": "<sha256>"}],
  "changed_files": ["src/example.py"],
  "unknown_items": [],
  "rollback": "restore the prior Git commit"
}
```

Before accepting it, reread the current Git identity, plan hash, source refs,
and proof hashes. A stale, failed, incomplete, advisory-only, or changed
receipt is not `VERIFIED`. A different accepted input creates a new feature
packet; it does not rewrite prior evidence.
