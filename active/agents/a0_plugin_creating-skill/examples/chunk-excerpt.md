# Example — a real chunk spec (chunk-01 Auth Core)

This excerpt shows the 5 required sections from `chunk-01-auth-core.md`: Goal / Files to write / Acceptance / DO NOT.

**Wave 1. Serial. Depends on chunk-00. BLOCKS everything else.**

## Goal

Rewrite auth so N free-Gmail accounts each get their own token, with an account registry and scope-aware default resolution. Backward compatible with the existing single `token.json`.

## Files to write

### 1. NEW `plugin/google/helpers/accounts.py`

```python
def _registry_path(config) -> Path: ...          # data/accounts.json
def load_registry(config) -> dict: ...           # missing file -> empty registry
def save_registry(config, registry) -> None: ... # secure_write_json
def get_account_token_path(config, email) -> Path: ...  # sanitize email
def register_account(config, email, scopes, label="") -> None: ...  # upsert; default if first
def remove_account(config, email) -> None: ...
def resolve_account(config, agent=None, explicit=None) -> str:
    # 1. explicit if registered, else raise GoogleAuthError
    # 2. config["auth"]["default_account"] if registered
    # 3. registry["default"]
    # 4. first account in registry
    # 5. none -> raise GoogleAuthError("No Google account connected. ...")
```

### 2. REWRITE `plugin/google/helpers/google_auth.py`

Keep the ENTIRE module; change only: SERVICE_SCOPES + SERVICE_API append; `_token_path(config, account)` via `resolve_account`; `migrate_legacy_token(config)` (move legacy `token.json`, register, delete, called in `get_credentials`); PKCE per state `data/.pkce_<state>` (0o600).

## Acceptance

```bash
cd $DEVAD_TOOLS_ROOT\10-Other\0a-plugins\a0_google_suite_plus\plugin\google
python -m py_compile helpers\accounts.py helpers\google_auth.py
python -c "import sys; sys.path.insert(0,'.'); from helpers import accounts, google_auth; print('imports OK')"
python -m pytest tests\test_multi_account.py -q   # skip if chunk-11 tests missing
```
PASS = compiles + imports OK. Report exact output.

## DO NOT

- Do not change any tool files in this chunk.
- Do not remove existing public functions (`get_google_config`, `get_enabled_services`, `is_service_enabled`, `get_scopes`, `secure_write_json`).
- Do not add new pip dependencies.