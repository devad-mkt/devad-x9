# V6-style Operating Reference

## Packet and receipt

Keep one packet per bounded outcome. It names the exact repository, worktree,
base SHA, source evidence, claimed paths, exclusions, acceptance tests,
security/release gates, rollback, STOP conditions, and next owner. A result
records the same identity plus changed paths, commands/proof references,
remaining risk, rollback, and an exact next action.

Use Git and the packet/receipt as durable truth. A message carries only task
ID plus canonical path/hash. The receiver rereads the file; it does not rely
on remembered chat context.

## Authority Envelope

Every packet binds a small authority envelope before the Worker begins:

```text
LANE_ID / TASK_ID / OWNER_ROLE
REPO / EXISTING_WORKTREE / BRANCH / BASE / HEAD
EXCLUSIVE_PATHS / SHARED_RESOURCES / COLLISION_SET
ALLOWED_ACTIONS / FORBIDDEN_EFFECTS / EXTERNAL_EFFECT_CEILING
ACCEPTANCE_PROOF / ROLLBACK / STOP_CONDITIONS
CANDIDATE_STATE: PRESERVED_CANDIDATE | INTEGRATED | LIVE_PROVED
NEXT_LOCAL | DEPENDENCY_WAIT:<EVENT>
RESUME_ON: RECEIPT_TYPE / RECEIPT_HASH / EXPIRY_RULE / NEXT_ACTION
NEXT_AUTONOMOUS_CHUNKS (packet-bound records only):
  CHUNK_ID / RECORD_SHA256 / EXACT_PATHS / ALLOWED_ACTION / REQUIRED_RECEIPTS /
  COLLISION_SET / FOCUSED_PROOF / ROLLBACK / STOP_CONDITIONS /
  CANDIDATE_STATE: READY | COMPLETE | WAITING_RECEIPT
LOCAL_CONTINUATION_RESERVE (optional, packet-bound):
  EXCLUSIVE_PATH_DOMAIN / ALLOWED_ACTION_DOMAIN / FOCUSED_PROOF / ROLLBACK /
  EFFECT_CEILING / OPTIONAL_SAME_WORKTREE_BRANCH_ROLLOVER
PRE_WAIT_SWEEP: PACKET_PATH / EXPECTED_PACKET_SHA256 / OBSERVED_PACKET_SHA256 /
  BLOCKED_CHUNK / EVENT / AUTHORIZED_CANDIDATE_COUNT+SHA256 /
  AUTHORIZED_CANDIDATE_RECORDS / INSPECTED_CANDIDATE_RECORDS+ELIGIBILITY /
  INSPECTED_CANDIDATE_COUNT+SHA256 / ELIGIBLE_CANDIDATE_RECORDS /
  ELIGIBLE_CANDIDATE_COUNT+SHA256 /
  SELECTED_CHUNK+ACTION_OR_NONE / BACKLOG_LOCALIZATION_DONE /
  LOCALIZATION_RECEIPT_PATH+SHA256 / LOCALIZATION_PACKET_SHA256 /
  LOCALIZATION_AUTHORIZED_CANDIDATES_SHA256 /
  LOCALIZATION_OUTCOME: NOT_RUN|NONE_FOUND|PROPOSAL_CREATED /
  EXPANSION_PROPOSAL_PATH+SHA256_OR_NONE / NO_AUTHORIZED_LOCAL_SLICE
```

Inside that envelope, the Worker must diagnose -> make the smallest owned
correction -> run focused proof -> continue. Parser, quoting, fixture,
harness, local-tool, and behavior-preserving claimed-path corrections do not
need Looper or Thinker permission. Keep a same-root-cause low-risk problem
local through three bounded correction cycles; those cycles do not count as
two distinct proof-bound approaches. Escalate after the third only when the
smallest next action crosses an authority boundary or cannot prove cleanup.

## Progress without a Controller

- An unavailable external receipt is
  `DEPENDENCY_WAIT:<AUTO_RESUME_EVENT>`, not a whole-task `BLOCKED` result.
  It pauses only that lane. Immediately run `PRE_WAIT_SWEEP` against the whole
  current authority envelope before saying no local route exists. Inspect every
  packet-bound `NEXT_AUTONOMOUS_CHUNKS` record: its canonical record includes
  `RECORD_SHA256`, and it is self-startable only when its paths/actions are
  strict envelope subsets, receipts are current, collision set is clear,
  proof/rollback/STOP remain valid, and it has no hard external effect. The
  stateless gate derives canonical authorized, inspected, and eligible
  inventory hashes, rejects an omitted authorized record or forged
  zero-eligible inventory, and requires the selected action to be one eligible
  `READY` record. That record is `CONTINUE_LOCAL` and starts its recorded action
  without a Looper approval. An incomplete sweep, stale
  packet/inventory pointer, or unclassified candidate is likewise
  `CONTINUE_LOCAL`; it is not permission to wait. A missing receipt alone also
  remains `CONTINUE_LOCAL` until this sweep is valid. With zero eligible
  records, do exactly one read-only backlog localization. A useful unbound local
  possibility becomes a local continuation record and starts without a Looper
  round only when that same `PROPOSAL_CREATED` receipt proves it stays in the
  packet-bound `LOCAL_CONTINUATION_RESERVE`: same objective/worktree, exclusive
  path/action domain, current proof/rollback, no shared resource, and no
  semantic or external effect. `--wait-case` returns `LOCAL_CONTINUATION_READY`.
  Anything outside the reserve remains a `CLAIM_EXPANSION_PROPOSAL` and waits
  for `CLAIM_EXPANSION_RECEIPT`; shared, semantic, security, or external-effect
  expansion remains Thinker/owner-bound. Only after no eligible candidate and
  no pending localization/continuation route, record
  `NO_AUTHORIZED_LOCAL_SLICE` once with the missing
  receipt/capability owner, preserved candidate identity, blocked chunk, and
  exact `RESUME_ON` action. Wait only for the named event; do not poll, re-run
  completed proof, or repeat the status report. A Looper cannot issue
  `CAN_CONTINUE_LOCAL:no` based on an old plan or a single completed check; it
  must cite the current `PRE_WAIT_SWEEP`. The stateless
  `style_autonomy_gate.py --wait-case` checks this admission only; it cannot
  wake a task or override a terminal host goal. On Windows PowerShell, pipe the
  JSON to `--case-stdin`; its schema selects the same classifier without quote
  loss. If a task host cannot resolve
  the default Python alias or shell hash helper, use the installed bundled
  interpreter or manually apply the same fields with an available read-only
  hash tool. That is `LOCAL_FALLBACK`, not a reason to wait, alter the
  environment, install dependencies, or ask Looper.
- A `DEPENDENCY_WAIT` gate result sets `should_subscribe=true`. Send one exact
  point-to-point handoff to the declared producer with event, consumer task,
  receipt predicate/expiry, and pre-bound resume action. The producer returns
  one sanitized terminal receipt directly to the consumer and Linker. This is
  not a dependency board, a scheduler, polling, or an approval request.
- A matching unexpired receipt matching the declared event and hash resumes the
  declared action without another review. A stale, mismatched, expired, or
  already-consumed receipt is `ZERO_DELTA`; it must not recreate work or emit a
  new escalation. The local `style_autonomy_gate.py --receipt-case` helper is a
  stateless classifier only, not a callback runtime.
- Thinker is decision-only: one stable material-diff review, a real
  architecture/security boundary, or two distinct proof-bound failures. It
  neither runs the queue nor supplies routine approvals.
- Looper is the single owner of the ordered packet/lane queue. It continues
  dependency-ready safe work and leads bounded repair/routing, without becoming
  a second project manager or taking product-coding claims.
- Linker sends only exact canonical path/hash/result-pointer signals; it never
  chooses, transforms, approves, retries, or executes work. Workers implement
  only their claimed packet paths and return proof.
- A shared-capability helper executes exactly one Looper-issued packet per
  active, non-overlapping canonical `COLLISION_SET`, not one packet globally.
  A set contains canonical resource-identity keys and any nonempty intersection
  conflicts. The Looper atomically reserves packet/hash, exact action, keys,
  and bounded expiry before dispatch. It releases the reservation only after a
  sanitized terminal receipt. Expiry alone never releases keys: one bounded
  reconciliation must first prove the executor stopped and cleanup/residue
  gates passed. It returns one sanitized terminal receipt
  and cannot select priorities, manage Workers, own policy, take product-code
  claims, create a second queue, run V7, or require a Thinker approval for a
  routine bounded repair.
- A Worker may own one lane-local `$z-subagent` helper when its question is
  decision-changing and its scope remains inside that Worker's existing
  worktree/claims and outside a shared resource. It is local, read-only, and
  reversible, has no child nesting, and cannot touch provider, production,
  secret, deploy, merge, shared-resource, security, architecture, destructive,
  spend, or owner-only operations. It may gather evidence but cannot replace a
  required Thinker or owner disposition. This is Worker-local execution, not a
  second manager or a Looper approval request.
- A `Worker Loop Fix` is a narrow STYLE skill/package/install/host-integration
  implementation Worker, not a Looper or manager; it stops after its bounded
  result. Task creation leaves `thinking` unset.
- A result is acknowledged once by rereading the durable receipt. Duplicate
  signals are zero-delta. If a signal is lost, resend the same pointer once;
  do not create a new manager, work order, or polling loop.

Before a new external capability epoch, run one targeted preflight for only
the required capability: writer/worktree identity, runtime/extensions, secret
transport, private network, rollback/backup, or browser/build support. Do not
repeat that preflight for each product chunk. Soft parser, quoting, harness,
fixture, command, and local-tool failures remain local corrections through
three same-root cycles.

## Outcome-bound delivery budget

A shared capability packet is one delivery outcome, not a sequence of
micro-packets. Before external execution, it binds the finish predicate, the
complete local preflight, focused proof, cleanup/rollback, and terminal
branches.

1. `PRE_WAIT_SWEEP` is a single local/silent check immediately before a true
   dependency wait. It is not independently routed, reviewed, or counted as
   progress.
2. Batch all same-root local corrections, then take one focused proof and one
   frozen review only if bytes materially changed or the hard boundary changed.
3. After an execution failure, perform at most one read-only discriminator.
   It leads either to one final batch/proof/execution or to one exact
   `HARD_BOUNDARY`; no V2/V3 child packet, intermediate-report review, or
   renamed retry is allowed.
4. Before an `ACTIVE` Worker starts, `--dispatch-case` requires a `READY` chunk
   or a packet-bound `LOCAL_CONTINUATION_RESERVE`; otherwise declare
   `EVENT_ONLY` with its exact receipt and do not keep a Worker open to poll,
   narrate, or invent backlog authority. A frozen prior candidate may roll over
   inside the same registered worktree only when the reserve says so and product
   bytes are clean; this never permits a new worktree, rebase, merge, or deploy.
   Do not deliver a classification-only message to an idle `EVENT_ONLY` or
   `SOURCE_COMPLETE` Worker. Wake it only for a new hash-bound `READY` mission
   or its exact matching `RESUME_ON` receipt.
5. Reservation, routing, hashing, and status changes are transport, not
   delivery. Only a focused product proof, accepted material result, or
   terminal authority boundary advances the lane.

This budget removes ceremony only. It never weakens secret non-rendering,
collision identity, cleanup, rollback, destructive, production, spend, or
owner-bound decisions.

Apply security controls proportionally to the evidence class. An explicitly
owner-authorized `DISPOSABLE_TEST_TRANSPORT` may use a temporary
non-production control plane without reusable gateway/principal receipts when
the requested outcome is product behavior only. It must retain exact
source/command binding, isolated state, product data-plane security predicates,
transient non-output secrets, collision control, expiry, and cleanup/residue
proof.
Record it as test-only evidence; never promote it to transport-security,
deployment, or live-acceptance proof.

## Sticky lane and task recovery

Keep a task, its native worktree, branch, base, and exclusive paths stable
until the bounded candidate is frozen. Remote-main movement alone is
`REBIND_DUE`, not a reason to stop local work, rebase, copy bytes, or replace a
valid candidate. Rebind at integration/release, a changed shared claim or
resource, a changed task/worktree identity, or new evidence that invalidates an
accepted assumption.

For a wrong task attachment, use this ladder once: continue in the correct
existing worktree if the same task can reach it; otherwise try one host move
that preserves it; otherwise create one successor task in the already
registered correct project. The successor rereads the compact packet and proves
`cwd`, branch, HEAD, staged state, and candidate acknowledgement before the old
task is marked superseded. Never create a replacement worktree, copy dirty
bytes, or retry attachment routes.

Looper keeps one durable ordered checklist. It serializes only packets whose
canonical resource-key `COLLISION_SET`s have a nonempty intersection;
independent lanes and lane-local helpers continue in parallel. For a shared
action, a Worker sends one `CAPABILITY_CLAIM` with packet pointer, canonical
resource keys, and exact action; the Looper atomically records packet/hash,
 action, keys, and bounded expiry before returning `CLAIM_FREE`, or returns
 `CLAIM_BUSY` on intersection. Release occurs only after a sanitized terminal
 receipt. Expiry alone never releases keys: one bounded reconciliation must
 first prove the executor stopped and cleanup/residue gates passed. This is
 collision control, not a design approval.
It
records one `AUTO_RESUME_EVENT` for each unavailable dependency and sends one
direct receipt pointer to the sticky Worker when that event is proved. A failed
callback/message route is a soft transport defect, not a product failure or a
reason to create a manager lane. A new message updates the existing lane
instead of creating another plan or queue. Only a security incident may
preempt the active item.

### Domain delivery default

Use one persistent `DOMAIN_DELIVERY_BRANCH` and existing native worktree for
each separable product domain. Multiple packet-bound local chunks accumulate on
that branch until a meaningful domain milestone; do not create per-chunk
branches, rebinds, rebases, PRs, or review rounds. `AUTOPILOT_LOCAL` starts the
next eligible local chunk and owns routine diagnosis, correction, and focused
proof without Looper approval. It cannot widen claims or cross runtime,
provider, production, secret, merge, deploy, or shared-resource boundaries.

After local proof, run `RC_BRANCH_TEST` from the exact domain branch and commit
SHA without merging or rebinding first. Stage1 is the default RC target. Testing
an unmerged branch on production needs separate exact owner approval for the
target, branch/SHA, window, rollback, and stop conditions. RC corrections stay
on the same branch and are retested there.

Only `OWNER_RC_APPROVED` and finished product coding open one bounded
current-main semantic rebind, frozen-range review, and integration disposition.
Before a Worker touches a path outside its domain envelope, it sends one
`CROSS_DOMAIN_CHANGE_NOTICE` with exact path, reason, effect, and deferral
status. Looper asks the owner only if early claim expansion, merge, or rebind is
actually required; otherwise the shared hunk waits for final integration while
the Worker continues its domain.

## Question admission

Before any external question, select exactly one:

| Class | Use it when |
| --- | --- |
| `CONTINUE_LOCAL` | Safe work, evidence gathering, coding, tests, or known next action is available. |
| `LOCAL_FALLBACK` | One preferred local route failed and a safe alternative exists. |
| `SUBAGENT_ONCE` | One difficult same-scope technical route failed; use one bounded helper. |
| `THINKER_ALLOWED` | Stable material diff, real architecture/security boundary, or two distinct proof-bound failures where judgment is needed. |
| `OWNER_REQUIRED` | Owner-only product/scope/production, secret, destructive, or spend decision. |

Missing or incomplete admission is `CONTINUE_LOCAL`, never `BLOCKED`. A
reviewer `BLOCK` with concrete findings is Worker defect evidence: fix inside
claims, rerun affected proof, and review the changed tree once.

For a deterministic answer before an outbound question, use the local,
stateless `../scripts/style_autonomy_gate.py` with this exact JSON shape:

```json
{
  "schema": "x9-style-autonomy-admission-v1",
  "architecture_security_boundary": false,
  "distinct_failed_approaches": 0,
  "judgment_needed": false,
  "owner_boundary": false,
  "same_root_cause_cycles": 0,
  "single_route_failed": false,
  "stable_material_diff": false,
  "subagent_available": false
}
```

It returns only the five classes above. Two distinct approaches require an
explicit `judgment_needed: true`; cycles 1-3 of the same root cause remain
local. Invalid input is `CONTINUE_LOCAL`.
It stores nothing, creates no task, cannot send a message, and cannot turn a
soft failure into a blocked lane. Use it only at an escalation decision; do
not add it to routine coding, test, or status cycles.

## Quarantined Controller trial

`x9-loop-code` is an experimental Controller trial for a fresh disposable
project. `devad-x9-loop` is only its compatibility name. Neither is a fallback
for ordinary work. A later classifier may expose
`STYLE_FALLBACK_AVAILABLE` only when no V7 ACTION is active and a host routing
failure is proven. It cannot bypass security, receipt, claim, provider,
deployment, destructive, or production boundaries.
