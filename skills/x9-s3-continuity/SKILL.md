---
name: x9-s3-continuity
description: "Provider-offline, Contabo-first selected-project S3 continuity with client-side encryption, immutable generations, verification, restore, and rollback."
---

# x9-s3-continuity

Compact public routing card for the standalone S3 continuity addon.

Use only for explicitly selected-project continuity work. The addon uses an injected, already-approved SDK boundary; it never discovers credential values, constructs a client, contacts a provider, or mutates a bucket by itself.

Full implementation: `skills/x9-s3-continuity/`.
Contract: `docs/S3_CONTINUITY_ADDON.md`.
Focused proof: `tests/test_x9_s3_continuity.py`.

- Keep real provider capability, credential, retention, and restore proof behind a separate owner-approved gate.
- Preserve path validation, authenticated encryption, immutable conditional writes, manifest/marker ordering, complete verification, and non-overwriting restore.
- Never publish credentials, bucket values, provider payloads, or live evidence.
