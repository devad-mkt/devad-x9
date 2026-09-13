---
name: html-page-cloner
description: Build high-fidelity landing-page clones from saved browser HTML, Chrome saved-page asset folders, screenshots, DOM exports, and optional GreenShift or WordPress handoff inputs. Use when Codex must create or validate a single-file HTML/CSS/JS landing page clone, mirror a captured website locally, compare desktop and mobile screenshots, recover lazy media, inline local and remote image/font assets, or prepare a later GreenShift conversion plan after approval.
---

# HTML Page Cloner

Use this skill to rebuild a landing page as a local mirror and a single-file HTML prototype from captured browser artifacts. Default scope is HTML/CSS/JS only. Plan GreenShift or WordPress upload only after the user approves the visual clone.

## Required Inputs

- Saved source HTML, usually Chrome "Save page as complete HTML".
- Saved asset folder next to the HTML, usually `<page name>_files`.
- Desktop reference screenshot.
- Mobile reference screenshot.
- Optional DOM export, GreenShift DOM, design notes, or previous validation reports.

If any required input is missing, search the task folder first. If still missing, stop and ask for that exact artifact.

## Repo Start

1. Read the nearest `AGENTS.md`.
2. Read the project landing-page master rules, for this repo usually `WP-LP/Devad.io LP Master Rules.txt`.
3. Create or reuse a dated task folder under the project, for example `WP-LP/tasks/YYYY-MM-DD-page-name-html-clone`.
4. Keep generated HTML, screenshots, validation JSON, validation Markdown, and handoff notes inside that task folder. Do not put large generated HTML, screenshots, or videos inside this skill folder.

## Build Workflow

1. Inventory inputs: source `.html`, `_files` folder, desktop screenshot, mobile screenshot, optional DOM export.
2. Try Browser Use for current-tab inspection when the user asks for it or the target is open in the in-app browser.
3. If Browser Use screenshot or DOM capture fails, record the error and use the Chrome CDP fallback script in this skill.
4. Generate the local mirror and single-file HTML:

```powershell
node .\scripts\build-single-file.cjs `
  --source-html "D:\path\source.html" `
  --assets-dir "D:\path\source_files" `
  --out-dir "D:\path\task\prototype" `
  --name "page-clone"
```

5. For Google AI Plans style pages, pass text checks:

```powershell
node .\scripts\build-single-file.cjs `
  --source-html "D:\path\Google AI Plans with Cloud Storage - Google One.html" `
  --assets-dir "D:\path\Google AI Plans with Cloud Storage - Google One_files" `
  --out-dir "D:\path\task\prototype" `
  --name "google-ai-plans" `
  --hero-text "Power your everyday with a" `
  --compare-text "Find the right Google One plan for you" `
  --faq-text "Frequently asked questions"
```

6. Capture validation screenshots:

```powershell
node .\scripts\capture-screenshots.cjs `
  --html "D:\path\task\prototype\page-clone-single-file.html" `
  --out-dir "D:\path\task\screenshots" `
  --report "D:\path\task\validation\screenshot-report.json"
```

7. Read the generated build and screenshot reports before declaring success.
8. Compare screenshots manually against the supplied desktop and mobile references. Note known gaps.
9. Only after approval, read `references/greenshift-wordpress.md` and plan the GreenShift conversion.

## Validation Gates

The HTML clone is not ready until these are true:

| Gate | Required Result |
| --- | --- |
| Source inventory | HTML, asset folder, desktop screenshot, and mobile screenshot are found |
| Local refs | `unresolvedLocalRefsInSingle` is `0` |
| Remote image/font refs | `remainingRemoteEmbeddableAssets` is `0` |
| MP4 policy | Remote MP4 exceptions are listed, or user explicitly requested embedded videos |
| Desktop screenshot | Generated and non-empty |
| Mobile screenshot | Generated and non-empty |
| Overflow | `horizontalOverflow` is false for desktop and mobile |
| Console | No captured console errors |
| Report | Build JSON, screenshot JSON, and Markdown summaries are saved |

MP4 embedding is optional because it can make the single-file output very large. Default to remote MP4 exceptions unless the user explicitly asks for full offline animation parity.

## Browser Use Rules

- Use Browser Use when the user explicitly requests `@browser-use`, in-app browser inspection, clicking, navigation, or screenshot checks.
- Browser Use may work for navigation and metadata while screenshot or DOM capture fails with a local app-server path error. Do not loop on it.
- After two Browser Use screenshot/DOM failures, switch to `scripts/capture-screenshots.cjs` and document the fallback.
- For local `file://` screenshots, prefer Chrome CDP fallback over adding npm dependencies.

## Circuit Breakers

- Limit any repeated subtask to three attempts.
- After two failures, inspect the exact error and change strategy before a third attempt.
- If `rg` is blocked with access denied, use PowerShell `Get-ChildItem` and `Select-String`.
- If `npm` is blocked by execution policy, use the bundled or system `node.exe` directly. These scripts require no npm install.

## Bundled Resources

- `scripts/build-single-file.cjs`: builds a mirror and single-file HTML, inlines local CSS/images/fonts, fetches remote image/font assets, restores lazy video sources, adds deterministic interaction JS, and writes build reports.
- `scripts/capture-screenshots.cjs`: launches Chrome headless through DevTools Protocol, captures desktop and mobile full-page screenshots, checks overflow and console errors, and writes screenshot reports.
- `references/greenshift-wordpress.md`: load only when converting an approved clone into GreenShift or WordPress block markup.
- `references/failure-playbook.md`: load when a capture, build, Browser Use, asset inlining, or validation step fails.

## Install Note

The portable canonical copy should live in `WP-LP\skills\html-page-cloner`. After formatting the PC, copy that folder to `$CODEX_HOME\skills\html-page-cloner` or `C:\Users\<user>\.codex\skills\html-page-cloner` so Codex can discover it in new chats.
