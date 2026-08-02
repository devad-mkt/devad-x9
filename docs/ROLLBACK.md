# Rollback

The installer keeps every replaced skill under:

    CODEX_HOME/x9-install-backups/<timestamp>/

It never deletes the failed installation. On validation or swap failure it
moves new folders to x9-install-failed and restores the backup automatically.

Manual rollback:

1. Stop new X9 Loop routing.
2. Keep project loop files as evidence; they do not wake or execute anything.
3. Move current six skill folders aside.
4. Restore the timestamped backup folders to CODEX_HOME/skills.
5. Restart Codex and validate the restored skill names.

The pre-v5 archive includes exact live skill folders, a v3 ZIP, and SHA-256
checksums.
