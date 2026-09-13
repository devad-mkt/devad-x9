# Terms and Completion States

Report applicable axes independently:

`SOURCE | TEST | BROWSER | PERSISTENCE | PROVIDER_EFFECT | DEPLOY | PRODUCTION | OWNER_ACCEPTANCE`

Use `NOT_STARTED`, `PARTIAL`, `PASS`, `FAIL`, `UNKNOWN`, `NOT_REQUIRED`, `EXTERNAL_GATED`, or `DEFERRED_PRESERVE` per axis.

Reject bare `done`, `complete`, `working`, `ready`, `restored`, `adopted`, or `PASS`. A screenshot, route 200, browser-memory draft, disabled control, fake, test, or subagent verdict proves only its named axis. `DEPLOYED` is not `PRODUCTION_PROVED`. A deferred row remains preserved, not abandoned or complete.

For integrations, define every provider's connection class explicitly. `Manual
user-owned credentials` means the customer owns the provider app/integration
and supplies credentials. It removes managed OAuth/install/discovery/provisioning
only; it never means UI-only, no backend, or permission to omit secure
persistence, authorization, adapters, lifecycle, and proof.
