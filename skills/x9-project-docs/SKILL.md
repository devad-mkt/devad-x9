---
name: x9-project-docs
description: Generate and validate compact source-bound project documentation from one accepted Style result or experimental controller-trial result. It is an optional derived docs/memory add-on, never routing authority.
---

# X9 Project Docs

Use this optional add-on after a bounded result is accepted. In normal Style,
consume exactly one `x9-loop-style-result-v1` receipt. In a trial, consume only
the trial's accepted result. Do not create proof, select work, dispatch a task,
or change public product docs without an explicit claim.

Write a compact packet only below `.devad/features/<feature-id>/`:

- `TASK.md`: direct-link sitemap;
- `FEATURE.json`: feature, accepted receipt hash, and file set;
- `MANIFEST.sha256`: exact hashes for the packet;
- a small numbered set of source/proof/decision notes.

Re-read the plan, current Git identity, source evidence, proof hashes, changed
files, and rollback before marking anything `VERIFIED`. Identical accepted input
is zero-delta; changed canonical input creates a new packet rather than
rewriting old evidence.

Generated docs and any memory index help a later task find evidence. They
cannot authorize code, claims, models, providers, push, deploy, or a receipt.
Read `references/project-docs-contract.md` before generation.
