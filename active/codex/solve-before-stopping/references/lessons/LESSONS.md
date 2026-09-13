# Blocker Lessons

Read only the matching lesson. Update an existing entry when the same class is
solved again; do not append duplicates.

## L-001 — Browser bridge failure is not a product blocker

- **Symptom:** Local app responds, but the in-app browser blocks localhost or
  the authenticated Chrome bridge times out or resets.
- **Proven mistake:** The Worker pauses the feature or changes product code to
  satisfy a host browser-tool defect.
- **Fast safe route:** Try the supported alternate browser bridge once. If it
  also fails, record `BROWSER_TOOL_ONLY`, preserve any URL/auth evidence, and
  continue packet-bound source, tests, type checks, lint, and build work.
- **Hard boundary:** Do not claim screenshot, DOM, or visual acceptance without
  a functioning approved browser. Do not substitute unapproved OS automation.
- **Regression check:** Browser failure is `PARTIAL` for the visual row while
  the product lane remains active when local chunks exist.

## L-002 — Remote-main movement does not invalidate a sticky lane

- **Symptom:** A Worker repeatedly stops for rebind, rebase, worktree
  reattachment, or review while still coding its own domain.
- **Proven mistake:** Integration safety is applied to every local chunk.
- **Fast safe route:** Keep the same task, worktree, and domain branch. Mark
  `REBIND_DUE`; continue owned non-conflicting work. Perform one semantic
  rebind and one frozen review at RC/integration.
- **Hard boundary:** Stop only for an actual path/resource collision, changed
  task identity, invalidated assumption, or required shared hunk.
- **Regression check:** No new worktree, branch, rebase, or PR per ordinary
  local chunk.

## L-003 — Reuse infrastructure, never stale security state

- **Symptom:** Repeated creation of disposable PostgreSQL resources after one
  credential, lease, logical database, or UI route becomes unsafe.
- **Proven mistake:** Reusing a service is confused with reusing exposed
  credentials, nonempty databases, quarantined leases, or unknown state.
- **Fast safe route:** Inventory the existing test pool once. Reuse a managed
  service only after fresh private/no-port/no-consumer/version/extension
  admission, then use a fresh non-rendering credential epoch and clean isolated
  logical database when authorized. Separate concurrent product proofs with
  distinct database/role identities rather than new managed services.
- **Hard boundary:** Credential exposure quarantines that credential epoch.
  Never print, reopen, or authenticate with it; provider rotation or secret
  injection remains owner/capability-bound.
- **Regression check:** No new resource is created while an existing service
  can be freshly admitted, and no stale secret/logical state is reused.
  The capability owner remains active until sanitized leases are delivered.

## L-004 — A failed local tool needs a fallback, not escalation

- **Symptom:** Missing Python alias, Git metadata lock, shell quoting, fixture,
  package path, or test runner pauses the Worker.
- **Proven mistake:** Environment convenience is mistaken for missing product
  authority.
- **Fast safe route:** Use the bundled runtime, another native interface, a
  copied read-only index for derivation, or the equivalent deterministic
  command. Keep the same bytes and scope. For runtime dependencies, classify
  installed client, loadable extension, transport/listener, admitted server,
  authentication, and required state separately; test the cheapest layers and
  escalate only the first missing one.
- **Hard boundary:** Do not clean, reset, or stash user work; install
  dependencies without authority; or bypass a safety hook.
- **Regression check:** The fallback proves the same predicate and leaves no
  unclassified residue. A broad “runtime unavailable” claim identifies the
  exact first failing layer rather than requesting a replacement stack.

## L-005 — Stop micro-packet and rereview loops

- **Symptom:** One capability failure produces V2/V3 packets, repeated hashes,
  reviewer questions, reservations, and status messages without delivery.
- **Proven mistake:** Transport and narration are counted as progress.
- **Fast safe route:** Bind one outcome, batch same-root corrections, review
  stable material bytes once, execute once, then allow one read-only
  discriminator and one final execution or hard boundary.
- **Hard boundary:** New material risk, changed executable bytes, security
  exposure, or changed authority still requires the appropriate review.
- **Regression check:** Two process-only cycles trigger a delivery reset.

## L-006 — A dependency wait pauses one chunk, not the goal

- **Symptom:** A Worker says paused, frozen, or waiting because one runtime
  receipt, second login role, provider callback, or capability is missing.
- **Proven mistake:** One acceptance row is conflated with every local chunk.
- **Fast safe route:** Scan current authority for an eligible local chunk and
  the unfinished authoritative domain plan, not only the last frozen
  candidate, and start the next same-domain chunk. If none exists, declare
  `EVENT_ONLY` once with a named resume
  receipt and `ACTION_NOW: NONE_CURRENT_SCOPE_COMPLETE`; do not invent filler
  work, call preservation an action, or repeat green checks.
- **Hard boundary:** Backlog prose is not authority. New paths, semantic owners,
  providers, or runtime effects still need the correct scope grant.
- **Regression check:** `PARALLEL_LOCAL` names a real action or
  `NONE_AFTER_CURRENT_SCOPE_CHECK`; a completed scope is never labeled
  `CONTINUE_LOCAL` merely because its candidate is retained, and a five-minute
  observation counts only material source/proof/runtime progress. Exact
  authoritative-plan coverage plus current proof is
  `TERMINAL_LOCAL_COMPLETE`; it is left idle instead of being forced to invent
  another chunk, while its external remainder is routed once to an active
  capability owner.

## L-007 — Security incidents preempt only the contaminated epoch

- **Symptom:** A provider/API/UI response unexpectedly renders a credential and
  the program stops or blindly retries with a new epoch.
- **Proven mistake:** Containment is either too broad or too weak.
- **Fast safe route:** Stop reading/using the value, quarantine the exact epoch
  and route, preserve sanitized identity evidence, and continue non-secret
  local work. Route one owner/capability containment action separately.
- **Hard boundary:** No reuse, echo, logging, manual alteration, or new secret
  epoch without an approved non-rendering path and cleanup contract.
- **Regression check:** The incident receipt contains no secret value and the
  next product action does not depend on the contaminated epoch.

## L-008 — Resumed authority invalidates stale blocked state

- **Symptom:** A Worker repeats an old dependency wait after the owner resumes
  the goal or explicitly permits another same-domain local slice.
- **Proven mistake:** Thread/goal status and the last frozen candidate are
  treated as stronger than current owner authority and current source.
- **Fast safe route:** Reclassify once, trace the real plan/source owner, choose
  the highest-value authorized vertical, then move from tracing to a file,
  focused proof, or authorized runtime action. Repair ordinary command and
  harness failures locally through the proof boundary.
- **Hard boundary:** New shared paths, providers, secrets, production effects,
  destructive actions, spend, and cross-domain semantic ownership still require
  their real authority.
- **Regression check:** Within one turn after resume, an unfinished local lane
  produces a concrete diff/proof/runtime action; a truly complete lane instead
  proves exact plan coverage and remains idle.

## L-009 — A lane wait must not terminate the host goal

- **Symptom:** After the same missing receipt appears three times, a Worker
  marks its whole Codex goal blocked even though the product program has an
  active capability owner or the owner has supplied a new test route.
- **Proven mistake:** Goal-tool blocked semantics are applied to
  `DEPENDENCY_WAIT`, `EVENT_ONLY`, or `TERMINAL_LOCAL_COMPLETE`.
- **Fast safe route:** Keep the host goal resumable, route the external
  remainder to exactly one capability owner, and resume the same Worker only
  on a matching receipt or new owner authority. Owner continuation immediately
  invalidates the old blocked classification.
- **Hard boundary:** Do not invent local work or weaken product, secret,
  destructive, production, spend, or cleanup invariants merely to keep a task
  visibly active.
- **Regression check:** Three repeated lane receipts never call the host goal
  `blocked`; a disposable test exception selects a different transport while
  explicitly remaining insufficient for production transport acceptance.

## L-010 — Preferred proof route failed; preserve invariant and change mechanism

- **Symptom:** CHAT PG, Dokploy, Tailscale, Taildrop, SSH stdin, browser, or a
  wrapper harness fails and the Worker converts that preferred route failure
  into `RESUME_ON`, `HARD_BOUNDARY`, or another package/review loop.
- **Proven mistake:** The route is treated as the invariant. For CHAT PG this
  repeatedly turned disposable product-behavior proof into sealed reusable
  gateway work.
- **Fast safe route:** State the evidence target first. If it is disposable
  behavior proof, keep fresh private PG18/vector/vectorscale, exact candidate,
  non-production isolation, transient non-output secrets, timeout, cleanup, and
  marker-only receipts, then split/fix the suite or use a structurally different
  safe mechanism. Do not build another gateway unless the target is sealed RC
  transport proof.
- **Hard boundary:** Secrets, production/provider/spend, destructive action,
  shared collision, or missing owner authority still stop that action.
- **Regression check:** A failed preferred route yields `ROUTE_BLOCKED` with a
  concrete `ACTION_NOW`, not a whole-goal blocker. Missing sealed gateway
  receipts block only sealed RC proof.
