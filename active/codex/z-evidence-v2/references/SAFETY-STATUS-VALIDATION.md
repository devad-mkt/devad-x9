# Safety, Status, and Validation

## Authority and privacy

Evidence authority does not imply product, test, Git, Sheet, database, provider,
runtime, deploy, billing, or live-record authority. Execute only exact named
live actions. Keep build, source push, deployment, and live proof separate.

Never retain customer names, phone/email, avatars, messages, attachments,
credentials/values, cookies/tokens/secrets, request headers/bodies, raw provider
responses, or raw DOM dumps. Secret scans report path/line/category, not values.

## Independent classifications

Evidence: `NATIVE_PROVED`, `NATIVE_PARTIAL`, `REFERENCE_PROVED`, `DOCS_ONLY`,
`ABSENT_AT_SHA`, `UNKNOWN`, `NOT_APPLICABLE`, `DEPRECATED`,
`EXCLUDED_BY_OWNER`.

Interaction: `SAFE_LIVE_OBSERVED`, `SOURCE_TRACED_NOT_CLICKED`,
`NOT_EXECUTED_UNSAFE`, `BLOCKED_4DEV`.

Decision: `REUSE`, `EXTEND`, `NEW`, `OWNER_DECISION`, `DROP`.

Do not collapse dimensions. A reference-proved unsafe control may be a native
`NEW` gap.

## Outcome

- `PASS`: every bounded predicate is proven.
- `PARTIAL`: named live/provider/deployment/unreachable-state proof is missing.
- `BLOCKED:<gate>`: the objective cannot proceed because required authority,
  identity, secret-safe access, or output ownership is absent.

A missing page blocks its live rows, not source work. A failed preferred tool is
a route blocker; try one structurally different allowed route.

## Per-file gates

- `Author: Codex`, date, packet/folder, snapshots, live state, legend, and TOC.
- Sibling/master/source links resolve.
- Material claims have citations.
- Code citations have line ranges and SHA/hash.
- No unsupported complete/live/delivered/read claims.
- No secret/customer content.
- UTF-8 and final newline.

## Per-packet gates

- Exactly five canonical Markdown files.
- Responsibilities are separated and cross-linked.
- Every candidate is classified; counts reconcile; IDs are unique.
- Shared/channel-specific behavior stays separated.
- Unsafe actions are `NOT_EXECUTED_UNSAFE`.
- Every gap has decision, dependency, and smallest proof.

## Global gates

- Approved folders exist/index; owner-excluded folders do not.
- Every Sheet/public/source candidate is classified.
- Conflicts are resolved or `UNKNOWN`.
- Master totals reconcile without shared double counting.
- Privacy/secret scan passes.
- Every report has SHA-256/bytes.
- Native/reference/browser snapshots are recorded.
- Git and external systems show no unauthorized mutation.

Use `scripts/validate_packet_library.py` for structure, then manually check
claim quality, denominator reconciliation, privacy, and no-mutation proof.

## Stable review

After bytes stabilize: compare taxonomy to folders, sample every family,
reconcile totals/exclusions, inspect every `UNKNOWN`/`ABSENT_AT_SHA`/
`OWNER_DECISION`, check links/citations/IDs, correct evidence-backed defects,
rerun affected gates, and freeze hashes/receipt.

