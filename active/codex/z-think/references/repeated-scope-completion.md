# Repeated Scope, Completion, And Activation Failures

Read this only after dirty or unowned work proceeds, narrative text is accepted
as completion, callbacks resolve through stale context, or safe source is
mistaken for activation permission.

## Scope Preflight

Before dispatch, execution, commit, or approval, bind repository, checkout,
base revision, task packet, ownership claims, exclusive resources, staged,
unstaged, untracked, and committed paths. Claims are permissions, not evidence
that the current checkout is clean. An unresolved breach produces no action.

## Canonical Completion

- Validate the exact result, proof, and event schema before callback or status
  transition. Plain Markdown and chat claims are non-authoritative.
- Resolve result and callback paths through the current task, dispatch, and
  packet. Do not infer them from actor identity or an older checkout.
- Verify that the output bytes, hashes, role, task, scope, and terminal state
  agree. A malformed completion remains incomplete.

## Separate Gates

Judge source correctness, commit readiness, installation, activation,
deployment, and runtime proof independently. A source candidate may be correct
while activation remains blocked by external jobs, permissions, credentials,
capacity, or environment state. Never clear one gate with evidence from
another.

## Receipt

Record `SCOPE_PREFLIGHT`, `CANONICAL_RESULT`, `CALLBACK_BINDING`,
`SOURCE_READINESS`, and `ACTIVATION_READINESS`.
