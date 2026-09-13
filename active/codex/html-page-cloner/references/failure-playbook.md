# Failure Playbook

Load this reference when clone capture, build, or validation fails.

## Browser Use Fails For Screenshots Or DOM

Symptom: Browser Use can report current URL/title but screenshot or DOM actions fail with an app-server path error.

Fix:

1. Record the Browser Use error in the validation notes.
2. Stop retrying after two failures.
3. Use `scripts/capture-screenshots.cjs`, which drives installed Chrome through CDP without Playwright or Puppeteer.

## `rg` Access Denied

Symptom: `rg.exe` returns access denied in this workspace.

Fix: Use PowerShell search instead:

```powershell
Get-ChildItem -Recurse -File "D:\path" | Select-String -Pattern "needle"
```

## `npm` Blocked

Symptom: PowerShell blocks `npm.ps1` because script execution is disabled.

Fix: Run dependency-free Node scripts directly with `node` or the bundled Node runtime. Do not add npm-only validation paths unless the user approves fixing execution policy.

## No Playwright Or Puppeteer

Symptom: screenshot tooling is unavailable.

Fix: Use the Chrome DevTools Protocol script in this skill. It requires only Chrome and Node with built-in `WebSocket`.

## Chrome Profile Cleanup EPERM On Windows

Symptom: screenshot capture succeeds but cleanup fails with `EPERM, Permission denied` on `.chrome-profile-*`.

Fix: kill Chrome, wait for process exit, then retry profile deletion with backoff. The bundled screenshot script includes this retry path.

## Lazy Media Blank

Symptoms: images or videos are blank in local screenshots.

Fix:

1. Force lazy images to eager loading in the builder.
2. Inline local assets and remote image/font assets.
3. Restore video `src` from `source[data-src]`.
4. Wait before screenshot capture.
5. If the blank media is an MP4 and videos were not embedded, list it as a remote video exception.

## MP4 Size Explosion

Symptom: single-file HTML becomes too large.

Fix: Leave MP4 assets remote by default. Embed MP4 only when the user explicitly asks for full offline animation parity.

## Filenames With Parentheses

Symptom: assets like `unnamed(1).png` fail to inline when regex replacement treats parentheses as groups.

Fix: Escape regex input or use literal string replacement. The bundled builder sorts asset refs by length and replaces literal forms.

## Large Single-File Output

Symptom: output can exceed tens of MB after image/font inlining.

Fix:

1. Keep it in the task folder, not in the skill.
2. Keep videos remote unless requested.
3. Commit scripts and reports, not large generated prototypes, unless the project explicitly wants them.

## GreenShift Raw Markup Risk

Symptom: GreenShift export has raw SVG, raw HTML, or block type mismatch.

Fix:

1. Treat the export as a reference, not final import content.
2. Normalize block comments and attributes.
3. Move CSS/JS to approved manager files.
4. Re-validate block structure before WordPress upload.
