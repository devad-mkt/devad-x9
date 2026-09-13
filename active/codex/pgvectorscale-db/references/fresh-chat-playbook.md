# Fresh-Chat PG18 VectorScale Playbook

Use this reference after the parent `pgvectorscale-db` skill has triggered. It gives a new Codex task enough context to choose the correct next action without recovering credentials or relying on an earlier chat’s memory.

## 1. Identify the request phase

Classify the request before taking any action.

| User intent | Phase | Safe response/action |
| --- | --- | --- |
| “Prepare the PG proof”, “what is needed?” | Preparation | Read the canonical PLAN, proof guide, and manifest. Verify Git identities and report the missing receipt. |
| “Install the reusable executor/gateway” | Capability installation | Require explicit host/operator authority, then follow the reviewed installer contract. Do not substitute raw Dokploy environment editing. |
| “Run the proof” | Execution | Require both capability receipts and an active atomic collision claim. Run the exact frozen command once through the forced principal. |
| “PG failed” or “clean it up” | Recovery | Use only the reviewed `reconcile` command and its nonce handle. Do not re-run or inspect secrets. |
| “Does PG pass?” | Evidence review | Read marker-only receipts and exact hashes. Do not infer a pass from a local test or source review. |
| “Use Stage1/prod/the old database” | Rejected target | Refuse the target and cite the canonical exclusions. Request a fresh private lease instead. |

Do not blend phases. A root login, browser session, source test, or service card is evidence for only its own phase.

## 2. Build a proof worksheet before tools

### Disposable behavior-proof exception

When the owner explicitly authorizes an unsafe method for a disposable test,
classify it as `DISPOSABLE_BEHAVIOR_PROOF`, not reusable capability or RC
proof. Missing `CHAT_PG18_TAILNET_PRINCIPAL_READY` and
`CHAT_PG18_CAPABILITY_INSTALLED` receipts do not stop this mode.

Use one owner-authorized temporary browser/API/root control-plane route to a
non-production test service. Preserve exact candidate/argv, fresh isolated
logical state, PostgreSQL 18 plus `vector` and `vectorscale`, non-super and
non-BYPASSRLS execution, the data-plane TLS behavior claimed by the product
test, collision control, a maximum 45-minute lease, and revoke/zero-residue
proof. Secrets may exist only transiently in the browser or executing process
and must never be emitted or retained.

Return `CHAT_PG18_DISPOSABLE_BEHAVIOR_PASS` only. It proves product behavior,
not reusable transport confinement, deploy readiness, or live acceptance.
Never use production, customer data, or a quarantined resource. Reusing an
existing non-production test service requires fresh admission and a new
isolated database/schema and credentials; a previously excluded resource needs
explicit owner re-admission by exact identity.

Create an in-memory worksheet or a body-free local note with these fields. Do not fill any field by guessing.

```text
project/worktree:
canonical PLAN:
proof guide:
one-lease manifest path + SHA256 + bytes:
candidate commit:
lockfile identity:
bound migration/test blobs:
NUL argv SHA256 + bytes:
role phase:
excluded resources:
collision key:
capability receipt status:
tailnet-principal receipt status:
run receipt status:
cleanup/reconcile status:
```

For a CHAT proof, also distinguish fake/source-only test evidence from the selected PostgreSQL proof suite. Include a guarded test only when the manifest binds its exact blob and its database-role requirements are compatible.

## 2a. Fast resume decision table

Do this before a broad host, Dokploy, browser, or old-chat search. Fill only
from the current project guide, manifest, Git objects, and sanitized receipts.
An old result is usable only when the frozen source identities still match.

For CHAT, start with `scripts/verify-chat-pg18-preflight.ps1`. Give it only the
worktree and, when present, relative `.txt` paths under
`.devad/features/chat-full-migration-1/artifacts/` to sanitized marker-only
receipt files. It makes no network or host call and returns the first unmet
condition.

| First unmet condition | Classification | Exact safe next action | Do not do |
| --- | --- | --- | --- |
| Candidate, manifest, command, lockfile, or bound blob differs | Frozen identity mismatch | Re-freeze/review the source packet before any admission. | Run dirty bytes or amend a gateway request. |
| Reviewed gateway/executor/policy bytes do not exist | Reviewed package absent | Have the host operator prepare an independently reviewed content-addressed package. | Write an ad-hoc root script, use a generic helper, or edit Dokploy environment values. |
| `CHAT_PG18_TAILNET_PRINCIPAL_READY` is absent | Principal gate absent | Tailnet policy administrator returns the exact TCP connectivity receipt for `chatproof` to the reviewed dedicated listener. | Use root SSH, Tailscale SSH, a wildcard Unix user, or an existing service. |
| Principal is ready but the installed receipt, command-gate proof, or dedicated-listener channel-gate proof is absent | Host capability absent | Operator installs and exercises the reviewed forced-command listener gate **and** its channel gate, then returns the exact installed-capability receipt. | Treat a login-shell wrapper, Tailscale SSH policy, an unreviewed `sshd_config`/`authorized_keys` pair, a daemon-wide toggle, or a browser session as complete confinement. |
| Both receipts match but no collision claim exists | Admission not reserved | Obtain one fresh atomic claim for the exact frozen suite. | Start a service, create a database, or reserve a historical resource. |
| Claim exists but source identities changed | Claim is unusable | Gateway recovery owner reconciles it; release only after canonical revoke, residue and nonce-scoped reconciliation PASS, then re-freeze and review. | Modify argv, tests, image or role phase in place. |
| Run returned a fixed failure marker | Classified runtime result | Follow the guide's single permitted cleanup/reconcile branch. | Retry, inspect raw logs, or use a broad cleanup command. |
| Revoke/residue is failed or unknown | Security stop | Leave recovery to the nonce-scoped gateway reconciliation owner. | Release ambiguity, reuse the lease, or declare a test result. |
| All conditions hold | Ready once | Re-hash, claim, invoke fixed `run` once, validate only canonical markers. | Add test files, flags, environment variables, or a second run. |

Use this normal absent-capability handoff exactly, without an invented gateway
marker:

```text
RESUME_ON=CHAT_PG18_TAILNET_PRINCIPAL_READY+CHAT_PG18_CAPABILITY_INSTALLED
```

This handoff applies only to `SEALED_RC_PROOF`. In
`DISPOSABLE_BEHAVIOR_PROOF`, continue through the smallest authorized temporary
test route instead of building the reusable gateway.

The reusable asset is the independently reviewed gateway plus this skill. Every
request nonce, collision claim, private resource, logical database, role,
secret and TLS material belongs to one lease and must be recreated.

## 3. Safe tool selection

For `DISPOSABLE_BEHAVIOR_PROOF`, an owner-authorized browser/API/root transport
may provision or connect the bounded test lease. This is a control-plane
exception only: it does not waive product data-plane TLS/role/RLS predicates,
source/command identity, collision control, cleanup, or secret non-output.

Use the smallest tool surface that can answer the current phase. Never use a tool simply because it is authenticated.

| Tool or surface | Safe uses | Never use it for |
| --- | --- | --- |
| Local shell | Git object/blob/hash verification; file hashes; syntax checks; marker-only local records. | Printing `.env`, credentials, DSNs, certificate data, raw logs, or applying a substitute local database proof. |
| `verify-chat-pg18-preflight.ps1` | Verify the frozen CHAT manifest/argv/blob bindings and exact sanitized receipt shapes before host contact. | Contact a host, inspect Dokploy, read environment/configuration, reserve a lease, or treat a missing receipt as a runtime failure. |
| `git show` / `git hash-object` | Verify the frozen candidate and files directly from the specified commit. | Treating dirty working-tree bytes as the frozen source. |
| `dokploy` skill / read-only inventory | Search for a reviewed gateway or inspect non-secret service-card identity and public-exposure metadata. | Calling environment/config/secret endpoints, extracting raw variables, or reusing a listed historical/shared database. |
| Authenticated browser / Chrome | Inspect visible non-secret service labels, policy pages, or user-approved UI state when the correct profile is available. | Reading or rendering credentials, modifying service configuration, or treating a browser cookie as an executor lease. |
| Root Tailscale SSH | Confirm host identity, Docker/Swarm availability, and installed gateway files by non-secret markers. | Bypassing the forced `chatproof` principal, modifying Tailnet ACL policy without admin authority, executing a general shell proof, or using a shared database. |
| Forced `chatproof` principal | Execute only the installed gateway’s fixed `run` or `reconcile` actions after all gates pass. | Shell access, arbitrary argv, forwarding, PTY, environment injection, or credential inspection. |
| Collaboration / reviewer threads | Ask for file-only review, collision reservation, or marker receipt validation. | Delegating secret collection, performing unreviewed host mutation, or bypassing a collision claim. |
| Official documentation browsing | Verify changing PostgreSQL/vector/vectorscale/Tailscale/Dokploy behavior from primary sources. | Replacing the project’s frozen manifest or security contract with a generic example. |

If a tool returns an object that could contain configuration or credentials, stop before opening it unless the current proof contract explicitly permits its marker-only form.

## 4. Read in the correct order

For each new proof task, read completely:

1. The project router and the routed rules.
2. The canonical feature PLAN.
3. The frozen PG proof guide.
4. The current one-lease manifest.
5. Any already-issued marker receipts and collision receipt.

Only then inspect the named candidate using Git object reads. Do not scan unrelated repos, old worktrees, downloaded archives, browser history, passwords, or environment files for “helpful” values.

## 5. Required receipts

### Tailnet connectivity receipt

Require a sanitized receipt with exactly the transport facts:

```text
CHAT_PG18_TAILNET_PRINCIPAL_READY
host_fingerprint_sha256=<64 lowercase hex>
principal=chatproof
transport=OPENSSH_OVER_TAILNET
tailnet_tcp_rule=PASS
listener_bind=TAILNET_ONLY
listener_identity_sha256=<64 lowercase hex>
```

This proves that a task-scoped principal can reach the host. It does not grant a command or prove a gateway.

### Installed capability receipt

Require the project guide’s exact receipt shape. At minimum it must bind:

```text
CHAT_PG18_CAPABILITY_INSTALLED
gateway_path=<absolute reviewed path>
gateway_sha256=<64 lowercase hex>
executor_path=<content-addressed absolute path>
executor_sha256=<64 lowercase hex>
policy_path=<content-addressed absolute path>
policy_sha256=<64 lowercase hex>
pg_image_digest=sha256:<64 lowercase hex>
runner_image_digest=sha256:<64 lowercase hex>
repository=<exact repository>
principal=chatproof
max_runtime_seconds=<positive bounded integer>
transport=OPENSSH_OVER_TAILNET
listener_bind=TAILNET_ONLY
listener_identity_sha256=<64 lowercase hex>
client_profile_path=/usr/local/share/devad/chat-pg18-proof/profiles/<CLIENT_PROFILE_SHA256>/client.conf
client_profile_sha256=<64 lowercase hex>
fixed_shell_commands=run,reconcile
tailnet_accept_env=0
command_enforcement=HOST_SIDE_ONLY
command_gate=PASS
channel_gate=PASS
pty=0
forwarding=0
agent=0
sftp=0
general_shell=0
sudoers_setenv=0
```

The independent review must also confirm root ownership, a host-side command
gate plus the dedicated listener channel gate, no PTY/forwarding/agent/SFTP/
general shell, root-only source mirror, sealed in-process secret binding,
verify-full TLS support, a fresh private resource policy, and a nonce-scoped
reconciliation handle. Tailscale SSH routes Tailnet port 22 to its own SSH
server and warns that `authorized_keys` command restrictions are not suitable
there; it is not the `chatproof` execution transport. Tailnet policy alone does
not document argv/path or channel controls. Only the reviewed, Tailnet-only
traditional OpenSSH listener may use `sshd_config` and `authorized_keys`
forced-command controls, and it must bind its identity in both receipts. The
policy artifact and non-secret client-profile descriptor must also be
path/hash-bound; the profile hash binds the endpoint and host-key policy before
the worker invokes it. The operator must demonstrate, without a resource mutation, that only canonical
`run`/`reconcile` syntax is accepted and shell, alternate command/path, PTY,
local/reverse/dynamic forwarding, agent forwarding, SFTP and client environment
are rejected over the actual listener. A login shell cannot prove channel
controls, and a daemon-wide toggle needs a separate owner-reviewed host-impact
decision. See [Tailscale SSH](https://tailscale.com/docs/features/tailscale-ssh)
and [SSH over Tailscale](https://tailscale.com/docs/reference/ssh-over-tailscale).

### Image and extension admission

Admit only a content-addressed PostgreSQL 18 image reference. Never promote a mutable image tag to proof evidence.

The official pgvectorscale pre-built-container route uses a Timescale PostgreSQL image and supports installing `vectorscale` with its `vector` dependency. Verify the selected, digest-pinned image and fresh target database instead of trusting a registry tag or builder label:

1. Verify the registry digest, selected architecture, image metadata, and PostgreSQL major version 18.
2. In the fresh target database, verify `pg_available_extensions` exposes both `vector` and `vectorscale` with a default version.
3. Verify `pg_available_extension_versions` for each extension’s exact version, dependency (`requires`), and `superuser`/`trusted` attributes before choosing the bootstrap path.
4. Create both extensions only through the sealed bootstrap connection, then verify their installed rows and versions in `pg_extension`.

Use the current official references only to validate product support: [pgvectorscale pre-built container](https://github.com/timescale/pgvectorscale#using-a-pre-built-docker-container), [PostgreSQL 18 extension availability](https://www.postgresql.org/docs/18/view-pg-available-extensions.html), and [extension-version metadata](https://www.postgresql.org/docs/18/view-pg-available-extension-versions.html). Exact image digest, bundled pgvector version, CPU requirements, preload behavior, and TLS/network/cleanup policy are unknown until the gateway’s own admission check; never infer them from a mutable upstream tag.

### Collision receipt

Require one atomic, unexpired reservation bound to the exact candidate, resource purpose, and proof suite. Never reserve before capability review. Release it only after canonical revoke, residue and nonce-scoped reconciliation PASS; expiry, a terminal branch or ambiguous cleanup does not release the claim.

### Run receipt

Require fixed, sanitized markers that bind:

```text
admission identity
request/executor/candidate/manifest/source identities
private resource cardinality/no-port/no-domain/no-consumer status
PostgreSQL 18 + vector + vectorscale status
verify-full TLS status
role and RLS status
frozen command result
credential/role revoke result
runner/database/schema/role/secret residue result
terminal PASS or first terminal failure class
```

Do not require, retain, or print the corresponding sensitive values.

## 6. Installation requirements

Treat installation as an operator-controlled infrastructure change, not a test command. Install it only with explicit authority for the exact host and Tailnet policy.

The reviewed installer must:

1. Place a root-owned gateway at the guide’s fixed path.
2. Place a content-addressed executor and policy artifact at paths derived from their hashes.
3. Create a reviewed traditional OpenSSH listener bound only to the host Tailnet address and a reviewed non-public port, with a dedicated host key and managed noninteractive `chatproof` client identity. Tailscale SSH is management-only and is not this listener.
4. Use per-user SSHD and authorized-key controls to force the root-owned gateway, reject a shell, alternate command/path and client environment injection, and reject PTY, local/reverse/dynamic forwarding, agent/X11 forwarding and SFTP/subsystem requests. Prove command and channel gates separately with a no-mutation matrix; a login shell alone is insufficient for the channel half.
5. Limit Tailnet TCP policy to the intended dedicated listener endpoint and exact task principal, never `autogroup:nonroot`; set no `AcceptEnv` allowlist.
6. Use a root-only repository mirror that verifies candidate, lockfile, manifest, command, and bound blobs.
7. Create a fresh nonshared private PG18 + vector + vectorscale service only through the gateway.
8. Keep all password, certificate, and DSN material in server process memory, tmpfs, or an equivalent sealed reference.
9. Enforce a bounded runtime and a cleanup/reconcile protocol that can remove only the nonce-owned resource and principals.
10. Emit only the approved marker receipts.

Do not “pre-install” a generic shell helper, create a reusable superuser, publish a port, store secrets in the repository, or attach a proof database to a live app.

## 6a. Operator-to-worker handoff

Use this exact sequence when a fresh task needs to cross from installation to
execution:

1. The operator supplies a reviewed content-addressed gateway/executor/policy
   package; contract documents alone are not executable bytes.
2. The Tailnet policy administrator issues the exact TCP principal-ready
   receipt for the reviewed dedicated OpenSSH listener.
3. The operator installs and verifies both the command-restricted, no-shell
   capability and the separate channel gate over the actual dedicated listener,
   then returns the installed-capability receipt.
4. The worker independently verifies both receipts and the frozen source
   identity, obtains a claim, and invokes the exact one-lease `run` action.
5. The worker accepts only canonical marker receipts, checks zero residue and
   records the result. The next run uses a new nonce/resource/claim.

If the package, principal receipt, or installed receipt is absent, return the
current canonical `RESUME_ON` event. Do not bridge the gap with root SSH, a
Dokploy environment write, an existing database, a generic helper, or a retry.

## 7. One-lease execution algorithm

After all receipts are valid:

1. Recompute every frozen hash immediately before sending the request.
2. Verify the requested tests exist in the candidate and match the bound blobs.
3. Verify a single compatible role phase. Exclude a suite with an incompatible current-role requirement rather than changing roles ad hoc.
4. Acquire the atomic collision claim.
5. Invoke the forced gateway’s exact `run` action with the exact sealed request. Do not add a flag, environment variable, test file, image tag, or retry.
6. Consume marker-only output. If the test fails, preserve the nonce only for the gateway’s documented cleanup owner.
7. Verify revocation and zero residue. Treat unknown residue as terminal failure.
8. Release the claim only after canonical revoke, residue and nonce-scoped reconciliation PASS, then record the exact terminal result in the canonical PLAN/proof guide.

Only one execution is allowed for a frozen request. A correction needs an identified cause, revised bytes, a new review, and a new reservation.

## 8. Role-phase rules

Run a suite with one compatible current database role. For example, a normal RLS proof may require a non-super, non-BYPASSRLS current role, while a composite-tenancy bootstrap test may require a separate bootstrap role. Do not combine them in one process merely because they share a database.

Use a server-internal bootstrap connection only when the frozen test contract explicitly requires it. Do not expose it through SSH arguments, terminal output, or source configuration.

## 9. Failure handling

Classify only the first demonstrated safe failure:

| Failure | Correct response |
| --- | --- |
| Missing gateway, executor, command gate, channel gate, or installed capability receipt | Report `RESUME_ON=CHAT_PG18_TAILNET_PRINCIPAL_READY+CHAT_PG18_CAPABILITY_INSTALLED`; do not create a substitute. |
| Missing Tailnet principal | Report `RESUME_ON=CHAT_PG18_TAILNET_PRINCIPAL_READY+CHAT_PG18_CAPABILITY_INSTALLED`; host root access is not a substitute. |
| Candidate/blob/argv mismatch | Stop before resource admission; re-freeze and review the source packet. |
| Role-phase mismatch | Split/exclude the incompatible suite through a reviewed manifest change. |
| Claim unavailable | Do not run; wait for or obtain a fresh atomic claim through the approved owner. |
| Gateway execution failure | Read only the fixed marker class; reconcile once only if the gateway protocol authorizes it. |
| Cleanup/residue unknown or failed | Mark terminal cleanup failure; do not retry the proof or use a broad cleanup command. |
| Browser/Dokploy data would be required | Stop; request a reference-only operator receipt rather than rendering configuration. |

Do not write a guessed DSN, use `docker exec` against an existing resource, retry a transport, or “just verify” by opening a database shell.

## 10. New-chat response template

Use this compact opening response after reading the canonical artifacts:

```text
I will use $pgvectorscale-db. I first need to verify the frozen candidate, manifest, command, and capability receipts. I will not use production, shared Stage1, historical proof services, public ports, or credentials. If CHAT_PG18_TAILNET_PRINCIPAL_READY and CHAT_PG18_CAPABILITY_INSTALLED are present and valid, I can obtain a collision claim and run the exact one-lease command once; otherwise I will return one sanitized RESUME_ON marker and continue only disjoint local work.
```

Use this terminal success shape:

```text
CHAT_PG18_TEST_SUITE_PASS exit=0 output_sha256=<sha256>
CHAT_PG18_REVOKE_PASS
CHAT_PG18_RESIDUE_PASS runner=0 resource=0 database=0 roles=0 secrets=0 tls=0 network=0 temporary_files=0 collision_claim=0
CHAT_PG18_TERMINAL outcome=PASS cleanup=PASS residue=0 elapsed_seconds=<integer>
```

Use this gateway terminal failure shape:

```text
CHAT_PG18_TERMINAL outcome=FAIL_<FIXED_CODE> cleanup=PASS|FAIL residue=0|UNKNOWN elapsed_seconds=<integer>
```

For pre-execution blocks, use only the canonical PLAN/guide event marker and its exact `RESUME_ON`; do not invent a gateway result marker. Replace angle-bracket values only with non-secret identifiers permitted by the project guide. Never include host addresses, database names, principals beyond the approved role label, command text, or error output.

## 11. Reuse rules

Reuse the gateway and skill, not the lease, credentials, database, roles, collision claim, or request nonce.

For every new proof:

- refresh the project-specific guide and manifest;
- verify the candidate and source bindings again;
- use a fresh private resource epoch and nonce;
- obtain a fresh collision claim;
- run at most the newly frozen suite;
- retain only marker receipts and cleanup evidence.

This makes the infrastructure durable while keeping every data-bearing test lease disposable.
