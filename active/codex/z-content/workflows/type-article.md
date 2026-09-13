# Workflow: Article / Guide — compact

Handles guides, comparisons, blog posts, listicles, scraped HTML cleanup, rewrites, and refreshes. Load `SKILL.md` first. Load `reference/conversion-copy-rules.md` for persuasion and `reference/omnichannel-search-rules.md` for full SEO+AEO+GEO output.

## Core structure

```text
H1: exact topic/entity
H2: user question
  bold source-grounded answer (<40 words; hard limit 45)
  EAV proof, examples, data, or table
H2: next question
Conclusion: only after preserved decision content
```

Use one exact H1. Convert H2s to literal questions only when meaning stays intact. Put a complete factual answer immediately after every eligible H2. Skip the snippet when the source does not support an answer. Bold the answer, not the keyword.

## Scraped/source-preservation mode

1. Read the main body; ignore navigation, sidebars, and footers.
2. Return `PAGE NOT FOUND 404`, `PAGE IS A FORUM`, `PAGE IS A LISTING`, or `PAGE IS A HOMEPAGE` for those classifications.
3. Remove only navigation, cookie/footer UI, author credits, affiliate disclosures, signup forms, bottom related links, and the original conclusion.
4. Copy first, format second. Keep every body sentence and section in order.
5. Map headings to H1–H3, bullets to `<ul><li>`, ordered steps to `<ol><li>`, and tables to semantic table tags.

Strict preservation gates:

- Keep cleaned body word count within ±10% of the source.
- Keep section paragraph depth unchanged.
- Preserve every named entity, number, price, statistic, quote, case study, caption, list item, table row, column, and recommendation.
- Never summarize, merge, or compress preserved source content unless the user explicitly requests it.
- Keep decision guides before any newly written conclusion.

## HTML and insertion rules

For raw HTML, output only valid requested article tags. Start with `<`, end with `>`, and emit no Markdown, fence, preamble, postamble, audit, or scorecard.

When product insertion is requested, use verified user/catalog/source data, add one product as the second H2, preserve surrounding source text, and add a row only when the existing comparison columns fit. Use `—` for unknown values; never invent features or reorder rows.

For non-preservation SEO work, inject question H2s, bold direct answers, metadata/schema/alt text only when the omnichannel reference is loaded, and keep source facts unchanged.

## Conversion additions

Load the conversion reference when active. Add one signaled human scenario per major section, mechanism/timing takeaway lines, image role/alt/caption markers, a consequence of the wrong choice, and a CTA bridge. Keep scenarios illustrative, claims verified, and one primary action clear.

## Conclusion and QA

Write a new conclusion only after all preserved content: summarize the value, state the decision cost, position the publication or resource, and give the requested next action.

Run the kernel QA plus:

- fidelity ±10% and entity/list/table preservation when a source exists;
- bold answer coverage under 40 words, hard limit 45;
- valid raw HTML with no Markdown when HTML is requested;
- conversion scenario, image, and CTA gates when active.
