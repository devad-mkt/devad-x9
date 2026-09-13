# A0 plugin audit checklist (Mode C)

Distilled from the real post-build audit of the a0-google-suite-v2 plugins; every item below caught an actual defect during that audit. Run against any existing plugin to answer "is this healthy / what did the build miss?". Evidence per item: file + line or command output. Mark PASS / FAIL / WARN.

## 1. Side effects that outlive the plugin (highest-value check)

- [ ] `hooks.py` exists? If yes, does `install()` create anything OUTSIDE the plugin dir (copies skills to `usr/skills/`, mirrors plugin dir somewhere)?
- [ ] `uninstall()` removes EVERY directory/file `install()` created. Real bug found: `uninstall` removed 7 of 10 skills — 3 orphaned dirs left behind.
- [ ] "the plugin must leave no leftover files outside plugin-owned paths unless documented" (plugin contract in `ref/a0-plugin-contract.md`).
- [ ] Any ad-hoc copy/mirror (e.g. `shutil.copytree` to another root) has a documented cleanup path, else drop it.

## 2. File naming / stale references (grep for old names)

- [ ] User-init scripts live in `execute.py` (contract), not `initialize.py`. Real findings: 2 plugins shipped `initialize.py`; references lived in `helpers/gremlins`, `install.sh`, regression tests, READMEs, and error strings.
- [ ] Grep the WHOLE plugin for the old file name after a rename (`.` references beyond the file itself).
- [ ] `hooks.py` renamed file references updated (e.g. a self-heal in `google_auth.py` pointing at the old script name).
- [ ] Error strings tell the user to run the CURRENT script name.

## 3. Imports

- [ ] Production `.py`: no `sys.path.insert` (tests may; note which).
- [ ] `usr.plugins.<name>` used for plugin's own modules; `from plugins.<name>` WARN (only valid if the target is a bundled core plugin).
- [ ] Cross-plugin import has a fallback when target may live under either root (`usr.` then `plugins.`).

## 4. Frontend contract

- [ ] Every store-using component wrapped in the Store Gate (`<div x-data><template x-if="$store.x">...`).
- [ ] No `alpine:init` listeners inside HTML (store logic lives in `.js`).
- [ ] Store modules in `.js`: `import { createStore } from "/js/AlpineStore.js"`, imported in `<head>` as `type="module"`.
- [ ] No inline error/success `<div>` blocks bound to `store.error`/similar. Use `toastFrontendError/Success/Info` from `/components/notifications/notification-store.js`. Real fixes: replaced inline `{{error}}` div + many `codeStatus`/`alert()` patterns in both config pages.

## 5. Manifest + config

- [ ] `plugin.yaml` present + parses (YAML load OK).
- [ ] `name` matches `^[a-z0-9_]+$` and matches folder name.
- [ ] Folder name contains NO hyphens (Python cannot import `my-plugin` as a package).
- [ ] `settings_sections` non-empty if `webui/config.html` exists.
- [ ] `per_project_config` / `per_agent_config` sane; `always_enabled` NOT true on a custom plugin.
- [ ] `default_config.yaml` parses; keys match what `webui/config.html` reads.

## 5b. Folder-name routing correctness (catches 404s and silent config failures)

- [ ] A0 uses the **folder name** (not the YAML `name`) for WebUI and API routes. Verify: `grep -r "get_config(" helpers/` and `grep -r "/api/plugins/" webui/` — the plugin name in these strings must match the actual folder name, or derive dynamically.
- [ ] WebUI store JS does NOT hardcode the plugin name in API URLs. Preferred: derive from `import.meta.url` (e.g. `new URL(import.meta.url).pathname.split("/").filter(Boolean)[1]`).
- [ ] Python code does NOT hardcode the plugin name in `plugins.get_config()` / `find_plugin_dir()` calls. Preferred: derive from `Path(__file__).resolve().parent.parent.name`.
- [ ] API handler docstrings show the correct URL prefix (`/api/plugins/<folder>/...`).

## 6. Gates re-run (prove no regression)

- [ ] `python -m py_compile` on every new/modified `.py` → exit 0.
- [ ] pytest offline (`python -m pytest tests -q`) → green.
- [ ] YAML parse of `plugin.yaml` + `default_config.yaml`.
- [ ] Simulation harness (`tests/simulate_e2e.py`) → prints ALL PASS, exit 0.

## 7. Counts vs statement of claim

- [ ] services / tools / skills / helpers count matches the README and plan architecture. Real: plan claimed 31 tools, build had 34 (drift — documented, not hidden).

## 8. Output

- [ ] Write `AUDIT-REPORT.md` beside the plugin: per-item table + real commands + `priority|file|change|risk` fix plan.
- [ ] If fixes requested: apply chunk-style (smallest-first: rename, then import, then frontend), re-run the affected gate per fix, list unapplied as "recommended".