# Rollback

Rollback is restore-only and generation-addressed:

1. identify the committed generation and its recorded predecessor;
2. verify the predecessor commit marker, manifest, and every encrypted object;
3. restore into a disposable target with quarantine enabled; and
4. preserve the newer generation and its marker for audit or owner retention.

`S3ContinuityAddon.rollback_to_previous()` refuses a generation without a
committed predecessor and never deletes objects. Provider retention or deletion
requires a separately approved external Work Order; this Worker has no such
authority.

The focused rollback regression proves that a second generation restores its
explicit predecessor and leaves the newer commit marker intact.
