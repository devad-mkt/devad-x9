# Security Boundary

## Required invariants

- Only explicitly `INCLUDED` projects are accepted.
- Project, generation, and object paths are normalized and reject absolute,
  parent-traversal, control-character, and separator escapes.
- AES-SIV comes from the installed `cryptography` library. There is no custom
  cipher or plaintext fallback.
- Key identity, generation, and object key are authenticated data.
- Every object is checked by ciphertext size/hash, authenticated decryption,
  plaintext size/hash, and manifest content root before restore.
- Conditional creation is required before any generation can be committed.
- A final commit marker is written last; its absence is incomplete.
- Restore quarantines collisions and never overwrites an existing target key.
- Credentials, bucket values, provider payloads, and logs are outside this
  package's configuration surface.

## Gate status

The P0 gate is provider-offline and uses only the deterministic fake store and
an injected SDK call recorder. The separate external Contabo gate remains
unrun and is required before any live/provider claim.

The public package now lists the addon in its source manifest and feature
registry. The separate external Contabo gate remains intentionally unrun:
provider capability negotiation, credential resolution, bucket authorization,
retention, and restore proof require an owner-approved external Work Order.
