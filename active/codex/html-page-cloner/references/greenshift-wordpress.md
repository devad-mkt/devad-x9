# GreenShift And WordPress Handoff

Load this reference only after the user approves the HTML/CSS/JS clone and asks for a WordPress or GreenShift version.

## Conversion Rules

1. Treat the approved single-file clone as the visual contract.
2. Convert structure into GreenShift blocks only after approval.
3. Keep raw HTML, raw `<style>`, raw `<script>`, and inline SVG out of final import markup unless the project rules explicitly allow them.
4. Move CSS and JS into the project-approved GreenShift style/script manager path.
5. Keep block comments balanced: every `<!-- wp:* -->` needs a matching close when the block type requires it.
6. Validate block JSON before upload. Escaped attributes inside comments must parse cleanly.
7. Keep vectors as sanitized image assets or approved icon blocks rather than raw SVG pasted into post content.
8. Keep large videos as hosted media unless the user requests full offline parity.

## Known Local DOM Case

For `greenshift-one-dom.txt`, the DOM export is useful as a structural reference but not final-import-safe by itself:

| Check | Observed |
| --- | --- |
| Block comments | 323 opens / 323 closes |
| JSON parse errors | 0 |
| Raw SVG markers | 4 |
| Block types | `html`, `inner`, `none`, `text` |

Before WordPress upload, normalize block types and remove or externalize raw SVG/style/script risks according to the LP master rules and the GreenShift handover document.

## Validation Commands

Use a local structural check before upload. Example PowerShell pattern:

```powershell
$dom = Get-Content -Raw "D:\path\greenshift-dom.txt"
($dom | Select-String '<!-- wp:' -AllMatches).Matches.Count
($dom | Select-String '<!-- /wp:' -AllMatches).Matches.Count
($dom | Select-String '<svg|<style|<script' -AllMatches).Matches.Count
```

Then validate the page in WordPress preview. Do not publish directly from a first conversion.

## Upload Gate

Do not upload or modify a live WordPress page until the user approves:

- Final desktop screenshot.
- Final mobile screenshot.
- Known gaps list.
- GreenShift conversion plan.
- Target WordPress page title or slug.
