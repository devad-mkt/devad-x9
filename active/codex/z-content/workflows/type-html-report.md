# Workflow: HTML Report — compact frozen-template contract

Handles single-file, mobile-first enterprise reports with cards, badges, alerts, detail tables, and no JavaScript. Load `SKILL.md` first. Start from `assets/html-report-skeleton.html`; never use the private design source.

## Frozen design rule

Content only. Do not edit `<style>`, CSS variables/selectors/media queries, class names, inline styles, font link, colors, radii, spacing, element order, nesting, or wrappers. Replace placeholders and text nodes. Duplicate/delete only whole repeated `<li>`, `<tr>`, `.card`, or `.highlight` blocks. Change only `<html lang>`/`dir` when required.

Use the existing inventory: `.header`, `.highlights`, indigo goals `.card`, `.info-card.blue/.red`, body `.card` + `.section-title` + `.sec-body`, `.badge.green/.red/.gray`, `.alert`, `.med-table`, `.conclusion`, and `.footer`. The footer carries provenance. Use `.med-table` for row-detail tables.

## Procedure

1. Collect verified names, dates, statuses, metrics, and sources.
2. Copy the skeleton to the output path without renaming it.
3. Fill header, highlights, goals, callouts, body cards, tables, conclusion, and footer in order.
4. Delete unused optional whole blocks; repeat existing blocks verbatim before editing text.
5. Keep every figure traceable to a source and date.

## QA

- Skeleton `<style>` is byte-identical to the starting skeleton.
- No `{{...}}` placeholders remain and no class falls outside the inventory.
- No names, dates, or medical/personal data came from the private example.
- The standalone file renders at 360px and prints.
- Green/red/gray status colors remain semantically consistent.
- Kernel truth, source, sentence, and HTML hygiene checks pass.
