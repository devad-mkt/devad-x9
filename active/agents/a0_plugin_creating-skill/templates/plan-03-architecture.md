# 03 — Target Architecture

End state for `<plugin-name>` at `<build-root>\<plugin-name>`. Every chunk in the plan steers toward this layout. If a chunk proposes anything outside these paths, it must add the item here first, in that same chunk, before writing code.

## 1. File layout

```
<build-root>\<plugin-name>\
├── plugin.yaml            # manifest (name ^[a-z0-9_]+$; settings_sections; scoping flags)
├── default_config.yaml    # defaults: feature toggles + per-feature settings
├── hooks.py               # lifecycle: install / pre_update / uninstall (if needed)
├── execute.py             # user-triggered setup/maintenance (if needed)
├── api\
│   └── <config>_api.py    # ApiHandler: get / set / auth_url / auth_callback
├── helpers\
│   ├── <feature>_client.py   # one client per external service
│   ├── <registry>.py         # state/credential store (NEW)
│   └── <shared>.py           # sanitize, dates, secure writes
├── tools\                 # Tool subclasses, one file per tool or per feature
├── skills\                # SKILL.md files (frontmatter: name, description)
├── webui\
│   ├── config.html        # settings UI (tabs per feature)
│   └── <feature>-store.js # Alpine store, Store Gate pattern
└── tests\
    ├── test_<feature>.py
    └── simulate_e2e.py     # fake-driven, prints ALL PASS, exit 0
```

Reference conventions: `ref/a0-plugin-contract.md` in the skill; place this tree under `usr/plugins/<plugin-name>/` when installed.

## 2. Data model

| Name | Fields | Store location |
| --- | --- | --- |
| `<credential>` | `user, scopes, created_at` | plugin data dir (0o600) |
| `<registry>` | `<id>`, label, default | registry JSON |
| `<config-view>` | feature toggles,<config keys> | `default_config.yaml` + runtime overrides |
| `<result>` | `status, message, summary` | return value only (never persisted) |

Only files under the plugin-owned data dir and config are written. No unmanaged state elsewhere.

## 3. Function signatures

```python
# NEW — <registry>; owns the keyed store.
def load_registry(config: "dict") -> "dict": ...
def get_<item>_path(config: "dict", key: str) -> Path: ...
def resolve_<item>(config: "dict", explicit: str | None = None) -> str: ...

# NEW — <feature>_client; injected for testability.
def build_<client>(<key>, config: "dict", creds=None, account=None) -> "<service>": ...

# REWRITE — split auth from the old single-entry helper.
def get_credentials(config: "dict", account: str | None = None) -> "creds": ...
def migrate_legacy_<state>(config: "dict") -> bool: ...

# NEW — tool-facing wrapper (every tool returns this).
def run_<tool>(args) -> "Response":
    return Response(message="...", break_loop=False)
```

Each function carries a 1-2 line comment in the real plan; NEW vs REWRITE marked explicitly.

## 4. Imports

```python
from usr.plugins.<plugin-name>.helpers.<feature>_client import ...
from usr.plugins.<plugin-name>.helpers.<registry> import ...
from usr.plugins.<plugin-name>.api.<config>_api import ...
```

- No `sys.path` hacks; no `from plugins.<name>...` for user plugins.
- Feature modules import helpers only, never each other.
- Type hints use `|` union syntax (Python 3.10+).

## 5. Scope / routes / UI plan

- Config keys to add: `<config-key>` (feature)<m>, `<config-key-2>` (threshold).
- API routes: `GET /plugins/<plugin-name>/<path>` and `POST /api/plugins/<plugin-name>/<handler>`.
- WebUI tabs to add: `<tab-1>`, `<tab-2>`; every store wrapped in the Store Gate pattern.
- Notifications via toastFrontendError/Success only — no inline error/success `<div>`.