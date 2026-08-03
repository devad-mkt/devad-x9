# Autopilot Install Intent And Efficient Release Flow

Classify the owner's request before installation, Controller initialization,
role creation, or an installed-state claim.

| Intent | Meaning | Allowed completion |
| --- | --- | --- |
| `STYLE_ONLY` | Use or follow named rules. Do not install a skill and do not initialize Controller state. | `STYLE_APPLIED` |
| `SKILL_ONLY` | Install, update, or verify the named packaged skill. Do not initialize a project Controller or roles. | `SKILLS_VERIFIED_EXISTING` when exact installed bytes already match; otherwise `SKILLS_INSTALLED` only after the install is proven |
| `FULL_PROJECT_LOOP` | The owner explicitly requests Loop/autopilot, or LOOPER + THINKER + LINKER + WORKER, for a named project. Install the verified package, initialize the project-local profile, enroll the requested roles, and run one bounded canary. | `LOOP_PROFILE_INITIALIZED`, then `LOOP_ACTIVATED` only after canary and activation gates pass |
| `VERIFY_ONLY` | Read-only verification. | A verification result only; never report `SKILLS_INSTALLED`, `LOOP_PROFILE_INITIALIZED`, or `LOOP_ACTIVATED` |

Resolve installation source from an explicit owner source or a configured,
hash-bound source. `devadio/x9-loop-private` branch `v7.3-lite` is this owner's
configured private-source example; it is not a universal or community default.
A repository checkout, package validation, or temporary install is not proof
that the active installed bytes changed.

## Cheap-First Gates

Run gates in this order:

1. Bind source, intent, scope, allowed target, tool/runtime availability, Git
   author, and the skill line-cap preflight.
2. Check links, paths, diff, manifest shape, and Python/PowerShell syntax.
3. Run focused regressions until the mechanically stable candidate is green.
4. Run package validation and security checks.
5. Run the full suite once.
6. Request one review of the stable staged diff only when the release contract
   requires it. Never request model judgment while a deterministic gate fails.
7. Create unchanged reviewed C1, attestation-only C2, fast-forward push, and
   remote readback.
8. Run temporary-install and live-install gates. A live replacement remains
   separately authorized and owner-run where the destructive guard applies.

After a failure, rerun the failed gate and only affected later gates. Do not
rerun an already valid full suite or review for unchanged bytes. In particular,
any deterministic false gate, including `external_wake_ready=false`, is a
typed `NO_GO` for that dependent action; do not call THINKER for an opinion.

Core Loop is event/callback driven and scheduler-independent. Project monitor
mode is `DISABLED` by default: `CORE_LOOP_READY` does not require a scheduler
provider. `EXTERNAL` evaluates a separate `EXTERNAL_WAKE_READY` gate using only
the exact project profile and approved monitor identity/hashes. Other projects'
Codex automations and unrelated OS jobs do not block core activation. The
runtime never creates, edits, runs, or approves a scheduler job.

## Quiet Autopilot

Emit progress only for a real state transition, blocker, owner action, or final
result. A background test or wait consumes no model narration. After each
completed action, immediately start the next authorized dependency-ready
action. Do not finish with `NEXT` while an in-scope action remains.

## Visible Tasks And Hidden Helpers

Visible Codex tasks and internal subagents are separate capabilities. Use the
visible task-creation tool's advertised model identifiers when creating a task;
if it advertises Luna, do not claim Luna is unavailable because an internal
subagent API exposes a different selector. Decide whether the requested actor
must be a visible task or a hidden bounded helper before creating either.
Hidden helpers never substitute for enrolled visible LOOP roles.

`smooth-coding`, `sdlc`, `xplan`, `tldr`, `devad-docs`, `devad-adoptions`, and
`dokploy` are packaged companion skills in this source release. They remain
separate skills with their own activation gates; packaging does not make them
Controller authority or require using every skill on every task.
