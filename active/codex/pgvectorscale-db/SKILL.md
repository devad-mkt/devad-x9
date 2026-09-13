---
name: pgvectorscale-db
description: Prepare, install, admit, execute, or review Devad's sealed PostgreSQL 18 plus vector and vectorscale proof leases. Use for CHAT ledger/RLS/migration proof, a fresh private PG18 proof resource, the devad-chat-pg18-proof gateway, CHAT_PG18_CAPABILITY_INSTALLED, CHAT_PG18_TAILNET_PRINCIPAL_READY, or verify-full PG test execution. Do not use for ordinary app databases, production queries, shared Stage1, or provider deployment.
---

# PG18 VectorScale Proof

Use this skill only for a sealed, disposable PostgreSQL 18 proof lease. Treat the project’s frozen proof guide and manifest as the authority for the current proof; this skill supplies the durable workflow, not substitute credentials or a database target.

## Start a fresh chat safely

When a user asks to “run the PG proof,” first state the exact phase: local source preparation, capability installation, lease admission, one frozen run, or evidence review. Then read [`references/fresh-chat-playbook.md`](references/fresh-chat-playbook.md) before selecting a tool or reporting a blocker.

Use that playbook for the safe tool matrix, receipt shapes, newcomer checklist, and recovery decisions. Start with its **Fast resume decision table**: it identifies the one missing layer without rediscovering old services, browser tabs, SSH history, credentials, or prior chats. Resolve all project-specific paths, IDs, commands, and hashes from the current project guide; never copy values from an old conversation.

For a CHAT proof, run [`scripts/verify-chat-pg18-preflight.ps1`](scripts/verify-chat-pg18-preflight.ps1) before any host inspection. It verifies the frozen Git bindings and optional sanitized receipt files locally; receipt files must be `.txt` artifacts under `.devad/features/chat-full-migration-1/artifacts/`. It never contacts a host, Dokploy, Docker, a database, or a browser and never reads environment/configuration values.

## False blocker guard

Do not accept or emit `BLOCKED`, `WAITING`, `FROZEN`, `HARD_BOUNDARY`,
`RESUME_ON`, or `OWNER_REQUIRED` for CHAT PG18 unless the message includes:

- `GOAL_OUTCOME`
- `EVIDENCE_TARGET`
- `FAILED_ROUTE`
- `WHY_ROUTE_FAILURE_APPLIES_TO_ALL_ALLOWED_ROUTES`
- `CHEAPEST_WORKAROUND_TESTED`
- `ACTION_NOW`
- `NEXT_MATERIAL_ACTION_OR_TRUE_OWNER_BOUNDARY`

If any field is missing, the correct response is
`REJECT_FALSE_BLOCKER:CONTINUE_LOCAL` plus the next direct action. Missing
sealed gateway/principal receipts block only `SEALED_RC_PROOF`; they do not
block an owner-authorized `DISPOSABLE_BEHAVIOR_PROOF`, source/test work, or a
suite split. A timeout or parser failure in the PG harness is
`ROUTE_BLOCKED:SPLIT_OR_FIX_TEST`, not authority to build another Dokploy,
Tailnet, SSH, gateway, packet, or review loop.

When the current CHAT worktree contains `.temp/chat-pg18-capability`, treat it
as a review candidate only. Its safe local sequence is `build-release.sh`,
`tests/package-static.sh`, and `tests/no-mutation-channel-matrix.sh`, followed
by one material review of the generated content-addressed release manifest.
Do not run its install or uninstall scripts locally, and do not treat a build
as either capability receipt or authority for a claim, host change, or PG run.

If that reviewed package has an intentionally fail-closed executor, the
shortest reusable local workaround is one bounded replacement of
`payload/executor`, plus its source-only runtime-state model and static tests.
Keep the listener, gateway, installer, policy packet, receipt fields and
cleanup protocol unchanged. The replacement may consume only the already-bound
digest-pinned image references and root-only candidate mirror; it must never
invent a DSN, mutable tag, raw Dokploy setting, transport route, or receipt.
Freeze and materially review that one new release. Thereafter every CHAT task
starts at preflight and reuses the capability rather than rebuilding it.

## Establish the truth lock

Before changing code, infrastructure, or a proof package:

1. Read the project router and its routed rules.
2. Read the canonical feature PLAN, the PG proof guide, and the one-lease manifest in full.
3. Record the exact worktree, candidate commit, manifest SHA/byte count, command SHA/byte count, lockfile identity, and every bound migration/test blob.
4. Verify the candidate objects directly from Git. Never use dirty working-tree bytes as a frozen candidate.
5. Confirm that the selected suite has one compatible database-role phase. Split or exclude any test requiring a conflicting current role; do not append it silently.

If a keyword or legacy artifact merely locates a possible implementation, trace the full route/controller/request/policy/service/model/job/event/UI/test chain before calling it reusable.

## Enforce the hard boundary

Never use or mutate:

- production databases, production services, shared Stage1, E7–E10, Dri, C0, quarantine/preserve-only resources, or historical logical databases;
- public ports, domains, ingress, provider calls, queues, browser credential surfaces, or raw Dokploy environment/configuration values;
- DSNs, passwords, CA material, role names, raw SQL output, or raw stderr in an artifact, invocation, log, or receipt.

Root Tailscale SSH is management transport only. It is not execution authority for a worker principal. A user’s root shell does not authorize a general worker shell, a Tailnet ACL change, or use of a shared database.

Do not treat raw Dokploy environment mutation as a sealed installer. Do not create an ad-hoc container, role, database, or secret outside the reviewed gateway.

### Optional noncanonical developer compatibility harness

The project guide may explicitly authorize a developer-local PostgreSQL
compatibility harness to accelerate migration/RLS/replay feedback. It is not a
PG proof lease and never replaces the paired capability receipts, gateway,
claim, verify-full marker set, or RC/deployment gate. Do not use one merely
because the sealed capability is absent.

Use it only when the current canonical PLAN marks the exact harness `READY`.
It must use a developer-local Docker context, a pre-existing digest-pinned
PG18/vector/vectorscale image, one fresh labeled database with no published
port/domain/consumer, a non-super/non-BYPASSRLS test role, current guarded
CHAT PostgreSQL tests, and label-scoped cleanup. It must not contact or mutate
Dokploy, a remote host, Tailnet, Stage1, production, E7-E10, Dri, C0, shared
resources, providers, or credentials. Its evidence label is only
`LOCAL_PG18_COMPATIBILITY_PROVED`; it must not emit or imitate any
`CHAT_PG18_*` receipt/terminal marker, and it cannot advance an RC, Stage1,
deployment, or live-proof result.

## Require capability before execution

First classify the evidence being requested:

- `SEALED_RC_PROOF` proves the reusable transport, credential confinement, and
  product database behavior. It requires the two capability receipts below.
- `DISPOSABLE_BEHAVIOR_PROOF` proves only the frozen migration, extension,
  role, RLS, and query behavior. Use it when the owner explicitly authorizes a
  test-only transport exception. It does **not** require the reusable gateway,
  Tailnet principal, or their receipts.

For `DISPOSABLE_BEHAVIOR_PROOF`, the Worker may use an owner-authorized
authenticated browser/API, root administration transport, or temporary test
connector to create or reach fresh isolated logical state on a non-production
test service. Credential material may exist transiently only inside the
browser or executing process; never echo, log, chat, commit, or retain it.
Require the exact frozen candidate and command, PostgreSQL 18, `vector`,
`vectorscale`, a non-super/non-BYPASSRLS role, the data-plane TLS behavior the
product test claims, a bounded collision claim, a maximum 45-minute lease, and
revoke/cleanup/residue proof. A temporary weaker control-plane transport does
not weaken those product predicates.

Do not use production, customer data, or a quarantined resource. Reuse an
existing test service only after fresh admission and only with a new isolated
database/schema and credentials; an explicitly excluded resource needs a new
owner re-admission by exact identity. Label the result
`CHAT_PG18_DISPOSABLE_BEHAVIOR_PASS`; it cannot satisfy a transport-security,
reusable-capability, deploy, or live-acceptance gate. Do not build a reusable
SSH/gateway package when this narrower proof is the requested finish line.

If the sealed gateway/principal receipts are absent, that blocks only
`SEALED_RC_PROOF`; it does not block an owner-authorized
`DISPOSABLE_BEHAVIOR_PROOF`. If a full PG/Pest suite times out or hangs,
classify it as `ROUTE_BLOCKED:SPLIT_OR_FIX_TEST` with
`ACTION_NOW=SPLIT_SUITE`: run the smallest ordered phases first
(`migration/RLS`, `replay ledger`, `delivery intent`, provider fake spines), or
fix the specific test harness. Do not create another Dokploy/Tailnet/gateway
packet merely because the suite runner failed.

The remaining receipt rules in this section apply to `SEALED_RC_PROOF`.

Do not run a PG proof until both receipts are present and independently verified.

1. `CHAT_PG18_TAILNET_PRINCIPAL_READY` contains a host-fingerprint SHA, `principal=chatproof`, `transport=OPENSSH_OVER_TAILNET`, `tailnet_tcp_rule=PASS`, `listener_bind=TAILNET_ONLY`, and `listener_identity_sha256=<64 lowercase hex>`. It conveys connectivity to that dedicated listener only—never command authority.
2. `CHAT_PG18_CAPABILITY_INSTALLED` binds the reviewed, root-owned gateway, executor and policy paths and hashes; pinned PG and runner image digests; `repository=<DEVAD_CORE_REPO>`; `principal=chatproof`; `transport=OPENSSH_OVER_TAILNET`; the same `listener_identity_sha256=<64 lowercase hex>`; a content-addressed non-secret `client_profile_path` plus matching `client_profile_sha256=<64 lowercase hex>` binding the dedicated endpoint/host-key policy; runtime limit; `fixed_shell_commands=run,reconcile`; and `sudoers_setenv=0`.

The installer must additionally prove a host-side, command-restricted
`chatproof` session gate plus a separately reviewed dedicated OpenSSH listener
channel gate;
`tailnet_accept_env=0`; `command_enforcement=HOST_SIDE_ONLY`;
`command_gate=PASS`; `channel_gate=PASS`; no PTY/port forwarding/agent
forwarding/SFTP/general shell; no SETENV sudoers; a root-only
candidate mirror; process-or-tmpfs-only secret binding; and an independently
executable nonce-scoped reconciliation handle. Tailscale SSH on Tailnet port
22 is excluded: it uses its own server and does not document the required
per-principal argv/path, PTY, agent, or forwarding controls. A reviewed
Tailnet-only traditional OpenSSH listener may use `sshd_config` and
`authorized_keys` forced-command restrictions as defense in depth, but only
when its listener identity, host impact and no-mutation matrix are bound in
the receipts. Require that matrix over the actual dedicated listener before
accepting the capability receipt. A login-shell wrapper alone cannot prove
SFTP, forwarding, agent or PTY denial; reject an unreviewed daemon-wide
disablement.

Release any collision claim only after canonical revoke, residue and nonce
reconciliation markers pass. A terminal branch, timeout or ambiguous cleanup
retains the claim for the gateway recovery owner.

If either receipt is missing, emit one sanitized boundary marker with exactly:

```text
RESUME_ON=CHAT_PG18_TAILNET_PRINCIPAL_READY+CHAT_PG18_CAPABILITY_INSTALLED
```

Keep progressing on disjoint local source work. Never retry an excluded resource or invent an alternative client path.

## Freeze and admit a one-lease proof

After capability is installed:

1. Re-hash the manifest, command bytes, candidate, lockfile, and every bound source object immediately before invocation.
2. Obtain an atomic collision reservation for the exact proof purpose.
3. Invoke only the fixed `run` command through the forced principal. The server-side gateway must create a fresh, nonshared private PG18 + vector + vectorscale resource with no published port, domain, consumer, or production attachment.
4. Keep TLS/CA/credentials inside the server process. Require verify-full TLS, a non-super/non-BYPASSRLS test role, and a server-internal bootstrap connection where the frozen suite requires it.
5. Run the exact frozen NUL-delimited test command once. Do not expand the suite, alter flags, substitute a runner image, or execute a retry.
6. Require fixed marker-only evidence for admission, candidate/source identities, private-resource/image/extension checks, verify-full TLS, role checks, test result, revocation, and zero residue.
7. Retain the collision reservation through every terminal branch until fixed revoke, residue, and nonce-scoped reconciliation markers pass. On interruption or a nonzero result, run only the fixed `reconcile` command once if the gateway’s protocol permits it; unknown cleanup is a security stop owned by the gateway recovery path.

Do not claim a general PG pass from SQLite, source review, a local Docker container, or a different database role. Do not run a PostgreSQL proof against a candidate that lacks the bound migrations/tests.

## Keep proof output safe

Output fixed status markers and hashes only. Good evidence states what passed or failed without exposing data, for example:

```text
CHAT_PG18_ADMISSION_PASS
CHAT_PG18_SOURCE_PASS
CHAT_PG18_RESOURCE_PASS
CHAT_PG18_TLS_PASS
CHAT_PG18_ROLE_PASS
CHAT_PG18_TEST_SUITE_PASS
CHAT_PG18_REVOKE_PASS
CHAT_PG18_RESIDUE_PASS
CHAT_PG18_TERMINAL
```

Use the project guide’s exact field shape for every marker; the list above is a name-only reminder, not an alternate receipt format. On failure, preserve the lease only for the gateway’s cleanup owner and report the first safe fixed terminal code plus cleanup state. Do not paste command output, environment values, network addresses, role/database names, certificate data, or test bodies.

## Update durable project state

After a successful run, update the same canonical PLAN and proof guide with the candidate identity, manifest identity, fixed terminal markers, scope actually executed, cleanup result, and remaining gates. Do not create competing packets or aliases.

Keep these distinctions explicit:

- A capability receipt authorizes a run; it is not itself a PG test result.
- A one-lease PG result does not prove browser, provider, deployment, or production behavior.
- A test role with non-BYPASSRLS authority cannot be conflated with a separate bootstrap-role phase.
- A local source/test milestone remains separate from external infrastructure acceptance.

## Recover efficiently

When blocked, first determine whether the problem is missing capability, missing frozen identity, role-phase incompatibility, resource admission, or cleanup evidence. Correct only the identified layer, then re-review and re-freeze. Avoid transport experiments, credential/UI fallbacks, and repeat runs; they consume the proof budget without improving evidence.
