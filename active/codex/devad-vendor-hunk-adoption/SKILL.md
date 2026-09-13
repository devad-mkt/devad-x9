---
name: devad-vendor-hunk-adoption
description: Safe vendor update adoption workflow for Devad-customized repositories. Use when comparing old upstream, new vendor packages or snapshots, and a customized Devad branch; when adopting Support Board, plugin, PHP, JS, minified JS, .htaccess, service worker, theme, AI, Slack, Boxcoin, or similar vendor changes without losing local customizations; when building protected-file manifests, hunk-level adoption reports, rollback commits, and staging deploy gates.
---

# Devad Vendor Hunk Adoption

Use this skill to adopt vendor updates into a customized Devad repo by evidence, not replacement. The default posture is protect-first, hunk-only, and reversible.

## Core Rules

- Treat vendor code as evidence, not as the deploy base.
- Never wholesale replace a customized file when a hunk-level overlay is possible.
- Never touch DB, production, `main`, live domains, secrets, config, uploads, logs, `.htaccess`, theme/CSS bundles, service workers, or core custom files unless the owner explicitly approves that exact scope.
- Preserve Devad behavior first: catalog intelligence, human-takeover suppression, tenant/workspace settings, custom routes, provisioning, storage, branding, and security hardening.
- Make small rollback commits by feature card. Avoid mixed commits that combine safe UI text with risky runtime behavior.
- Use sidecars only for bounded decisions. Codex remains responsible for the diff, verification, and final claims.

## Evidence Lanes

Build a three-way view before coding:

1. **Old clean upstream**: the previous vendor branch/package before Devad edits.
2. **New clean vendor evidence**: official ZIP/package when available. If only a live/staging full replacement snapshot exists, label it provisional evidence.
3. **Current Devad target**: the customized branch that will receive hunks.

Classify every changed file as:

- `take`: safe vendor bugfix or option with no Devad conflict.
- `adapt`: useful vendor behavior that must be rewritten around Devad custom logic.
- `defer`: needs owner decision, live config, API contract, browser proof, or more evidence.
- `reject`: theme overwrite, unrelated bundle churn, junk paths, language/media/version noise, or blind replacement.
- `protect`: Devad custom files and behaviors that must not be overwritten.

## Protected Manifest

Before edits, record:

- repo root, branch, upstream, HEAD, dirty files, and `.devad` status.
- protected files and why they are protected.
- source evidence branches/packages and SHAs.
- exact target deployment domain, if any.

If the target branch is dirty, first create a labeled baseline commit or a patch artifact that captures existing Devad changes without secrets. Exclude config and secret-bearing files from baseline patches unless the owner explicitly approves read-only inspection.

## Adoption Workflow

1. Create an isolated adoption branch or worktree from the target Devad branch.
2. Import or verify the new vendor evidence on a separate upstream/evidence branch.
3. Generate file lists and focused diffs with `git diff --name-status`, `--numstat`, and exact path filters.
4. Produce a decision table by feature card, not by file.
5. Apply one feature card at a time with manual hunks.
6. For minified JS, prefer a proven local minifier only when the repo has a reliable build path. Otherwise patch tiny minified hunks surgically and verify the exact behavior.
7. Commit each feature card separately with a clear message.
8. Update the task report after each chunk with changed files, verification, deferred items, and rollback commit.

## Verification Gates

Run only checks relevant to the touched files, but do not skip basics:

- `git diff --check`
- `git diff --name-only <previous>..HEAD` exact file-scope gate
- syntax checks such as `php -l`, `node --check`, and JSON parsing
- secret scan for changed content before pushing
- protected-file diff check against the manifest
- source evidence check for copied model names, setting IDs, URLs, or protocol details
- browser proof on staging when UI, theme, service worker, auth, chat flow, or admin settings are touched

For AI or security-sensitive hunks, add a compact sidecar review packet with exact allowed files and direct questions. Treat model output as advice only, and verify every useful claim locally.

## Deploy Gate

Deploy only to the explicitly approved staging target. Before any SSH checkout or server change, ask the owner with a loud approval gate and require an exact approval phrase.

Minimum gate text:

```text
DEPLOY APPROVAL NEEDED
Deploy branch <branch> to <staging-domain> for testing?
Reply "APPROVE <domain> deploy" to proceed.
No DB. No main. No production. No other domains.
```

If a deploy fails, roll back by checking out the previous known-good branch or SHA. Do not use destructive reset commands unless explicitly requested.

## Reporting

Report in this order:

1. TLDR status and whether `.devad` was used, missing, stale, or skipped.
2. Branch/SHA and pushed status.
3. Adopted commits by feature card.
4. Protected/excluded items.
5. Deferred owner decisions and missing evidence.
6. Verification performed and verification not performed.
7. Exact deploy gate phrase if staging is ready but not approved.
