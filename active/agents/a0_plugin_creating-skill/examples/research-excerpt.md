# Research-phase excerpt (from 01-research-summary.md)

> Demonstrates Phase 1 (Research): the "single bottleneck" that drives the whole plan.

**Single-account bottleneck (confirmed by code read):**
- `helpers/google_auth.py::_token_path(config)` → `data/token.json` (one global file)
- `get_credentials(config)` loads that one token, refreshes, returns
- `generate_auth_url(config)` → one OOB flow, PKCE verifier in one `.pkce_verifier` file
- `exchange_auth_code(config, code)` → overwrites the one `token.json`
- No account keying, no account registry, no account parameter in any tool
- Tools call `build_service("gmail", config)` — always the same account

**Config flow:** `plugins.get_plugin_config("google", agent=agent)` already returns scope-resolved config (global → project → agent profile). But auth ignores this — credentials/token live in a global `data/` dir, not in scoped config.

**A0 platform facts (section 2):**
- **Plugin discovery:** `usr/plugins/` (user, high priority) then `plugins/` (core). `plugin.yaml` manifest required.
- **Scoped config:** native, 3 scopes — agent profile > project > global; `per_project_config` / `per_agent_config` flags.
- **Secrets:** `helpers/secrets.py` — masked `§§secret(KEY)` placeholders; tokens should be masked if ever surfaced.
- **`_oauth` plugin precedent:** per-provider tokens at `usr/plugins/_oauth/<provider>/auth.json` with 0o600 perms — the convention we mirror.

**Options researched (section 3, one-liners):**
- Task-1 (multi-account): A. Account-keyed token store (WINNER, 92%) · B. Duplicate installs (35%) · C. gog/gws CLI (70%) · D. OAuth broker (55%) · E. Reuse `_oauth` registry (60%)
- Task-2 (all apps + Ads): A. Extend plugin + separate Ads plugin (WINNER, 90%) · B. CLI only (72%) · C. MCP servers (68%) · D. SaaS (65%) · E. n8n/Make/Zapier (45%)

**Google API caveat (section 4):**
- **Unverified OAuth app caveat:** sensitive scopes on a "Testing" consent screen → refresh tokens expire in 7 days (weekly re-auth) until verified. Plan must warn users and keep scopes minimal per enabled service.