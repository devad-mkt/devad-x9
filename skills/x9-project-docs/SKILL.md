---
name: x9-project-docs
description: Generate and validate compact source-bound project documentation from one accepted Style receipt or experimental Controller result; use for the optional profile-local project brain/docs add-on.
---

# X9 Project Docs

Use this optional add-on after a bounded result is accepted. In stable
`STYLE_ONLY`, it consumes a direct `x9-loop-style-result-v1` receipt. In an
explicit `$x9-loop-code` trial, it may instead consume an accepted canonical
`x9-loop-result-v2`. It turns bound evidence into a compact feature packet; it
never creates proof, selects work, dispatches a task, or changes public product
docs without an explicit claim.

## Contract

- Style input is one accepted `x9-loop-style-result-v1` receipt with an exact
  plan reference, current Git identity, source spans, proof hashes, profile,
  changed paths, no unknown items, and rollback. Controller input remains the
  exact accepted `x9-loop-result-v2` binding of feature packet, plan, Work
  Order, dispatch/event, Worker, profile, base, result, proofs, and manifest.
- Output is derived only at `.devad/features/<feature>/`; caller-supplied output roots are rejected. It contains `TASK.md`, `FEATURE.json`,
  `MANIFEST.sha256`, and the numbered Markdown packet described in
  `references/project-docs-contract.md`.
- `TASK.md` is a direct-link sitemap. Every linked file is local, present, and
  manifest-bound. Evidence labels remain `VERIFIED` only when the exact Style
  receipt or experimental Controller result is accepted.
- Generation is idempotent: repeating it with identical inputs is byte-identical
  and zero-delta.
  Changed canonical inputs require a new run and preserve the prior packet.
- Profile memory is derived at
  `.devad/profiles/profile-<sha256(profile-id)[:32]>/memory/project-memory.sqlite`.
  Callers do not supply a database path; memory cannot authorize work,
  Controller actions, or a Style packet.

## Safe use

Read current Git and the exact receipt/packet files first. Validate the
sitemap, manifest, source references, result identity, and profile identity
before writing. Keep generated docs small, local, deterministic, and
secret-free.
Do not call providers, models, deployment, schedulers, pollers, or installed
skill replacement. Use the shared project-brain helpers when available.
