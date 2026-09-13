# Workflow: HTML Report (Enterprise, Mobile-First)

Handles: enterprise-grade single-file HTML reports rendered from data, audits, or source docs — styled cards, status badges, detail tables, alerts. Output is one self-contained .html file (no JS, no external assets except the Google Fonts link).

Load `SKILL.md` first. The design source is a private mobile summary template (kept in read-only source). The reusable skeleton lives at `assets/html-report-skeleton.html` — always start from it, never from the private example.

---

## IRON RULE: Content Only

The HTML/CSS design is FROZEN. Previous failures came from models "improving" it.

Forbidden (any single violation = failed output):
- Editing anything inside `<style>` (rules, variables, selectors, media queries).
- Renaming, adding, or inventing CSS classes.
- Changing element order, nesting, or wrapper divs of existing blocks.
- Changing inline `style="..."` attributes, the font `<link>`, colors, radii, or spacing.

Allowed:
- Replacing `{{PLACEHOLDER}}` tokens and any text node with real content.
- Duplicating or deleting WHOLE repeating blocks (a `<li>`, a `<tr>`, a `.card`, a `.highlight`) exactly as they exist in the skeleton.
- `<b>` for key facts, `<span class="k">` for field labels — these classes already exist.
- `lang`/`dir` attributes on `<html>` for LTR reports (change these two attributes only; the design holds).

If the content needs a component the skeleton lacks: fit it into the nearest existing component. Do not build a new one.

## Component Inventory (class → use)

| Component | Class / block | Purpose | Required |
|---|---|---|---|
| Header | `.header` (`h1`, `.sub`, `.meta > span > b`) | Title, purpose line, update date, 2–3 meta chips | Yes |
| Highlights | `.highlights > .highlight` (`.label`, `.label.warn`) | 2–4 top findings, one line each | Optional |
| Goals card | `.card` (indigo inline style) + `ol.goals` | Numbered key objectives / recommendations | Optional |
| Callout | `.info-card.blue` / `.info-card.red` | One focused block: diagnosis, summary, risk | Optional |
| Body section | `.card > h2.section-title + .sec-body` (`h3`, `p`, `ul.bullets`) | Narrative section with subheads and bullets | Yes (repeat) |
| Status badge | `.badge.green` / `.badge.red` / `.badge.gray` | Status chips in titles, groups, rows | As needed |
| Alert | `.alert` (`h3`, `p`, `ul`) | Critical warning, red right-border | Optional |
| Detail table | `table.med-table` — name is a frozen design token, use for ANY row-detail table | Rows with `.dname`, `.dtags`, `.detail > .k`; `tr.active`/`tr.stopped`; `.status-active`/`.status-stopped`; `.dep-hi`/`.dep-lo` | Optional (repeat) |
| Conclusion | `.conclusion` | Amber per-section or final verdict box | Recommended |
| Footer | `.footer` | One-line provenance/disclaimer | Yes |

## Fill Procedure

1. Collect all facts first (numbers, names, dates, statuses). P1 applies: never invent.
2. Copy `assets/html-report-skeleton.html` to the output path. Rename nothing.
3. Fill header → highlights → goals → callouts → body sections → tables → conclusion → footer, top to bottom.
4. Repeat table rows / bullets by duplicating existing blocks verbatim, then editing only their text nodes.
5. Delete unused optional blocks entirely (whole wrapper included).
6. Keep every figure traceable to source; cite source + date inside `.footer` or the block's text.

## HTML Report QA Additions

- [ ] `<style>` block byte-identical to the skeleton (diff it).
- [ ] Zero `{{...}}` placeholders left; zero classes outside the inventory table.
- [ ] No content copied from the personal reference example (names, dates, medical data).
- [ ] File opens standalone; renders correctly at 360px width and prints.
- [ ] Status colors consistent: green=active/good, red=critical/stopped, gray=neutral.
- [ ] Sentence rules (U1–U7) apply to the text inside every block.
