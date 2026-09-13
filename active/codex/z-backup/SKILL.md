---
name: z-backup
description: Back up, verify, and restore personal Codex/X9 profile state to an owner-selected private Git remote. Use when the user asks for Codex daily backup, x9 backup, format rescue, restore after PC format, session backup, skill backup, .codex/.agents backup, GitHub backup sync, or automation of Codex personal data/customization backups.
---

# zBackup

Use this skill to preserve the local Codex profile state needed for recovery
after a PC format without committing raw auth tokens, install caches, or runtime
payloads.

## Default Paths

- Backup repo: `<backup-clone>`
- Remote: provide a private owner-selected remote through `CODEX_X9_BACKUP_REMOTE`; never use a public repository.
- Codex profile: `$HOME\.codex`
- Agents profile: `$HOME\.agents`
- OpenCode config: `$HOME\.config\opencode`

## Commands

Run a no-copy inventory first:

```powershell
& "<backup-clone>\scripts\sync-codex-x9-backup.ps1" -Mode DryRun
```

Run the daily backup and push only if checks pass:

```powershell
& "<backup-clone>\scripts\sync-codex-x9-backup.ps1" -Mode Daily -Push
```

Check a restore without writing files:

```powershell
& "<backup-clone>\scripts\restore-codex-x9-backup.ps1" -TargetProfile "$HOME" -DryRun
```

## Rules

- Read `references/backup-policy.md` before changing include/exclude rules,
  Git LFS settings, or secret handling.
- Read `references/restore-checklist.md` before restoring after a format.
- Treat `PASS` as valid only when snapshot redaction, Git commit/push, Git LFS,
  manifest, and secret-scan checks all pass.
- Treat restore as `PARTIAL` until app-layer checks can see restored threads
  and project roots. Disk files alone are not proof.
- Do not print raw secrets, auth JSON, cookies, OAuth codes, provider keys,
  or full matched secret lines.
- Include installed copies of the twenty-one X9 Loop Style/Code skills and their manifests in
  profile backup scope when policy permits.
- Project `.devad` remains source-controlled in its private project repo.
  Backup may preserve a second copy, but it never replaces project Git truth.
- Verify the X9 Loop kit README, SOURCE_MANIFEST.sha256, and benchmark
  ledger are present before calling an X9 profile backup complete.

## Status Labels

- `PASS`: backup committed and pushed, LFS active, snapshot redaction ran, no
  excluded paths tracked, and secret scan passed.
- `PARTIAL`: files copied or committed locally, but push or app-visible restore
  proof is missing.
- `BLOCKED`: secret scan, Git auth, LFS, repo access, or unsafe running Codex
  process prevents the requested action.

## Provenance (consolidated 2026-09-12)

Canonical body: `z-backup` (2026-08-13 00:38:44, 9 files, sha256 `98ff2275b2bd56ee`).

Former names now disabled: `CODEX/codex-x9-backup`, `LOOPX_PKG/codex-x9-backup`, `NINELLC/codex-x9-backup`.

Unique content from disabled copies is preserved under `references/preserved/` and is NOT authoritative; this body wins on any conflict.
