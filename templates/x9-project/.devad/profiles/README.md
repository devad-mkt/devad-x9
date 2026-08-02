# Project profiles

The Controller-bound project profile ID maps to a filesystem-safe directory:
`profile-<sha256(canonical-profile-id)[:32]>`. Each profile keeps derived local
memory under `memory/project-memory.sqlite`; callers do not choose a database
path and profiles cannot read one another.

SQLite, WAL/SHM, migration sidecars, failed attempts, and temporary exports are
runtime state. They are ignored here and never replace Git, Controller packets,
accepted receipts, or exact source bytes as authority.
