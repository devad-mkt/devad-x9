# S3 Continuity Addon

Status: provider-offline P0 candidate. The package has its own configuration,
encryption, generation protocol, tests, rollback path, and failure domain. It
does not create an S3 client, read credentials, contact Contabo, mutate a
bucket, or become Controller authority.

## Configuration contract

`ContaboS3Config` is the first-provider profile. It returns only safe options
for an already-approved S3 SDK factory:

| Option | Contract |
| --- | --- |
| `provider` | `contabo` only |
| `endpoint` | HTTPS origin; default is the Contabo-compatible endpoint from the read-only reference |
| `region` | non-empty SDK region, default `default` |
| `use_path_style_endpoint` | required `true` |
| `bucket_env` | name of the external-gate environment variable, not its value |
| `access_key_env` / `secret_key_env` | names only; never read by this package |
| `namespace` | lowercase path-safe project namespace |

`sdk_options()` contains endpoint, region, path-style, and SDK version only.
The external provider gate owns credential resolution, bucket authorization,
and client construction.

## Generation protocol

`S3ContinuityAddon.create_generation()` accepts one explicitly `INCLUDED`
project and a mapping of selected logical object paths to bytes. It:

1. validates project, generation, and relative object identities;
2. encrypts each object with `cryptography` AES-SIV and authenticates the key
   identity, generation, and object key;
3. conditionally creates immutable encrypted objects;
4. writes a canonical manifest containing plaintext and ciphertext hashes;
5. downloads and verifies the manifest and every object; and
6. conditionally creates `GENERATION_COMMITTED.json` last.

Missing commit markers are incomplete generations. Object or marker collisions
fail closed. A marker binds the predecessor, manifest hash, object count,
content root, and negotiated capability profile.

## Capability and restore boundaries

The injected store supplies a `CapabilityProfile`; the addon does not assume
AWS behavior. Conditional create is mandatory. Client-side hashes are the safe
fallback when provider checksums are unavailable. Explicit generation keys are
the safe restore fallback when provider versioning is unavailable. Retention is
reported as owner-controlled unless separately proven by an external gate.

Restore verifies all objects before changing a target. Existing target keys are
quarantined by default and are never overwritten; `conflict_policy="fail"`
rejects a non-empty collision. `rollback_to_previous()` restores only the
committed predecessor and does not delete generations.

## Failure domain and external gate

`ConfigError`, `CapabilityError`, `ProviderError`, `GenerationConflict`,
`GenerationIncomplete`, `GenerationVerificationError`, `RestoreConflict`, and
`RollbackUnavailable` remain inside the addon boundary. No failure falls back
to another addon, Cognee, Controller state, or an unencrypted local copy.

Real Contabo capability negotiation, credentials, conditional writes,
checksums, versioning, retention, and restore drills require a separate
Controller-selected external-call Work Order with owner-approved budget and
receipt. P0 proves only the provider-offline fake and the SDK translation seam.

The read-only Core references supplied for reuse are configuration, smoke, and
focused-test evidence only. Their credentials, bucket names, Laravel coupling,
and source bytes are not imported.
