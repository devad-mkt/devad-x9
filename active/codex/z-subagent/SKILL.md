---
name: z-subagent
description: Route bounded workers with explicit scope, callbacks, and cost-aware proof; run the optional evidence/implementation/reviewer team loop for one bounded slice; bind worker models from the live thread/chat inventory rather than a remembered table.
---

# z-subagent

Use this entrypoint for a single bounded worker packet, or for a one-slice
evidence/implementation/reviewer team loop when the work genuinely needs three
separate roles. Bind the objective, repository/worktree, exact read/write scope,
forbidden effects, model/effort, focused proof, rollback, stop condition, and one
direct result receipt before dispatch. Keep worker work independent when claims
do not intersect; do not create a second manager, scheduler, polling loop, or
approval relay.

Workers diagnose and repair routine local failures inside their envelope. Route
only real security, architecture, destructive, secret, spend, production, or
owner boundaries upward. Meter verified result cost and stop after the bounded
proof rather than narrating or retrying.

The complete portable skill body is preserved in
`references/portable-full-skill.md`; read it when the packet needs detailed
routing, callback, or token-accounting rules.

Former names now archived as old reference: `subagents`, `x-subagent`,
`loop-subagents`, `loopsub`, `AGENTS/x-subagent`, `LOOPX/z-subagent`,
`NINELLC/x-subagent`.

## Model and profile selection (thread/chat based)

Model choice is resolved from **the runtime inventory of the thread/chat that is
actually running**, never from a remembered table. A skill cannot enforce a model
tier; it can only request, attest, and fall back honestly.

### Precedence

This section is the sole authority for binding a model or reasoning effort. Any
concrete model named elsewhere in this skill or in an archived copy
(`gpt-6-astra`, Astra-light/medium/high, Spark, Terra, Luna, Sol, Ultra) is
**historical evidence**, not a live binding. Where such a name conflicts with the
live thread/chat inventory, the live inventory wins and the conflict is recorded,
not silently reconciled.

The archived `subagents` copy records an owner policy that disallows Luna for
independent-exec routing. That intent is preserved here as a scope rule rather
than a hardcoded name: a mechanical/low tier worker is bounded to logs,
redaction, hashing, inventory, and extraction, and may not select a baseline,
approve a denominator, make architecture/security decisions, or issue final
acceptance. Where the live thread exposes a different low tier, the same bounded
scope applies to it.

### Resolve before every dispatch

1. Read the model actually serving the current thread/chat. That is the default
   for a worker unless task risk justifies an admitted change.
2. Probe the live role/model inventory exposed by the runtime for this thread.
   Do not assume a profile exists because another thread or an older run had it.
3. Pick the **lowest safe** admitted profile. Task risk and blast radius matter
   more than hierarchy; a child may run a lower or higher profile than the
   parent.
4. Escalate only on a named insufficiency - a specific failed predicate,
   cross-surface ambiguity, or verified difficult failure. Environment,
   permission, sandbox, and network failures are route corrections, never model
   escalations. Urgency alone never justifies the top rung.
5. Keep the critical decision with the parent/root. A low-tier or mechanical
   worker may do bounded logs, redaction, hashing, inventory, and extraction; it
   may not select the historical baseline, approve a retention denominator, make
   architecture/security decisions, or issue final acceptance.

### Record with every dispatch

```text
THREAD_MODEL_CONTEXT:    <model actually serving this thread/chat>
LIVE_ROLE_INVENTORY:     <roles/models the runtime exposes right now, probed>
REQUESTED_MODEL_PROFILE: <profile the packet asks for>
ADMITTED_MODEL_PROFILE:  <profile the runtime actually attested>
TOKEN_MODE:              LOW | NORMAL | <explicit critical allowance>
TOKEN_BOUNDARY:          <named files only; compact result; no broad history>
PROFILE_FALLBACK:        NONE | <requested -> admitted, with reason>
```

`REQUESTED_MODEL_PROFILE` and `ADMITTED_MODEL_PROFILE` must both be written. If
the requested profile is unavailable, mark `PROFILE_FALLBACK` with the actual
model and effort and continue only when the fallback is still safe for the task
risk; otherwise stop and return the packet. Never silently inherit the parent's
model or effort. Never claim a profile ran unless runtime telemetry attests it;
otherwise report `TOKEN_USAGE: UNKNOWN`.

A low-token instruction is a prompt boundary, not a billing guarantee. Report
actual token telemetry when available.
## Tickets evidence correction guard

For the Tickets lane, use Astra-light (`gpt-6-astra`, low) for ordinary
planning/review; Astra-high is prohibited and Astra-medium is exceptional only
for a documented critical major boundary. Every review must persist its result
to the named Markdown receipt before code is admitted; chat-only notes are
`RECEIPT_NOT_PERSISTED`.

Never treat a local `ChatAccount` row or `manual_user_id` discovery snapshot as
external ownership or tenant authorization. Classify it as
`LOCAL_OWNER_RECORD`/`LOOKUP_SNAPSHOT`; require a separately named
`AUTHENTICATED_OWNER_BINDING` or `OPERATOR_APPROVED_BINDING` plus row-level
allow/deny tests before generating an installer, direct Tickets link, visitor
session or notification target. Preserve both settings ledgers: owner
`23 parents + 25 nested = 48` and raw source `23 parents + 27 nested = 50`,
with every raw key, crosswalk and discrepancy disposition. Never delete or
merge controls to force the headline count.

### Astra quote lock: split ownership and denominators before advice

When Astra reports that CORE “has a `ChatAccount` owner” or that a feature
has “48 settings,” the dispatch is incomplete until the reviewer writes this
five-field record to the durable artifact:

```text
LOCAL_RECORD: <exact model/lookup and source anchors>
EXTERNAL_AUTHORITY: AUTHENTICATED_OWNER_BINDING | OPERATOR_APPROVED_BINDING | UNKNOWN
OWNER_COUNT: 23 parents + 25 nested = 48
RAW_COUNT: 23 parents + 27 nested = 50
ADMISSION_GATE: <dependent rows, allow/deny test, and stop condition>
```

`LOCAL_RECORD` is evidence of a CORE lookup only. `EXTERNAL_AUTHORITY` must
name the independent binding and row-level tests; otherwise it remains
`UNKNOWN` and cannot authorize an installer, direct link, visitor session or
notification. Count fields are separate ledgers, not competing guesses:
enumerate every raw key and retain the two-key discrepancy. A reviewer may
correct a prior report, but must update the plan/progress/receipt hashes in
the same turn; an unpersisted correction never changes admission.

### Correction terms (use these meanings verbatim)

| Term | Meaning | What it cannot prove |
| --- | --- | --- |
| `LOCAL_OWNER_RECORD` | A CORE model row such as `ChatAccount`, or a manual lookup/snapshot (`manual_user_id`). | External ownership, tenant authorization, installer admission, or visitor access. |
| `EXTERNAL_AUTHORITY` | An independently verified `AUTHENTICATED_OWNER_BINDING` or `OPERATOR_APPROVED_BINDING` for the exact account/workspace/public-ID/site relation. | It is not inferred from a numeric ID, active flag, email, route, or discovery result. |
| `OWNER_COUNT` | The owner-requested settings denominator: `23` parent rows plus `25` nested controls (`48`). | It is not a flat raw-row count. |
| `RAW_COUNT` | The complete source inventory: `23` parent rows plus `27` nested controls (`50`). | It is not silently reduced to `48`; the two-key discrepancy remains crosswalked. |
| `ADMISSION_GATE` | The named dependent rows, row-level allow/deny proof, and exact stop condition required before coding or release. | A reviewer message or a UI draft is not proof. |

When any term is absent or overloaded in a worker packet, return
`RECEIPT_NOT_PERSISTED`/`REQUEST_CHANGES` and require the same permitted
reviewer to repair the durable artifact before implementation.

### Astra refresh replay gate

When a later Astra refresh corrects an earlier report, persist the correction
before coding rather than treating it as chat context. The durable receipt must
record `CORRECTED_CLAIM`, `SAFE_CLASSIFICATION`, `CORRECTION_EFFECT`, and
`RECHECK_PROOF` (commands/tests plus updated plan/progress/receipt hashes).
For Tickets, `ChatAccount`/manual discovery remains local lookup evidence only
until an independent owner binding and foreign-row allow/deny tests pass; the
OWNER `23 + 25 = 48` and RAW `23 + 27 = 50` ledgers remain separate with the
full crosswalk. Packets predating the replay are stale, and a chat-only note is
`RECEIPT_NOT_PERSISTED`.

## Astra-light refresh invariant (2026-09-12)

Normalize “CORE has a `ChatAccount` owner” as local lookup evidence only:
`ChatAccount`/`manual_user_id` is `LOCAL_OWNER_RECORD`/`LOOKUP_SNAPSHOT`.
External authority requires an exact authenticated or operator-approved
account/workspace/public-ID/site binding plus same-tenant allow and
foreign/manual-unverified deny tests. Otherwise keep
`EXTERNAL_AUTHORITY=UNKNOWN` and do not admit installer, direct-link, visitor,
or notification rows.

Normalize “48 settings” as `OWNER_COUNT=23 parents + 25 nested = 48` while
retaining `RAW_COUNT=23 parents + 27 nested = 50` and the two-row crosswalk.
Parents are structural, not nested controls. Missing distinctions stale the
packet and require re-binding before code.

## Refresh-delta replay rule (2026-09-12)

Treat later Astra corrections as typed evidence deltas. Persist the quote and
keep `ChatAccount`/`manual_user_id` as `LOCAL_OWNER_RECORD`/`LOOKUP_SNAPSHOT`
only; external ownership stays `UNKNOWN` until an independently verified exact
account/workspace/public-ID/site binding plus same-tenant/foreign-row tests.
Record OWNER `23` parents + `25` nested = `48` separately from RAW `23` +
`27` nested = `50`. Rebind packet, progress, receipt and hashes, then require
the same Astra-light `ADMITTED` receipt before coding; never collapse ledgers.

### Quote-shape normalization (mandatory for similar corrections)

Do not reduce a qualified reviewer sentence to its positive noun. Persist:

```text
CLAIM_SUBJECT: <system/model/row actually observed>
OBSERVED_FACT: <bounded local fact>
LIMITER: <explicit non-proof or exclusion>
AUTHORITY_STATUS: <LOCAL_OWNER_RECORD | LOOKUP_SNAPSHOT | EXTERNAL_AUTHORITY | UNKNOWN>
COUNT_AXIS: <OWNER_COUNT | RAW_COUNT | NOT_A_COUNT>
```

“CORE has a `ChatAccount` owner, but manual discovery is not proof of external
account ownership” therefore remains local lookup evidence with
`EXTERNAL_AUTHORITY=UNKNOWN`; “48 settings” remains OWNER 23 parents + 25
nested while RAW stays 23 + 27. Missing fields require `REQUEST_CHANGES`,
persistence, hash rebinding, and the same Astra-light admission.

### Astra-light quote replay checklist (2026-09-12)

The quoted refresh is a required pre-dispatch check, not optional commentary:

```text
CLAIM_SUBJECT: CORE ChatAccount + manual discovery
OBSERVED_FACT: a local owner lookup/snapshot exists
LIMITER: manual discovery is not proof of external account ownership
AUTHORITY_STATUS: LOCAL_OWNER_RECORD | LOOKUP_SNAPSHOT | UNKNOWN
COUNT_AXIS: OWNER_COUNT=23 parents + 25 nested = 48; RAW_COUNT=23 parents + 27 nested = 50
```

The packet must name the dependent rows, same-tenant allow test, foreign/manual-unverified deny test, and exact stop condition. A missing field makes the packet stale; the same Astra-light reviewer must persist the correction and new hashes before any worker may code.

### Astra refresh quote ingestion (2026-09-12)

Persist the full qualified correction before accepting a worker packet:

```text
CLAIM_SUBJECT: CORE ChatAccount + manual discovery
OBSERVED_FACT: a local owner lookup/snapshot exists
LIMITER: manual discovery is not proof of external account ownership
AUTHORITY_STATUS: LOCAL_OWNER_RECORD | LOOKUP_SNAPSHOT | UNKNOWN
COUNT_AXIS: OWNER_COUNT=23 parents + 25 nested = 48; RAW_COUNT=23 parents + 27 nested = 50
CORRECTION_EFFECT: reopen installer/direct-link/visitor/notification rows and rebind settings crosswalk
RECHECK_PROOF: exact artifact hashes plus same-tenant allow and foreign/manual-unverified deny tests
```

Never promote a local `ChatAccount` or manual lookup into external authority,
or flatten the two count ledgers. Chat-only advice is
`RECEIPT_NOT_PERSISTED`; require the same Astra-light reviewer to persist and
re-hash the correction before code is admitted.

### Control-isolation proof guard (2026-09-12)

A denial test proves the named control only when every unrelated admission
predicate is valid first. Before claiming coverage for session expiry, contact
or conversation drift, audience/scope drift, revocation, disabled/suspended
workspace, or foreign-workspace binding, build a schema-valid eligible control,
snapshot `used_at`, session count, and `last_seen_at`, then mutate exactly one
field and assert callback-not-run plus no consume/session/last-seen mutation.
If setup fails an earlier predicate, label it `SETUP_REJECTION` and do not
count it as coverage of the intended control. Rebind the packet and receipt
when this guard exposes masked coverage.


## Team loop: evidence / implementation / reviewer

Use this loop only when one bounded slice genuinely needs three separate roles.
Otherwise dispatch one direct worker or act locally. Three roles only:

| Role | Writes? | Question it owns |
| --- | --- | --- |
| evidence | read-only | What is true today, and what could the denominator be missing? |
| implementation | owned paths only | Build the accepted delta. |
| reviewer | read-only | Try to falsify retention with concrete counterexamples. |

The parent owns integration, admission, and final truth. Roles have
non-overlapping questions; do not ask each role to redo the others' full job
merely to manufacture agreement. Reuse long-lived agents for the same role and
domain through follow-up tasks. Forbid child agents unless the owner explicitly
expands the loop.

1. Choose one channel, settings page, workflow, or feature with exact owned paths
   and a visible completion predicate. Never batch unrelated features. For an
   existing surface, first build a historical feature-retention ledger from
   immutable Git objects, current source, accepted receipts, and user-marked
   behavior. When the owner selects a prior implementation as the base, bind its
   SHA/path and feature list as `OWNER_SELECTED_BASELINE`; every row is required
   unless the owner explicitly rejects it. Do not let "divergent history"
   downgrade it.
2. Dispatch the strongest admitted evidence role with no product writes. Require
   authoritative source identity, reference behavior, UI and DOM states, hidden
   and conditional behavior, current owner, exact delta, privacy scan, and
   UNKNOWN or effect-gated boundaries.
3. Recompute evidence hashes and independently reproduce the three highest-risk
   claims. Also name and test three plausible ways the evidence denominator could
   be wrong. Reject stale authority, missing states, unsupported completeness,
   circular agreement, or a denominator that silently omits previously
   implemented behavior before coding.
4. Give the implementation worker only the accepted evidence and exact owned
   paths. Require reuse of existing components, working local interactions,
   honest disabled external effects, focused tests, and no invented provider,
   storage, or runtime contract.
5. Use a different admitted role for read-only acceptance review when possible.
   Require `PASS` or concrete `REQUEST_CHANGES`; do not reward activity or
   documentation volume.
6. Send concrete failures back to the same implementer. Permit one bounded
   correction at a time. Rerun focused proof without creating a new plan or
   packet.
7. Inspect the stable final diff, run deterministic focused checks, and exercise
   the real local browser flow at required viewports with a deterministic
   non-empty fixture when the page is data-driven. Keep SOURCE, TEST, BROWSER,
   PROVIDER, DEPLOYED, and LIVE verdicts separate.
8. Freeze the accepted slice and select the next item. Do not let evidence run
   more than one ready slice ahead of implementation. An active recovery slice
   advances only after `OWNER_ACCEPTED` or an explicit owner-approved defer;
   generic continuation text or a helper callback cannot advance it.

For serial provider/feature programmes, "one ready slice ahead" is disabled:
evidence may run for the active slice only. Later folders may exist solely as
`QUEUED_NOT_ADMITTED` routing markers and must remain unsearched/unpopulated.
Only the parent may promote the active folder through `EVIDENCE_ACCEPTED` and
`SEMANTIC_UNION_SELECTED`, after current-source verification and three omission
hypotheses. Then - and only then - implementation may continue the chosen
existing owner set.

For a recovery programme, process one area at a time. The evidence pack must
contain redacted exact-task-message extracts, immutable Git history and path
renames, current owner mapping, external/reference evidence only where useful,
and a synthesis choosing `REUSE_SHA`, `SEMANTIC_UNION`, `PROTECT_CURRENT`,
`DROP_OWNER_APPROVED`, or `DEFER_GATED`. Do not infer that newer security,
tenancy, RLS, migration, or PostgreSQL work is correct; rebind its exact
commits, tests, receipts, failure modes and negative isolation proof.

### Team-loop dispatch rules

- Use `fork_turns="none"` and include complete task-local context, paths,
  constraints, proof, and callback.
- Every write packet binds `ACTIVE_PROGRAM_PHASE`, `ACTIVE_SLICE_ID`,
  `ACTIVE_SLICE_STATE`, `ADVANCE_GATE`, absolute `TARGET_ROOT`, read-only
  `REFERENCE_ROOTS`, resolved write paths, and preimage hashes. Cross-worktree
  writes use absolute paths. Before and after each patch, verify every resolved
  path is under `TARGET_ROOT` and reference roots are unchanged.
- If a patch hits the wrong root, mutates a reference worktree, or returns
  truncated/ambiguous output, stop the slice. Restore the exact Git preimages,
  verify their hashes, record the incident, and only then retry with a smaller
  target-bound patch.
- Assign exclusive write paths. Keep evidence and review roles read-only.

### Acceptance rubric

Check every applicable item: evidence coverage and current source authority;
exact workflow and information architecture; visible, hidden, loading, empty,
error, disabled, selected, modal, and permission states; observable behavior for
every enabled control; visible reasons for unavailable effects; responsive
density, keyboard flow, labels, focus, announcements, and overflow; tenant
isolation, authorization, secret absence, and lifecycle-status honesty; reuse of
existing components and avoidance of one-file growth; behavior proof rather than
source-string assertions alone; a feature-retention matrix mapping every
previously accepted behavior to current source, a populated fixture, and rendered
interaction proof; mutually exclusive mode-to-fields matrices for conditional
settings, with inactive fields absent and excluded from validation; and no
provider, persistence, deployment, or live claim without direct proof.

### Anti-blind acceptance gate

- Agent reports are evidence candidates, never authority. The parent must
  inspect the claimed stable bytes and reproduce the highest-risk results.
- Thinker, Looper, worker, reviewer, and continuation messages cannot close,
  defer, reorder, or advance the canonical active slice. The parent must re-read
  its current row and acceptance gate before routing any proposed next task.
- For feature-rich pages, a zero-row fixture, blank/empty screenshot, route 200,
  hidden props, or string-containment test is `REQUEST_CHANGES`, not browser
  `PASS`.
- Browser proof must exercise representative list, selection, detail, enabled
  local interaction, disabled effect, invalid, recovery, keyboard, and mobile
  states.
- Before final acceptance, reconcile `previous behavior -> current owner ->
  focused test -> rendered interaction -> verdict`. Any unexplained missing row
  fails retention.
- If source history and the current packet disagree, stop implementation and
  expand the evidence denominator before editing.

### Stop and reset rules

- After two process-only turns, execute the smallest safe edit, test, or browser
  action.
- Treat a failed preferred tool or route as blocking only that proof route. Try
  the cheapest structurally different allowed route.
- Stop the slice only for a genuine product authority, destructive, secret,
  spend, production, or cross-owner boundary.
- Cap review and repair at three evidence-backed cycles. Then shrink the slice or
  identify one concrete contract contradiction.
- Never mark the wider goal blocked because one slice or external proof tier is
  pending.

### Callback contracts

```text
EVIDENCE_READY | active slice | authority | artifacts+hashes | coverage | UNKNOWN/effect gates | privacy/stale scan
CODE_READY | active slice | target root verified | reference roots unchanged | changed paths | behavior changed | focused proof | intentionally unimplemented effects
PASS | REQUEST_CHANGES | active-slice authority check | exact issue+location | observable acceptance predicate | tiered verdict
ACCEPTED_SLICE | owner acceptance/defer | source SHA/worktree | SOURCE/TEST/BROWSER/PROVIDER tiers | next slice
```

Recovery callbacks add:

```text
RECOVERY_EVIDENCE_READY | area | source thread/message anchors | branches/worktrees/merge-base/path renames | candidate SHAs | current-new protections | omissions | hashes
RECOVERY_DECISION_READY | area | REUSE_SHA/SEMANTIC_UNION/PROTECT_CURRENT/DROP_OWNER_APPROVED/DEFER_GATED | retained rows | unresolved backend | next bounded slice
```

## Admission, receipts, and recovery

Admit or decline before dispatch: use the loop only when one visible predicate,
exclusive paths, distinct evidence and review roles, planned proof, and a local
safe slice all exist. Otherwise use one direct worker or act locally. Do not loop
routine edits, vague contracts, status work, or provider/secret/production
boundaries. A missing mandatory field is `LOOPSUB_DECLINED`, not permission to
start a weaker loop.

Parent admission binds identity, dirty state, live role inventory, exclusive
paths, planned proof, forbidden effects, stop condition, the canonical active
slice, and its owner-controlled advance gate.

Chain: `ADMITTED -> EVIDENCE_ACCEPTED -> CODE_READY -> REVIEW -> REPAIR? ->
ACCEPTED`. Each receipt names parent/superseded receipt, hashes, time, and
collision state. A changed shared or untracked artifact invalidates old evidence
until rebound. Workers do not message each other or self-accept; the parent
alone routes and merges. Pass only objective, base/hash, paths, accepted
evidence pointers, invariants, forbidden effects, proof, stop condition, and
callback. Do not pass raw chat, broad logs, or worker transcripts.

Recovery receipts also list `RETAINED`, `EXTENDED`, `OWNER_DROPPED`,
`DEFER_GATED`, `UNRESOLVED_BACKEND`, `POPULATED_BROWSER`, and
`NEGATIVE_TENANCY_SECURITY_PROOF`. A reviewer compares these rows with the owner
denominator and searches for missing behavior; agreement with the worker is not
a review method.

For recovery/restore/exact-parity slices, admission additionally requires
`HISTORY_START`, `SOURCE_THREAD_IDS`, `HISTORICAL_BRANCHES_SEARCHED`,
`WORKTREES_SEARCHED`, `MERGE_BASE`, `PATH_RENAMES`, `OWNER_SELECTED_BASELINE`,
`CURRENT_NEW_WORK_TO_PROTECT`, and a row-level retention denominator. The
historian must use immutable Git objects and exact task-message anchors. Chat
summaries are discovery evidence, not code authority. No implementer starts until
the parent independently verifies the baseline and three likely omission
hypotheses.

A zero-row screen, screenshot, route 200, string assertion, timeout summary, or
prose green claim is never Browser `PASS` for a feature-rich surface.

Detailed admission, proof, and pilot material is preserved at
`references/admission-and-receipts.md`, `references/proof-and-recovery.md`, and
`references/pilot-evaluation.md`.

## Concurrency, dispatch mechanics, and cost

### Long-Running Goal Mode

For a large, multi-chunk goal, the accountable manager may run up to **three
active subagents at once** when the lanes are genuinely independent and the extra
concurrency reduces wall time: one implementation writer; one disjoint
source/contract mapper or second writer in a separate worktree; one disjoint
reviewer, verifier, or second independent product lane. Use fewer than three
whenever fewer lanes are dependency-ready. Three is a ceiling, not a target.

- Keep one accountable manager for current truth, authority, Work Orders,
  verification, serial integration, and the final user-facing result.
- An optional project THINKER stays idle between consultations. Ask it before a
  non-deterministic hard blocker, a material sequence or contract change, after
  two distinct failed approaches, or at an architecture, security, destructive,
  or irreversible boundary. It advises; it does not implement or compete with
  the manager.
- Subagents have separate reasoning sessions but may share a filesystem. Every
  lane needs an exact worktree, base SHA, owned paths, resources, exclusions,
  tests, and callback.
- Never allow overlapping writers. A second or third writer requires separate
  worktrees, pairwise-disjoint paths, resources, and dependencies, plus a named
  serial integration order.
- No child nesting. The manager must be able to name every live agent and claim.
- Use live states: `PLANNED`, `DISPATCHED`, `ACKED_RUNNING`, `DONE`, `BLOCKED`,
  and `STOPPED`. Never call work active before live acknowledgement.
- A lane-local blocker pauses only that lane. Release its claims and continue
  the next dependency-ready disjoint lane.

Delivery loop:

`MAP -> FREEZE CONTRACT -> HASH-BOUND WORK ORDER -> IMPLEMENT -> SELF-GATE -> FREEZE DIFF -> INDEPENDENT REVIEW -> CALLBACK -> MANAGER VERIFY -> SERIAL INTEGRATION -> NEXT WHOLE MISSION`

### Default Concurrency Budget

- Allow at most **one active subagent per parent task**. An agent is active from
  spawn until it returns, is cancelled, or is explicitly stopped.
- Do not spawn a second agent while one is active. Do not let a child spawn its
  own children.
- Long-Running Goal Mode above overrides this ordinary-task default and permits
  up to three active subagents with pairwise-disjoint claims and a credible
  wall-time benefit.
- Outside Long-Running Goal Mode, parallel subagents require an explicit owner
  request plus disjoint objectives, non-overlapping write scopes, and a credible
  wall-time benefit. A large task or deep model alone is not enough.
- One-at-a-time is a ceiling, not a target. Do not delegate work the parent can
  finish faster with one or two direct reads or commands.
- Never use a subagent for deterministic transport, waiting, polling, hashing,
  status relay, formatting, or a command whose output the parent can inspect
  directly.
- Do not duplicate a slow child's objective in the parent. Continue only disjoint
  main-lane work; if the child is no longer useful, cancel it before taking over.
- Dispatch once and wait once with a bounded timeout. One focused follow-up is
  allowed when new evidence makes it necessary; repeated follow-ups or polling
  require stopping the agent and simplifying the route.

### Runtime And Context Mechanics

- Before dispatch, inspect the live agent list and available model overrides.
  Never claim `ACKED_RUNNING` until the runtime reports the child running.
- Set the model and reasoning effort explicitly for every cost-routed spawn. Do
  not assume prose routing changes the runtime configuration.
- Prefer `fork_turns="none"` with a complete task-local packet. Use a small
  positive recent-turn fork only when those turns are necessary. Avoid
  `fork_turns="all"`: it copies noisy history, increases token use, and may
  prevent an explicit model override in runtimes where full-history forks must
  inherit the parent profile.
- Subagents inherit the parent turn's sandbox and approval state unless an
  available custom agent safely narrows it. Never expect a stronger model to
  bypass a filesystem, network, approval, or external-resource boundary.

### Recheck Whether Delegation Is Worth It

Evaluate delegation at all three checkpoints, not only at task start:

1. **Frame:** Delegate one independent read or hypothesis only when it saves more
   time than dispatch and synthesis cost.
2. **After first evidence or failure:** Consider one orthogonal diagnosis when it
   can change the next action; a failed route alone does not require an agent.
3. **Before final proof:** Use an independent verifier only for a material,
   nondeterministic claim not already covered by deterministic proof or a
   required review gate.

Delegate when the task is bounded and independent and has a clear read-only or
claimed-file boundary. Do not delegate when it would expose secrets, create
conflicting edits, bypass owner approval, repeat accepted proof, or cost more
than the work itself.

### Side Questions During Coding

Keep the implementation lane focused. When a coding task produces a side
question, delegate it as a **read-only side quest** if its answer is useful but
does not need the same files or an immediate decision. The side quest must not
edit code, run destructive actions, change the plan, or expand scope. Its final
response is limited to `ANSWER`, `EVIDENCE`, `BLOCKS_MAIN: yes/no`, and
`NEXT_SAFE_ACTION`. The main agent keeps coding only when `BLOCKS_MAIN: no`;
otherwise pause the affected edit, verify the answer, and decide explicitly.

### Devad X9 Workspace Boundary

When a task touches Devad or any path under `$DEVAD_ROOT`, first read `$z-x9`. Those
rules override generic workspace or worktree advice in this skill.

- Do not create loose files or new project/worktree folders at `$DEVAD_ROOT` root.
- Native Codex task worktrees belong under the host-managed `$DEVAD_ROOT\0-cdx-wt`;
  never predict, rename, or manually relocate their IDs.
- A subagent never selects or creates its own Devad worktree. The parent or host
  must provision and bind the exact path before dispatch. Treat a proposed new
  top-level `$DEVAD_ROOT` helper path as `WORKSPACE_POLICY_CONFLICT`, not as a
  manual-worktree fallback.
- New temporary artifacts belong in `$DEVAD_ROOT\.temp\<task-id-or-date-slug>`.
- External references belong in the owning registered
  `N-core-<app>-ref\<topic>\<yyyy-mm-dd>-<slug>` folder.
- Existing active or dirty noncanonical worktrees stay in place until their
  changes are classified, committed or preserved, pushed, integrated, and proven
  restorable. A subagent must not clean, remove, raw-copy, or filesystem-move a
  Git worktree.
- A Devad dispatch packet must bind the exact repository/worktree, base SHA,
  owned paths, shared-file exclusions, and allowed artifact location. If those
  facts are missing or conflict with the current registry, return
  `WORKSPACE_POLICY_MISSING` or `WORKSPACE_POLICY_CONFLICT` without product
  writes.

### Cost And Intelligence Report

After a subagent run, report one compact row:

| Profile | Intelligence evidence | Cost evidence | Result | Next |
| --- | --- | --- | --- | --- |
| Attested model and effort | Same-harness score or task-quality proof | Runtime usage or dated benchmark estimate | Pass, fail, or unknown | Stop or named escalation |

When telemetry includes `input_tokens`, `cached_input_tokens`, and
`output_tokens`, report
`approx_new_token_volume = input_tokens - cached_input_tokens + output_tokens`.
Otherwise report `Unknown`. This is not official billing. Never convert API
dollars into Codex quota without measured quota telemetry.

Record a lesson only when it is reusable: create one sanitized file under
`references/lessons/` only when the run exposes a reusable failure, a repeated
coordination problem, or comparable model/cost evidence. Never include secrets,
full sensitive prompts, or invented token figures.

## Trigger map and role boundary

| Signal | Read/use |
| --- | --- |
| Native role, packet, runtime, token question | this skill (`$z-subagent`) |
| Historical adoption/ownership rebind | `$z-native-adopt` (was `semantic-adoption`) |
| Reference evidence or privacy | `$z-evidence` |
| Canonical plan/checklist or product-candidate cutoff | `$z-plan` |
| Collision, Git/worktree, security, commit, release | `$z-loop-style` plus `$z-x9` |

Do not load all linked skills by default or duplicate their authority. Named
roles/models must be live and attested; never silently substitute, bridge, relax
permissions, or revive a stale child.

## Keep it lean

Treat the code, focused tests, browser proof, and concise callbacks as the
ledger. Do not create controller ledgers, recurring status packets, another plan
family, or loop telemetry for ordinary feature delivery.

## Preserved capabilities (merged 2026-09-12)

Unique content recovered from archived variants. The canonical body above
wins where they overlap; these sections are the non-overlapping remainder.

### From `AGENTS__x-subagent`

## Coding profiles — current pilots, not permanent defaults

### From `AGENTS__x-subagent / references / luna-coding-rules`

Sources: [official subagent documentation](https://learn.chatgpt.com/docs/agent-configuration/subagents), [model-selector bug report](https://github.com/openai/codex/issues/34964), [CLI profile-inheritance bug report](https://github.com/openai/codex/issues/33881), [community packet advice](https://www.reddit.com/r/codex/comments/1vdb20n/how_to_use_subagents_without_lighting_your_tokens/), and [community Luna efficiency discussion](https://www.reddit.com/r/codex/comments/1vh9nc6/how_to_efficiently_use_luna_max_subagents/).

### From `AGENTS__x-subagent / benchmarks / 2026-08-09-luna-vs-terra-high-rollout / REPORT`

An isolated nine-test Python fixture repaired a deterministic rollout planner: reject dependency cycles, retain the highest-ranked jobs per service, prune jobs whose prerequisites were not retained, return a deterministic topological tuple, and apply a global limit without emitting a dependent before its prerequisite.

## Accepted comparison

| Factor | Luna Max custom role | Terra High native worker |
| --- | ---:|---:|
| Runtime attestation | `gpt-5.6-luna`, `max`, V2, `luna-max-worker` | `gpt-5.6-terra`, `high`, V2, `worker` |
| Child terminal receipt | Yes | Yes |
| Manager proof | 9/9 pass; scope clean; critical diff inspected | 9/9 pass; scope clean; critical diff inspected |
| Changed files | `src/planner.py` only | `src/planner.py` only |
| Child duration | 135.159 s | **66.671 s** |
| Input / cached / output | 372,575 / 340,480 / 5,374 | 174,774 / 148,736 / 2,920 |
| Total tokens | 377,949 | **177,694** |
| Standard API-list-price equivalent* | **$0.019677** | $0.116863 |
| Result | Cost winner | Latency and lower-token winner |

\*This is an API-price equivalent, not an observable Codex plan-credit charge. It applies current Standard short-context rates: Luna $0.20/$0.02/$1.20 and Terra $2.00/$0.20/$12.00 per million input/cached-input/output tokens. Formula: `(uncached input × input rate + cached input × cached rate + output × output rate) / 1,000,000`. The [official pricing table](https://developers.openai.com/api/docs/pricing) is the source. Reasoning tokens are a subset of output and were not charged twice.

## Errors and risks observed

## Routing consequence


## Provenance (consolidated 2026-09-12; subagent family merged 2026-09-12)

Canonical body: `z-subagent`, merged from `x-subagent`
(2026-09-12 07:42:27, 77 files, sha256 `171d812a44d4bca4`).

Former names now archived as old reference (moved, never deleted):

- `subagents` -> `$CODEX_HOME\skills-archive\CODEX__subagents`
- `loop-subagents` -> `$AGENTS_HOME\skills-archive\AGENTS__loop-subagents`
- `loopsub` -> `$AGENTS_HOME\skills-archive\AGENTS__loopsub`
- `AGENTS/x-subagent`, `LOOPX/z-subagent`, `NINELLC/x-subagent` -> per-root `skills-disabled`

Unique content from archived copies is preserved under `references/preserved/`
and is NOT authoritative; this body wins on any conflict. Legacy model tables
(Spark/Terra/Luna/Sol, Astra tiers) were the one genuine conflict: they are kept
verbatim in the archive and replaced here by
"Model and profile selection (thread/chat based)".
