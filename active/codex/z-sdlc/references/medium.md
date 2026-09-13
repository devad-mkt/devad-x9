# Medium Mode

Use Medium for moderate ambiguity or impact while keeping token and process cost low. It is a compressed Ultra reasoning pass plus risk-selected SDLC evidence.

## Compact Context Map

Record only what affects the change:

- Existing behavior or equivalent
- Canonical server/component owner
- UI/config/feature flag when relevant
- Persistence and runtime consumption path
- Tenant, permission, quota, or compatibility boundary
- Existing tests and release gates
- Material unknowns

Use `VERIFIED`, `NOT_APPLICABLE`, or `UNKNOWN`. Narrow to discovery when a material owner or behavior remains unknown.

## One-Pass Ultra Loop

1. **Frame:** Objective, constraints, acceptance, and changed risks.
2. **Explore:** Compare the current/reuse route with one credible alternative.
3. **Decide:** Choose by correctness, simplicity, reversibility, and evidence cost.
4. **Execute:** Implement one vertical slice with a red/green check when behavior changes.
5. **Challenge:** Test one strongest sibling, misuse, tenant, compatibility, interruption, or retry case.
6. **Verify:** Run focused and repository-required gates; inspect exact diff.

## Evidence Selection

Choose only relevant checks:

- Trust boundary: validation, authorization, injection, secret-safe logging
- Multi-tenant: workspace ownership and cross-tenant denial
- Persistence: defaults, migration compatibility, atomicity, copy/rerun behavior
- Async/external: idempotency, retries, timeout ambiguity, safe degradation
- User interface: real interaction, accessibility, responsive state, console/network failures
- Operational: rollback or monitoring only when runtime behavior changes

## Anti-Bloat Rules

- Reuse current services and gates before introducing policy, wrappers, or infrastructure.
- One reviewer or specialist is enough unless independent evidence or distinct domains justify more.
- Do not generate a full compliance packet, architecture suite, or repo audit for one moderate change.
- Documentation changes only when a public contract, operator procedure, or non-obvious ownership rule changed.

## Escalate to High When

The change is destructive, production-stateful, payment/auth/tenant critical, difficult to reverse, repeatedly fails, or needs deployment/activation judgment.

## Stop Condition

The acceptance behavior, strongest material edge, and applicable repository gates pass; compatibility and rollback are understood where state changed; optional improvements are separated from completion.
