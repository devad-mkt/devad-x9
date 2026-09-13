# Agent Zero plugin contract (reference)

Synthesis of the Agent Zero plugin authoring system. Source: agent0ai/agent-zero skills (`a0-create-plugin`, `a0-review-plugin`, `a0-contribute-plugin`, `a0-router`, `a0-debug`) and `plugins/AGENTS.md` / `plugins/README.md`. This file is the single reference for the `a0_plugin_creating` skill.

## Manifest (plugin.yaml)

Every plugin needs a `plugin.yaml` at its root or it is **not discovered**.

```yaml
name: my_plugin              # ^[a-z0-9_]+$ ; must match directory name
title: My Plugin
description: What this plugin does.
version: 1.0.0
settings_sections:
  - agent
per_project_config: false
per_agent_config: false
always_enabled: false        # true = lock ON (framework-only; NOT for custom plugins)
```

- `name`: lowercase, numbers, underscores only (`^[a-z0-9_]+$`). Required by CI for community plugins and must exactly match the index folder name.
- **Folder name must use `[a-z0-9_]` only — never hyphens.** Python cannot import packages with hyphens, and A0 uses the folder name (not the YAML name) for WebUI routes (`/plugins/<folder>/...`) and API routes (`/api/plugins/<folder>/...`). A YAML name that differs from the folder causes silent 404s on the settings panel and broken config lookups.
- `settings_sections` valid values: `agent`, `external`, `mcp`, `developer`, `backup`. `[]` = no subsection.
- Activation defaults ON when no toggle rule exists. A plugin with `webui/config.html` must declare at least one `settings_sections` entry.

### A0's actual routing behavior (critical)

Agent Zero indexes plugins by **directory name**, not by the `name` field in `plugin.yaml`. This means:
- WebUI assets are served at `/plugins/<folder>/webui/...`
- API handlers are dispatched via `/api/plugins/<folder>/<handler>`
- `helpers.plugins.get_config("<folder>")` is how tools and APIs fetch plugin settings
- `helpers.plugins.find_plugin_dir("<folder>")` is how A0 locates the plugin directory

If the YAML `name` differs from the folder, A0 uses the **folder** everywhere. Plugin code that hardcodes the YAML name (e.g. `plugins.get_config("my_plugin")` when the folder is `my-plugin`) will silently get empty config and the WebUI settings panel will 404.

**Safe pattern:** derive the plugin name at runtime from the actual directory:
- Python: `Path(__file__).resolve().parent.parent.name`
- JavaScript: `new URL(import.meta.url).pathname.split("/").filter(Boolean)[1]`

This makes the plugin correct regardless of what the folder is named.

## Directory layout

```
usr/plugins/<name>/
  plugin.yaml           # REQUIRED manifest
  execute.py            # optional user-triggered script
  hooks.py              # optional framework runtime hooks (install | pre_update | uninstall)
  default_config.yaml   # optional settings fallback
  README.md, LICENSE, __init__.py
  agents/<profile>/agent.yaml   # optional distributed agent profiles
  api/                            # API Handlers (ApiHandler subclasses)
  tools/                          # Tool subclasses
  helpers/                        # shared Python logic
  prompts/                        # prompt templates
  conf/model_providers.yaml       # model provider add/override (bundle only; merge after base)
  extensions/
    python/<point>/               # named Python lifecycle extensions
    python/_functions/<module>/<qualname>/<start|end>/  # implicit @extensible hooks
    webui/<point>/                # HTML/JS hook extensions
  webui/
    config.html          # settings UI
    <pages>.html / <store>.js
```

- Discovery roots, in priority order: (1) `usr/plugins/<name>/` user plugins; (2) `plugins/<name>/` core/community shipped from the framework tree. Directories starting with `.` are skipped.
- Do NOT use the retired flattened extension form `extensions/python/<module>_<qualname>_<start|end>/` — only the deep `_functions/...` layout resolves.

## Import conventions

- Core plugins shipped from `plugins/` may use `plugins.<name>...`.
- User plugins under `usr/plugins/` MUST use `usr.plugins.<name>...`, and avoid `sys.path` hacks or persistent symlink-based imports.
- Correct: `from usr.plugins.<name>.helpers.module import x`, `from agent import AgentContext`, `from initialize import initialize_agent`.
- Avoid: `sys.path.insert(...)`, `from plugins.<name>...` for user plugins.

## Settings & scoping

- Plugin settings defaults belong in bundled `default_config.yaml`; runtime user settings belong under `usr/`.
- Resolution order: project/profile → project → user/profile → user plugin config → bundled `default_config.yaml`.
- `webui/config.html` binds plugin values to `config.*` and modal state/actions to `context.*` through `$store.pluginSettingsPrototype`.
- Provider overrides live in plugin `conf/model_providers.yaml` and merge after base `conf/model_providers.yaml`.
- Global and scoped activation are independent (`.toggle-1` / `.toggle-0`); `always_enabled: true` forces ON and disables toggles.

## Frontend: Store Gate + notifications

- The **Store Gate** wrapper is mandatory in any component accessing `$store`:
  ```html
  <div x-data>
    <template x-if="$store.myPluginStore">
      <div x-init="$store.myPluginStore.onOpen()" x-destroy="$store.myPluginStore.cleanup()">
        <!-- Content -->
      </div>
    </template>
  </div>
  ```
- Separate store modules (`.js`): `import { createStore } from "/js/AlpineStore.js"`, import in `<head>` via `<script type="module" src="/plugins/<name>/webui/my-store.js">`. No `alpine:init` listeners inside HTML.
- User feedback uses the A0 notification system ONLY — never inline error/success `<div>` blocks:
  - `toastFrontendError(msg, "Plugin Name")` / `toastFrontendSuccess(...)` / `toastFrontendWarning` / `toastFrontendInfo` (import from `/components/notifications/notification-store.js`).
- Plugin routes: `GET /plugins/<name>/<path>`, `POST /api/plugins/<name>/<handler>`, `POST /api/plugins` (management actions).

## hooks.py vs execute.py

- `execute.py`: manual, user-triggered setup/post-install/maintenance/repair/migration/refresh. `def main()` plus `if __name__ == "__main__": sys.exit(main())`. Return `0` success, non-zero failure, print progress. Prefer rerunnable.
- `hooks.py`: framework-internal lifecycle, loaded on demand via `helpers.plugins.call_plugin_hook(...)`. Runs in the framework runtime (`/opt/venv-a0` in Docker). Function names EXACTLY `install` / `pre_update` / `uninstall` (not `on_install`). May be sync or async; must be reversible/cleanup-safe.
- Pip installs via `sys.executable -m pip install` hit the framework venv; to install into the agent runtime (`/opt/venv`) target it explicitly from a subprocess.
- First rule of side effects: deleting a plugin leaves no leftover symlinks, services, or files outside plugin-owned paths unless documented with cleanup.

## Extension layouts

- Named lifecycle hooks: `extensions/python/<point>/`.
- Implicit `@extensible` hooks: `extensions/python/_functions/<module>/<qualname>/<start|end>/` — preserves every module and nested qualname segment.
- Frontend HTML extensions: `extensions/webui/<point>/`, root Alpine scope, `x-move-*` for static breakpoints. JS extensions: same path, export a default function.
- Banners/discovery cards via Python `banners` extensions: dicts with unique `id`, `type` (`info`/`warning`/`error` banners; `hero`/`feature` cards), `priority`, display fields (`title`, `html`, `description`, `thumbnail`, `icon`, `cta_text`, `cta_action`, `dismissible`, `cta_action`). Community = `type: "feature"`; CTA actions `open-plugin-config:<name>`, `open-plugin-hub`, `open-url:<url>`.
- `_a0_connector` history replay stays bounded: paged `connector_context_snapshot` payloads; `last_sequence` = Agent Zero log-output cursor.

## Common mistakes (table)

| Mistake | Fix |
|---|---|
| Plugin in `/a0/plugins/` instead of `/a0/usr/plugins/` | Use `usr/plugins/<name>/` |
| Forgetting `plugin.yaml` (silently not discovered) | Add manifest first |
| `from plugins.<name>` or `sys.path` hacks for user plugins | Use `usr.plugins.<name>...` |
| Missing Store Gate `$store` errors | Wrap every store component |
| Inline error/success `<div>` blocks | Use `toastFrontendError/Success` |
| Retired flattened extension path | Use `extensions/python/_functions/<module>/<qualname>/<start|end>/` |
| `hooks.py` named `on_install` etc. | Use `install` / `pre_update` / `uninstall` |
| `sys.executable -m pip` for the agent runtime | Target `/opt/venv` explicitly |
| `execute.py` without `main()` guard | Add `if __name__ == "__main__": sys.exit(main())` |
| `always_enabled: true` on a custom plugin | Reserve for framework core plugins |
| Hyphen in folder name (e.g. `my-plugin/`) | Rename to underscores: `my_plugin/` — hyphens break Python imports and A0 route matching |
| YAML `name` differs from folder name | A0 uses the folder name for routes/config; hardcode the folder name or derive dynamically |
| Hardcoded plugin name in `get_config()` / API URLs | Derive from `Path(__file__).parent.parent.name` (Python) or `import.meta.url` (JS) |

## Dry-run / self-check commands

- `python3 -c "import yaml; yaml.safe_load(open('plugin.yaml'))"`
- `python3 -m py_compile <file>.py` on every new/modified `.py`
- grep that every store name in `.js` matches `$store.<name>` in HTML, and no inline `<div>` error/success blocks
- grep for `sys.path` / `from plugins.` (must not appear for user plugins)
- confirm `hooks.py` function names and `execute.py` guard
- confirm folder name matches YAML `name` and contains no hyphens
- grep plugin code for hardcoded plugin name strings in `get_config()` / API URLs — should derive dynamically
- (optional) run the `a0-review-plugin` 4-phase audit as an independent final pass