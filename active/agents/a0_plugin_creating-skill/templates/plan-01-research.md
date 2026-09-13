# 01 — Research Summary

Scope recap for `<plugin-name>`: what exists today, what the framework gives us, and the external-API facts that constrain the design. Full option scoring lives in `02-decisions-winners.md`; this file is the lightweight narrative.

## 1. Current shape

```
<build-root>\<plugin-name>\
├── plugin.yaml          # manifest: name, scoping flags, settings_sections
├── hooks.py / execute.py
├── helpers\
│   ├── <auth>.py        # e.g. ONE global credential file (bottleneck)
│   └── <client>.py
├── tools\               # N tools
├── skills\              # M skills
├── api\<config>_api.py   # get / auth_url / auth_callback / set
└── webui\config.html     # tabs: ...
```

- Services: <service-count>. Tools: <tool-count>. Skills: <skill-count>.
- **Bottleneck:** <one-line on the single problem that drives the whole plan>, e.g. "one global token.json blocks multi-account use".

## 2. Framework facts

- Discovery roots: `usr/plugins/` (user) then `plugins/` (core). `plugin.yaml` required or the plugin is silently not discovered.
- Scoped config (`per_project_config` / `per_agent_config`) resolves global → project → agent profile. Custom plugins default to `usr/plugins/`.
- Secrets & tokens use plugin-owned paths; write with 0o600 and never log them.
- Store Gate pattern required on every frontend component that touches `$store`; notifications via toastFrontendError/Success only.
- Sub-agents (`helpers/subagents.py`) let the agent execute parallel chunks.
- Toggle files (`.toggle-1` / `.toggle-0`) control activation; `always_enabled: true` is framework-only.

## 3. External-API facts

- Scope list: `s1`, `s2`, ... (add/remove per enabled feature; keep minimal).
- Rate limits: leave per service, e.g. `N req/min/property`; bursty polling must be backoff-aware.
- Auth caveats: unverified OAuth app → refresh tokens expire ~7 days; developer-token approval can take days–weeks.
- Every external call is a side effect and is banned from the dry-run test suite.

## 4. Options researched

- Full scored tables in `02-decisions-winners.md`; short list here: `<option-a>` (WINNER), `<option-b>`, `<option-c>`.