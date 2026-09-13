# Current active catalog

This directory is the sanitized public snapshot of the current Codex and
Agent skill entrypoints. It keeps the two source roots visible under
`codex/` and `agents/`, records one catalog entry per discovered skill, and
uses portable placeholders instead of profile-specific paths.

`seo-content-engine` is published once as `z-content`; the original name is a
compatibility alias, not a second active body. The older root `skills/`
package remains available for legacy Style G consumers and is not the default
installer source.

The catalog omits credentials, cookies, environment files, runtime databases,
logs, generated benchmark/recovery evidence, disabled entrypoint snapshots,
and machine-specific identity or repository paths. Run
`scripts/validate_active_catalog.py` before publishing a change.
