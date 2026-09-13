# Source-to-Native Mapping

## Freeze inputs

Record path, hash, bytes, version, and retrieval date for the plan, Sheet
export/archive, evidence manifest, public pages, licensed root, native
remote/ref/SHA, and accepted receipts. Use one native SHA. Record later remote
movement separately; never mix snapshots silently.

## Inventory before reading

Use `rg --files` to enumerate Sheet HTML/tables, evidence/manifests, licensed
UI/backend files, native pages/components/routes/controllers/services/models/
jobs/events/tests, and output folders. Hash inputs before interpretation.
Preserve unknown output; a collision blocks only that packet.

## Parse Sheet exports structurally

Read table names, headers, stable IDs, and relationship columns. Extract
feature/page/chunk/control/setting/journey IDs, parent/child/alias relations,
status/gap/decision/traceability/acceptance, applicability, and citations.
Keyword search is discovery only. Join by stable IDs and classify every row.

Do not write the live Sheet without explicit connector authority for bounded
preimage/write/readback.

## Enumerate public sources

Collect every feature/docs/changelog subpage. Canonicalize by URL, slug, title,
and content hash; preserve aliases. Record advertised behavior, versioned
additions/fixes/removals/contradictions, and exclusions. Public docs remain
`DOCS_ONLY` until supported by live UI/source. Cite canonical pages directly.

## Map licensed reference

Search UI labels, settings, routes/actions, listeners, requests, handlers,
provider adapters, callbacks, errors, retries, and versions. Trace:

`surface -> control -> listener -> request -> handler -> persistence/provider
-> callback/receipt -> rendered state`

Cite path, tight lines, hash/version, and behavior. Quote small identifiers
only; do not copy large licensed code bodies.

## Map native code

Prefer frozen Git object reads:

```powershell
git ls-remote <remote> <ref>
git grep -n <query> <sha> -- <scope>
git show <sha>:<path>
```

Trace React/Inertia pages/components/hooks, Wayfinder bindings, Laravel
routes/controllers/requests/policies/services, models/migrations/jobs/events/
outbox, provider adapters/webhooks/receipts/reconciliation, and Pest tests.
Current native patterns are the implementation seam; reference architecture is
not copied.

Every code claim includes repository@SHA, path, tight line range, symbol, and
the supported claim.

## Prove absence

Use `ABSENT_AT_SHA` only with SHA, searched scopes/types, exact queries/aliases,
likely owner domains, exclusions, and limitations. One failed keyword query is
`UNKNOWN`.

## Decide change mode

Record:

`EXISTING_FEATURE | UI_SETTINGS | SERVER_AUTHORITY | PLAN_ENTITLEMENT |
REFERENCE_REUSE | PERSISTENCE_CONSUMPTION | INTEGRATED_HISTORY | TEST_PROOF |
GAP | CHANGE_MODE`

Use `REUSE`, `EXTEND`, `NEW`, `OWNER_DECISION`, or `DROP`. Propose the smallest
vertical bundle and focused proof; do not implement in an evidence-only mission.

## Contradictions

For every conflict record ID, source/version/date, strongest evidence,
disposition, unresolved question, and dependent rows. Never silently merge
versions. Preserve `UNKNOWN` when evidence cannot decide.

## Rebind after integration

An accepted commit being reachable from a merge proves history, not that its
behavior won the merge. For every decisive owner-approved surface:

- bind the predecessor commit and path, expected blob when still applicable,
  and one semantic predicate or focused regression before integration;
- inspect the resulting integration-tip path and rerun that proof after the
  merge or cherry-pick;
- classify a stale selected blob or contradicted predicate as
  `SEMANTIC_INTEGRATION_DRIFT`, even when ancestry, CI, and health checks pass;
- refresh dependent source mapping to the verified integration SHA before
  issuing another implementation contract.

Use exact blob equality only when no legitimate later change is expected.
Otherwise compare the bounded behavior and its focused test. Never resolve
drift by importing a whole historical branch.
